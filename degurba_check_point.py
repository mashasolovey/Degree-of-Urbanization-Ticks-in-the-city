from pathlib import Path

import rasterio
from pyproj import Transformer
from rasterio.transform import rowcol

TIF = Path(__file__).parent / "data" / "DGUR_LEVEL2_GRD_1KM_2021.tif"

URBAN = {130, 223, 222, 221}
RURAL = {313, 312, 311}

NAMES = {
    130: "Urban Centre",
    223: "Dense Urban Cluster",
    222: "Semi-dense Urban Cluster",
    221: "Suburban / peri-urban",
    313: "Rural cluster",
    312: "Low density rural",
    311: "Very low density rural",
    310: "Water",
}

with rasterio.open(TIF) as src:
    transformer = Transformer.from_crs(
        "EPSG:4326", src.crs, always_xy=True
    )

    while True:
        text = input("\nCoordinates (lat, lon), or q: ")

        if text.lower() == "q":
            break

        lat, lon = map(float, text.replace(",", " ").split())

        x, y = transformer.transform(lon, lat)
        row, col = rowcol(src.transform, x, y)

        cells = src.read(
            1,
            window=((row - 1, row + 2), (col - 1, col + 2))
        )

        centre = int(cells[1, 1])

        neighbours = [
            int(cells[0, 0]), int(cells[0, 1]), int(cells[0, 2]),
            int(cells[1, 0]),                    int(cells[1, 2]),
            int(cells[2, 0]), int(cells[2, 1]), int(cells[2, 2]),
        ]

        print("\nCentral:", centre, "-", NAMES.get(centre))

        print()
        print(f"{cells[0,0]:3}  {cells[0,1]:3}  {cells[0,2]:3}")
        print(f"{cells[1,0]:3} [{centre:3}] {cells[1,2]:3}")
        print(f"{cells[2,0]:3}  {cells[2,1]:3}  {cells[2,2]:3}")

        if centre in URBAN:
            print("Decision: INCLUDE - urban/peri-urban")

        elif centre in RURAL:
            if any(x in URBAN for x in neighbours):
                print("Urban neighbour: YES")
                print("Decision: INCLUDE - urban-edge")
            else:
                print("Urban neighbour: NO")
                print("Decision: EXCLUDE - rural")

        elif centre == 310:
            print("Decision: CHECK - water")

        else:
            print("Decision: CHECK")