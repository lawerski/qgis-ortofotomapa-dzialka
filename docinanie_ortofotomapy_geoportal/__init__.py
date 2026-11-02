"""Punkt wejścia dla menedżera wtyczek QGIS."""


def classFactory(iface):
    from .plugin import OrthoClipPlugin

    return OrthoClipPlugin(iface)
