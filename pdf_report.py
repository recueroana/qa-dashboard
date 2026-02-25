from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import matplotlib.pyplot as plt
import os


def gerar_pdf(resumo, kpis):

    file_path = "relatorio_qa_dashboard.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AUTOMATION METRICS REPORT", styles["Title"]))
    elements.append(Spacer(1, 20))

    tabela_kpi = Table([
        ["Squads", kpis["total_squads"]],
        ["Produtos", kpis["total_produtos"]],
        ["Cobertura Média", f'{kpis["cobertura"]:.1f}%'],
        ["Automation Gap", kpis["gap_total"]],
    ])

    tabela_kpi.setStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ])

    elements.append(tabela_kpi)
    elements.append(Spacer(1, 20))

    # graphic
    plt.figure()
    plt.bar(resumo["squad"], resumo["cobertura"])
    plt.title("Cobertura por Squad")
    plt.xticks(rotation=45)

    img_path = "grafico.png"
    plt.tight_layout()
    plt.savefig(img_path)
    plt.close()

    elements.append(Image(img_path, width=450, height=250))

    doc.build(elements)

    os.remove(img_path)

    return file_path