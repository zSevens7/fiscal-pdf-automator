import pdfplumber
import re

class Extractor:
    @staticmethod
    def identify_and_extract(pdf_path):
        data = {
            "type": "OUTRO",
            "empresa": None,
            "cnpj": None,
            "mes": None,
            "valor_compensado": 0.0,
            "cp_segurados": 0.0,
            "cp_patronal": 0.0,
            "cp_terceiros": 0.0
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                # Remove sujeira comum em leitura de tabelas
                clean_text = full_text.replace('"', ' ').replace("'", " ")
        except Exception as e:
            print(f"Erro ao ler PDF: {e}")
            return data

        # --- 1. DCTFWEB (Capa e Dados) ---
        # ATUALIZADO: Procura a frase completa para não confundir com o Resumo de Débitos
        if "Recibo de Entrega da Declaração" in clean_text and "DCTFWeb" in clean_text:
            data["type"] = "DCTFWEB"
            
            # CNPJ
            cnpj_match = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", clean_text)
            if cnpj_match: data["cnpj"] = cnpj_match.group(0)

            # MÊS: Evita pegar 30/0001 focando em anos 20xx
            mes_match = re.search(r"(0[1-9]|1[0-2])/(20\d{2})", clean_text)
            if mes_match:
                data["mes"] = f"{mes_match.group(1)}/{mes_match.group(2)}"

            # NOME
            match_nome = re.search(r"Nome\s+([A-Z\s\.]+)(?:CNPJ|Período)", clean_text)
            if match_nome:
                data["empresa"] = match_nome.group(1).strip()
            elif "HYDRA" in clean_text:
                data["empresa"] = "HYDRA ENGENHARIA E SANEAMENTO LTDA"

        # --- 2. RESUMO DE CRÉDITOS ---
        # ATUALIZADO: Aceita "RELATÓRIO DE CRÉDITOS" também
        elif "RESUMO DE CRÉDITOS" in clean_text or "RELATÓRIO DE CRÉDITOS" in clean_text:
            data["type"] = "RESUMO_CREDITO"
            # Procura valor da Compensação
            match_comp = re.search(r"Compensação\s+([\d\.]+,\d{2}|[\d\.,]+)", clean_text)
            if match_comp:
                val_str = match_comp.group(1)
                numeros = re.findall(r"[\d\.,]+", val_str)
                if numeros:
                    data["valor_compensado"] = Extractor.parse_br_number(numeros[-1])

        # --- 3. PER/DCOMP (Correção da Soma) ---
        elif "PER/DCOMP" in clean_text or "COMPENSAÇÃO" in clean_text:
            data["type"] = "PERDCOMP"
            
            # Estratégia "Bloco de Valores":
            # O texto costuma vir: "CP TERCEIROS" ... "CP PATRONAL" ... "VALOR" ... "127.679,42" ... "495.571,13"
            
            if "VALOR" in clean_text:
                # Pega tudo que vem depois da palavra VALOR
                parts = clean_text.split("VALOR")
                if len(parts) > 1:
                    bloco_valores = parts[-1] 
                    # Acha todos os números com formato de dinheiro (X.XXX,XX)
                    valores_encontrados = re.findall(r"(\d{1,3}(?:\.\d{3})*,\d{2})", bloco_valores)
                    
                    if len(valores_encontrados) >= 2:
                        # Baseado no seu PDF: 
                        # O 1º valor (127k) é Terceiros
                        # O 2º valor (495k) é Patronal
                        v1 = Extractor.parse_br_number(valores_encontrados[0])
                        v2 = Extractor.parse_br_number(valores_encontrados[1])
                        
                        # Lógica de segurança: O maior geralmente é patronal, mas vamos confiar na ordem do PDF
                        data["cp_terceiros"] = v1
                        data["cp_patronal"] = v2
                    elif len(valores_encontrados) == 1:
                        data["cp_patronal"] = Extractor.parse_br_number(valores_encontrados[0])

        elif "RESUMO DE DÉBITOS" in clean_text:
            data["type"] = "RESUMO_DEBITO"
        
        elif "DARF" in clean_text:
            data["type"] = "DARF"

        return data

    @staticmethod
    def parse_br_number(val_str):
        if not val_str: return 0.0
        try:
            clean = val_str.replace(".", "").replace(",", ".")
            return float(clean)
        except:
            return 0.0