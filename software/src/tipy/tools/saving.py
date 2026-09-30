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
from datetime import UTC, datetime
from enum import Enum
from importlib.metadata import version
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from pydantic import BaseModel

# Current schema version for HDF5 files
SCHEMA_VERSION = "1.1"
COMPATIBLE_VERSIONS = ["1.0", "1.1"]

# HDF5 dataset and group names
KEY_RF_DATA = "rf_data"
KEY_ACQUISITION_PARAMS = "acquisition_parameters"
KEY_METADATA = "metadata"
KEY_RAW_BITSTREAM = "raw_bitstream"
KEY_PACKET_TIMESTAMPS = "packet_timestamps"
KEY_FRAME_TIMESTAMPS = "frame_timestamps"


def _get_package_version() -> str:
    """Get tipy package version from metadata."""
    return version("tipy")


def _json_safe_value(value: Any) -> Any:
    """Convert common Python values into HDF5-friendly scalars."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def _read_text_attr(value: Any) -> str:
    """Decode an HDF5 attribute that should contain JSON text."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def save_acquisition_hdf5(
    data: np.ndarray,
    config: BaseModel,
    output: Path,
    *,
    metadata: dict[str, Any] | None = None,
    compression: str | None = "gzip",
    compression_opts: int | None = 4,
    overwrite: bool = False,
) -> None:
    """Save ultrasound acquisition data to HDF5 format with metadata.

    Args:
        data: RF data array, typically shaped (num_shots, num_channels, num_samples)
        config: Pydantic configuration model (e.g., ProtocolExampleConfig)
        output: Output HDF5 file path (must have .h5 or .hdf5 extension)
        metadata: Optional additional metadata dict (timestamps, raw_bytes, etc.)
        compression: Compression algorithm ('gzip', 'lzf', None). Default: 'gzip'
        compression_opts: Compression level for gzip (0-9). Default: 4
        overwrite: If True, overwrite existing file. Default: False

    Raises:
        FileExistsError: If output file exists and overwrite=False
        FileNotFoundError: If output directory does not exist
        ValueError: If output file has wrong extension

    Example:
        >>> from tipy.protocol.example.config import ProtocolExampleConfig
        >>> config = ProtocolExampleConfig.model_validate(config_dict)
        >>> data = np.random.randint(0, 1024, (100, 32, 2000), dtype=np.uint16)
        >>> save_acquisition_hdf5(data, config, Path("acquisition.h5"))
    """
    if output.suffix not in [".h5", ".hdf5"]:
        raise ValueError(f"Expected .h5 or .hdf5 file extension, got: {output.suffix}")

    metadata = metadata or {}

    # Use mode "x" for exclusive creation (fail if exists) or "w" to overwrite
    mode = "w" if overwrite else "x"

    try:
        f = h5py.File(output, mode)
    except FileNotFoundError:
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    except FileExistsError:
        raise FileExistsError(
            f"Output file already exists: {output}. Use overwrite=True to replace."
        )

    with f:
        # Create main RF data dataset with compression
        dset = f.create_dataset(
            KEY_RF_DATA,
            data=data,
            compression=compression,
            compression_opts=compression_opts,
            chunks=True,  # Enable chunking for efficient partial reads
        )

        # Add dimensional metadata to dataset
        dset.attrs["shape_description"] = "(shots, channels, samples)"
        if data.ndim == 3:
            dset.attrs["num_shots"] = data.shape[0]
            dset.attrs["num_channels"] = data.shape[1]
            dset.attrs["num_samples"] = data.shape[2]
        dset.attrs["dtype"] = str(data.dtype)

        # Store acquisition configuration as JSON
        f.attrs["config"] = config.model_dump_json()
        f.attrs["config_type"] = config.__class__.__name__
        f.attrs["schema_version"] = SCHEMA_VERSION
        f.attrs["compatible_versions"] = json.dumps(COMPATIBLE_VERSIONS)

        # Temporal metadata
        f.attrs["acquisition_timestamp"] = datetime.now(UTC).isoformat()
        f.attrs["tipy_version"] = _get_package_version()

        # Create acquisition_parameters group for quick access to key params
        acq_params = f.create_group(KEY_ACQUISITION_PARAMS)
        _store_acquisition_params(acq_params, config)

        # Store optional metadata
        if metadata:
            meta_group = f.create_group(KEY_METADATA)

            # Store raw bitstream if provided
            if "raw_bytes" in metadata:
                raw_data = metadata["raw_bytes"]
                if isinstance(raw_data, (bytes, bytearray, memoryview)):
                    raw_data = np.frombuffer(raw_data, dtype=np.uint8)
                else:
                    raw_data = np.asarray(raw_data)
                meta_group.create_dataset(
                    KEY_RAW_BITSTREAM, data=raw_data, compression="gzip"
                )

            packet_timestamps = metadata.get(
                "packet_timestamps", metadata.get("timestamps")
            )
            if packet_timestamps is not None:
                meta_group.create_dataset(
                    KEY_PACKET_TIMESTAMPS,
                    data=np.asarray(packet_timestamps, dtype=np.float64),
                )

            frame_timestamps = metadata.get(KEY_FRAME_TIMESTAMPS)
            if frame_timestamps is not None:
                meta_group.create_dataset(
                    KEY_FRAME_TIMESTAMPS,
                    data=np.asarray(frame_timestamps, dtype=np.float64),
                )

            # Store any other custom metadata as attributes
            for key, value in metadata.items():
                if key not in [
                    "raw_bytes",
                    "timestamps",
                    "packet_timestamps",
                    KEY_FRAME_TIMESTAMPS,
                ] and isinstance(
                    value, (str, int, float, bool, np.generic, Enum, Path)
                ):
                    meta_group.attrs[key] = _json_safe_value(value)


