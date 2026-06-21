import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="🏐 Previsão VNL 2026",
    page_icon="🏐",
    layout="wide"
)

# Título
st.title("🏐 Previsão VNL 2026 - Dashboard Interativo")
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# =============================================================================
# CARREGAR DADOS
# =============================================================================

# Tenta carregar o arquivo CSV gerado pelo pipeline
try:
    df_previsao = pd.read_csv('previsao_vnl_2026.csv')
except:
    # Se não existir, usa dados de exemplo (para teste)
    dados_exemplo = {
        'time': ['Brasil', 'Itália', 'Polônia', 'Japão', 'EUA', 'Turquia', 'China', 'Sérvia'],
        'rating': [100.0, 94.1, 92.3, 89.9, 87.6, 87.5, 85.6, 78.4],
        'rating_2024': [100.0, 94.1, 92.3, 89.9, 87.6, 87.5, 85.6, 78.4],
        'rating_2025': [100.0, 94.1, 92.3, 89.9, 87.6, 87.5, 85.6, 78.4],
        'rating_2026': [100.0, 94.1, 92.3, 89.9, 87.6, 87.5, 85.6, 78.4]
    }
    df_previsao = pd.DataFrame(dados_exemplo)

# =============================================================================
# SIDEBAR - FILTROS
# =============================================================================

st.sidebar.header("⚙️ Filtros")

# Selecionar times
times_disponiveis = df_previsao['time'].tolist()
times_selecionados = st.sidebar.multiselect(
    "Selecione os times",
    times_disponiveis,
    default=times_disponiveis[:8]
)

# =============================================================================
# LAYOUT PRINCIPAL - COLUNAS
# =============================================================================

col1, col2 = st.columns([2, 1])

# =============================================================================
# GRÁFICO 1: Probabilidades de Título
# =============================================================================

with col1:
    st.subheader("📊 Probabilidades de Título")
    
    df_filtrado = df_previsao[df_previsao['time'].isin(times_selecionados)]
    df_filtrado = df_filtrado.sort_values('rating', ascending=False)
    
    fig1 = px.bar(
        df_filtrado,
        x='time',
        y='rating',
        color='time',
        text='rating',
        title='Rating por Time (0-100)',
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={'rating': 'Rating', 'time': 'Seleção'}
    )
    fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

# =============================================================================
# GRÁFICO 2: Evolução do Rating (2024 → 2025 → 2026)
# =============================================================================

with col2:
    st.subheader("📈 Evolução do Rating")
    
    # Prepara dados para o gráfico de linhas
    df_evolucao = df_filtrado.melt(
        id_vars=['time'],
        value_vars=['rating_2024', 'rating_2025', 'rating_2026'],
        var_name='Ano',
        value_name='Rating'
    )
    df_evolucao['Ano'] = df_evolucao['Ano'].str.replace('rating_', '')
    
    fig2 = px.line(
        df_evolucao,
        x='Ano',
        y='Rating',
        color='time',
        markers=True,
        title='Evolução do Rating por Time',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# =============================================================================
# GRÁFICO 3: Radar (Perfil Técnico - se tiver dados de fundamentos)
# =============================================================================

st.subheader("🔄 Perfil Técnico Comparativo")

# Cria dados fictícios de fundamentos para demonstração
# Na prática, você carregaria do arquivo CSV com colunas: ataque, bloqueio, saque
if 'ataque' in df_previsao.columns:
    df_radar = df_previsao[df_previsao['time'].isin(times_selecionados[:4])]
    categorias = ['Ataque', 'Bloqueio', 'Saque']
    
    fig3 = go.Figure()
    for i, time in enumerate(df_radar['time'].head(4)):
        fig3.add_trace(go.Scatterpolar(
            r=[
                df_radar[df_radar['time'] == time]['ataque'].values[0],
                df_radar[df_radar['time'] == time]['bloqueio'].values[0],
                df_radar[df_radar['time'] == time]['saque'].values[0]
            ],
            theta=categorias,
            fill='toself',
            name=time
        ))
    fig3.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 50])),
        showlegend=True,
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("ℹ️ Dados de fundamentos (ataque, bloqueio, saque) não disponíveis no CSV atual. Para ativar, inclua essas colunas no arquivo de dados.")

# =============================================================================
# TABELA DE DADOS
# =============================================================================

with st.expander("📋 Ver tabela completa de dados"):
    st.dataframe(df_previsao.style.format({
        'rating': '{:.1f}',
        'rating_2024': '{:.1f}',
        'rating_2025': '{:.1f}',
        'rating_2026': '{:.1f}'
    }))

# =============================================================================
# RODAPÉ
# =============================================================================

st.divider()
st.caption("📊 Dados atualizados automaticamente via Prefect Cloud | Fonte: Volleyball World")
