# Prototyp: Wendeltreppe "Walnut Spiral"

Freitragende Wendeltreppe aus Massivholz: Mittelsäule aus Eiche (Ø 200 mm),
15 Keilstufen aus Nussbaum (45 mm), geschwungener Handlauf als Helix (R 880 mm,
900 mm über Trittfläche), Stahl-Baluster und verdecktes LED-Band (2700 K) unter
jeder Stufe (schwebender Lichteffekt).

## Kennwerte
- Geschoßhöhe: 2700 mm (15 Stufen x 180 mm Steigung)
- Durchmesser: 1900 mm, Auftritt an der Lauflinie (r=600): 251 mm
- Drehung: 360° über die gesamte Treppe (24° pro Stufe)
- Handlauflänge: ca. 6837 mm

## Inhalt
- `treppe.py` – parametrischer Generator (alle Maße als Parameter oben im File)
- `out/grundriss.svg`, `out/lauflinie.svg` – Grundriss und Abwicklung der Lauflinie
- `out/teileliste.csv` – Stückliste für den Prototypenbau

## Alles Weitere erzeugen
Die Binär-Artefakte (Renderings als PNG, `treppe.stl` / `treppe.glb`) werden lokal
generiert:

    pip install numpy matplotlib trimesh shapely mapbox-earcut scipy
    python3 treppe.py

Dann liegen in `out/` auch: ansicht_perspektive.png, ansicht_front.png,
ansicht_oben.png, detail_stufen.png, ansicht_led_unten.png, detail_led.png,
grundriss.png, lauflinie.png, treppe.stl, treppe.glb.
