# models/pdf_generator.py
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

class PDFGeneratorModel:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle('FichaTitle', parent=self.styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1A252C'), alignment=1, spaceAfter=15)
        self.subtitle_style = ParagraphStyle('FichaSubtitle', parent=self.styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor('#2980B9'), spaceBefore=10, spaceAfter=5)
        self.text_style = ParagraphStyle('FichaText', parent=self.styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#2C3E50'))

    def _linha(self, chave, valor):
        return [Paragraph(f"<b>{chave}:</b>", self.text_style), Paragraph(str(valor or "—"), self.text_style)]

    def _tabela(self, dados, cols=(150, 350)):
        t = Table(dados, colWidths=list(cols))
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 5),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F4F6F7')),
        ]))
        return t

    def build_pdf(self, sheet_type, d):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []

        if sheet_type == "conjurador":
            story.append(Paragraph(f"FICHA DE CONJURADOR: {d['NOME']}", self.title_style))
            story.append(Spacer(1, 10))
            story.append(self._tabela([self._linha("Idade", f"{d['IDADE']} anos"), self._linha("Grau de Ressonância", f"Grau {d['GRAU']}"), self._linha("Escola", d['ESCOLA'])]))
            story.append(Paragraph("RECURSOS", self.subtitle_style))
            story.append(self._tabela([self._linha("Vida Máxima", f"{d['VIDA_MAX']}"), self._linha("Conexão Máxima", f"{d['CONEXAO_MAX']}")]))
            story.append(Paragraph("PASSIVA DA ESCOLA", self.subtitle_style))
            story.append(Paragraph(d.get('PASSIVA_ESCOLA',''), self.text_style))
            story.append(Paragraph("ATRIBUTOS", self.subtitle_style))
            story.append(Table([
                [Paragraph(f"<b>Brutalidade:</b> {d['BRUTALIDADE']}", self.text_style), Paragraph(f"<b>Rapidez:</b> {d['RAPIDEZ']}", self.text_style)],
                [Paragraph(f"<b>Vitalidade:</b> {d['VITALIDADE']}", self.text_style), Paragraph(f"<b>Influência:</b> {d['INFLUÊNCIA']}", self.text_style)],
                [Paragraph(f"<b>Sintonia:</b> {d['SINTONIA']}", self.text_style), Paragraph(f"<b>Astúcia:</b> {d['ASTÚCIA']}", self.text_style)],
            ], colWidths=[250,250]))
            story.append(Paragraph("PERÍCIAS TREINADAS", self.subtitle_style))
            story.append(Paragraph(d.get('PERICIAS') or "—", self.text_style))
            story.append(Paragraph("BACKGROUND", self.subtitle_style))
            story.append(Paragraph(d.get('BACKGROUND') or "—", self.text_style))
            story.append(Paragraph("INVENTÁRIO", self.subtitle_style))
            story.append(Paragraph(d.get('INVENTARIO') or "—", self.text_style))

        elif sheet_type == "conjuracao":
            story.append(Paragraph(f"CONJURAÇÃO: {d['NOME']}", self.title_style))
            story.append(Spacer(1, 10))
            story.append(self._tabela([
                self._linha("Matriz Fundamental", d['MATRIZ']),
                self._linha("Sub-Matriz", d['SUB_MATRIZ']),
                self._linha("Custo / Ganho", f"Consome {d['CUSTO']} | Gera {d['GANHO']} Conexão"),
                self._linha("Ação Exigida", d['GASTO_ACAO']),
                self._linha("Alcance", d['ALCANCE']),
                self._linha("Área", d['AREA']),
                self._linha("Dano", d.get('DANO') or "—"),
            ]))
            story.append(Paragraph("EFEITOS MECÂNICOS", self.subtitle_style))
            story.append(Paragraph(d.get('EFEITOS') or "—", self.text_style))
            story.append(Paragraph("DESCRIÇÃO NARRATIVA", self.subtitle_style))
            story.append(Paragraph(d.get('DESCRICAO') or "—", self.text_style))

        elif sheet_type == "familiar":
            story.append(Paragraph(f"FAMILIAR: {d['NOME']}", self.title_style))
            story.append(Spacer(1, 10))
            story.append(self._tabela([
                self._linha("Espécie / Porte", f"{d['ESPECIE']} ({d['PORTE']})"),
                self._linha("Matrizes", f"{d['MATRIZ']} / Sub: {d['SUB_MATRIZ']}"),
                self._linha("Nível de Ameaça", d['AMEACA']),
                self._linha("Cobertura / Coloração", f"{d['COBERTURA']} | {d['COLORACAO']}"),
                self._linha("Temperamento / Hábito", f"{d['TEMPERAMENTO']} | {d['HABITO']}"),
                self._linha("Socialização / Bioma", f"{d['SOCIALIZACAO']} | {d['BIOMA']}"),
            ]))
            story.append(Paragraph("HABILIDADES FÍSICAS", self.subtitle_style))
            story.append(Paragraph(d.get('HAB_FISICAS') or "—", self.text_style))
            story.append(Paragraph("PODERES DA MATRIZ", self.subtitle_style))
            story.append(Paragraph(d.get('HAB_MATRIZ') or "—", self.text_style))

        elif sheet_type == "reliquia":
            story.append(Paragraph(f"RELÍQUIA: {d['NOME']}", self.title_style))
            story.append(Spacer(1, 10))
            story.append(self._tabela([
                self._linha("Nível", d['NIVEL']),
                self._linha("Núcleo", d['NUCLEO']),
                self._linha("Familiar Vinculado", d.get('FAMILIAR') or "—"),
                self._linha("Matriz / Sub-Matriz", f"{d['MATRIZ']} / {d['SUB_MATRIZ']}"),
                self._linha("Alcance Base", d['ALCANCE']),
                self._linha("Dano Próprio", d.get('DANO') or "—"),
            ]))
            story.append(Paragraph("CONJURAÇÕES GRAVADAS", self.subtitle_style))
            story.append(Paragraph(d.get('CONJURACOES') or "—", self.text_style))
            story.append(Paragraph("DESCRIÇÃO E HISTÓRICO", self.subtitle_style))
            story.append(Paragraph(d.get('DESCRICAO') or "—", self.text_style))

        doc.build(story)
        buffer.seek(0)
        return buffer