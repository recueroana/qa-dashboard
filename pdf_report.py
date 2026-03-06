from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import matplotlib.pyplot as plt
import os


def gerar_pdf(resumo, kpis):

    # clean up any previous reports matching our naming pattern
    import glob
    for old in glob.glob("relatorio_qa_dashboard_*.pdf"):
        try:
            os.remove(old)
        except Exception:
            pass

    # generate a unique filename with timestamp to avoid overwriting
    from datetime import datetime
    file_path = f"relatorio_qa_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AUTOMATION METRICS REPORT", styles["Title"]))
    elements.append(Spacer(1, 20))

    tabela_kpi = Table([
        ["Squads", kpis["total_squads"]],
        ["Produtos", kpis["total_produtos"]],
        ["Cobertura Média", f'{kpis["cobertura"]:.2f}%'],
        ["Automation Gap", f'{kpis["gap_total"]:.2f}%'],
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