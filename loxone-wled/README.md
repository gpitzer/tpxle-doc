# Loxone ↔ WLED

Steuerung eines WLED-Controllers über die **WLED-HTTP-API** (`/win&...`, GET) per *Virtueller Ausgang*.
Funktioniert ohne Zusatzsoftware direkt in Loxone Config.

## Einrichtung

1. WLED eine **feste IP** geben (Router-Reservierung oder WLED > Config > WiFi Setup), z. B. `192.168.2.157`.
2. Loxone Config: **Virtueller Ausgang** anlegen, Adresse `http://192.168.2.157`
   (oder `WLED_VirtualOutput.xml` importieren, IP anpassen).
3. Option *„Verbindung nach dem Senden schließen"* aktivieren.
4. Pro Funktion einen **Virtuellen Ausgang Befehl** anlegen (Tabelle unten).
5. Befehle mit Bausteinen verbinden (Schalter, Lichtsteuerung, Taster, Slider im Web/App).

## Befehle

| Funktion | Befehl bei EIN | Befehl bei AUS | Befehl für Analogwert |
|---|---|---|---|
| Ein/Aus | `/win&T=1` | `/win&T=0` | – |
| Toggle | `/win&T=2` | – | – |
| Helligkeit | – | – | `/win&A=<v.0>` (0–255) |
| Rot / Grün / Blau | – | – | `/win&R=<v.0>`, `/win&G=<v.0>`, `/win&B=<v.0>` (0–255) |
| Weiß (RGBW) | – | – | `/win&W=<v.0>` |
| Effekt | – | – | `/win&FX=<v.0>` |
| Geschwindigkeit | – | – | `/win&SX=<v.0>` |
| Intensität | – | – | `/win&IX=<v.0>` |
| Palette | – | – | `/win&FP=<v.0>` |
| Preset laden | – | – | `/win&PL=<v.0>` |
| Nachtlicht | `/win&ND&NL=1` | `/win&NL=0` | – |

Mehrere Parameter lassen sich kombinieren, z. B. Warmweiß 50 %:
`/win&T=1&A=128&R=255&G=147&B=41`

## Wertebereiche umrechnen

Loxone-Lichtsteuerung (RGB) und Dimmer liefern **0–100 %**, WLED erwartet **0–255**.
Zwischen Ausgang und Virtuellem Ausgang einen **Formel-Baustein** setzen: `I1 * 2.55`.
Alternativ Befehl `/win&A=<v.0>` belassen und den Analogwert direkt mit 0–255 füttern (Slider mit Min 0 / Max 255).

## Status zurücklesen (optional)

*Virtueller HTTP-Eingang* mit URL `http://192.168.2.157/win` und Intervall z. B. 10 s.
Befehlserkennung für Helligkeit: `<ac>\v</ac>` (0 = aus). Damit lässt sich der Schalter synchron halten, wenn WLED anders bedient wird.

## Zwei RGB-Streifen (deine WLED-Konfiguration)

Laut LED-Setup hängen beide Streifen am selben WLED, mit „Make a segment for each output“:

| Streifen | GPIO | LEDs | WLED-Segment |
|---|---|---|---|
| 1 | 16 | 100 (0–99) | 0 |
| 2 | 2 (reversed) | 180 (100–279) | 1 |

Drei Virtuelle Ausgänge, je mit eigener Vorlage:
- `WLED_VirtualOutput.xml`: **beide Streifen** gemeinsam
- `WLED_VirtualOutput_Streifen1.xml`: nur Streifen 1, Befehle beginnen mit `/win&SS=0&SV=1&...`
- `WLED_VirtualOutput_Streifen2.xml`: nur Streifen 2, Befehle beginnen mit `/win&SS=1&SV=1&...`

Test im Browser (nur Streifen 2 rot): `http://192.168.2.157/win&SS=1&SV=1&R=255&G=0&B=0`
Wenn dabei trotzdem beide Streifen rot werden, die Segmente in WLED unter *Segments* prüfen (zwei Segmente, je eines „selected“)
und mir das Ergebnis schicken; dann passe ich die Befehle an.
Zuverlässigster Weg für getrennte Szenen: Presets in der WLED-App speichern und per `PL=<nr>` aufrufen.

Hinweise zu deinem Setup:
- 280 LEDs ≈ bis zu ca. 16 A bei Volllast Weiß. In WLED unter *LED Preferences* **Maximum Current** setzen (passend zum Netzteil), solange der Helligkeitslimiter aus ist.
- Streifen 2 ist „reversed“: Effekte laufen dort gegenläufig, was bei Wischeffekten gewollt sein kann.
- GPIO 2 ist beim ESP32 ein Boot-Pin; funktioniert meist, bei Boot-Problemen auf einen anderen GPIO wechseln.

## Tipps

- Presets (Ein/Aus-Szenen, Effekte, Farben) zuerst in der WLED-App speichern, in Loxone nur per `PL=<nr>` aufrufen – am robustesten.
- Nicht schneller als ca. 5 Befehle/Sekunde senden (Slider mit Impulsbegrenzung/Entprellung betreiben).
- Mehrere WLED-Geräte: je ein eigener Virtueller Ausgang.
- Effekt-/Palettennummern: WLED > Info, oder `http://<IP>/json/effects` bzw. `/json/palettes`.

## Hinweis zur Verifikation

Die WLED-Parameter (`T`, `A`, `R/G/B/W`, `FX`, `SX`, `IX`, `FP`, `PL`, `ND`, `NL`) entsprechen der dokumentierten WLED-HTTP-API.
Die XML-Vorlage habe ich nicht gegen Loxone Config getestet; falls der Import abgelehnt wird, die Tabelle manuell eintragen.
