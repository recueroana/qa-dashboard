import streamlit as st
import pandas as pd
import plotly.express as px
import os

from database import (
    criar_tabelas,
    inserir_produto,
    inserir_modulo,
    listar_produtos,
    listar_modulos
)

criar_tabelas()

st.set_page_config(page_title="QA Engineering Dashboard", layout="wide")

st.title("QA Automation Engineering Dashboard")

# ----------------------------
# Product Registration
# ----------------------------

st.sidebar.header("Cadastro Produto")

# product form cleaning
if "clear_product" not in st.session_state:
    st.session_state.clear_product = False
if st.session_state.clear_product:
    st.session_state.squad = ""
    st.session_state.produto = ""
    st.session_state.modulos_necessitam = 0
    st.session_state.clear_product = False

# use session_state keys so we can clear after submission
squad = st.sidebar.text_input("Squad", key="squad")
produto = st.sidebar.text_input("Produto", key="produto")
modulos_necessitam = st.sidebar.number_input(
    "Qtde de módulos que necessitam automação",
    min_value=0,
    key="modulos_necessitam"
)

if st.sidebar.button("Cadastrar Produto"):
    inserir_produto(squad, produto, modulos_necessitam)
    st.sidebar.success("Produto cadastrado!")
    st.session_state.clear_product = True

# show the value after inserting

# ----------------------------
# Module Registration
# ----------------------------

st.sidebar.header("Cadastro Módulo")

produtos = listar_produtos()

if not produtos.empty:

    # module form cleanup
    if "clear_module" not in st.session_state:
        st.session_state.clear_module = False
    if st.session_state.clear_module:
        st.session_state.produto_select = ""
        st.session_state.modulo = ""
        st.session_state.testes_necessarios = 0
        st.session_state.testes_automatizados = 0
        st.session_state.clear_module = False

    produto_select = st.sidebar.selectbox(
        "Produto",
        produtos["produto"],
        key="produto_select"
    )

    produto_id = int(produtos[produtos["produto"] == produto_select]["id"].values[0])

    modulo = st.sidebar.text_input("Nome do módulo", key="modulo")

    # coerce any bad session state to integer ('' or None -> 0)
    if "testes_necessarios" in st.session_state:
        try:
            st.session_state.testes_necessarios = int(st.session_state.testes_necessarios or 0)
        except Exception:
            st.session_state.testes_necessarios = 0
    if "testes_automatizados" in st.session_state:
        try:
            st.session_state.testes_automatizados = int(st.session_state.testes_automatizados or 0)
        except Exception:
            st.session_state.testes_automatizados = 0

    testes_necessarios = st.sidebar.number_input(
        "Testes necessários",
        min_value=0,
        key="testes_necessarios"
    )

    testes_automatizados = st.sidebar.number_input(
        "Testes automatizados",
        min_value=0,
        key="testes_automatizados"
    )

    if st.sidebar.button("Cadastrar módulo"):

        inserir_modulo(
            produto_id,
            modulo,
            testes_necessarios,
            testes_automatizados
        )

        st.sidebar.success("Módulo cadastrado!")
        st.session_state.clear_module = True

# ----------------------------
# Data
# ----------------------------

produtos = listar_produtos()
# ensure new column exists and is numeric for legacy rows
if "modulos_necessitam_automacao" not in produtos.columns:
    produtos["modulos_necessitam_automacao"] = 0
else:
    produtos["modulos_necessitam_automacao"] = produtos["modulos_necessitam_automacao"].fillna(0).astype(int)

modulos = listar_modulos()

# ensure the id columns used for merging are numeric with matching types
# SQLite can sometimes return them as objects if there were nulls or mixed types
modulos["produto_id"] = pd.to_numeric(modulos["produto_id"], errors="coerce").astype("Int64")
produtos["id"] = pd.to_numeric(produtos["id"], errors="coerce").astype("Int64")


modulos = modulos.dropna(subset=["produto_id"])
produtos = produtos.dropna(subset=["id"])


df = modulos.merge(
    produtos,
    left_on="produto_id",
    right_on="id"
)

# ----------------------------
# Health Score módulo
# ----------------------------

df["health_modulo"] = df.apply(
    lambda row: (row["testes_automatizados"] / row["testes_necessarios"] * 100)
    if row["testes_necessarios"] > 0 else 0,
    axis=1
)

# ----------------------------
# Health Score produto
# ----------------------------

health_produto = (
    df.groupby(["produto", "squad"])
    .agg({
        "testes_necessarios": "sum",
        "testes_automatizados": "sum",
        "modulo": "count"  # count modules per product
    })
    .reset_index()
)
health_produto = health_produto.rename(columns={"modulo": "modulos_cadastrados"})

health_produto = health_produto.merge(
    produtos[["produto", "modulos_necessitam_automacao"]].drop_duplicates(),
    on="produto",
    how="left"
)
health_produto["modulos_necessitam_automacao"] = health_produto["modulos_necessitam_automacao"].fillna(0).astype(int)

# calculate module coverage (what % of modules have been registered)
health_produto["cobertura_modulos"] = health_produto.apply(
    lambda r: (r["modulos_cadastrados"] / r["modulos_necessitam_automacao"] * 100)
    if r["modulos_necessitam_automacao"] > 0 else 0,
    axis=1
)

# calculate test coverage (what % of required tests have been automated)
health_produto["cobertura_testes"] = health_produto.apply(
    lambda r: (r["testes_automatizados"] / r["testes_necessarios"] * 100)
    if r["testes_necessarios"] > 0 else 0,
    axis=1
)

