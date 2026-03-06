# QA Dashboard

Este projeto é um painel de métricas de testes automatizados de QA, desenvolvido em Python utilizando Streamlit, Plotly e Pandas. Ele permite o cadastro, visualização e análise de cobertura de testes automatizados por squad, além de gerar relatórios em PDF.

## Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação de dados
- **Plotly**: Gráficos interativos
- **SQLite**: Banco de dados local (via `sqlite3`)
- **reportlab**: Geração de relatórios em PDF

## Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/recueroana/qa-dashboard.git
cd qa-dashboard
```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

```bash
python -m venv venv
# Ative o ambiente virtual:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt

pip install matplotlib
```

## Como Usar

1. **Execute o aplicativo Streamlit:**

```bash
streamlit run app.py
```

2. **Acesse o painel:**

Abra o navegador e acesse o endereço exibido no terminal (geralmente http://localhost:8501).

3. **Primeira execução:**

O banco de dados será criado automaticamente na primeira execução, não é necessário criar manualmente.

4. **Cadastro de dados:**

- Preencha o formulário com as informações da squad, produto, testes necessários e automatizados.
- Clique em "Cadastrar" para salvar.

5. **Visualização e análise:**

- Filtre por squads, visualize KPIs, gráficos e o score de saúde.
- Gere relatórios em PDF clicando no botão "Gerar relatório PDF" na barra lateral; o arquivo gerado virá com carimbo de data/hora no nome e estará disponível para download.

## Estrutura do Projeto

```
qa-dashboard/
├── app.py            # Código principal do dashboard
├── database.py       # Funções de acesso ao banco de dados SQLite
├── pdf_report.py     # Geração de relatórios em PDF
├── requirements.txt  # Dependências do projeto
```

## Dependências Principais

- streamlit
- pandas
- plotly
- reportlab

Todas as dependências estão listadas em `requirements.txt`.

## Observações

- O banco de dados SQLite será criado automaticamente no diretório do projeto.
- Para reiniciar os dados, basta apagar o arquivo do banco de dados (caso exista).

## Autor

- [Ana Carolina Recuero](https://github.com/seu-usuario)

---
