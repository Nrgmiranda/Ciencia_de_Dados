# app_streamlit.py

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

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

# --- Cabeçalho ---
st.markdown("<h1 style='text-align: center;'>📊 World Happiness Dashboard 2011–2024</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Visualização interativa do World Happiness Report com base na Ladder Score e fatores explicativos.</p>", unsafe_allow_html=True)

# --- Filtros laterais ---
st.sidebar.header("🎛️ Filtros")

anos = st.sidebar.multiselect(
    "Selecione ano(s):",
    sorted(df['Year'].unique()),
    default=[2023, 2024]
)

paises = st.sidebar.multiselect(
    "Selecione país(es):",
    sorted(df['Country'].unique()),
    default=["Brazil", "Sweden", "United States"]
)

df_filtro = df[
    (df['Year'].isin(anos)) &
    (df['Country'].isin(paises))
]

# --- Métricas ---
st.sidebar.metric("Total de países", df_filtro['Country'].nunique())
st.sidebar.metric("Período", f"{min(anos)}–{max(anos)}")

# --- Gráfico: Evolução Ladder Score ---
st.markdown("## 📈 Evolução da Ladder Score por país")

line_chart = (
    alt.Chart(df_filtro)
    .mark_line(point=alt.OverlayMarkDef(color='black'))
    .encode(
        x=alt.X("Year:O", title="Ano"),
        y=alt.Y("Ladder_score:Q", title="Ladder Score"),
        color=alt.Color("Country:N", legend=alt.Legend(title="País")),
        tooltip=["Country", "Year", "Ladder_score"]
    )
    .properties(height=400)
    .interactive()
)
st.altair_chart(line_chart, use_container_width=True)

# --- Gráfico: Top 10 países por Ladder Score ---
if anos:
    ano_ult = max(anos)
    df_ano = df[df["Year"] == ano_ult]
    top10 = df_ano.nlargest(10, "Ladder_score")

    st.markdown(f"## 🏆 Top 10 países em {ano_ult}")
    fig_top10 = px.bar(
        top10.sort_values("Ladder_score"),
        x="Ladder_score",
        y="Country",
        orientation="h",
        color="Ladder_score",
        labels={"Ladder_score": "Ladder Score", "Country": "País"},
        color_continuous_scale="viridis",
        height=500
    )
    fig_top10.update_layout(yaxis_title=None)
    st.plotly_chart(fig_top10, use_container_width=True)

# --- Gráfico: Fatores explicativos ---
st.markdown("## 🔎 Tendência de fatores explicativos")

fatores = ["GDP", "Social_support", "Health", "Freedom", "Generosity", "Corruption", "Dystopia_residual"]
fator_sel = st.selectbox("Selecione o fator:", fatores, index=0)

df_fatores = df_filtro[["Year", "Country", fator_sel]]

graf_fator = (
    alt.Chart(df_fatores)
    .mark_line(point=True)
    .encode(
        x=alt.X("Year:O", title="Ano"),
        y=alt.Y(fator_sel, title=fator_sel.replace("_", " ")),
        color="Country:N",
        tooltip=["Country", "Year", fator_sel]
    )
    .properties(height=400)
    .interactive()
)
st.altair_chart(graf_fator, use_container_width=True)

# --- Tabela de dados brutos ---
with st.expander("📄 Visualizar dados brutos"):
    st.dataframe(df_filtro.reset_index(drop=True))
