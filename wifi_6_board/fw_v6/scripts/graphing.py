from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSlider,
    QLabel,
)
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

# from pybf.pybf.visualization import plot_image


# plot_image(
#     data[50], image_x_range=(-0.025, 0.025), image_z_range=(0.0, 0.025), db_range=40
# )


class MainWindow(QMainWindow):
    def __init__(self, img_data: np.ndarray) -> None:
        super().__init__()

        self.setWindowTitle("Ultrasound Data Visualization")
        self.setGeometry(500, 200, 1200, 1200)
        self.setStyleSheet("background-color: black;")
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.img_data = img_data

        self.db_range_slider = QSlider()
        self.db_range_slider.setMinimum(10)
        self.db_range_slider.setMaximum(100)
        self.db_range_slider.setValue(42)
        self.db_range_slider.setOrientation(Qt.Horizontal)
        self.db_range_slider.setTickPosition(QSlider.TicksBelow)
        self.db_range_slider.setTickInterval(5)
        self.db_range_slider.setSingleStep(1)
        self.db_range_slider.setPageStep(5)
        self.db_range_slider.valueChanged.connect(self.update_db_range)
        self.db_range_value = QLabel(str(self.db_range_slider.value()))

        self.graphWidget = pg.PlotWidget()
        self.imageItem = pg.ImageItem(self.img_data[self.img_data.shape[0] // 3].T)
        self.imageItem.setLevels(
            [img_data.max() - self.db_range_slider.value(), img_data.max()]
        )
        self.graphWidget.addItem(self.imageItem)
        self.graphWidget.setAspectLocked(True)

        self.slider = QSlider()
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.img_data.shape[0] - 1)
        self.slider.setValue(self.img_data.shape[0] // 3)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(5)
        self.slider.setTracking(True)
        self.slider.valueChanged.connect(self.update_image)
        self.slider_value = QLabel("0")

        layout = QVBoxLayout()
        layout.addWidget(self.graphWidget)
        layout.addWidget(QLabel("Frame"))
        layout.addWidget(self.slider)
        layout.addWidget(self.slider_value)
        layout.addWidget(QLabel("DB Range"))
        layout.addWidget(self.db_range_slider)
        layout.addWidget(self.db_range_value)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_image(self, value: int) -> None:
        self.imageItem.setImage(self.img_data[value].T)
        self.imageItem.setLevels(
            [self.img_data.max() - self.db_range_slider.value(), self.img_data.max()]
        )
        self.slider_value.setText(str(value))

    def update_db_range(self, value: int) -> None:
        self.imageItem.setLevels([self.img_data.max() - value, self.img_data.max()])
        self.db_range_value.setText(str(value))


def main() -> None:
    data = np.load("beamformed_data.npy")

    data_db = 20 * np.log10(data + 1e-6)

    app = QApplication([])
    window = MainWindow(data_db)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
