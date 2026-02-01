from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit # Importante para quebrar texto longo
from datetime import datetime

class Generator:
    @staticmethod
    def format_currency(value):
        try:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return "R$ 0,00"

    @staticmethod
    def create_cover(filename, data):
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Cores Oficiais
        COR_AZUL = colors.HexColor("#1F3864")
        COR_CINZA = colors.HexColor("#F2F2F2")
        COR_LINHA = colors.HexColor("#D9D9D9")
        
        # --- 1. CABEÇALHO AZUL ---
        c.setFillColor(COR_AZUL)
        c.rect(0, height - 3*cm, width, 3*cm, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 1.8*cm, "CONSOLIDAÇÃO TRIBUTÁRIA")
        
        # Data de Geração
        c.setFont("Helvetica", 9)
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        c.drawRightString(width - 1*cm, height - 2.5*cm, f"Gerado em: {data_hoje}")

        # --- 2. CAIXA DE DADOS (Dinâmica) ---
        # Aumentamos a altura da caixa para caber nomes grandes (3.5 cm)
        box_height = 3.5*cm 
        cursor_y = height - 4.5*cm 
        
        c.setFillColor(COR_CINZA)
        c.roundRect(1.5*cm, cursor_y - box_height, width - 3*cm, box_height, 10, fill=True, stroke=False)
        
        c.setFillColor(colors.black)
        
        # --- LADO ESQUERDO: EMPRESA ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, cursor_y - 1*cm, "EMPRESA:")
        
        empresa_nome = str(data.get('empresa', ''))
        c.setFont("Helvetica", 12)
        
        # Lógica para quebrar linha se o nome for muito grande
        # Largura disponível = Largura Página - Margem Esq - Espaço da Data na Direita
        max_width = width - 11*cm 
        lines = simpleSplit(empresa_nome, "Helvetica", 12, max_width)
        
        text_y = cursor_y - 1*cm
        for line in lines:
            c.drawString(4.5*cm, text_y, line)
            text_y -= 0.5*cm # Desce para a próxima linha
            
        # CNPJ (Agora ele desce automaticamente se o nome tiver várias linhas)
        cnpj_y = text_y - 0.2*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, cnpj_y, "CNPJ:")
        c.setFont("Helvetica", 12)
        c.drawString(4.5*cm, cnpj_y, str(data.get('cnpj', '')))
        
        # --- LADO DIREITO: MÊS (Separado para não colidir) ---
        c.setFont("Helvetica-Bold", 12)
        # Alinhado bem à direita da caixa
        c.drawRightString(width - 2.5*cm, cursor_y - 1*cm, "MÊS DE APURAÇÃO")
        
        c.setFillColor(COR_AZUL)
        c.setFont("Helvetica-Bold", 16)
        c.drawRightString(width - 2.5*cm, cursor_y - 1.8*cm, str(data.get('mes', '')))

        # --- 3. TABELA DE VALORES ---
        # O cursor começa abaixo da caixa cinza
        cursor_y = cursor_y - box_height - 1.5*cm 
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1.5*cm, cursor_y, "Detalhamento dos Impostos")
        
        # Linha azul grossa
        c.setStrokeColor(COR_AZUL)
        c.setLineWidth(2)
        c.line(1.5*cm, cursor_y - 0.2*cm, width - 1.5*cm, cursor_y - 0.2*cm)
        
        def draw_row(label, value, y):
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            c.drawString(1.5*cm, y, label)
            c.drawRightString(width - 1.5*cm, y, Generator.format_currency(value))
            # Linha cinza fina
            c.setStrokeColor(COR_LINHA)
            c.setLineWidth(1)
            c.line(1.5*cm, y - 0.3*cm, width - 1.5*cm, y - 0.3*cm)

        cursor_y -= 1.5*cm
        draw_row("CP Segurados", data.get('cp_segurados', 0.0), cursor_y)
        cursor_y -= 1.0*cm
        draw_row("CP Patronal", data.get('cp_patronal', 0.0), cursor_y)
        cursor_y -= 1.0*cm
        draw_row("CP Terceiros", data.get('cp_terceiros', 0.0), cursor_y)

        # --- 4. TOTAL EM DESTAQUE ---
        cursor_y -= 2.0*cm
        c.setFillColor(COR_AZUL)
        c.roundRect(1.5*cm, cursor_y - 0.5*cm, width - 3*cm, 1.5*cm, 6, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2.5*cm, cursor_y, "TOTAL COMPENSADO:")
        c.setFont("Helvetica-Bold", 18)
        c.drawRightString(width - 2.5*cm, cursor_y, Generator.format_currency(data.get('valor_compensado', 0.0)))

        # Rodapé Discreto
        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, 1*cm, "Documento gerado automaticamente pelo Sistema de Consolidação Tributária")
        
        c.save()