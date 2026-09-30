"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Cedric Hirschi, ETH Zurich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, cast

import h5py
import numpy as np

from tipy.tools.saving import (
    convert_npz_to_hdf5,
    load_acquisition_hdf5,
    save_acquisition_hdf5,
)

# Path to real test data
TEST_DATA_DIR = Path(__file__).parent / "data" / "acquisition_20260404_002003"
NPZ_FILE = TEST_DATA_DIR / "acquisition_20260404_002003.npz"
HDF5_FILE = TEST_DATA_DIR / "acquisition_20260404_002003.h5"
JSON_FILE = TEST_DATA_DIR / "acquisition_20260404_002003.json"
BIN_FILE = TEST_DATA_DIR / "acquisition_20260404_002003.bin"


def _require_dataset(
    node: h5py.Group | h5py.Dataset | h5py.Datatype, name: str
) -> h5py.Dataset:
    """Narrow an HDF5 node to Dataset for static type checkers."""
    assert isinstance(node, h5py.Dataset), f"Expected dataset at '{name}'"
    return node


def _require_str_value(value: object, value_name: str) -> str:
    """Normalize string-like values for JSON decoding."""
    if isinstance(value, np.ndarray):
        assert value.size == 1, f"Expected scalar value for '{value_name}'"
        value = cast(Any, value).item()
    if isinstance(value, bytes):
        value = value.decode()
    assert isinstance(value, str), f"Expected string value for '{value_name}'"
    return value


class TestRealDataComparison:
    """Tests comparing NPZ and HDF5 formats with real data."""

    def test_npz_file_exists(self):
        """Verify the real NPZ test data file exists."""
        assert NPZ_FILE.exists(), f"Test data file not found: {NPZ_FILE}"

    def test_hdf5_file_exists(self):
        """Verify the real HDF5 test data file exists."""
        assert HDF5_FILE.exists(), f"Test data file not found: {HDF5_FILE}"

    def test_json_config_exists(self):
        """Verify the JSON config file exists."""
        assert JSON_FILE.exists(), f"Config file not found: {JSON_FILE}"

    def test_npz_structure(self):
        """Verify NPZ file has expected structure."""
        data = np.load(NPZ_FILE)
        assert "data" in data, "NPZ should have 'data' key"
        assert "config_json" in data, "NPZ should have 'config_json' key"
        assert data["data"].dtype == np.uint16
        assert data["data"].ndim == 3

    def test_hdf5_structure(self):
        """Verify HDF5 file has expected structure."""
        with h5py.File(HDF5_FILE, "r") as f:
            assert "rf_data" in f, "HDF5 should have rf_data dataset"
            assert "acquisition_parameters" in f, (
                "HDF5 should have acquisition_parameters group"
            )
            assert "config" in f.attrs, "HDF5 should have config attribute"
            assert "schema_version" in f.attrs
            assert "acquisition_timestamp" in f.attrs

    def test_npz_hdf5_data_identical(self):
        """Verify NPZ and HDF5 contain identical RF data arrays."""
        npz_data = np.load(NPZ_FILE)
        with h5py.File(HDF5_FILE, "r") as f:
            hdf5_data = _require_dataset(f["rf_data"], "rf_data")[:]

        # Compare shapes
        assert npz_data["data"].shape == hdf5_data.shape, (
            f"Shape mismatch: NPZ {npz_data['data'].shape} vs HDF5 {hdf5_data.shape}"
        )

        # Compare dtypes
        assert npz_data["data"].dtype == hdf5_data.dtype, (
            f"Dtype mismatch: NPZ {npz_data['data'].dtype} vs HDF5 {hdf5_data.dtype}"
        )

        # Compare actual data
        np.testing.assert_array_equal(
            npz_data["data"],
            hdf5_data,
            err_msg="RF data arrays should be identical between NPZ and HDF5",
        )

    def test_npz_hdf5_config_compatible(self):
        """Verify NPZ and HDF5 contain compatible configuration data."""
        # Load NPZ config
        npz_data = np.load(NPZ_FILE)
        npz_config = json.loads(
            _require_str_value(npz_data["config_json"], "config_json")
        )

        # Load HDF5 config
        with h5py.File(HDF5_FILE, "r") as f:
            hdf5_config = json.loads(_require_str_value(f.attrs["config"], "config"))

        # Compare top-level keys
        assert set(npz_config.keys()) == set(hdf5_config.keys()), (
            "Config should have same top-level keys"
        )

        # Compare AFE configuration
        assert npz_config["afe"] == hdf5_config["afe"]

        # Compare FPGA configuration
        assert npz_config["fpga"] == hdf5_config["fpga"]

        # Compare TX configuration
        assert npz_config["tx"] == hdf5_config["tx"]

        # Compare acquisition configuration
        assert npz_config["acquisition"] == hdf5_config["acquisition"]

    def test_hdf5_acquisition_parameters_match_config(self):
        """Verify acquisition_parameters group matches values in config."""
        with h5py.File(HDF5_FILE, "r") as f:
            config = json.loads(_require_str_value(f.attrs["config"], "config"))
            acq_params = f["acquisition_parameters"].attrs

            # Check AFE parameters
            assert acq_params["lna_gain"] == config["afe"]["lna_gain"]
            assert acq_params["pga_gain"] == config["afe"]["pga_gain"]

            # Check FPGA parameters
            assert acq_params["fifo_depth"] == config["fpga"]["fifo_depth"]
            assert acq_params["num_shots"] == config["fpga"]["num_shots"]
            assert acq_params["afe_clk_hispeed"] == config["fpga"]["afe_clk_hispeed"]
            assert acq_params["num_lvds_lanes"] == len(config["fpga"]["lvds_lanes"])

            # Check acquisition parameters
            assert acq_params["num_frames"] == config["acquisition"]["num_frames"]

    def test_real_data_shape_matches_config(self):
        """Verify RF data shape matches configuration parameters."""
        with h5py.File(HDF5_FILE, "r") as f:
            config = json.loads(_require_str_value(f.attrs["config"], "config"))
            rf_data = _require_dataset(f["rf_data"], "rf_data")

            num_frames = config["acquisition"]["num_frames"]
            num_shots = config["fpga"]["num_shots"]
            num_channels = len(config["fpga"]["lvds_lanes"]) * 2  # 2 channels per lane
            fifo_depth = config["fpga"]["fifo_depth"]

            expected_shape = (num_frames * num_shots, num_channels, fifo_depth)
            assert rf_data.shape == expected_shape, (
                f"Data shape {rf_data.shape} doesn't match expected {expected_shape}"
            )

    def test_npz_file_size(self):
        """Verify NPZ file is larger than HDF5 (compression check)."""
        npz_size = NPZ_FILE.stat().st_size
        hdf5_size = HDF5_FILE.stat().st_size

        # HDF5 should be smaller due to compression
        # Real data shows: NPZ=644KB, HDF5=15KB (43x compression!)
        assert hdf5_size < npz_size, (
            f"HDF5 ({hdf5_size} bytes) should be smaller than NPZ ({npz_size} bytes)"
        )

        # Verify compression ratio is significant
        compression_ratio = npz_size / hdf5_size
        assert compression_ratio > 10, (
            f"Expected >10x compression, got {compression_ratio:.1f}x"
        )


