from GUI import Okno
from PySide6.QtWidgets import QApplication
import sys
import pandas as pd

if __name__ == "__main__":
    app = QApplication(sys.argv)

    okno = Okno(pd.DataFrame(columns=["masa próbki", "masa azbestu", "materiał", "typ azbestu"]))
    okno.show()
    sys.exit(app.exec())