import streamlit as st
import pandas as pd
import plotly.express as px

from database import criar_tabela, inserir_dado, carregar_dados
from pdf_report import gerar_pdf

criar_tabela()

st.set_page_config(layout="wide")
st.title("🚀 QA Automated Testing Metrics")

# ================= FORM =================

with st.form("cadastro", clear_on_submit=True):

    c1, c2 = st.columns(2)
    squad = c1.text_input("Squad")
    produto = c2.text_input("Produto")

    c3, c4 = st.columns(2)
    necessarios = c3.number_input("Testes necessários", min_value=0)
    automatizados = c4.number_input("Automatizados", min_value=0)

    if st.form_submit_button("Cadastrar"):
        inserir_dado(squad, produto, necessarios, automatizados)
        st.success("Cadastro realizado!")

# ================= DATE =================

df = carregar_dados()

if not df.empty:

    df["cobertura"] = (
        df["testes_automatizados"] /
        df["testes_necessarios"].replace(0, 1)
    ) * 100

    # ================= FILTER =================
    squads = st.multiselect(
        "Filtrar squads",
        options=df["squad"].unique(),
        default=df["squad"].unique()
    )

    df = df[df["squad"].isin(squads)]

    # ================= SUMMARY =================
    resumo = (
        df.groupby("squad")
        .agg({
            "produto": "count",
            "testes_necessarios": "sum",
            "testes_automatizados": "sum"
        })
        .reset_index()
    )

    resumo["cobertura"] = (
        resumo["testes_automatizados"] /
        resumo["testes_necessarios"].replace(0, 1)
    ) * 100

    resumo["gap"] = (
        resumo["testes_necessarios"]
        - resumo["testes_automatizados"]
    )

    # ================= KPIs =================

    kpis = {
        "total_squads": df["squad"].nunique(),
        "total_produtos": len(df),
        "cobertura": resumo["cobertura"].mean(),
        "gap_total": int(resumo["gap"].sum())
    }

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Squads", kpis["total_squads"])
    k2.metric("Produtos", kpis["total_produtos"])
    k3.metric("Cobertura Média", f'{kpis["cobertura"]:.1f}%')
    k4.metric("Automation Gap", kpis["gap_total"])

    st.divider()

    # ================= HEALTH SCORE =================

    def health(c):
        if c >= 80:
            return "🟢 Saudável"
        elif c >= 50:
            return "🟡 Atenção"
        return "🔴 Risco"

    resumo["health"] = resumo["cobertura"].apply(health)
    resumo["cobertura"] = resumo["cobertura"].round(2)

    st.subheader("Health Score")
    st.dataframe(resumo[["squad", "cobertura", "health"]])

    # ================= GRAPHICS =================

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(resumo, x="squad", y="cobertura",
                     color="cobertura",
                     title="Cobertura por Squad")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        trend = df.groupby("data_registro")["cobertura"].mean().reset_index()

        fig2 = px.line(trend,
                       x="data_registro",
                       y="cobertura",
                       title="Evolução da Cobertura")
        st.plotly_chart(fig2, use_container_width=True)

    # ================= PDF =================

    if st.button("📄 Gerar Relatório Métricas"):
        file_path = gerar_pdf(resumo, kpis)

        with open(file_path, "rb") as f:
            st.download_button(
                "⬇️ Baixar PDF",
                f,
                "QA_Metrics_Report.pdf"
            )