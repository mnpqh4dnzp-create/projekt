from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QTableWidget, QTableWidgetItem,
    QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QComboBox, QSplitter
)
from PySide6.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import pandas as pd

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

        self.dane_widoczne = dataframe.copy()

        self.setWindowTitle("Analiza próbek azbestu")
        self.resize(1200, 700)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        filters_layout = QHBoxLayout()

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

        typ_layout = QVBoxLayout()
        typ_layout.addWidget(QLabel("Typ azbestu"))

        self.lista_typ = QListWidget()
        typy = (
            self.df["typ_azbestu"]
            .str.split(",")
            .explode()
            .str.strip()
        )

        typy = typy[typy != ""].unique()

        for t in sorted(typy):
            item = QListWidgetItem(t)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_typ.addItem(item)

        typ_layout.addWidget(self.lista_typ)
        filters_layout.addLayout(typ_layout)

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


        self.btn_filtruj = QPushButton("Filtruj")
        self.btn_filtruj.clicked.connect(self.filtruj)
        main_layout.addWidget(self.btn_filtruj)

        self.btn_wyczysc = QPushButton("Wyczyść filtry")
        self.btn_wyczysc.clicked.connect(self.wyczysc_filtry)
        main_layout.addWidget(self.btn_wyczysc)

        self.btn_wykres = QPushButton("Generuj wykres")
        self.btn_wykres.clicked.connect(self.generuj_wykres)
        main_layout.addWidget(self.btn_wykres)

        self.btn_export_csv = QPushButton("Eksport statystyk CSV")
        self.btn_export_csv.clicked.connect(self.eksport_csv)
        main_layout.addWidget(self.btn_export_csv)

        self.btn_export_pdf = QPushButton("Eksport wykresów PDF")
        self.btn_export_pdf.clicked.connect(self.eksport_pdf)
        main_layout.addWidget(self.btn_export_pdf)


        self.combo_wykres = QComboBox()
        self.combo_wykres.addItems([
            "Scatter (masa vs procent)",
            "Histogram masa próbki",
            "Histogram procent azbestu",
            "Barplot - materiał vs średni % azbestu"
        ])

        main_layout.addWidget(self.combo_wykres)

        self.tabela = QTableWidget()
        self.tabela.setSortingEnabled(True)

        self.statystyka_label = QLabel()
        self.statystyka_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.statystyka_label.setStyleSheet("font-size: 13px;")
        self.statystyka_label.setWordWrap(True)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.tabela)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        right_layout.addWidget(QLabel("Statystyka danych"))
        right_layout.addWidget(self.statystyka_label)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        self.zaladuj_tabele(self.df)
        self.aktualizuj_statystyki(self.df)


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
        self.aktualizuj_statystyki(dane)

        self.dane_widoczne = dane.copy()

    def wyczysc_filtry(self):

        for i in range(self.lista_material.count()):
            self.lista_material.item(i).setCheckState(Qt.Unchecked)

        for i in range(self.lista_typ.count()):
            self.lista_typ.item(i).setCheckState(Qt.Unchecked)

        self.min_masa.clear()
        self.max_masa.clear()
        self.min_proc.clear()
        self.max_proc.clear()

        self.dane_widoczne = self.df.copy()
        self.zaladuj_tabele(self.dane_widoczne)
        self.aktualizuj_statystyki(self.dane_widoczne)


    def aktualizuj_statystyki(self, dane):
        if dane.empty:
            self.statystyka_label.setText("Brak danych")
            return

        stats = dane[["masa_probki", "procent_azbestu"]].describe().T

        tekst = ""

        for index, row in stats.iterrows():
            tekst += f"""
    {index}
    Średnia: {row['mean']:.2f}
    Odchylenie std: {row['std']:.2f}
    Min: {row['min']:.2f}
    Max: {row['max']:.2f}
    Mediana: {dane[index].median():.2f}
    -----------------------
    """

        self.statystyka_label.setText(tekst)

    def generuj_wykres(self):
        if self.tabela.rowCount() == 0:
            QMessageBox.warning(self, "Brak danych", "Brak danych do wygenerowania wykresu.")
            return

        wybor = self.combo_wykres.currentText()

        masy = []
        procenty = []
        materiały = []

        kolumny = [
            self.tabela.horizontalHeaderItem(i).text()
            for i in range(self.tabela.columnCount())
        ]

        try:
            idx_masa = kolumny.index("masa_probki")
            idx_proc = kolumny.index("procent_azbestu")
            idx_material = kolumny.index("material")
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Brak wymaganych kolumn w tabeli.")
            return

        for row in range(self.tabela.rowCount()):
            try:
                masa = float(self.tabela.item(row, idx_masa).text())
                proc = float(self.tabela.item(row, idx_proc).text())
                material = self.tabela.item(row, idx_material).text()

                masy.append(masa)
                procenty.append(proc)
                materiały.append(material)
            except (ValueError, AttributeError):
                continue

        if not masy:
            QMessageBox.warning(self, "Błąd", "Nie udało się odczytać danych liczbowych.")
            return

        plt.figure()

        # Scatter
        if wybor == "Scatter (masa vs procent)":
            plt.scatter(masy, procenty)
            plt.xlabel("masa_probki")
            plt.ylabel("procent_azbestu")
            plt.title("Zależność masy próbki od procentu azbestu")
            plt.grid(True)

        # Histogram masa
        elif wybor == "Histogram masa próbki":
            plt.hist(masy, bins=20)
            plt.xlabel("Masa próbki")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram masy próbek")
            plt.grid(True)

        # Histogram procent
        elif wybor == "Histogram procent azbestu":
            plt.hist(procenty, bins=20)
            plt.xlabel("Procent azbestu")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram procentowej zawartości azbestu")
            plt.grid(True)

        # Barplot materiał → średni procent azbestu
        elif wybor == "Barplot - materiał vs średni % azbestu":
            df_temp = self.df.copy()

            avg_data = (
                df_temp.groupby("material")["procent_azbestu"]
                .mean()
                .sort_values()
            )

            plt.bar(avg_data.index, avg_data.values)
            plt.xlabel("Materiał")
            plt.ylabel("Średni procent azbestu")
            plt.title("Średni procent azbestu według materiału")
            plt.xticks(rotation=45)
            plt.grid(True)

        plt.tight_layout()
        plt.show()

    def eksport_csv(self):
        if self.tabela.rowCount() == 0:
            QMessageBox.warning(self, "Błąd", "Brak danych do eksportu.")
            return

        dane = []

        for row in range(self.tabela.rowCount()):
            try:
                masa = float(self.tabela.item(row, 0).text())
                proc = float(self.tabela.item(row, 1).text())
                dane.append([masa, proc])
            except:
                continue

        df_stats = pd.DataFrame(dane, columns=["masa_probki", "procent_azbestu"])

        stats = df_stats.describe().T

        stats["mediana"] = df_stats.median()

        stats.to_csv("statystyki.csv", encoding="utf-8")

        QMessageBox.information(self, "OK", "Eksport statystyk do CSV zakończony.")

    def eksport_pdf(self):
        if self.tabela.rowCount() == 0:
            QMessageBox.warning(self, "Błąd", "Brak danych do eksportu.")
            return

        masy = []
        procenty = []

        for row in range(self.tabela.rowCount()):
            try:
                masy.append(float(self.tabela.item(row, 0).text()))
                procenty.append(float(self.tabela.item(row, 1).text()))
            except:
                continue

        with PdfPages("wykresy.pdf") as pdf:

            # Scatter
            plt.figure()
            plt.scatter(masy, procenty)
            plt.xlabel("masa_probki")
            plt.ylabel("procent_azbestu")
            plt.title("Zależność masy próbki od procentu azbestu")
            plt.grid(True)

            pdf.savefig()
            plt.close()

            # Histogram masa
            plt.figure()
            plt.hist(masy, bins=20)
            plt.xlabel("Masa próbki")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram masy próbek")
            plt.grid(True)

            pdf.savefig()
            plt.close()

            # Histogram procent
            plt.figure()
            plt.hist(procenty, bins=20)
            plt.xlabel("Procent azbestu")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram procent azbestu")
            plt.grid(True)

            # Barplot materiał → średni procent azbestu
            plt.figure()

            df_temp = self.df.copy()

            avg_data = (
                df_temp.groupby("material")["procent_azbestu"]
                .mean()
                .sort_values()
            )

            plt.bar(avg_data.index, avg_data.values)
            plt.xlabel("Materiał")
            plt.ylabel("Średni procent azbestu")
            plt.title("Średni procent azbestu według materiału")
            plt.xticks(rotation=45)
            plt.grid(True)

            pdf.savefig()
            plt.close()

            pdf.savefig()
            plt.close()

        QMessageBox.information(self, "OK", "Eksport wykresów do PDF zakończony.")