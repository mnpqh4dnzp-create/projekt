import pandas as pd
import matplotlib.pyplot as plt

with open("C:\\Users\\MiQuRs\\source\\repos\\TEST\\TEST\\probki.txt", encoding="utf-8") as f:
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

masa_probki_k = [p[0] for p in probki]
masa_azbestu_k = [p[1] for p in probki]
material_k = [p[2] for p in probki]
typ_azbestu_k = [p[3] for p in probki]

#print(masa_probki_k[:5])
#print(material_k[:5])

# Rodzaje materiałów
lfd = [p for p in probki if p[2] == "LFD"]
lf = [p for p in probki if p[2] == "LF"]
sbd = [p for p in probki if p[2] == "SBD"]
lbd = [p for p in probki if p[2] == "LBD"]
ac = [p for p in probki if p[2] == "AC"]
wp = [p for p in probki if p[2] == "WP"]

# Typy azbestu 
ch = [p for p in probki if "CH" in p[3]]
am = [p for p in probki if "AM" in p[3]]
cr = [p for p in probki if "CR" in p[3]]
an = [p for p in probki if "AN" in p[3]]

# Masy
masy_probek = [p for p in probki if p[0] > 1]
masy_azbestu = [p for p in probki if p[1] > 1]

#for w in ac:
#    print(w)

# Listy mas azbestu wg materiału
lista_material = {}

for p in probki:
    material = p[2]
    masa_azbestu = p[1]

    if material not in lista_material:
        lista_material[material] = []

    lista_material[material].append(masa_azbestu)

print("Listy mas azbestu wg materiału:\n")

for material, lista in lista_material.items():
    print(material, "->", lista)

# Listy mas azbestu wg typu azbestu
lista_typ = {}

for p in probki:
    masa_azbestu = p[1]
    typy = p[3].split(",")

    for typ in typy:
        typ = typ.strip()

        if typ not in lista_typ:
            lista_typ[typ] = []

        lista_typ[typ].append(masa_azbestu)

print("\nListy mas azbestu wg typu:\n")

for typ, lista in lista_typ.items():
    print(typ, "->", lista)

# Listy mas próbek wg materiału

lista_masa_probki_material = {}

for p in probki:
    material = p[2]     
    masa_probki = p[0]

    if material not in lista_masa_probki_material:
        lista_masa_probki_material[material] = []

    lista_masa_probki_material[material].append(masa_probki)

print("\nListy mas próbek wg materiału:\n")

for material, lista in lista_masa_probki_material.items():
    print(material, "->", lista)

# Listy mas próbek wg typu azbestu

lista_masa_probki_typ = {}

for p in probki:
    masa_probki = p[0]
    typy = p[3].split(",")  

    for typ in typy:
        typ = typ.strip()

        if typ not in lista_masa_probki_typ:
            lista_masa_probki_typ[typ] = []

        lista_masa_probki_typ[typ].append(masa_probki)

print("\nListy mas próbek wg typu azbestu:\n")

for typ, lista in lista_masa_probki_typ.items():
    print(typ, "->", lista)

# Listy mas próbek do mas azbestu

lista_masa_probki_i_azbestu_typ = {}

listy_mas_probki_do_mas_azbestu = {}

for p in probki:
    masa_probki = p[0]
    masa_azbestu = p[1]
    typy = p[3].split(",")

    for typ in typy:
        typ = typ.strip()

        if typ not in listy_mas_probki_do_mas_azbestu:
            listy_mas_probki_do_mas_azbestu[typ] = []

        listy_mas_probki_do_mas_azbestu[typ].append((masa_probki, masa_azbestu))

print("\nListy mas próbki do mas azbestu wg typu:\n")

for typ, lista in listy_mas_probki_do_mas_azbestu.items():
    print(typ, "->", lista)
     


#Pandas

df = pd.DataFrame(probki, columns=["masa_probki", "masa_azbestu", "material", "typ_azbestu"])


#podstawowe srednie i mediany

print("Średnia masa próbki:")
print(df["masa_probki"].mean())


print("\nŚrednia masa azbestu:")
print(df["masa_azbestu"].mean())


print("\nMediana masa próbki:")
print(df["masa_probki"].median())


print("\nMediana masa azbestu:")
print(df["masa_azbestu"].median())


print("\nŚrednia masa azbestu wg materiału:")
print(df.groupby("material")["masa_azbestu"].mean())


print("\nŚrednia masa azbestu wg typu azbestu:")

df_typ = df.copy()
df_typ["typ_azbestu"] = df_typ["typ_azbestu"].str.split(",")
df_typ = df_typ.explode("typ_azbestu")
df_typ["typ_azbestu"] = df_typ["typ_azbestu"].str.strip()

print(df_typ.groupby("typ_azbestu")["masa_azbestu"].mean())

# procentowa zawartosc azbestu w probce

df["procent_azbestu"] = (df["masa_azbestu"] / df["masa_probki"]) * 100

print("\nProcentowy udział azbestu w próbce:\n")
print(df[["masa_probki", "masa_azbestu", "procent_azbestu"]])


# Matplotlib, histogramy

# Masy próbki 
plt.figure()
plt.hist(df["masa_probki"], bins=10)
plt.xlabel("Masa próbki")
plt.ylabel("Liczba próbek")
plt.title("Histogram masy próbek")
plt.show()


#Masy azbestu
plt.figure()
plt.hist(df["masa_azbestu"], bins=10)
plt.xlabel("Masa azbestu")
plt.ylabel("Liczba próbek")
plt.title("Histogram masy azbestu")
plt.show()


#Procentowa zawartość azbestu
plt.figure()
plt.hist(df["procent_azbestu"], bins=10)
plt.xlabel("Procent azbestu w próbce")
plt.ylabel("Liczba próbek")
plt.title("Histogram procentowej zawartości azbestu")
plt.show()


#Masa azbestu dla typu materiału
plt.figure()
plt.hist(df[df["material"] == "AC"]["masa_azbestu"], bins=10)
plt.xlabel("Masa azbestu")
plt.ylabel("Liczba próbek")
plt.title("Histogram masy azbestu dla materiału AC")
plt.show()


#Wykres rozrzutu masa próbki vs masa azbestu 

plt.figure()
plt.scatter(df["masa_probki"], df["masa_azbestu"])
plt.xlabel("Masa próbki")
plt.ylabel("Masa azbestu")
plt.title("Wykres rozrzutu: masa próbki vs masa azbestu")
plt.show()

#Wykres rozrzutu masa próbki vs zawartosc procentowa azbestu
plt.figure()
plt.scatter(df["masa_probki"], df["procent_azbestu"])
plt.xlabel("Masa próbki")
plt.ylabel("Procent azbestu")
plt.title("Masa próbki vs procent azbestu")
plt.show()






   