def load_acquisition_hdf5(
    path: Path,
) -> tuple[np.ndarray, dict[str, Any], dict[str, Any]]:
    """Load ultrasound acquisition data from HDF5 format.

    Args:
        path: Path to HDF5 file

    Returns:
        Tuple of (data, config, metadata) where:
        - data: RF data as numpy array
        - config: Configuration dict (deserialize with Pydantic if needed)
        - metadata: Dict with acquisition metadata and timing info

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file has wrong extension or incompatible schema version

    Example:
        >>> data, config_dict, metadata = load_acquisition_hdf5(Path("acquisition.h5"))
        >>> print(f"Loaded {data.shape} with {metadata['num_channels']} channels")
    """
    if path.suffix not in [".h5", ".hdf5"]:
        raise ValueError(f"Expected .h5 or .hdf5 file extension, got: {path.suffix}")

    try:
        f = h5py.File(path, "r")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")

    with f:
        # Check schema version compatibility
        schema_version = f.attrs.get("schema_version", "unknown")
        if schema_version not in COMPATIBLE_VERSIONS:
            compatible = json.loads(f.attrs.get("compatible_versions", "[]"))
            if schema_version not in compatible:
                raise ValueError(
                    f"Incompatible schema version: {schema_version}. "
                    f"Expected one of {COMPATIBLE_VERSIONS}"
                )

        # Load RF data
        rf_data = f[KEY_RF_DATA]
        if not isinstance(rf_data, h5py.Dataset):
            raise TypeError(f"{KEY_RF_DATA} dataset is missing or invalid")
        data = rf_data[:]

        # Parse configuration
        config = json.loads(_read_text_attr(f.attrs["config"]))

        # Extract metadata
        metadata = {
            "schema_version": schema_version,
            "config_type": f.attrs.get("config_type"),
            "acquisition_timestamp": f.attrs.get("acquisition_timestamp"),
            "tipy_version": f.attrs.get("tipy_version"),
        }

        # Add acquisition parameters if available
        if KEY_ACQUISITION_PARAMS in f:
            acq_group = f[KEY_ACQUISITION_PARAMS]
            if not isinstance(acq_group, h5py.Group):
                raise TypeError(f"{KEY_ACQUISITION_PARAMS} group is invalid")

            acq_params = {}
            for key, value in acq_group.attrs.items():
                acq_params[key] = value
            metadata[KEY_ACQUISITION_PARAMS] = acq_params

        # Add custom metadata if available
        if KEY_METADATA in f:
            meta_group = f[KEY_METADATA]
            if not isinstance(meta_group, h5py.Group):
                raise TypeError(f"{KEY_METADATA} group is invalid")

            # Load timestamps if available
            packet_timestamps = meta_group.get(KEY_PACKET_TIMESTAMPS)
            if isinstance(packet_timestamps, h5py.Dataset):
                metadata[KEY_PACKET_TIMESTAMPS] = packet_timestamps[:]

            frame_timestamps = meta_group.get(KEY_FRAME_TIMESTAMPS)
            if isinstance(frame_timestamps, h5py.Dataset):
                metadata[KEY_FRAME_TIMESTAMPS] = frame_timestamps[:]

            # Load raw bitstream size if available
            raw_bitstream = meta_group.get(KEY_RAW_BITSTREAM)
            if isinstance(raw_bitstream, h5py.Dataset):
                metadata["raw_bitstream_size"] = raw_bitstream.shape[0]

            # Load custom attributes
            for key, value in meta_group.attrs.items():
                metadata[key] = value

    return data, config, metadata


