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
import tempfile
from pathlib import Path
from typing import Any, cast

import h5py
import numpy as np
import pytest
from pydantic import BaseModel

from tipy.tools.saving import (
    KEY_FRAME_TIMESTAMPS,
    KEY_PACKET_TIMESTAMPS,
    SCHEMA_VERSION,
    convert_npz_to_hdf5,
    load_acquisition_hdf5,
    save_acquisition_hdf5,
)


# Minimal test configuration model
class AcquisitionConfig(BaseModel):
    """Minimal test configuration."""

    fpga: dict
    afe: dict
    acquisition: dict


def make_test_config():
    """Create a test configuration."""
    return AcquisitionConfig(
        fpga={
            "fifo_depth": 2000,
            "num_shots": 100,
            "lvds_lanes": [0, 1, 2, 3],
            "afe_clk_hispeed": 30_000_000,
        },
        afe={
            "lna_gain": "21dB",
            "pga_gain": "24dB",
        },
        acquisition={
            "num_frames": 10,
        },
    )


def _require_dataset(
    node: h5py.Group | h5py.Dataset | h5py.Datatype, name: str
) -> h5py.Dataset:
    """Narrow an HDF5 node to Dataset for static type checkers."""
    assert isinstance(node, h5py.Dataset), f"Expected dataset at '{name}'"
    return node


def _require_group(
    node: h5py.Group | h5py.Dataset | h5py.Datatype, name: str
) -> h5py.Group:
    """Narrow an HDF5 node to Group for static type checkers."""
    assert isinstance(node, h5py.Group), f"Expected group at '{name}'"
    return node


def _require_str_attr(value: object, attr_name: str) -> str:
    """Normalize HDF5 attribute values to string for JSON decoding."""
    if isinstance(value, np.ndarray):
        # HDF5 string attrs can come back as scalar ndarrays.
        assert value.size == 1, f"Expected scalar attribute '{attr_name}'"
        value = cast(Any, value).item()
    if isinstance(value, bytes):
        value = value.decode()
    assert isinstance(value, str), f"Expected string attribute '{attr_name}'"
    return value


