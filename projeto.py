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

    # Renomear colunas para facilitar o uso
    df = df.rename(columns={
        'Country name': 'Country',
        'year': 'Year',
        'Ladder score': 'Ladder_score',
        'Logged GDP per capita': 'GDP',
        'Social support': 'Social_support',
        'Healthy life expectancy': 'Health',
        'Freedom to make life choices': 'Freedom',
        'Generosity': 'Generosity',
        'Perceptions of corruption': 'Corruption',
        'Dystopia + residual': 'Dystopia_residual',
        'Regional indicator': 'Region'
    })

    return df

# --- Visualização ---
df = load_data()

st.title("🌍 World Happiness Report (2011–2024)")
st.markdown("Visualização interativa do índice de felicidade global")

# Filtro de país
countries = st.multiselect("Selecione os países:", df["Country"].unique(), default=["Brazil", "Norway", "Finland"])

# Filtrar os dados
df_filtered = df[df["Country"].isin(countries)]

# --- Gráfico: Evolução da felicidade ---
st.subheader("📈 Evolução da Ladder Score ao longo dos anos")
fig = px.line(df_filtered, x="Year", y="Ladder_score", color="Country", markers=True)
st.plotly_chart(fig, use_container_width=True)

# --- Gráfico: Indicadores de Contribuição (Altair) ---
st.subheader("📊 Indicadores por País e Ano")
year = st.slider("Selecione o ano", int(df["Year"].min()), int(df["Year"].max()), 2024)
df_year = df[df["Year"] == year]
df_year = df_year[df_year["Country"].isin(countries)]

indicators = ["GDP", "Social_support", "Health", "Freedom", "Generosity", "Corruption"]

chart = alt.Chart(df_year).transform_fold(
    indicators,
    as_=['Indicator', 'Value']
).mark_bar().encode(
    x=alt.X('Indicator:N', title='Indicador'),
    y=alt.Y('Value:Q', title='Valor'),
    color='Country:N',
    column='Country:N'
).properties(height=400).interactive()

st.altair_chart(chart, use_container_width=True)
