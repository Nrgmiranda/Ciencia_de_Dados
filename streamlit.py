# streamlit.py

import sys
import os

# Impedir import circular
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if module_path not in sys.path:
    sys.path.insert(0, module_path)

# Renomear import para evitar conflito
import streamlit as stlib
import pandas as pd
import altair as alt
import plotly.express as px

@stlib.cache_data
def load_data():
    url = (
        "https://happiness-report.s3.us-east-1.amazonaws.com/"
        "2025/Data+for+Figure+2.1+(2011%E2%80%932024).xlsx"
    )
    df = pd.read_excel(url)

    df = df.rename(columns={
        'Country name': 'Country',
        'Ladder score': 'Ladder_score',
        'Explained by: Log GDP per capita': 'GDP',
        'Explained by: Social support': 'Social_support',
        'Explained by: Healthy life expectancy': 'Health',
        'Explained by: Freedom to make life choices': 'Freedom',
        'Explained by: Generosity': 'Generosity',
        'Explained by: Perceptions of corruption': 'Corruption',
        'Dystopia + residual': 'Dystopia_residual'
    })

    return df

df = load_data()

stlib.set_page_config(layout="wide")

stlib.title("📊 World Happiness Dashboard 2011–2024")
stlib.markdown("Visualização interativa do World Happiness Report com base na Ladder Score e fatores explicativos.")

anos = stlib.sidebar.multiselect(
    "Selecione ano(s):",
    sorted(df['Year'].unique()),
    default=[2023, 2024]
)

paises = stlib.sidebar.multiselect(
    "Selecione país(es):",
    sorted(df['Country'].unique()),
    default=["Brazil", "Sweden", "United States"]
)

df_filtro = df[
    (df['Year'].isin(anos)) &
    (df['Country'].isin(paises))
]

stlib.sidebar.metric("Total de países", df_filtro['Country'].nunique())
stlib.sidebar.metric("Período", f"{min(anos)}–{max(anos)}")

stlib.subheader("📈 Evolução da Ladder Score por país")
line = (
    alt.Chart(df_filtro)
    .mark_line(point=True)
    .encode(
        x="Year:O",
        y="Ladder_score:Q",
        color="Country:N",
        tooltip=["Country", "Year", "Ladder_score"]
    )
    .interactive()
)
stlib.altair_chart(line, use_container_width=True)

if anos:
    ano_ult = max(anos)
    df_ano = df[df["Year"] == ano_ult]
    top10 = df_ano.nlargest(10, "Ladder_score")
    stlib.subheader(f"🏆 Top 10 países em {ano_ult}")
    fig = px.bar(
        top10,
        x="Ladder_score",
        y="Country",
        orientation="h",
        color="Ladder_score",
        labels={"Ladder_score": "Ladder Score", "Country": "País"},
        color_continuous_scale="viridis"
    )
    stlib.plotly_chart(fig, use_container_width=True)

stlib.subheader("🔎 Tendência de fatores explicativos")
fatores = ["GDP", "Social_support", "Health", "Freedom", "Generosity", "Corruption", "Dystopia_residual"]
fator_sel = stlib.selectbox("Selecione o fator:", fatores)

df_fatores = df_filtro[["Year", "Country", fator_sel]]

graf_fator = (
    alt.Chart(df_fatores)
    .mark_line(point=True)
    .encode(
        x="Year:O",
        y=alt.Y(fator_sel, title=fator_sel.replace("_", " ")),
        color="Country:N",
        tooltip=["Country", "Year", fator_sel]
    )
    .interactive()
)
stlib.altair_chart(graf_fator, use_container_width=True)

with stlib.expander(
