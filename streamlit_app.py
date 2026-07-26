"""Entry point / router for the PA admissions toolkit (multi-page Streamlit app)."""

import streamlit as st

st.set_page_config(page_title="PA Admissions Toolkit", page_icon="🩺", layout="centered")

file_score_page = st.Page(
    "pages_file_score.py",
    title="ISU File Score Estimator",
    icon="🩺",
    default=True,
)
program_explorer_page = st.Page(
    "pages_program_explorer.py",
    title="PA Program Explorer",
    icon="🎓",
)

nav = st.navigation([file_score_page, program_explorer_page])
nav.run()
