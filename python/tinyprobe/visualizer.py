"""
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich
        Sergei Vostrikov, ETH Zurich

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

import threading
import atexit

import numpy as np
import scipy.signal as ss
from plotly.graph_objects import Figure as PlotlyFigure, Scatter as PlotlyScatter
from plotly.graph_objs import (
    Layout,
    YAxis,
    Scatter,
    Annotation,
    Annotations,
    Data,
    Figure,
    Font,
)
import matplotlib.pyplot as plt
from matplotlib._pylab_helpers import Gcf

from pybf.pybf.visualization import LivePlot
from pybf.pybf.image_settings import ImageSettings
from pybf.scripts.beamformer_cartesian_realtime import BFCartesianRealTime
from tinyprobe.bytestream_parser import parse_bitstream


class TPVisualizer:
    def __init__(self):
        self._data = None
        self._data_lock = threading.Lock()

        self.config = {
            "renderer": "browser",
            "f_sampling": None,
            "tx_strategy": None,
            "rx_mapping": None,
            "channels_list": None,
            "plot_channel": None,
            "image_resolution": [400, 400],
            "image_range": [[-0.03, 0.03], [0.00, 0.12]],
            "lat_pixel_density": 5,
            "db_range": 60,
            "decimation_factor": 1,
            "interpolation_factor": 10,
            "start_time": 6.1e-6,
            "correction_time_shift": 60e-9,
            "alpha_fov_apod": 40,
            "transducer": None,
            "fifo_read_depth": 2048,
        }

        self._thread = None
        self._thread_running = False

    def configure(self, config: dict):
        """Configure the visualizer with the given settings.

        Arguments:
            config (dict): Configuration settings for the visualizer.

        Returns:
            None
        """
        for key, value in config.items():
            if key in self.config:
                self.config[key] = value
            else:
                raise ValueError(f"Unknown configuration key: {key}")

    def push_data(self, data: bytes | np.ndarray):
        """Push data to the visualizer.

        Arguments:
            data (bytes | np.array): Data to be visualized.

        Returns:
            None
        """
        if not isinstance(data, np.ndarray) and not isinstance(data, bytes):
            raise ValueError(
                "Data must be of type np.ndarray or bytes, not", type(data)
            )

        with self._data_lock:
            self._data = data.copy() if isinstance(data, np.ndarray) else data

    def plot_channels(self):
        if self._data is None:
            return

        data = self._pull_data()

        if self.config["f_sampling"] is None or self.config["channels_list"] is None:
            raise ValueError("Sampling frequency and channel list must be set.")

        time = np.arange(0, data.shape[0]) / self.config["f_sampling"]

        step = 1.0 / len(self.config["channels_list"])
        kwargs = dict(
            domain=[0, 0 + step], showticklabels=False, zeroline=False, showgrid=False
        )

        layout = Layout(yaxis=YAxis(kwargs), showlegend=False)
        traces = [Scatter(x=time, y=data[:, self.config["channels_list"][0]])]

        for ii in range(1, len(self.config["channels_list"])):
            kwargs.update(domain=[0 + ii * step, 0 + (ii + 1) * step])
            layout.update({"yaxis%d" % (ii + 1): YAxis(kwargs), "showlegend": False})
            traces.append(
                Scatter(
                    x=time,
                    y=data[:, self.config["channels_list"][ii]],
                    yaxis="y%d" % (ii + 1),
                )
            )

        annotations = Annotations(
            [
                Annotation(
                    x=-0.06,
                    y=0,
                    xref="paper",
                    yref="y%d" % (ii + 1),
                    text=ch_name,
                    font=Font(size=12),
                    showarrow=False,
                )
                for ii, ch_name in enumerate(
                    ["Ch. " + str(i) for i in self.config["channels_list"]]
                )
            ]
        )
        layout.update(annotations=annotations)

        # layout.update(autosize=False, width=1000, height=1000)
        fig = Figure(data=Data(traces), layout=layout)
        fig.show(renderer=self.config["renderer"])

    def plot_trace(self):
        if self._data is None:
            return

        data = self._pull_data()

        if self.config["f_sampling"] is None or self.config["plot_channel"] is None:
            raise ValueError("Sampling frequency and plot channel must be set.")

        data = data[:, self.config["plot_channel"]]
        time = np.arange(0, data.shape[0]) / self.config["f_sampling"]

        fig = PlotlyFigure()
        fig.add_trace(PlotlyScatter(x=time, y=data, mode="lines+markers", name="lines"))

        fig.update_layout(
            title="Data from channel " + str(self.config["plot_channel"]),
            xaxis_title="Time",
            yaxis_title="Signal",
        )

        fig.show(renderer=self.config["renderer"])

    def _live_plot_thread(self):
        self._thread_running = True

        f_pass = [
            0.55 * self.config["transducer"].f_central_hz,
            1.45 * self.config["transducer"].f_central_hz,
        ]  # Passband: 90% of the central frequency
        gstop = 60  # Minimum attenuation in the stopband (dB)

        # Normalize frequencies to the Nyquist frequency
        nyq = self.config["f_sampling"] / 2
        wp = np.array(f_pass) / nyq

        # Design the Chebyshev type II filter
        b, a = ss.iirfilter(
            N=5,
            Wn=wp,
            rs=gstop,
            btype="band",
            analog=False,
            ftype="cheby2",
            output="ba",
        )

        img_config = ImageSettings(
            self.config["image_range"][0][0],
            self.config["image_range"][0][1],
            self.config["image_range"][1][0],
            self.config["image_range"][1][1],
            self.config["lat_pixel_density"],
            self.config["transducer"],
        )

        bf = BFCartesianRealTime(
            self.config["f_sampling"],
            self.config["tx_strategy"],
            self.config["transducer"],
            self.config["decimation_factor"],
            self.config["interpolation_factor"],
            self.config["image_resolution"],
            img_config,
            db_range=self.config["db_range"],
            start_time=self.config["start_time"],
            correction_time_shift=self.config["correction_time_shift"],
            alpha_fov_apod=self.config["alpha_fov_apod"],
            bp_filter_params=None,
        )

        live_plot = LivePlot(
            self.config["image_resolution"],
            image_x_range=self.config["image_range"][0],
            image_z_range=self.config["image_range"][1],
            db_range=self.config["db_range"],
        )

        while self._thread_running:
            if self._data is None:
                continue

            data = self._pull_data()

            data_filt = ss.filtfilt(b, a, data)
            img_data = bf.beamform(
                data_filt[self.config["rx_mapping"], :][
                    : len(self.config["channels_list"]), :
                ],
                numba_active=True,
            )

            if live_plot.update_the_figure(np.abs(img_data)):
                self._thread_running = False
                print("User quit live plot.")
                break

    def start_live_plot(self):
        required_configs = [
            "transducer",
            "f_sampling",
            "image_range",
            "lat_pixel_density",
            "tx_strategy",
            "rx_mapping",
            "decimation_factor",
            "interpolation_factor",
            "image_resolution",
            "db_range",
            "start_time",
            "correction_time_shift",
            "alpha_fov_apod",
            "fifo_read_depth",
            "channels_list",
        ]

        for config in required_configs:
            if self.config[config] is None:
                raise ValueError(
                    f"Configuration '{config}' must be set for live plotting."
                )

        if self._thread_running:
            return

        self._thread = threading.Thread(target=self._live_plot_thread)
        self._thread.start()
        self._thread_running = True

        # Unregister the atexit callback that calls Gcf.destroy_all
        try:
            atexit.unregister(Gcf.destroy_all)
        except Exception as e:
            print("Error unregistering Gcf.destroy_all:", e)

    def stop_live_plot(self):
        if self._thread_running:
            print("Stopping live plot...")
            self._thread_running = False
            self._thread.join()
            self._thread = None
        else:
            print("Live plot is not running.")

        try:
            plt.close("all")
        except Exception as _:
            pass

    def _pull_data(self) -> np.ndarray:
        with self._data_lock:
            if isinstance(self._data, bytes):
                # If the data is in bytes, parse it
                data = parse_bitstream(
                    self._data,
                    dbg_msgs=False,
                    bit_slip_arr=[-2] * 16,
                    read_size_samples=self.config["fifo_read_depth"],
                    n_activ_ch=len(self.config["channels_list"]),
                    bits_per_sample=10,
                )
            else:
                data = self._data

        return data
