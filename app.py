"""AirlinePulse Streamlit entry point. Run with: streamlit run app.py"""
import streamlit as st
from app.model import train_notebook_model
from app.ui import apply_theme, render_evaluator, render_feedback

apply_theme()

@st.cache_resource(show_spinner="Preparing the notebook classifier and evaluation…")
def get_project_resources():
    return train_notebook_model()

model,data,bounds,numeric,categorical,artifacts=get_project_resources()
page=st.sidebar.radio("Explore AirlinePulse",["Share feedback","Project evaluation"])
st.sidebar.markdown("---")
st.sidebar.caption("23CSE301 · Machine Learning capstone")
if page=="Share feedback":
    render_feedback(data,model,bounds,numeric,categorical)
else:
    render_evaluator(artifacts)
