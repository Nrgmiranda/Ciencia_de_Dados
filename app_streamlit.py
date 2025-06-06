# arquivo: app_streamlit.py

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# 1. Carregar dados diretamente do link
@st.cache_data
def load_data():
    url = (
        "https://happiness-report.s3.us-east-1.amazonaws.com/"
        "2025/Data+for+Figure+2.1+(2011%E2%80%932024).xlsx"
    )
    df = pd.read_excel(url)
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
    df = df.rename(columns={'country_name': 'country', 'year': 'year'})
    return df

df = load_data()

st.title("🌍 Dashboard de Felicidade Mundial 2011–2024")
st.markdown(
    "Exploração interativa dos níveis de felicidade (Cantril Ladder)"
)

# 2. Filtros laterais
anos = st.sidebar.multiselect(
    "Selecione ano(s):",
    sorted(df['year'].unique()),
    default=[2023, 2024]
)
paises = st.sidebar.multiselect(
    "Selecione país(es):",
    sorted(df['country'].unique()),
    default=["Brazil", "United States", "Sweden"]
)

df_filtro = df[
    (df['year'].isin(anos)) &
    (df['country'].isin(paises))
]

# 3. Métricas gerais
st.sidebar.markdown("### Métricas Globais")
st.sidebar.metric("Total de países", df_filtro['country'].nunique())
st.sidebar.metric("Períodos analisados", f"{min(anos)}–{max(anos)}")

# 4. Gráfico de linhas interativo por país
st.subheader("Evolução da Felicidade por País")
line = (
    alt.Chart(df_filtro)
    .mark_line(point=True)
    .encode(
        x="year:O",
        y="life_evaluation:Q",
        color="country:N",
        tooltip=["country", "year", "life_evaluation"]
    )
    .interactive()
)
st.altair_chart(line, use_container_width=True)

# 5. Ranking por ano selecionado
if anos:
    ano_corrente = max(anos)
    df_ano = df[df['year'] == ano_corrente]
    top10 = df_ano.nlargest(10, 'life_evaluation')
    st.subheader(f"Top 10 países em {ano_corrente}")
    fig = px.bar(
        top10,
        x='life_evaluation',
        y='country',
        orientation='h',
        color='life_evaluation',
        color_continuous_scale='viridis',
        labels={'life_evaluation':'Cantril Ladder', 'country':'País'}
    )
    st.plotly_chart(fig, use_container_width=True)

# 6. Análise de tendências por fatores
st.subheader("Contribuição dos Fatores (ex: PIB, suporte social, saúde...)")
fatores = [
    'log_gdp_per_capita', 'social_support',
    'healthy_life_expectancy', 'freedom',
    'generosity', 'perceptions_of_corruption'
]
df_fatores = df_filtro.melt(
    id_vars=['country', 'year', 'life_evaluation'],
    value_vars=fatores,
    var_name='fator',
    value_name='valor'
)
filtro_fator = st.selectbox("Selecione o fator:", fatores, index=0)
df_fat_filtrado = df_fatores[df_fatores['fator'] == filtro_fator]

fat_line = (
    alt.Chart(df_fat_filtrado)
    .mark_line(point=True)
    .encode(
        x='year:O',
        y='valor:Q',
        color='country:N',
        tooltip=['country', 'year', 'valor']
    )
    .interactive()
)
st.altair_chart(fat_line, use_container_width=True)

# 7. Dados brutos (expandir)
with st.expander("📋 Mostrar tabela completa"):
    st.dataframe(df_filtro.reset_index(drop=True))
