"""Przycięcie rastra do jednej zaznaczonej działki, bez zależności od okna QGIS."""

from pathlib import Path
from tempfile import TemporaryDirectory


class ClipRequestError(ValueError):
    pass


def output_path(value):
    if not isinstance(value, str) or not value.strip():
        raise ClipRequestError("Wskaż plik wyjściowy GeoTIFF.")
    path = Path(value.strip()).expanduser()
    if not path.suffix:
        path = path.with_suffix(".tif")
    if path.suffix.lower() not in (".tif", ".tiff"):
        raise ClipRequestError("Wynik musi być plikiem .tif lub .tiff.")
    if not path.parent.is_dir():
        raise ClipRequestError("Folder docelowy nie istnieje.")
    if path.exists():
        raise ClipRequestError("Plik już istnieje. Wybierz nową nazwę, aby nie nadpisać ortofotomapy.")
    return str(path.resolve())


def validate_layers(raster, parcel, raster_class, polygon_type):
    if not isinstance(raster, raster_class) or not raster.isValid():
        raise ClipRequestError("Wybierz poprawną ortofotomapę jako warstwę rastrową.")
    if raster.providerType() != "gdal":
        raise ClipRequestError("Wczytaj lokalną ortofotomapę (np. GeoTIFF), a nie podkład WMS/WMTS.")
    if parcel is None or not parcel.isValid() or parcel.geometryType() != polygon_type:
        raise ClipRequestError("Wybierz wektorową warstwę poligonową działek z Geoportalu.")
    if not raster.crs().isValid() or not parcel.crs().isValid():
        raise ClipRequestError("Obie warstwy muszą mieć poprawnie przypisany układ współrzędnych (CRS).")
    if parcel.selectedFeatureCount() != 1:
        raise ClipRequestError("Zaznacz dokładnie jedną działkę w warstwie Geoportalu.")


def clip_orthophoto(raster, parcel, destination):
    """Eksportuje wybraną działkę do maski i zwraca ścieżkę wynikowego TIFF."""
    from qgis.core import (
        QgsProcessingContext,
        QgsProcessingFeedback,
        QgsProject,
        QgsRasterLayer,
        QgsWkbTypes,
    )
    import processing

    validate_layers(raster, parcel, QgsRasterLayer, QgsWkbTypes.PolygonGeometry)
    destination = output_path(destination)
    context = QgsProcessingContext()
    context.setProject(QgsProject.instance())
    feedback = QgsProcessingFeedback()

    # GDAL nie korzysta z zaznaczenia w warstwie WFS. Maska zawiera tylko wybraną działkę.
    with TemporaryDirectory(prefix="qgis_dzialka_") as directory:
        mask_file = str(Path(directory) / "wybrana_dzialka.gpkg")
        selected = processing.run(
            "native:saveselectedfeatures",
            {"INPUT": parcel, "OUTPUT": mask_file},
            context=context,
            feedback=feedback,
        )
        result = processing.run(
            "gdal:cliprasterbymasklayer",
            {
                "INPUT": raster,
                "MASK": selected["OUTPUT"],
                "CROP_TO_CUTLINE": True,
                "KEEP_RESOLUTION": True,
                "ALPHA_BAND": True,
                "DATA_TYPE": 0,
                "OUTPUT": destination,
            },
            context=context,
            feedback=feedback,
        )
    return result["OUTPUT"]
