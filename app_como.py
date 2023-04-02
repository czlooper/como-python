import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import numpy as np
from io import StringIO


#with open('../config.yaml') as file:
#    config = yaml.load(file, Loader=SafeLoader)

#authenticator = stauth.Authenticate(
#    config['credentials'],
#    config['cookie']['name'],
#    config['cookie']['key'],
#    config['cookie']['expiry_days'],
#    config['preauthorized']
#)
#
#hashed_passwords = stauth.Hasher(['abc', 'def']).generate()

# podminky
def podminka(radek):
    if ((radek.name + 1) >= len(df_pruchod)) & (df_pruchod.loc[radek.name, "ID_ctecky"] != 10707): # pokud jde o poslední řádek a ID_ctecky není Příchod
        return "Odchod"
    elif ((radek.name + 1) >= len(df_pruchod)) & (df_pruchod.loc[radek.name, "ID_ctecky"] != 10708): # pokud jde o poslední řádek a ID_ctecky není Odchod
        return "Chyba - Chybí odchod"
    elif (radek["ID_ctecky"] == 10707) & (df_pruchod.loc[radek.name+1, "ID_ctecky"] == 10708) & (df_pruchod.loc[radek.name+1, "Datum"] == df_pruchod.loc[radek.name, "Datum"]): # pokud v rámci jednoho dne ID_ctecky je příchod a příští průchod je odchod 
        return "Příchod"
    elif (radek["ID_ctecky"] == 10707) & (df_pruchod.loc[radek.name+1, "ID_ctecky"] == 10708) & (df_pruchod.loc[radek.name+1, "Datum"] != df_pruchod.loc[radek.name, "Datum"]): # pokud v rámci ruznych dnu ID_ctecky je příchod a příští průchod je odchod
        return "Chyba - Chybí odchod a následující návštěvě chybí příchod"
    elif (radek["ID_ctecky"] == 10707) & (df_pruchod.loc[radek.name+1, "ID_ctecky"] == 10707) & (df_pruchod.loc[radek.name+1, "Datum"] == df_pruchod.loc[radek.name, "Datum"]): # pokud v rámci jednoho dne ID_ctecky je příchod a příští průchod je také příchod
        return "Chyba - Chybí odchod"
    elif (radek["ID_ctecky"] == 10707) & (df_pruchod.loc[radek.name+1, "ID_ctecky"] == 10707) & (df_pruchod.loc[radek.name+1, "Datum"] != df_pruchod.loc[radek.name, "Datum"]): # pokud v rámci ruznych dnu ID_ctecky je příchod a příští průchod je také příchod
        return "Chyba - Chybí odchod"
    elif (radek["ID_ctecky"] == 10708) & (df_pruchod.loc[radek.name+1, "ID_ctecky"] == 10708): # pokud ID_ctecky je odchod a příští průchod je také odchod
        return "Chyba - Následující návštěvě chybí příchod"
    elif (radek["ID_ctecky"] == 10708) & (df_pruchod.loc[radek.name+1, "ID_ctecky"] == 10707): # pokud ID_ctecky je odchod a příští průchod je příchod
        return "Odchod"
    else:
        return "Logická chyba - přehodnotit podmínky"

