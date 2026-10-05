import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Evasão Escolar Brasil", layout="wide", page_icon="🏫")

# Identificação Acadêmica
st.title("🏫 Análise de Evasão Escolar no Ensino Médio Brasileiro (2015-2024)")
st.markdown("""
- **Aluno:** Miguel Soares Marreiros  
- **Curso:** Sistemas de Informação — Centro Universitário La Salle (Unilasalle-RJ)  
- **Professor:** Alexandre Neves Louzada  
- **Disciplina:** Linguagem de Programação — Análise e Visualização de Dados com Python  
""")
st.markdown("---")

# Função para carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados/simulacao_evasao_escolar_brasil.csv")
    return df

df = carregar_dados()

# ==================== BARRA LATERAL: FILTROS ====================
st.sidebar.header("Filtros Dinâmicos")

ano_min, ano_max = int(df['ano'].min()), int(df['ano'].max())
ano_selecionado = st.sidebar.slider("Ano", ano_min, ano_max, (ano_min, ano_max))

regioes = df['regiao'].unique().tolist()
regiao_selecionada = st.sidebar.multiselect("Região", regioes, default=regioes)

estados = df[df['regiao'].isin(regiao_selecionada)]['uf'].unique().tolist()
estado_selecionado = st.sidebar.multiselect("Estado", estados, default=estados)

redes = df['rede_ensino'].unique().tolist()
rede_selecionada = st.sidebar.multiselect("Rede de Ensino", redes, default=redes)

series = df['serie'].unique().tolist()
serie_selecionada = st.sidebar.multiselect("Série do Ensino Médio", series, default=series)

riscos = df['nivel_risco'].unique().tolist()
risco_selecionado = st.sidebar.multiselect("Nível de Risco", riscos, default=riscos)

# Aplicar Filtros
df_filtrado = df[
    (df['ano'] >= ano_selecionado[0]) & (df['ano'] <= ano_selecionado[1]) &
    (df['regiao'].isin(regiao_selecionada)) &
    (df['uf'].isin(estado_selecionado)) &
    (df['rede_ensino'].isin(rede_selecionada)) &
    (df['serie'].isin(serie_selecionada)) &
    (df['nivel_risco'].isin(risco_selecionado))
]

# ==================== KPIs OBRIGATÓRIOS ====================
col1, col2, col3, col4, col5 = st.columns(5)

taxa_media = df_filtrado['taxa_evasao'].mean()
total_evasoes = df_filtrado['evasoes'].sum()

estado_critico = df_filtrado.groupby('uf')['taxa_evasao'].mean().idxmax() if not df_filtrado.empty else "N/A"
rede_critica = df_filtrado.groupby('rede_ensino')['taxa_evasao'].mean().idxmax() if not df_filtrado.empty else "N/A"
serie_critica = df_filtrado.groupby('serie')['taxa_evasao'].mean().idxmax() if not df_filtrado.empty else "N/A"

col1.metric("Taxa Média de Evasão", f"{taxa_media:.2f}%")
col2.metric("Total de Evasões", f"{total_evasoes:,.0f}".replace(',', '.'))
col3.metric("Estado + Crítico", estado_critico)
col4.metric("Rede + Afetada", rede_critica)
col5.metric("Série + Crítica", serie_critica)

st.markdown("---")

# ==================== GRÁFICOS (ABAS) ====================
aba1, aba2, aba3, aba4 = st.tabs(["Evolução e Regional", "Escolaridade e Risco", "Correlações", "Tabela de Dados"])

with aba1:
    st.subheader("Evolução Temporal da Evasão")
    df_tempo = df_filtrado.groupby('ano')['taxa_evasao'].mean().reset_index()
    fig_linha = px.line(df_tempo, x='ano', y='taxa_evasao', markers=True, title="Taxa Média de Evasão por Ano")
    st.plotly_chart(fig_linha, use_container_width=True)

    st.subheader("Comparação Regional (Por Estado)")
    df_estado = df_filtrado.groupby('uf')['taxa_evasao'].mean().reset_index().sort_values('taxa_evasao', ascending=False)
    fig_bar_est = px.bar(df_estado, x='uf', y='taxa_evasao', color='taxa_evasao', color_continuous_scale='Reds', title="Evasão por Estado")
    st.plotly_chart(fig_bar_est, use_container_width=True)

with aba2:
    st.subheader("Evasão por Série do Ensino Médio")
    df_serie = df_filtrado.groupby('serie')['taxa_evasao'].mean().reset_index()
    fig_serie = px.bar(df_serie, x='serie', y='taxa_evasao', color='serie', title="Taxa de Abandono por Série")
    st.plotly_chart(fig_serie, use_container_width=True)

    st.subheader("Evasão por Nível de Risco e Rede de Ensino")
    fig_rede = px.box(df_filtrado, x='rede_ensino', y='taxa_evasao', color='nivel_risco', title="Distribuição de Evasão")
    st.plotly_chart(fig_rede, use_container_width=True)

with aba3:
    st.subheader("Relação: Renda Familiar x Taxa de Evasão")
    fig_scatter = px.scatter(df_filtrado, x='renda_media_familiar', y='taxa_evasao', color='regiao', opacity=0.7, 
                             title="Impacto da Renda na Evasão (Dispersão)", trendline="ols")
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("**Interpretação Textual:** Gráficos de dispersão mostram que, em geral, regiões com menor renda familiar média apresentam taxas de evasão mais acentuadas, o que evidencia o fator socioeconômico como um dos principais motores do abandono escolar.")

with aba4:
    st.subheader("Exploração Detalhada (Tabela Dinâmica)")
    st.dataframe(df_filtrado)

# Conclusão Executiva
st.markdown("---")
st.markdown("### Conclusão Executiva")
st.markdown("""
A análise dos dados revela que a evasão no Ensino Médio está fortemente atrelada a indicadores socioeconômicos.
A rede pública e o primeiro ano do Ensino Médio costumam apresentar as taxas mais críticas de abandono. Políticas públicas
focadas em complementação de renda, melhoria da infraestrutura e suporte ao aluno logo no ingresso do ensino médio 
podem mitigar drasticamente estes números.
""")
