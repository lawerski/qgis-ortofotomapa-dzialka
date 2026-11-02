"""Okno wyboru ortofotomapy, działki i pliku wynikowego."""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsRasterLayer
from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel

from .clip_logic import ClipRequestError, clip_orthophoto


class ClipDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Przytnij ortofotomapę do działki")
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Wczytaj ortofotomapę i wektorową warstwę działek z Geoportalu. "
            "Zaznacz na mapie jedną działkę, która będzie maską wycinania."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.raster_combo = QgsMapLayerComboBox(self)
        self.parcel_combo = QgsMapLayerComboBox(self)
        self.raster_combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.parcel_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        form.addRow("Ortofotomapa:", self.raster_combo)
        form.addRow("Działki (Geoportal):", self.parcel_combo)

        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText("Nowy plik .tif")
        browse = QPushButton("Wybierz…", self)
        browse.clicked.connect(self.choose_file)
        path_row = QWidget(self)
        path_layout = QHBoxLayout(path_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse)
        form.addRow("Wynik GeoTIFF:", path_row)
        layout.addLayout(form)

        note = QLabel(
            "Wynik zachowuje rozdzielczość ortofotomapy; poza granicą działki będzie przezroczysty. "
            "Pliki źródłowe pozostaną bez zmian."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.button(QDialogButtonBox.Ok).setText("Przytnij i zapisz")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self, "Zapisz przyciętą ortofotomapę", self.path_edit.text(), "GeoTIFF (*.tif *.tiff)"
        )
        if filename:
            self.path_edit.setText(filename)


class OrthoClipPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Przytnij ortofotomapę do działki…", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Ortofotomapa i działka", self.action)

    def unload(self):
        if self.action is not None:
            self.iface.removePluginMenu("&Ortofotomapa i działka", self.action)
            self.action.deleteLater()
            self.action = None

    def run(self):
        dialog = ClipDialog(self.iface.mainWindow())
        active = self.iface.activeLayer()
        if isinstance(active, QgsRasterLayer) and active.isValid():
            dialog.raster_combo.setLayer(active)

        while dialog.exec_() == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                filename = clip_orthophoto(
                    dialog.raster_combo.currentLayer(),
                    dialog.parcel_combo.currentLayer(),
                    dialog.path_edit.text(),
                )
                result_layer = QgsRasterLayer(filename, "Ortofotomapa - wybrana działka", "gdal")
                if not result_layer.isValid():
                    raise RuntimeError("Wynik zapisano, ale QGIS nie może wczytać pliku. Sprawdź ścieżkę.")
                QgsProject.instance().addMapLayer(result_layer)
            except ClipRequestError as exc:
                error = str(exc)
            except Exception as exc:
                error = str(exc)
                QgsMessageLog.logMessage(error, "Ortofotomapa i działka", Qgis.Critical)
            else:
                error = None
            finally:
                QApplication.restoreOverrideCursor()

            if error:
                QMessageBox.warning(dialog, "Nie udało się przyciąć ortofotomapy", error)
                continue
            self.iface.messageBar().pushMessage(
                "Ortofotomapa i działka", "GeoTIFF zapisano i dodano do projektu.",
                level=Qgis.Success, duration=5,
            )
            return
