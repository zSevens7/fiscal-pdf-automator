import os
from extractor import Extractor

class Processor:
    def __init__(self, input_folder):
        self.input_folder = input_folder
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
            "DARF": None
        }

    def process_all_files(self):
        try:
            files = [f for f in os.listdir(self.input_folder) if f.lower().endswith('.pdf')]
        except FileNotFoundError:
            print(f"Erro: Pasta não encontrada: {self.input_folder}")
            return {}

        if not files:
            print("Nenhum PDF encontrado.")
            return self.consolidated

        for file in files:
            path = os.path.join(self.input_folder, file)
            print(f"Processando: {file}...")
            
            # Chama o extrator
            data = Extractor.identify_and_extract(path)
            tipo = data.get("type")

            if tipo == "DCTFWEB":
                self.files_by_type["DCTFWEB"] = path
                if data.get("empresa"): self.consolidated["empresa"] = data.get("empresa")
                if data.get("cnpj"): self.consolidated["cnpj"] = data.get("cnpj")
                if data.get("mes"): self.consolidated["mes"] = data.get("mes")

            elif tipo == "RESUMO_CREDITO":
                self.files_by_type["RESUMO_CREDITO"] = path

            elif tipo == "PERDCOMP":
                self.files_by_type["PERDCOMP"].append(path)
                self.consolidated["cp_segurados"] += data.get("cp_segurados", 0.0)
                self.consolidated["cp_patronal"] += data.get("cp_patronal", 0.0)
                self.consolidated["cp_terceiros"] += data.get("cp_terceiros", 0.0)
            
            elif tipo == "RESUMO_DEBITO":
                self.files_by_type["RESUMO_DEBITO"].append(path)
            
            elif tipo == "DARF":
                self.files_by_type["DARF"] = path

        # SOMA FINAL (Garante que o total bata com as partes)
        self.consolidated["valor_compensado"] = (
            self.consolidated["cp_segurados"] +
            self.consolidated["cp_patronal"] +
            self.consolidated["cp_terceiros"]
        )

        return self.consolidated

    def get_ordered_list(self, cover_path):
        ordered = [cover_path]
        if self.files_by_type["DCTFWEB"]: ordered.append(self.files_by_type["DCTFWEB"])
        if self.files_by_type["RESUMO_CREDITO"]: ordered.append(self.files_by_type["RESUMO_CREDITO"])
        if self.files_by_type["RESUMO_DEBITO"]: ordered.extend(self.files_by_type["RESUMO_DEBITO"])
        if self.files_by_type["PERDCOMP"]: ordered.extend(self.files_by_type["PERDCOMP"])
        if self.files_by_type["DARF"]: ordered.append(self.files_by_type["DARF"])
        return ordered