#uzivatel = st.number_input("Zadejte číslo karty klienta", key="klic1", step=1)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='Latin2', sep = ";", header = None, names = ["Stav", "Typ_pruchodu", "Prazdna1", "Skupina","Cislo_karty", "Prazdna2", "Skupina2", "Umisteni", "Termin", "Cislo_karty_interni", "Zpusob_zapisu", "ID_ctecky", "Prazdna3", "Prazdna4", "ID_karty_externi"])

    # Rozdělení Termin na Datum a Cas
    df[['Datum', 'Cas']] = df['Termin'].str.split(' ', expand=True)

    # Výběr dat uživatele (karty)
    #uzivatel = int(input("Zadejte číslo karty k vyhodnocení: "))
    #uzivatel = int("345")
    karty = set(df['Cislo_karty'].tolist())
    uzivatel = st.selectbox("Vyberte ze seznamu číslo karty", karty)
    df_karta = df.loc[df["Cislo_karty"] == uzivatel,["Cislo_karty", "ID_ctecky", "Datum", "Cas"]].reset_index(drop=True)

    # příprava prázdných data frame
    df_souhrn_pruchodu = pd.DataFrame()
    df_souhrn_pruchodu_all = pd.DataFrame()
    df_chybar = pd.DataFrame()

    df_chybar_temp = pd.DataFrame()

    # pruchody  
    df_pruchod = df_karta.loc[:,:].reset_index(drop = True)
    df_pruchod['Typ_pruchodu'] = df_pruchod.apply(podminka, axis=1) # přidání sloupce Typ_pruchodu a aplikace podmínky rozčlenění
    df_souhrn_pruchodu = pd.concat([df_souhrn_pruchodu, df_pruchod], axis = 0).reset_index(drop = True) # Přidání průchodu do souhrnu 
    df_souhrn_pruchodu["Cas_int"] = pd.to_timedelta(df_souhrn_pruchodu['Cas']+":00").dt.total_seconds() / 3600 # Převod Cas(str) na Cas_int(int)
    df_souhrn_pruchodu['Cas_int'] = np.where(df_souhrn_pruchodu.loc[:,'Typ_pruchodu'] == 'Příchod', -df_souhrn_pruchodu.loc[:,'Cas_int'], df_souhrn_pruchodu.loc[:,'Cas_int']) # Dle sloupce Typ_pruchodu upravuje hodnotu Cas_int na *(-1)
    df_souhrn_pruchodu_all = df_souhrn_pruchodu.copy() # kopie průchodů vč. chyb pro pozdější výpis
    
    # chybar  
    df_chybar_temp = df_souhrn_pruchodu.loc[df_souhrn_pruchodu["Typ_pruchodu"].str.contains("Chyba")] # uložení řádků s chybou
    df_indexy_chyb = df_souhrn_pruchodu[df_souhrn_pruchodu["Typ_pruchodu"].str.contains("Chyba")].index # indexy řádků s chybou
    df_souhrn_pruchodu_all = df_souhrn_pruchodu_all.loc[:,["Datum","Cas","Typ_pruchodu", "ID_ctecky"]] # vytvoření pohledového chybáře
    df_souhrn_pruchodu_all_view = df_souhrn_pruchodu_all.loc[:,["Datum","Cas","Typ_pruchodu"]] # vytvoření pohledového chybáře
    df_souhrn_pruchodu.drop(df_indexy_chyb, inplace=True) # vymazání řádků s chybou
    df_chybar = pd.concat([df_chybar, df_chybar_temp], axis=0).reset_index(drop = True) # doplnění průchodového chybar_temp do chybare
    df_chybar_view = df_chybar.loc[:,["Datum","Cas","Typ_pruchodu"]] # vytvoření pohledového chybáře
    #print(df_souhrn_pruchodu) # pracovní výpis průchodů
    n = df_chybar.shape[0] # zjištění počtu chyb v chybáři

    # přepočet stráveného času na hod - min
    Stravene_hodiny = int(df_souhrn_pruchodu['Cas_int'].sum()) 
    Stravene_minuty = round(((df_souhrn_pruchodu['Cas_int'].sum()) - (Stravene_hodiny))*60)

    # výpis informačního řádku
    st.text(f"Uživatel s kartou {df_souhrn_pruchodu.iloc[0,0]} strávil v COMO {Stravene_hodiny} hodin a {Stravene_minuty} minut. \nZáznamy obsahují {n} chyb.\n")
    if n > 0: # pokud existují chyby
        # pd.set_option('display.max_rows', None) # zruší omezení výpisu počtu řádků
        # pd.set_option('display.max_colwidth', None) # zruší omezení výpisu počtu sloupců
        st.markdown("---")
        st.text("Chybář")
        st.dataframe(df_chybar_view, width = 1000) # výpis chybáře
        st.markdown("---")
        st.text("Podrobný výpis")
        st.dataframe(df_souhrn_pruchodu_all_view, width = 1000) # vypiš průchody