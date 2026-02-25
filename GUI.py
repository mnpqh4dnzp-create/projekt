from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QTableWidget, QTableWidgetItem,
    QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt


class Okno(QWidget):
    def pokaz_tylko_zaznaczone(self, lista_widget):
        for i in range(lista_widget.count()):
            item = lista_widget.item(i)

            if item.checkState() == Qt.Checked:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def __init__(self, dataframe):
        super().__init__()
        self.df = dataframe

        self.setWindowTitle("Analiza próbek azbestu")
        self.resize(1200, 700)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        filters_layout = QHBoxLayout()

        # Materiały
        material_layout = QVBoxLayout()
        material_layout.addWidget(QLabel("Materiał"))

        self.lista_material = QListWidget()
        for m in sorted(self.df["material"].unique()):
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_material.addItem(item)

        material_layout.addWidget(self.lista_material)
        filters_layout.addLayout(material_layout)

        # Typ azbestu
        typ_layout = QVBoxLayout()
        typ_layout.addWidget(QLabel("Typ azbestu"))

        self.lista_typ = QListWidget()
        typy = (
            self.df["typ_azbestu"]
            .str.split(",")
            .explode()
            .str.strip()
        )

        # Usuń puste wartości
        typy = typy[typy != ""].unique()

        for t in sorted(typy):
            item = QListWidgetItem(t)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_typ.addItem(item)

        typ_layout.addWidget(self.lista_typ)
        filters_layout.addLayout(typ_layout)

        # Zakresy
        zakres_layout = QVBoxLayout()
        zakres_layout.addWidget(QLabel("Zakres masy próbki"))

        self.min_masa = QLineEdit()
        self.min_masa.setPlaceholderText("Min")

        self.max_masa = QLineEdit()
        self.max_masa.setPlaceholderText("Max")

        zakres_layout.addWidget(self.min_masa)
        zakres_layout.addWidget(self.max_masa)

        zakres_layout.addWidget(QLabel("Zakres % zawartości azbestu"))

        self.min_proc = QLineEdit()
        self.min_proc.setPlaceholderText("Min %")

        self.max_proc = QLineEdit()
        self.max_proc.setPlaceholderText("Max %")

        zakres_layout.addWidget(self.min_proc)
        zakres_layout.addWidget(self.max_proc)

        filters_layout.addLayout(zakres_layout)

        main_layout.addLayout(filters_layout)

        # Przyciski
        self.btn_filtruj = QPushButton("Filtruj")
        self.btn_filtruj.clicked.connect(self.filtruj)
        main_layout.addWidget(self.btn_filtruj)

        self.btn_wyczysc = QPushButton("Wyczyść filtry")
        self.btn_wyczysc.clicked.connect(self.wyczysc_filtry)
        main_layout.addWidget(self.btn_wyczysc)

        # =========================
        # TABELA
        # =========================

        self.tabela = QTableWidget()
        self.tabela.setSortingEnabled(True)
        main_layout.addWidget(self.tabela)

        self.zaladuj_tabele(self.df)

    # ===================================
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

    # ===================================
    def filtruj(self):
        dane = self.df.copy()

        # Materiały
        wybrane_materialy = [
            self.lista_material.item(i).text()
            for i in range(self.lista_material.count())
            if self.lista_material.item(i).checkState() == Qt.Checked
        ]

        if wybrane_materialy:
            dane = dane[dane["material"].isin(wybrane_materialy)]

        # Typy azbestu
        wybrane_typy = [
            self.lista_typ.item(i).text()
            for i in range(self.lista_typ.count())
            if self.lista_typ.item(i).checkState() == Qt.Checked
        ]

        if len(wybrane_typy) > 0:
            wybrane_set = set(wybrane_typy)

            maska = dane["typ_azbestu"].str.split(",").apply(
                lambda lista: set(t.strip() for t in lista if t.strip()) == wybrane_set
            )

            dane = dane[maska]

        # Zakres masy
        try:
            if self.min_masa.text():
                dane = dane[dane["masa_probki"] >= float(self.min_masa.text())]
            if self.max_masa.text():
                dane = dane[dane["masa_probki"] <= float(self.max_masa.text())]
        except ValueError:
            pass

        # Zakres procentu
        try:
            if self.min_proc.text():
                dane = dane[dane["procent_azbestu"] >= float(self.min_proc.text())]
            if self.max_proc.text():
                dane = dane[dane["procent_azbestu"] <= float(self.max_proc.text())]
        except ValueError:
            pass

        if dane.empty:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Brak wybranych danych"
            )
            return
        self.zaladuj_tabele(dane)

    # WYCZYŚĆ FILTRY
    def wyczysc_filtry(self):

        for i in range(self.lista_material.count()):
            self.lista_material.item(i).setCheckState(Qt.Unchecked)

        for i in range(self.lista_typ.count()):
            self.lista_typ.item(i).setCheckState(Qt.Unchecked)

        self.min_masa.clear()
        self.max_masa.clear()
        self.min_proc.clear()
        self.max_proc.clear()

        self.zaladuj_tabele(self.df)