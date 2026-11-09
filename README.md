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

## 3D direkt auf GitHub ansehen
- `out/treppe_preview.stl` anklicken → GitHub zeigt das Modell interaktiv im 3D-Viewer
  (Low-Poly-Vorschau: 15 Keilstufen + Mittelsäule)

## Inhalt
- `treppe.py` – parametrischer Generator (alle Maße als Parameter oben im File)
- `out/grundriss.svg`, `out/lauflinie.svg` – Grundriss und Abwicklung der Lauflinie
- `out/teileliste.csv` – Stückliste für den Prototypenbau
- `out/treppe_preview.stl` – 3D-Vorschau für den GitHub-Viewer

## Vollmodell + Renderings lokal erzeugen
    pip install numpy matplotlib trimesh shapely mapbox-earcut scipy
    python3 treppe.py

Dann liegen in `out/` auch: treppe.stl / treppe.glb (Vollmodell, 14.200 Faces) und
ansicht_perspektive.png, ansicht_front.png, ansicht_oben.png, detail_stufen.png,
ansicht_led_unten.png, detail_led.png, grundriss.png, lauflinie.png.
