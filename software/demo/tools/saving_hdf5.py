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

from pathlib import Path

import numpy as np

from tipy.protocol.example.config import ProtocolExampleConfig
from tipy.tools.logging import setup_logging
from tipy.tools.saving import load_acquisition_hdf5, save_acquisition_hdf5

log = setup_logging("INFO")

output = Path(__file__).parent / "example_acquisition.h5"

# Fake RF volume: (shots, channels, samples)
data = np.random.randint(0, 1024, (8, 16, 256), dtype=np.uint16)
config = ProtocolExampleConfig()

save_acquisition_hdf5(
    data,
    config,
    output,
    metadata={
        "packet_timestamps": np.linspace(0.0, 0.7, num=8),
        "frame_timestamps": np.array([0.0]),
        "operator": "demo",
    },
    overwrite=True,
)
log.info(f"Wrote {output} ({output.stat().st_size} bytes)")

loaded, config_dict, metadata = load_acquisition_hdf5(output)
log.info(f"Loaded shape={loaded.shape}, dtype={loaded.dtype}")
log.info(
    f"Config type={metadata.get('config_type')}, schema={metadata.get('schema_version')}"
)
log.info(f"Acquisition params keys={list(metadata.get('acquisition_parameters', {}))}")
log.info(f"Packet timestamps={metadata.get('packet_timestamps')}")

assert np.array_equal(loaded, data)
assert config_dict["acquisition"]["num_frames"] == config.acquisition.num_frames
log.info("Round-trip OK")
