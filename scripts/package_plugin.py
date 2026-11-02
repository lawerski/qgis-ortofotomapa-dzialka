"""Zbuduj powtarzalny ZIP do instalacji przez menedżera wtyczek QGIS."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "docinanie_ortofotomapy_geoportal"
OUTPUT = ROOT / "Ortofotomapa-do-dzialki-QGIS.zip"
FILES = ["__init__.py", "plugin.py", "clip_logic.py", "metadata.txt", "README.md"]


def main():
    with ZipFile(OUTPUT, "w") as archive:
        for name in sorted(FILES):
            path = PLUGIN / name
            entry = ZipInfo(f"{PLUGIN.name}/{name}", date_time=(2020, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, path.read_bytes())
    with ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        assert f"{PLUGIN.name}/metadata.txt" in archive.namelist()
        assert f"{PLUGIN.name}/__init__.py" in archive.namelist()
    print(OUTPUT)


if __name__ == "__main__":
    main()
