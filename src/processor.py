import os
from extractor import Extractor

class Processor:
    def __init__(self, input_folder):
        self.input_folder = input_folder
        self.all_input_files = []  # Lista para guardar TODOS os arquivos encontrados
        self.consolidated = {
            "empresa": "Não Identificada",
            "cnpj": "Não Identificado",
            "mes": "Não Identificado",
            "valor_compensado": 0.0,
            "cp_segurados": 0.0,
            "cp_patronal": 0.0,
            "cp_terceiros": 0.0
        }
        self.files_by_type = {
            "DCTFWEB": None,
            "RESUMO_CREDITO": None,
            "RESUMO_DEBITO": [],
            "PERDCOMP": [],
            "DARF": []  # Mudei para lista por segurança
        }

    def process_all_files(self):
        try:
            # Pega todos os PDFs, ignorando arquivos temporários ou já consolidados
            raw_files = [f for f in os.listdir(self.input_folder) if f.lower().endswith('.pdf')]
            self.all_input_files = [
                os.path.join(self.input_folder, f) 
                for f in raw_files 
                if not f.startswith("CONSOLIDADO") and not f.startswith("temp_")
            ]
        except FileNotFoundError:
            print(f"Erro: Pasta não encontrada: {self.input_folder}")
            return {}

        if not self.all_input_files:
            print("Nenhum PDF válido encontrado para processar.")
            return self.consolidated

        for path in self.all_input_files:
            print(f"Lendo: {os.path.basename(path)}...")
            
            # Chama o extrator
            data = Extractor.identify_and_extract(path)
            tipo = data.get("type")

            # --- CLASSIFICAÇÃO DOS ARQUIVOS ---
            if tipo == "DCTFWEB":
                self.files_by_type["DCTFWEB"] = path
                if data.get("empresa"): self.consolidated["empresa"] = data.get("empresa")
                if data.get("cnpj"): self.consolidated["cnpj"] = data.get("cnpj")
                if data.get("mes"): self.consolidated["mes"] = data.get("mes")

            elif tipo == "RESUMO_CREDITO":
                self.files_by_type["RESUMO_CREDITO"] = path
                # Valor é ignorado aqui para usar o cálculo matemático seguro abaixo

            elif tipo == "PERDCOMP":
                self.files_by_type["PERDCOMP"].append(path)
                # Soma cumulativa
                self.consolidated["cp_segurados"] += data.get("cp_segurados", 0.0)
                self.consolidated["cp_patronal"] += data.get("cp_patronal", 0.0)
                self.consolidated["cp_terceiros"] += data.get("cp_terceiros", 0.0)
            
            elif tipo == "RESUMO_DEBITO":
                self.files_by_type["RESUMO_DEBITO"].append(path)
            
            elif tipo == "DARF":
                self.files_by_type["DARF"].append(path)

        # --- REGRA DE OURO (MATEMÁTICA) ---
        # Recalcula o total compensado somando as partes para garantir exatidão
        self.consolidated["valor_compensado"] = (
            self.consolidated["cp_segurados"] +
            self.consolidated["cp_patronal"] +
            self.consolidated["cp_terceiros"]
        )

        return self.consolidated

    def get_ordered_list(self, cover_path):
        """
        Monta a lista final de PDFs.
        Ordem: Capa -> Recibos Principais -> Resumos -> Comprovantes -> O que sobrou (Aspirador)
        """
        ordered = [cover_path]
        
        # 1. Prioridades (Ordem Bonita)
        if self.files_by_type["DCTFWEB"]: 
            ordered.append(self.files_by_type["DCTFWEB"])
            
        if self.files_by_type["RESUMO_CREDITO"]: 
            ordered.append(self.files_by_type["RESUMO_CREDITO"])
            
        if self.files_by_type["RESUMO_DEBITO"]: 
            ordered.extend(self.files_by_type["RESUMO_DEBITO"])
            
        if self.files_by_type["PERDCOMP"]: 
            ordered.extend(self.files_by_type["PERDCOMP"])
            
        if self.files_by_type["DARF"]: 
            ordered.extend(self.files_by_type["DARF"])

        # 2. O "ASPIRADOR" (Segurança Total)
        # Verifica se algum arquivo da pasta input ficou de fora da lista 'ordered'
        # Se ficou, anexa ele no final para garantir que o cliente receba TUDO.
        for original_file in self.all_input_files:
            if original_file not in ordered:
                print(f"Aviso: O arquivo '{os.path.basename(original_file)}' não foi classificado, mas será anexado no final.")
                ordered.append(original_file)

        return ordered