module_health_sum = (
    df.groupby("produto")["health_modulo"].sum()
)

health_produto["health_produto_eng"] = health_produto.apply(
    lambda r: (module_health_sum.get(r["produto"], 0) / r["modulos_necessitam_automacao"])
    if r["modulos_necessitam_automacao"] > 0 else 0,
    axis=1
)

health_produto["health_produto"] = (
    (health_produto["cobertura_modulos"] + health_produto["cobertura_testes"]) / 2
).round(1)

# ----------------------------
# Health Score Squad
# ----------------------------

health_squad = (
    health_produto.groupby("squad")
    .agg({
        "testes_necessarios": "sum",
        "testes_automatizados": "sum"
    })
    .reset_index()
)

health_squad["health_squad"] = health_squad.apply(
    lambda row: (row["testes_automatizados"] / row["testes_necessarios"] * 100)
    if row["testes_necessarios"] > 0 else 0,
    axis=1
)

# ----------------------------
#Coverage by Squad and Product
# ----------------------------

coverage_df = (
    df.groupby(["produto", "squad"])
    .agg(
        modulos_cadastrados=("modulo", "count"),
        testes_necessarios=("testes_necessarios", "sum"),
        testes_automatizados=("testes_automatizados", "sum"),
    )
    .reset_index()
)

coverage_df = coverage_df.merge(
    produtos[["produto", "modulos_necessitam_automacao"]].drop_duplicates(),
    on="produto",
    how="left"
)
coverage_df["modulos_necessitam_automacao"] = coverage_df["modulos_necessitam_automacao"].fillna(0).astype(int)

# calculate coverage percentages
coverage_df["cobertura_modulos"] = coverage_df.apply(
    lambda r: (r["modulos_cadastrados"] / r["modulos_necessitam_automacao"] * 100)
    if r["modulos_necessitam_automacao"] > 0 else 0,
    axis=1
).round(2)
coverage_df["cobertura_testes"] = coverage_df.apply(
    lambda r: (r["testes_automatizados"] / r["testes_necessarios"] * 100)
    if r["testes_necessarios"] > 0 else 0,
    axis=1
).round(2)

# ----------------------------
# KPIs
# ----------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Produtos",
    len(produtos)
)

col2.metric(
    "Total Módulos",
    len(modulos)
)

coverage = (
    round(health_produto['health_produto_eng'].mean(), 2)
    if not health_produto.empty else 0
)
col3.metric(
    "Cobertura Engenharia",
    f"{coverage:.2f}%"
)

# ----------------------------
# Health Product Chart
# ----------------------------

# PDF report generation
from pdf_report import gerar_pdf

# button to create PDF
if st.sidebar.button("Gerar relatório PDF"):
    # Prepare a summary and KPIs
    resumo = (
        health_produto.groupby("squad")["health_produto_eng"].mean().reset_index()
        .rename(columns={"health_produto_eng": "cobertura"})
    )
    kpis = {
        "total_squads": len(health_squad),
        "total_produtos": len(health_produto),
        "cobertura": health_produto["health_produto_eng"].mean() if not health_produto.empty else 0,
        "gap_total": 100 - (health_produto["health_produto_eng"].mean() if not health_produto.empty else 0)
    }
    pdf_path = gerar_pdf(resumo, kpis)
    st.sidebar.success(f"PDF gerado: {pdf_path}")
    # provide download link
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    st.sidebar.download_button(
        label="Baixar relatório PDF",
        data=pdf_bytes,
        file_name=os.path.basename(pdf_path),
        mime="application/pdf"
    )

# ----------------------------
# Health Product Chart
# ----------------------------

st.subheader("Health Score por Produto (Engenharia)")

fig1 = px.bar(
    health_produto,
    x="produto",
    y="health_produto_eng",  
    color="squad",
    text_auto=True
)
fig1.update_traces(texttemplate="%{y:.2f}%")

st.plotly_chart(fig1, use_container_width=True)

# ----------------------------
# Health Squad Chart
# ----------------------------

st.subheader("Health Score por Squad")

fig2 = px.bar(
    health_squad,
    x="squad",
    y="health_squad",
    text_auto=True
)

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# Health by Module
# ----------------------------

st.subheader("Health Score por Módulo")

fig3 = px.bar(
    df,
    x="modulo",
    y="health_modulo",
    color="produto",
    text_auto=True
)

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# Coverage by Squad and Product
# ----------------------------

st.subheader("Cobertura completa por Squad e Produto")

if coverage_df.empty:
    st.info("Nenhum dado disponível. Cadastre produtos e módulos para ver a cobertura.")
else:
    # show percentage metrics in table
    st.dataframe(
        coverage_df[[
            "squad",
            "produto",
            "modulos_necessitam_automacao",
            "modulos_cadastrados",
            "cobertura_modulos",
            "testes_necessarios",
            "testes_automatizados",
            "cobertura_testes",
        ]]
    )

    
    fig_cover = px.bar(
        coverage_df,
        x="produto",
        y="cobertura_testes",
        color="squad",
        text_auto=True,
        title="% de testes automatizados por produto/squad"
    )
    st.plotly_chart(fig_cover, use_container_width=True)

# ----------------------------
# Detailed table
# ----------------------------

st.subheader("Detalhamento")

if df.empty:
    st.info("Nenhum módulo cadastrado ainda.")
else:
    st.dataframe(
        df[[
            "squad",
            "produto",
            "modulo",
            "testes_necessarios",
            "testes_automatizados",
            "health_modulo"
        ]]
    )