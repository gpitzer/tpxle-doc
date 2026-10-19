# Displayhalter für Waveshare 7,5" e-Paper + e-Paper ESP32 Driver Board

Neu konstruiert (nicht aus den SolidWorks-Dateien abgeleitet), im Stil des 10,85"-Originals:
flacher Sockel, Panel lehnt 15° nach hinten in einem Schlitz, Elektronik im hohlen Sockel.

Dateien
- `Case_7.5_Body.stl` – Sockel (offene Seite nach unten aufs Druckbett, ohne Support)
- `Case_7.5_Body_print.stl` – Sockel umgedreht (Oberseite auf dem Bett), ohne Support
- `Case_7.5_BackPlate.stl` – Rückplatte (Rückseite auf dem Bett): Tasche fürs Panel, Seitenwände, Haltelippe oben
- `Case_7.5_BottomCover.stl` – Bodenplatte mit Platinentasche (flach drucken)
- `Case_7.5_Plate.3mf` – beide Teile auf einer Platte (Bambu Studio)
- `build_case.py` – Parameter oben im Skript anpassen, dann `python3 -I build_case.py <Ordner>`

Montage: Platine in die Tasche der Bodenplatte, FFC durch das Fenster im Schlitzboden zum Panel,
Panel von unten in die Tasche der Rückplatte schieben (Lippe oben hält es), Rückplatte samt Panel in den Schlitz stecken, Bodenplatte mit 4× M3-Blechschrauben (Vorbohrung 2,6 mm) anschrauben.

Annahmen (bitte prüfen): Panel 170,2 × 111,2 × 1,18 mm, Board 48,25 × 29,46 mm (Waveshare-Produktseiten).
Lochbild und USB-C-Position des Boards sind nicht angegeben: USB-C-Öffnung sitzt in der rechten
Stirnwand, Platine liegt auf 4 Pads ohne Schrauben. Nach Ankunft des Boards ggf. `USB_*`/`BOARD_*` anpassen.
