import streamlit as st

from config.settings import settings
from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page


st.set_page_config(
    page_title="GitHub Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


pages = {
    "Dashboard": dashboard_page,
    "Repository": repository_page,
    "Contributors": contributors_page,
    "Code Insights": code_insights_page,
}


selected_page = st.sidebar.radio("Navigation", list(pages.keys()))

if settings.app_title:
    st.title(settings.app_title)

pages[selected_page]()
