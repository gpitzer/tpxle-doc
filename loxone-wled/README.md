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

## Zwei RGB-Streifen

Beide Streifen am selben WLED (eine IP):
- **Gemeinsam steuern** (Standard): alle Befehle oben wirken auf beide Streifen, nichts weiter nötig.
- **Getrennt steuern**: in WLED unter *Segments* zwei Segmente anlegen (z. B. Segment 0 = Streifen 1, Segment 1 = Streifen 2).
  Vor den Parametern das Segment wählen, z. B. nur Streifen 2 rot: `/win&SS=1&SV=1&R=255&G=0&B=0`
  (`SS` = Segment-ID, `SV=1` = Segment auswählen; bitte einmal testen, ich konnte das nicht prüfen).
- Hängt jeder Streifen an einem **eigenen WLED-Controller**: je einen Virtuellen Ausgang pro IP anlegen.

## Tipps

- Presets (Ein/Aus-Szenen, Effekte, Farben) zuerst in der WLED-App speichern, in Loxone nur per `PL=<nr>` aufrufen – am robustesten.
- Nicht schneller als ca. 5 Befehle/Sekunde senden (Slider mit Impulsbegrenzung/Entprellung betreiben).
- Mehrere WLED-Geräte: je ein eigener Virtueller Ausgang.
- Effekt-/Palettennummern: WLED > Info, oder `http://<IP>/json/effects` bzw. `/json/palettes`.

## Hinweis zur Verifikation

Die WLED-Parameter (`T`, `A`, `R/G/B/W`, `FX`, `SX`, `IX`, `FP`, `PL`, `ND`, `NL`) entsprechen der dokumentierten WLED-HTTP-API.
Die XML-Vorlage habe ich nicht gegen Loxone Config getestet; falls der Import abgelehnt wird, die Tabelle manuell eintragen.
