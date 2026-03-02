from GUI import Okno
from PySide6.QtWidgets import QApplication
import sys
import pandas as pd

with open("probki.csv", encoding="utf-8") as f:
    lines = f.readlines()

dane = lines[1:]
probki = []

for linia in dane:
    linia = linia.strip()
    if not linia:
        continue

    parts = linia.split()

    masa_probki = float(parts[0].replace(",", "."))
    masa_azbestu = float(parts[1].replace(",", "."))
    material = parts[2]
    typ_azbestu = parts[3]

    probki.append([masa_probki, masa_azbestu, material, typ_azbestu])

# PANDAS
df = pd.DataFrame(
    probki,
    columns=["masa_probki", "masa_azbestu", "material", "typ_azbestu"]
)

df["procent_azbestu"] = (
    df["masa_azbestu"] / df["masa_probki"] * 100
)

df["procent_azbestu"] = df["procent_azbestu"].round(4)

# START GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = Okno(df)
    okno.show()
    sys.exit(app.exec())