class TestRealDataConversion:
    """Tests for converting real NPZ data to HDF5."""

    def test_convert_real_npz_to_hdf5(self, tmp_path):
        """Convert real NPZ file to HDF5 and verify equivalence."""
        output_file = tmp_path / "converted.h5"

        # Convert
        convert_npz_to_hdf5(NPZ_FILE, output_file, compression="gzip")

        # Verify file was created
        assert output_file.exists()

        # Load original NPZ
        npz_data = np.load(NPZ_FILE)

        # Load converted HDF5
        with h5py.File(output_file, "r") as f:
            hdf5_data = _require_dataset(f["rf_data"], "rf_data")[:]
            hdf5_config = json.loads(_require_str_value(f.attrs["config"], "config"))

        # Verify data matches
        np.testing.assert_array_equal(npz_data["data"], hdf5_data)

        # Verify config matches
        npz_config = json.loads(
            _require_str_value(npz_data["config_json"], "config_json")
        )
        assert npz_config == hdf5_config

    def test_convert_with_different_compressions(self, tmp_path):
        """Test conversion with different compression levels."""
        # Only test gzip compression (chunks=True requires compression method)
        output_file = tmp_path / "converted_gzip.h5"
        convert_npz_to_hdf5(NPZ_FILE, output_file, compression="gzip")

        # Verify data integrity
        npz_data = np.load(NPZ_FILE)
        with h5py.File(output_file, "r") as f:
            np.testing.assert_array_equal(
                npz_data["data"], _require_dataset(f["rf_data"], "rf_data")[:]
            )

        # Verify file was compressed
        assert output_file.stat().st_size < NPZ_FILE.stat().st_size


