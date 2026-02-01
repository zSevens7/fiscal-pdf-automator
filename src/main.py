import os
import sys

# Garante que o Python encontre os arquivos na mesma pasta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor import Processor
from generator import Generator
from merger import Merger

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_COVER = os.path.join(OUTPUT_DIR, "temp_capa.pdf")
# --------------------------------

def run():
    print("="*40)
    print("SISTEMA DE CONSOLIDAÇÃO TRIBUTÁRIA")
    print("="*40)

    # 1. Iniciar Processamento (Sem API Key)
    proc = Processor(INPUT_DIR)
    dados_finais = proc.process_all_files()

    if not dados_finais or not dados_finais.get("empresa") or dados_finais["empresa"] == "Não Identificada":
        print("Aviso: Empresa não identificada plenamente, mas gerando arquivo mesmo assim.")

    print(f"Empresa Identificada: {dados_finais['empresa']}")
    print(f"Mês de Apuração: {dados_finais['mes']}")
    print("Gerando consolidado...")

    # 2. Gerar Capa
    Generator.create_cover(TEMP_COVER, dados_finais)

    # 3. Merge Final
    lista_final = proc.get_ordered_list(TEMP_COVER)
    nome_arquivo = f"CONSOLIDADO - {dados_finais['empresa']} - {dados_finais['mes'].replace('/', '-')}.pdf"
    caminho_final = os.path.join(OUTPUT_DIR, nome_arquivo)
    
    Merger.merge_pdfs(lista_final, caminho_final)

    # Limpeza
    if os.path.exists(TEMP_COVER):
        os.remove(TEMP_COVER)

    print("\n" + "="*40)
    print("PROCESSO FINALIZADO COM SUCESSO!")
    print(f"Arquivo salvo em: {caminho_final}")
    print("="*40)

if __name__ == "__main__":
    run()