import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="World Happiness Dashboard", layout="wide")

# --- Carregar os dados ---
@st.cache_data
def load_data():
    url = (
        "https://happiness-report.s3.us-east-1.amazonaws.com/"
        "2025/Data+for+Figure+2.1+(2011%E2%80%932024).xlsx"
    )
    df = pd.read_excel(url)

    # Renomear colunas
    df = df.rename(columns={
        'Country name': 'Country',
        'Ladder score': 'Ladder_score',
        'Logged GDP per capita': 'GDP',
        'Social support': 'Social_support',
        'Healthy life expectancy': 'Health',
        'Freedom to make life choices': 'Freedom',
        'Generosity': 'Generosity',
        'Perceptions of corruption': 'Corruption',
        'Dystopia + residual': 'Dystopia_residual',
        'Year': 'Year'
    })

    return df

# --- Carregar dados ---
df = load_data()

# --- Sidebar ---
st.sidebar.t