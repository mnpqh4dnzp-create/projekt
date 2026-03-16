from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QTableWidget, QTableWidgetItem,
    QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QComboBox, QSplitter, QFileDialog
)
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from tooltips import TOOLTIPS

class Okno(QWidget):
    def import_csv(self):
        sciezka, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz plik CSV",
            "",
            "CSV Files (*.csv *.txt)"
        )

        if not sciezka:
            return

        try:
            df = pd.read_csv(
                sciezka,
                sep=r'\s+',
                engine='python',
                names=["masa próbki", "masa azbestu", "materiał", "typ azbestu"],
                skiprows=1
            )

            df["masa próbki"] = df["masa próbki"].astype(str).str.replace(",", ".").astype(float)
            df["masa azbestu"] = df["masa azbestu"].astype(str).str.replace(",", ".").astype(float)

            df["procentowa zawartość azbestu"] = (df["masa azbestu"] / df["masa próbki"] * 100).round(4)

            self.df = df
            self.dane_widoczne = df.copy()

            if not df.empty:
                self.lista_materiał.clear()
                for m in sorted(df["materiał"].unique()):
                    item = QListWidgetItem(m)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    if m in TOOLTIPS:
                        item.setToolTip(TOOLTIPS[m])
                    self.lista_materiał.addItem(item)

                self.lista_typ.clear()
                typy = df["typ azbestu"].str.split(",").explode().str.strip()
                typy = typy[typy != ""].unique()
                for t in sorted(typy):
                    item = QListWidgetItem(t)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    if t in TOOLTIPS:
                        item.setToolTip(TOOLTIPS[t])
                    self.lista_typ.addItem(item)

            self.zaladuj_tabele(df)
            self.aktualizuj_statystyki(df)

        except Exception as e:
            QMessageBox.warning(self, "Błąd importu", str(e))

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

        materiał_layout = QVBoxLayout()
        materiał_layout.addWidget(QLabel("Materiał"))

        self.lista_materiał = QListWidget()
        for m in sorted(self.df["materiał"].unique()):
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

            if m in TOOLTIPS:
                item.setToolTip(TOOLTIPS[m])

            self.lista_materiał.addItem(item)

        materiał_layout.addWidget(self.lista_materiał)
        filters_layout.addLayout(materiał_layout)

        typ_layout = QVBoxLayout()
        typ_layout.addWidget(QLabel("Typ azbestu"))

        self.lista_typ = QListWidget()
        typy = (
            self.df["typ azbestu"]
            .str.split(",")
            .explode()
            .str.strip()
        )

        typy = typy[typy != ""].unique()

        for t in sorted(typy):
            item = QListWidgetItem(t)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

            if t in TOOLTIPS:
                item.setToolTip(TOOLTIPS[t])

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

        self.btn_import = QPushButton("Import CSV")
        self.btn_import.clicked.connect(self.import_csv)
        main_layout.addWidget(self.btn_import)


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
            "Histogram procentowa zawartość azbestu",
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

        wybrane_materiały = [
            self.lista_materiał.item(i).text()
            for i in range(self.lista_materiał.count())
            if self.lista_materiał.item(i).checkState() == Qt.Checked
        ]

        if wybrane_materiały:
            dane = dane[dane["materiał"].isin(wybrane_materiały)]

        wybrane_typy = [
            self.lista_typ.item(i).text()
            for i in range(self.lista_typ.count())
            if self.lista_typ.item(i).checkState() == Qt.Checked
        ]

        if len(wybrane_typy) > 0:
            wybrane_set = set(wybrane_typy)

            maska = dane["typ azbestu"].str.split(",").apply(
                lambda lista: set(t.strip() for t in lista if t.strip()) == wybrane_set
            )

            dane = dane[maska]

        try:
            if self.min_masa.text():
                dane = dane[dane["masa próbki"] >= float(self.min_masa.text())]
            if self.max_masa.text():
                dane = dane[dane["masa próbki"] <= float(self.max_masa.text())]
        except ValueError:
            pass

        try:
            if self.min_proc.text():
                dane = dane[dane["procentowa zawartość azbestu"] >= float(self.min_proc.text())]
            if self.max_proc.text():
                dane = dane[dane["procentowa zawartość azbestu"] <= float(self.max_proc.text())]
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

        for i in range(self.lista_materiał.count()):
            self.lista_materiał.item(i).setCheckState(Qt.Unchecked)

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

        stats = dane[["masa próbki", "procentowa zawartość azbestu"]].describe().T

        tekst = ""

        for index, row in stats.iterrows():
            tekst += f"""
    {index}
    Średnia: {row['mean']:.4f} g
    Odchylenie std: {row['std']:.4f} g
    Min: {row['min']:.4f} g
    Max: {row['max']:.4f} g
    Mediana: {dane[index].median():.4f} g
    -----------------------
    """

        self.statystyka_label.setText(tekst)

    def generuj_opis_statystyczny(self, df):

        if df.empty:
            return "Brak danych do analizy."

        n = len(df)

        masa_mean = df["masa próbki"].mean()
        masa_std = df["masa próbki"].std()
        masa_min = df["masa próbki"].min()
        masa_max = df["masa próbki"].max()

        proc_mean = df["procentowa zawartość azbestu"].mean()
        proc_std = df["procentowa zawartość azbestu"].std()
        proc_min = df["procentowa zawartość azbestu"].min()
        proc_max = df["procentowa zawartość azbestu"].max()

        cv = proc_std / proc_mean * 100 if proc_mean != 0 else 0

        if cv < 10:
            zmiennosc = "niską zmienność wyników"
        elif cv < 30:
            zmiennosc = "umiarkowaną zmienność wyników"
        else:
            zmiennosc = "wysoką zmienność wyników"

        opis = f"""
    INTERPRETACJA WYNIKÓW
    ------------------------------

    Analizie poddano {n} próbek materiałów zawierających azbest.

    Średnia masa próbki wynosiła {masa_mean:.4f} g (SD = {masa_std:.4f} g),
    przy zakresie od {masa_min:.4f} g do {masa_max:.4f} g.

    Średnia procentowa zawartość azbestu wynosiła {proc_mean:.4f} %
    (SD = {proc_std:.4f} %), przy wartościach od {proc_min:.4f} % do {proc_max:.4f} %.

    Analiza zmienności wskazuje na {zmiennosc}.
    """

        return opis

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
            idx_masa = kolumny.index("masa próbki")
            idx_proc = kolumny.index("procentowa zawartość azbestu")
            idx_materiał = kolumny.index("materiał")
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Brak wymaganych kolumn w tabeli.")
            return

        for row in range(self.tabela.rowCount()):
            try:
                masa = float(self.tabela.item(row, idx_masa).text())
                proc = float(self.tabela.item(row, idx_proc).text())
                materiał = self.tabela.item(row, idx_materiał).text()

                masy.append(masa)
                procenty.append(proc)
                materiały.append(materiał)
            except (ValueError, AttributeError):
                continue

        if not masy:
            QMessageBox.warning(self, "Błąd", "Nie udało się odczytać danych liczbowych.")
            return

        plt.figure()

        # Scatter
        if wybor == "Scatter (masa vs procent)":
            plt.scatter(masy, procenty)
            plt.xlabel("masa próbki (g)")
            plt.ylabel("procentowa zawartość azbestu")
            plt.title("Zależność masy próbki od procentu azbestu")
            plt.grid(True)

        # Histogram masa
        elif wybor == "Histogram masa próbki":
            plt.hist(masy, bins=20)
            plt.xlabel("Masa próbki (g)")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram masy próbek")
            plt.grid(True)

        # Histogram procent
        elif wybor == "Histogram procentowa zawartość azbestu":
            plt.hist(procenty, bins=20)
            plt.xlabel("procentowa zawartość azbestu")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram procentowej zawartości azbestu")
            plt.grid(True)

        # Barplot materiał → średni procentowa zawartość azbestu
        elif wybor == "Barplot - materiał vs średni % azbestu":
            df_temp = self.df.copy()

            avg_data = (
                df_temp.groupby("materiał")["procentowa zawartość azbestu"]
                .mean()
                .sort_values()
            )

            plt.bar(avg_data.index, avg_data.values)
            plt.xlabel("Materiał")
            plt.ylabel("Średni procentowa zawartość azbestu")
            plt.title("Średni procentowa zawartość azbestu według materiału")
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

        if not dane:
            QMessageBox.warning(self, "Błąd", "Brak poprawnych danych.")
            return

        df = self.dane_widoczne.copy()

        stats = {
            "Masa próbki (g)": [
                df["masa próbki"].mean(),
                df["masa próbki"].std(),
                df["masa próbki"].min(),
                df["masa próbki"].max(),
                df["masa próbki"].median(),
                len(df)
            ],
            "Zawartość azbestu (%)": [
                df["procentowa zawartość azbestu"].mean(),
                df["procentowa zawartość azbestu"].std(),
                df["procentowa zawartość azbestu"].min(),
                df["procentowa zawartość azbestu"].max(),
                df["procentowa zawartość azbestu"].median(),
                len(df)
            ]
        }

        raport = "RAPORT STATYSTYCZNY ANALIZY AZBESTU\n\n"
        raport += f"{'Parametr':<25}{'Średnia':<10}{'Odchylenie std':<18}{'Min':<10}{'Max':<10}{'Mediana':<10}{'Liczba próbek'}\n"
        raport += "-" * 80 + "\n"

        for parametr, values in stats.items():
            raport += (
                f"{parametr:<25}"
                f"{values[0]:<10.4f}"
                f"{values[1]:<18.4f}"
                f"{values[2]:<10.4f}"
                f"{values[3]:<10.4f}"
                f"{values[4]:<10.4f}"
                f"{values[5]}\n"
            )

        raport += "\n"

        opis = self.generuj_opis_statystyczny(df)

        raport += opis

        with open("raport_statystyczny.txt", "w", encoding="utf-8") as f:
            f.write(raport)

        csv_df = pd.DataFrame({
            "Parametr": list(stats.keys()),
            "Średnia": [stats[k][0] for k in stats],
            "Odchylenie std": [stats[k][1] for k in stats],
            "Min": [stats[k][2] for k in stats],
            "Max": [stats[k][3] for k in stats],
            "Mediana": [stats[k][4] for k in stats],
            "Liczba próbek": [stats[k][5] for k in stats],
        })

        csv_df.round(4).to_csv("raport_statystyczny.csv", sep=";", index=False)

        QMessageBox.information(self, "OK", "Eksport raportu zakończony.")

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
            plt.xlabel("masa próbki")
            plt.ylabel("procentowa zawartość azbestu")
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
            plt.xlabel("procentowa zawartość azbestu")
            plt.ylabel("Liczba próbek")
            plt.title("Histogram procentowa zawartość azbestu")
            plt.grid(True)

            # Barplot materiał → średni procentowa zawartość azbestu
            plt.figure()

            df_temp = self.df.copy()

            avg_data = (
                df_temp.groupby("materiał")["procentowa zawartość azbestu"]
                .mean()
                .sort_values()
            )

            plt.bar(avg_data.index, avg_data.values)
            plt.xlabel("Materiał")
            plt.ylabel("Średni procentowa zawartość azbestu")
            plt.title("Średni procentowa zawartość azbestu według materiału")
            plt.xticks(rotation=45)
            plt.grid(True)

            pdf.savefig()
            plt.close()

            pdf.savefig()
            plt.close()

        QMessageBox.information(self, "OK", "Eksport wykresów do PDF zakończony.")