from GUI import Okno
from PySide6.QtWidgets import QApplication
import sys
import pandas as pd

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Startujemy z pustym DataFrame
    okno = Okno(pd.DataFrame(columns=["masa_probki", "masa_azbestu", "material", "typ_azbestu"]))
    okno.show()
    sys.exit(app.exec())