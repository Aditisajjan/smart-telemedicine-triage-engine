import streamlit as st

def calc_bmi(w, h):
    if h <= 0 or w <= 0:
        return None, "—"
    bmi = round(w/(h/100)**2, 1)
    cat = "Underweight" if bmi < 18.5 else ("Normal" if bmi < 25 else ("Overweight" if bmi < 30 else "Obese"))
    return bmi, cat

def set_bg(color):
    st.markdown(f"<style>.stApp{{background-color:{color}!important;}}</style>", unsafe_allow_html=True)