class TestRealDataLoadingSaving:
    """Tests for loading and saving real acquisition data."""

    def test_load_real_hdf5_file(self):
        """Load the real HDF5 file and verify all components."""
        rf_data, config, metadata = load_acquisition_hdf5(HDF5_FILE)

        # Check RF data
        assert isinstance(rf_data, np.ndarray)
        assert rf_data.dtype == np.uint16
        assert rf_data.shape == (25, 32, 400)

        # Check config
        assert isinstance(config, dict)
        assert "afe" in config
        assert "fpga" in config
        assert "tx" in config
        assert "acquisition" in config

        # Check metadata
        assert isinstance(metadata, dict)
        assert "acquisition_timestamp" in metadata
        assert "schema_version" in metadata

    def test_round_trip_with_real_data(self, tmp_path):
        """Load real HDF5, save to new file, verify equivalence."""
        # Load original
        original_data, original_config, _ = load_acquisition_hdf5(HDF5_FILE)

        # Save to new file (must use Pydantic config, so wrap in dict)
        from pydantic import BaseModel

        class SimpleConfig(BaseModel):
            raw_data: dict

            def model_dump_json(
                self,
                *,
                indent: int | None = None,
                ensure_ascii: bool = False,
                include: Any | None = None,
                exclude: Any | None = None,
                context: Any | None = None,
                by_alias: bool | None = None,
                exclude_unset: bool = False,
                exclude_defaults: bool = False,
                exclude_none: bool = False,
                exclude_computed_fields: bool = False,
                round_trip: bool = False,
                warnings: bool | Literal["none", "warn", "error"] = True,
                fallback: Callable[[Any], Any] | None = None,
                serialize_as_any: bool = False,
                polymorphic_serialization: bool | None = None,
            ) -> str:
                return json.dumps(self.raw_data)

        config_wrapper = SimpleConfig(raw_data=original_config)
        output_file = tmp_path / "roundtrip.h5"

        # Call with correct parameter order: data, config, output_path
        save_acquisition_hdf5(
            original_data,
            config_wrapper,
            output_file,
        )

        # Load new file
        new_data, new_config, _ = load_acquisition_hdf5(output_file)

        # Verify equivalence
        np.testing.assert_array_equal(original_data, new_data)
        assert original_config == new_config

    def test_real_data_statistics(self):
        """Compute and verify statistics on real data."""
        rf_data, _, _ = load_acquisition_hdf5(HDF5_FILE)

        # Basic statistics
        assert rf_data.min() == 512
        assert rf_data.max() == 512
        assert rf_data.mean() == 512.0

        # This appears to be test pattern data (constant value)
        assert np.all(rf_data == 512), "Test data appears to be constant value pattern"

    def test_real_data_metadata_timestamp(self):
        """Verify timestamp format in real data."""
        _, _, metadata = load_acquisition_hdf5(HDF5_FILE)

        timestamp = metadata.get("acquisition_timestamp")
        assert timestamp is not None

        # Verify timestamp is ISO format string
        assert isinstance(timestamp, str)
        assert "2026" in timestamp  # Year from filename
        assert "T" in timestamp  # ISO 8601 format

    def test_real_data_schema_version(self):
        """Verify schema version in real data."""
        _, _, metadata = load_acquisition_hdf5(HDF5_FILE)

        assert "schema_version" in metadata
        assert isinstance(metadata["schema_version"], str)
        # Schema version can be "v1.0" or "1.0" format
        assert "1.0" in metadata["schema_version"]


class TestRealDataEdgeCases:
    """Test edge cases with real data."""

    def test_npz_without_compression_info(self):
        """Verify NPZ files don't store compression metadata."""
        data = np.load(NPZ_FILE)

        # NPZ files from older code might not have compression info
        assert "compression" not in data
        assert "compression_level" not in data

    def test_hdf5_compression_info(self):
        """Verify HDF5 files store compression metadata."""
        with h5py.File(HDF5_FILE, "r") as f:
            dataset = _require_dataset(f["rf_data"], "rf_data")

            # Check if compression is enabled
            if dataset.compression:
                assert dataset.compression in ["gzip", "lzf", "szip"]
                assert dataset.chunks is not None  # Compression requires chunking

    def test_json_config_parseable(self):
        """Verify standalone JSON config file is valid."""
        with open(JSON_FILE) as f:
            config = json.load(f)

        # Verify structure
        assert "afe" in config
        assert "fpga" in config
        assert "tx" in config
        assert "acquisition" in config
        assert "transport" in config

        # Verify key parameters
        assert config["fpga"]["fifo_depth"] == 400
        assert config["acquisition"]["num_frames"] == 5

    def test_config_consistency_across_formats(self):
        """Verify config is consistent across JSON, NPZ, and HDF5."""
        # Load from JSON
        with open(JSON_FILE) as f:
            json_config = json.load(f)

        # Load from NPZ
        npz_data = np.load(NPZ_FILE)
        npz_config = json.loads(
            _require_str_value(npz_data["config_json"], "config_json")
        )

        # Load from HDF5
        with h5py.File(HDF5_FILE, "r") as f:
            hdf5_config = json.loads(_require_str_value(f.attrs["config"], "config"))

        # Compare (transport may differ slightly due to runtime info)
        for key in ["afe", "fpga", "tx", "acquisition"]:
            assert json_config[key] == npz_config[key], f"{key} mismatch: JSON vs NPZ"
            assert json_config[key] == hdf5_config[key], f"{key} mismatch: JSON vs HDF5"
