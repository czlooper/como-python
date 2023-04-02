import streamlit as st
import pandas as pd
import plotly.express as px

st.header("Moje první aplikace")
st.header("Vypočtu ti obvod a obsah či objem, plochu a součet hran")

st.markdown("---")


volba = st.radio("Vyber si tvar", ["Čtverec", "Obdelník","Krychle"])
if volba == "Čtverec":
    number = st.number_input("Zadejte délku strany čtverce", key="klic1")
    st.text(f"Obsah čtverce je {number**2} cm\u00b2 a jeho obvod je {number*4} cm.")
elif volba == "Obdelník":
    number_a = st.number_input("Zadejte délky strany a obdelníku", key="klic2")
    number_b = st.number_input("Zadejte délky strany a obdelníku", key="klic3")
    st.text(f"Obsah obdelníku je {number_a*number_b} cm\u00b2 a jeho obvod je {2*(number_a+number_b)} cm.")
else: 
    number_hrana_a = st.number_input("Zadejte délku hrany krychle", key="klic4")
    st.text(f"Objem krychle je {number_hrana_a**3} cm\u00b3, plocha je {number_hrana_a*number_hrana_a*6} cm\u00b2 a delka všech hran je {number_hrana_a*12} cm")