def convert_npz_to_hdf5(
    npz_path: Path,
    hdf5_path: Path,
    *,
    overwrite: bool = False,
    compression: str | None = "gzip",
) -> None:
    """Convert NPZ acquisition file to HDF5 format.

    Args:
        npz_path: Input NPZ file path
        hdf5_path: Output HDF5 file path
        overwrite: If True, overwrite existing HDF5 file
        compression: Compression algorithm for HDF5 file

    Raises:
        FileNotFoundError: If NPZ file does not exist
        ValueError: If NPZ file is missing required fields

    Example:
        >>> convert_npz_to_hdf5(Path("old.npz"), Path("new.h5"))
    """
    if not npz_path.exists():
        raise FileNotFoundError(f"NPZ file not found: {npz_path}")

    # Load NPZ data
    with np.load(npz_path) as npz:
        if "data" not in npz:
            raise ValueError(f"NPZ file missing 'data' field: {npz_path}")

        data = npz["data"]

        # Parse config if available
        if "config_json" in npz:
            config_json = npz["config_json"].item()
            config_dict = json.loads(config_json)
        else:
            config_dict = {}

    # Create a minimal config wrapper for NPZ conversion
    class NPZConfig(BaseModel):
        """Minimal config wrapper for NPZ conversion."""

        raw_config: dict[str, Any]

        def model_dump_json(self, **kwargs: Any) -> str:
            """Override to return JSON from raw_config."""
            return json.dumps(self.raw_config)

    config = NPZConfig(raw_config=config_dict)

    # Save to HDF5
    metadata = {
        "source_format": "npz",
        "source_file": str(npz_path),
        "conversion_timestamp": datetime.now(UTC).isoformat(),
    }

    save_acquisition_hdf5(
        data,
        config,
        hdf5_path,
        metadata=metadata,
        compression=compression,
        overwrite=overwrite,
    )


def _store_acquisition_params(group: h5py.Group, config: BaseModel) -> None:
    """Store acquisition parameters in HDF5 group for quick access.

    Args:
        group: HDF5 group to store parameters in
        config: Configuration model
    """
    config_dict = config.model_dump(mode="json")

    # Try to extract common ultrasound parameters
    # This is flexible to work with different config structures
    if "fpga" in config_dict:
        fpga = config_dict["fpga"]
        group.attrs["fifo_depth"] = fpga.get("fifo_depth", -1)
        group.attrs["num_shots"] = fpga.get("num_shots", -1)

        if "lvds_lanes" in fpga:
            group.attrs["num_lvds_lanes"] = len(fpga["lvds_lanes"])

        if "afe_clk_hispeed" in fpga:
            group.attrs["afe_clk_hispeed"] = fpga["afe_clk_hispeed"]

    if "afe" in config_dict:
        afe = config_dict["afe"]
        group.attrs["lna_gain"] = _json_safe_value(afe.get("lna_gain", "unknown"))
        group.attrs["pga_gain"] = _json_safe_value(afe.get("pga_gain", "unknown"))

    if "acquisition" in config_dict:
        acq = config_dict["acquisition"]
        group.attrs["num_frames"] = acq.get("num_frames", -1)
