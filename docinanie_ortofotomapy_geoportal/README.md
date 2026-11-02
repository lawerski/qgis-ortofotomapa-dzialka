# Ortofotomapa do działki

Prosta wtyczka do QGIS 3.28+ do wycięcia **ortofotomapy rastrowej** według granicy jednej wybranej działki ewidencyjnej. Wynik zapisuje jako nowy GeoTIFF. Źródłowa ortofotomapa i warstwa działek nie są modyfikowane.

## Instalacja

1. W QGIS otwórz **Wtyczki → Zarządzanie i instalacja wtyczek → Instaluj z pliku ZIP**.
2. Wskaż `Ortofotomapa-do-dzialki-QGIS.zip` i włącz wtyczkę.
3. Jeśli menu wtyczki nie pojawia się, uruchom ponownie QGIS.

Wtyczka używa standardowego modułu **Processing** i dostawcy GDAL w QGIS; nie wymaga osobnego instalowania pakietów Pythona.

## Użycie

1. Wczytaj do QGIS swoją georeferencyjną ortofotomapę jako lokalną warstwę rastrową, np. GeoTIFF. Sam podkład WMS/WMTS nie wystarczy.
2. Wczytaj **wektorową warstwę działek** z Geoportalu. Możesz użyć oficjalnej wtyczki GUGiK [Pobierz dane GUGiK](https://www.geoportal.gov.pl/aktualnosci/gugik-udostepnia-wtyczke-do-pobierania-danych-bezposrednio-do-oprogramowania-qgis/) albo warstwy EGiB z WFS. Adres zbiorczej usługi: `https://mapy.geoportal.gov.pl/wss/service/PZGIK/EGIB/WFS/UslugaZbiorcza`.
3. Uaktywnij warstwę działek i narzędziem **Zaznacz obiekty** zaznacz dokładnie jedną działkę. Samo kliknięcie narzędziem identyfikacji nie jest zaznaczeniem.
4. Otwórz **Wtyczki → Ortofotomapa i działka → Przytnij ortofotomapę do działki…**. Wskaż ortofotomapę, warstwę działek i nazwę nowego pliku `.tif`.
5. Kliknij **Przytnij i zapisz**. Wynik zostanie dodany do projektu.

Maska powstaje z **jednej zaznaczonej działki**, nie z całej warstwy WFS. Algorytm zachowuje rozdzielczość wejściową, przycina do granicy i tworzy przezroczysty obszar poza działką. Różne CRS warstw są obsługiwane przez Processing/GDAL, ale oba muszą być poprawnie przypisane. Wtyczka nie nadpisuje istniejącego pliku wynikowego.

## Kiedy wynik nie powstaje

- **Brak działki**: zaznacz obiekt w warstwie poligonowej; WMS/WMTS nie jest warstwą działek.
- **Zaznaczono kilka**: zostaw jedną działkę.
- **Brak georeferencji**: sprawdź CRS ortofotomapy i działek.
- **Brak pokrycia**: wybrana działka musi leżeć na ortofotomapie.
- **Błąd GDAL**: sprawdź dziennik QGIS **Widok → Panele → Dziennik komunikatów**, folder zapisu i źródło rastra. Przy nieudanym zapisie może zostać częściowy plik wynikowy; usuń go po sprawdzeniu i ponów pod inną nazwą.

Kod używa `native:saveselectedfeatures` do zrobienia tymczasowej maski GeoPackage, a następnie `gdal:cliprasterbymasklayer` z `CROP_TO_CUTLINE`, `KEEP_RESOLUTION` i `ALPHA_BAND`. W tym środowisku wykonano testy logiki i składni, ale pełnego uruchomienia w QGIS nie było - zalecany jest test na kopii ortofotomapy i jednej działce.
