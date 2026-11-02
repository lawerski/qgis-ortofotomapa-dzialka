import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from docinanie_ortofotomapy_geoportal.clip_logic import (
    ClipRequestError,
    clip_orthophoto,
    output_path,
    validate_layers,
)


class CRS:
    def isValid(self):
        return True


class Raster:
    def isValid(self):
        return True

    def providerType(self):
        return "gdal"

    def crs(self):
        return CRS()


class Parcel:
    def __init__(self, selected=1):
        self.selected = selected

    def isValid(self):
        return True

    def geometryType(self):
        return 2

    def selectedFeatureCount(self):
        return self.selected

    def crs(self):
        return CRS()


class ClipLogicTests(unittest.TestCase):
    def test_rejects_zero_or_multiple_parcels(self):
        for count in (0, 2):
            with self.subTest(count=count), self.assertRaises(ClipRequestError):
                validate_layers(Raster(), Parcel(count), Raster, 2)

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wynik.tif"
            path.write_bytes(b"original")
            with self.assertRaises(ClipRequestError):
                output_path(str(path))
            self.assertEqual(b"original", path.read_bytes())

    def test_mask_contains_selection_before_gdal_clip(self):
        core = types.ModuleType("qgis.core")
        core.QgsRasterLayer = Raster
        core.QgsWkbTypes = types.SimpleNamespace(PolygonGeometry=2)
        core.QgsProject = types.SimpleNamespace(instance=lambda: "project")

        class Context:
            def setProject(self, project):
                self.project = project

        core.QgsProcessingContext = Context
        core.QgsProcessingFeedback = lambda: "feedback"
        calls = []

        def run(name, params, **_kwargs):
            calls.append((name, params))
            return {"OUTPUT": params["OUTPUT"]}

        with tempfile.TemporaryDirectory() as directory:
            dest = str(Path(directory) / "dzialka.tif")
            with patch.dict(sys.modules, {"qgis": types.ModuleType("qgis"),
                                          "qgis.core": core,
                                          "processing": types.SimpleNamespace(run=run)}):
                self.assertEqual(dest, clip_orthophoto(Raster(), Parcel(), dest))
        self.assertEqual("native:saveselectedfeatures", calls[0][0])
        self.assertEqual("gdal:cliprasterbymasklayer", calls[1][0])
        self.assertEqual(calls[0][1]["OUTPUT"], calls[1][1]["MASK"])
        self.assertTrue(calls[1][1]["CROP_TO_CUTLINE"])
        self.assertTrue(calls[1][1]["KEEP_RESOLUTION"])
        self.assertTrue(calls[1][1]["ALPHA_BAND"])


if __name__ == "__main__":
    unittest.main()