class TestSaveAcquisitionHDF5:
    def test_save_basic(self):
        """Test basic HDF5 save operation."""
        data = np.random.randint(0, 1024, (100, 32, 2000), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            assert output.exists()
            assert output.stat().st_size > 0

    def test_save_creates_rf_data_dataset(self):
        """Test that rf_data dataset is created with correct shape."""
        data = np.random.randint(0, 1024, (100, 32, 2000), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            with h5py.File(output, "r") as f:
                assert "rf_data" in f
                rf_data = _require_dataset(f["rf_data"], "rf_data")
                assert rf_data.shape == data.shape
                assert np.array_equal(rf_data[:], data)

    def test_save_stores_config_metadata(self):
        """Test that configuration is stored as metadata."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            with h5py.File(output, "r") as f:
                assert "config" in f.attrs
                config_attr = _require_str_attr(f.attrs["config"], "config")
                stored_config = json.loads(config_attr)
                assert stored_config["fpga"]["fifo_depth"] == 2000

    def test_save_stores_schema_version(self):
        """Test that schema version is stored."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            with h5py.File(output, "r") as f:
                assert f.attrs["schema_version"] == SCHEMA_VERSION

    def test_save_with_compression(self):
        """Test that compression works and reduces file size."""
        data = np.zeros((100, 32, 2000), dtype=np.uint16)  # Highly compressible
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            compressed_high = Path(tmpdir) / "compressed_high.h5"
            compressed_low = Path(tmpdir) / "compressed_low.h5"

            save_acquisition_hdf5(
                data, config, compressed_high, compression="gzip", compression_opts=9
            )
            save_acquisition_hdf5(
                data, config, compressed_low, compression="gzip", compression_opts=1
            )

            # High compression should result in smaller file
            assert compressed_high.stat().st_size <= compressed_low.stat().st_size

    def test_save_with_metadata(self):
        """Test saving with additional metadata."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()
        metadata = {
            "raw_bytes": b"test data",
            "timestamps": [1.0, 2.0, 3.0],
            "frame_timestamps": [1.0, 3.0],
            "custom_field": "custom_value",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output, metadata=metadata)

            with h5py.File(output, "r") as f:
                assert "metadata" in f
                metadata_group = _require_group(f["metadata"], "metadata")
                assert "raw_bitstream" in metadata_group
                assert KEY_PACKET_TIMESTAMPS in metadata_group
                assert KEY_FRAME_TIMESTAMPS in metadata_group
                assert metadata_group.attrs["custom_field"] == "custom_value"

    def test_save_raises_if_directory_missing(self):
        """Test that error is raised if output directory doesn't exist."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        output = Path("/nonexistent/directory/test.h5")
        with pytest.raises(FileNotFoundError, match="Output directory does not exist"):
            save_acquisition_hdf5(data, config, output)

    def test_save_raises_if_wrong_extension(self):
        """Test that error is raised for wrong file extension."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.npz"
            with pytest.raises(ValueError, match="Expected .h5 or .hdf5"):
                save_acquisition_hdf5(data, config, output)

    def test_save_raises_if_file_exists_without_overwrite(self):
        """Test that error is raised if file exists and overwrite=False."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            with pytest.raises(FileExistsError, match="already exists"):
                save_acquisition_hdf5(data, config, output, overwrite=False)

    def test_save_overwrites_if_requested(self):
        """Test that file can be overwritten when overwrite=True."""
        data1 = np.ones((10, 8, 100), dtype=np.uint16)
        data2 = np.zeros((10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data1, config, output)
            save_acquisition_hdf5(data2, config, output, overwrite=True)

            with h5py.File(output, "r") as f:
                rf_data = _require_dataset(f["rf_data"], "rf_data")
                assert np.array_equal(rf_data[:], data2)

    def test_save_creates_acquisition_parameters_group(self):
        """Test that acquisition_parameters group is created."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            with h5py.File(output, "r") as f:
                assert "acquisition_parameters" in f
                acq_params = f["acquisition_parameters"]
                assert acq_params.attrs["fifo_depth"] == 2000
                assert acq_params.attrs["num_shots"] == 100
                assert acq_params.attrs["num_lvds_lanes"] == 4


class TestLoadAcquisitionHDF5:
    def test_load_basic(self):
        """Test basic HDF5 load operation."""
        original_data = np.random.randint(0, 1024, (100, 32, 2000), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(original_data, config, output)

            data, loaded_config, metadata = load_acquisition_hdf5(output)

            assert np.array_equal(data, original_data)
            assert loaded_config["fpga"]["fifo_depth"] == 2000
            assert metadata["schema_version"] == SCHEMA_VERSION

    def test_load_returns_metadata(self):
        """Test that load returns comprehensive metadata."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output)

            _, _, metadata = load_acquisition_hdf5(output)

            assert "acquisition_timestamp" in metadata
            assert "tipy_version" in metadata
            assert "config_type" in metadata
            assert "acquisition_parameters" in metadata

    def test_load_with_custom_metadata(self):
        """Test loading file with custom metadata."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()
        save_metadata = {
            "timestamps": [1.0, 2.0, 3.0],
            "frame_timestamps": [1.0, 3.0],
            "custom_field": "test_value",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.h5"
            save_acquisition_hdf5(data, config, output, metadata=save_metadata)

            _, _, metadata = load_acquisition_hdf5(output)

            assert KEY_PACKET_TIMESTAMPS in metadata
            assert np.array_equal(metadata[KEY_PACKET_TIMESTAMPS], [1.0, 2.0, 3.0])
            assert np.array_equal(metadata[KEY_FRAME_TIMESTAMPS], [1.0, 3.0])
            assert metadata["custom_field"] == "test_value"

    def test_load_raises_if_file_missing(self):
        """Test that error is raised if file doesn't exist."""
        path = Path("/nonexistent/file.h5")
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_acquisition_hdf5(path)

    def test_load_raises_if_wrong_extension(self):
        """Test that error is raised for wrong file extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npz"
            path.touch()
            with pytest.raises(ValueError, match="Expected .h5 or .hdf5"):
                load_acquisition_hdf5(path)


class TestConvertNPZToHDF5:
    def test_convert_basic(self):
        """Test basic NPZ to HDF5 conversion."""
        data = np.random.randint(0, 1024, (100, 32, 2000), dtype=np.uint16)
        config_dict = {"test": "config"}
        config_json = json.dumps(config_dict)

        with tempfile.TemporaryDirectory() as tmpdir:
            npz_path = Path(tmpdir) / "test.npz"
            hdf5_path = Path(tmpdir) / "test.h5"

            # Create NPZ file
            np.savez(npz_path, data=data, config_json=config_json)

            # Convert
            convert_npz_to_hdf5(npz_path, hdf5_path)

            assert hdf5_path.exists()

            # Verify conversion
            loaded_data, _, metadata = load_acquisition_hdf5(hdf5_path)
            assert np.array_equal(loaded_data, data)
            assert metadata["source_format"] == "npz"

    def test_convert_raises_if_npz_missing(self):
        """Test that error is raised if NPZ file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            npz_path = Path(tmpdir) / "missing.npz"
            hdf5_path = Path(tmpdir) / "output.h5"

            with pytest.raises(FileNotFoundError, match="NPZ file not found"):
                convert_npz_to_hdf5(npz_path, hdf5_path)

    def test_convert_raises_if_npz_missing_data(self):
        """Test that error is raised if NPZ missing 'data' field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            npz_path = Path(tmpdir) / "test.npz"
            hdf5_path = Path(tmpdir) / "test.h5"

            # Create NPZ without 'data' field
            np.savez(npz_path, wrong_field=np.array([1, 2, 3]))

            with pytest.raises(ValueError, match="missing 'data' field"):
                convert_npz_to_hdf5(npz_path, hdf5_path)

    def test_convert_without_config(self):
        """Test conversion of NPZ file without config."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)

        with tempfile.TemporaryDirectory() as tmpdir:
            npz_path = Path(tmpdir) / "test.npz"
            hdf5_path = Path(tmpdir) / "test.h5"

            # Create NPZ without config
            np.savez(npz_path, data=data)

            # Should still convert successfully
            convert_npz_to_hdf5(npz_path, hdf5_path)

            loaded_data, _, _ = load_acquisition_hdf5(hdf5_path)
            assert np.array_equal(loaded_data, data)


class TestRoundTrip:
    def test_save_load_roundtrip(self):
        """Test that data survives save/load cycle."""
        original_data = np.random.randint(0, 1024, (50, 16, 1000), dtype=np.uint16)
        config = make_test_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "roundtrip.h5"

            save_acquisition_hdf5(original_data, config, output)
            loaded_data, _, _ = load_acquisition_hdf5(output)

            assert np.array_equal(loaded_data, original_data)
            assert loaded_data.dtype == original_data.dtype
            assert loaded_data.shape == original_data.shape

    def test_save_load_with_metadata_roundtrip(self):
        """Test that metadata survives save/load cycle."""
        data = np.random.randint(0, 1024, (10, 8, 100), dtype=np.uint16)
        config = make_test_config()
        original_metadata = {
            "timestamps": [1.0, 2.0, 3.0, 4.0],
            "frame_timestamps": [1.0, 3.0],
            "experiment_id": "exp_001",
            "temperature": 25.5,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "roundtrip.h5"

            save_acquisition_hdf5(data, config, output, metadata=original_metadata)
            _, _, loaded_metadata = load_acquisition_hdf5(output)

            assert np.array_equal(
                loaded_metadata[KEY_PACKET_TIMESTAMPS], original_metadata["timestamps"]
            )
            assert np.array_equal(
                loaded_metadata[KEY_FRAME_TIMESTAMPS],
                original_metadata["frame_timestamps"],
            )
            assert loaded_metadata["experiment_id"] == "exp_001"
            assert loaded_metadata["temperature"] == 25.5
