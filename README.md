# Ortofotomapa do działki

Wtyczka QGIS do przycięcia lokalnej ortofotomapy do granicy jednej wybranej działki z wektorowej warstwy Geoportalu. Wynik jest zapisywany jako GeoTIFF z przezroczystością poza działką.

[Pobierz paczkę do instalacji w QGIS](Ortofotomapa-do-dzialki-QGIS.zip)

## Jak użyć

1. W QGIS wybierz **Wtyczki → Zarządzanie i instalacja wtyczek → Instaluj z pliku ZIP** i wskaż pobraną paczkę.
2. Dodaj lokalną, georeferencyjną ortofotomapę (np. GeoTIFF).
3. Wczytaj poligonową warstwę działek z Geoportalu, na przykład przez [wtyczkę GUGiK](https://www.geoportal.gov.pl/aktualnosci/gugik-udostepnia-wtyczke-do-pobierania-danych-bezposrednio-do-oprogramowania-qgis/) lub zbiorczy WFS EGiB. Zaznacz **dokładnie jedną** działkę narzędziem wyboru obiektów.
4. Uruchom **Wtyczki → Ortofotomapa i działka → Przytnij ortofotomapę do działki…** i wskaż nowy plik `.tif`.

Wtyczka korzysta z działki już wczytanej do QGIS; sama nie pobiera danych z Geoportalu. Podkład WMS/WMTS nie zastąpi wektorowej warstwy działek. Dane wejściowe pozostają bez zmian, a istniejący plik wynikowy nie jest nadpisywany.

Szczegółowa instrukcja i opis błędów są w [README wtyczki](docinanie_ortofotomapy_geoportal/README.md).

## Jak to działa

Kod eksportuje wybrany poligon do tymczasowej maski (`native:saveselectedfeatures`), a następnie wywołuje `gdal:cliprasterbymasklayer` z przycięciem do granicy, zachowaniem rozdzielczości i kanałem alfa. Dostępne są testy walidacji oraz przekazania parametrów do algorytmu. W tym repozytorium nie wykonano jeszcze pełnego testu w QGIS z prawdziwą ortofotomapą i działką.

```bash
python3 -m unittest discover -s docinanie_ortofotomapy_geoportal/tests -v
python3 scripts/package_plugin.py
```
