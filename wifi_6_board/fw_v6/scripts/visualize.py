import argparse

import numpy as np

from visualize_functions import (
    import_packages,
    load_configs,
    load_data,
    preprocess_data,
    beamform_data,
)


def main(vis_config_path: str, data_file_path: str) -> None:
    print("Loading configurations...")
    config, vis_config = load_configs(vis_config_path)

    print("Loading data...")
    data = load_data(config, vis_config, data_file_path)

    np.save("raw_data.npy", data.astype(np.float16))

    print(f"Preprocessing {data.shape[0]} shots...")
    data = preprocess_data(config, vis_config, data)

    np.save("preprocessed_data.npy", data.astype(np.float16))

    print(f"Beamforming {data.shape[0]} shots...")
    img_data = beamform_data(config, vis_config, data)

    np.save("beamformed_data.npy", np.abs(img_data).astype(np.float16))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ultrasound Data Visualization")
    parser.add_argument(
        "vis_config",
        type=str,
        help="Path to the visualization configuration file.",
    )
    parser.add_argument(
        "data",
        type=str,
        help="Path to the ultrasound data file.",
    )

    args = parser.parse_args()

    print("Initializing...")
    import_packages()

    main(args.vis_config, args.data)

    import graphing

    graphing.main()
