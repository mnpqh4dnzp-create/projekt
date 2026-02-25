import proj
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit
)

class Okno(QWidget):
    def __init__(self, dataframe):
        super().__init__()
        self.df = dataframe
        self.setWindowTitle("Analiza próbek azbestu")
        self.resize(1000, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ===== FILTRY =====
        filter_layout = QHBoxLayout()

        # Materiał
        self.combo_material = QComboBox()
        self.combo_material.addItem("Wszystkie")
        self.combo_material.addItems(sorted(self.df["material"].unique()))

        # Typ azbestu
        self.combo_typ = QComboBox()
        self.combo_typ.addItem("Wszystkie")
        typy = (
            self.df["typ_azbestu"]
            .str.split(",")
            .explode()
            .str.strip()
            .unique()
        )
        self.combo_typ.addItems(sorted(typy))

        # Zakres masy próbki
        self.min_masa = QLineEdit()
        self.min_masa.setPlaceholderText("Min masa")

        self.max_masa = QLineEdit()
        self.max_masa.setPlaceholderText("Max masa")

        # Przyciski
        self.btn_filtruj = QPushButton("Filtruj")
        self.btn_filtruj.clicked.connect(self.filtruj)

        self.btn_wykres = QPushButton("Wykres (scatter)")
        self.btn_wykres.clicked.connect(self.pokaz_wykres)

        # Dodanie do layoutu
        filter_layout.addWidget(QLabel("Materiał:"))
        filter_layout.addWidget(self.combo_material)
        filter_layout.addWidget(QLabel("Typ:"))
        filter_layout.addWidget(self.combo_typ)
        filter_layout.addWidget(self.min_masa)
        filter_layout.addWidget(self.max_masa)
        filter_layout.addWidget(self.btn_filtruj)
        filter_layout.addWidget(self.btn_wykres)

        self.layout.addLayout(filter_layout)

        # ===== TABELA =====
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        self.zaladuj_tabele(self.df)

    def zaladuj_tabele(self, dane):
        self.tabela.setRowCount(len(dane))
        self.tabela.setColumnCount(len(dane.columns))
        self.tabela.setHorizontalHeaderLabels(dane.columns)

        for i in range(len(dane)):
            for j in range(len(dane.columns)):
                self.tabela.setItem(
                    i, j,
                    QTableWidgetItem(str(dane.iloc[i, j]))
                )

    def filtruj(self):
        dane = self.df.copy()

        # Materiał
        material = self.combo_material.currentText()
        if material != "Wszystkie":
            dane = dane[dane["material"] == material]

        # Typ azbestu
        typ = self.combo_typ.currentText()
        if typ != "Wszystkie":
            dane = dane[dane["typ_azbestu"].str.contains(typ)]

        # Zakres masy
        try:
            min_val = float(self.min_masa.text()) if self.min_masa.text() else None
            max_val = float(self.max_masa.text()) if self.max_masa.text() else None

            if min_val is not None:
                dane = dane[dane["masa_probki"] >= min_val]
            if max_val is not None:
                dane = dane[dane["masa_probki"] <= max_val]

        except ValueError:
            pass

        self.aktualne_dane = dane
        self.zaladuj_tabele(dane)

    def pokaz_wykres(self):
        dane = getattr(self, "aktualne_dane", self.df)

        plt.figure()
        plt.scatter(dane["masa_probki"], dane["masa_azbestu"])
        plt.xlabel("Masa próbki")
        plt.ylabel("Masa azbestu")
        plt.title("Scatter po filtrach")
        plt.show()


# ===== URUCHOMIENIE GUI =====
app = QApplication(sys.argv)
okno = Okno(df)
okno.show()
sys.exit(app.exec())