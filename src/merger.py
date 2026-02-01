from PyPDF2 import PdfWriter, PdfReader
import os

class Merger:
    @staticmethod
    def merge_pdfs(ordered_list, final_path):
        writer = PdfWriter()
        current_page = 0

        # Mapeamento de nomes bonitos para o Índice
        labels = {
            "temp_capa": "Capa e Resumo",
            "Recibo": "DCTFWeb (Recibo)",
            "ResumoCreditos": "Resumo de Créditos",
            "ResumoDebitos": "Resumo de Débitos",
            "recibo-perdcomp": "Comprovante PER/DCOMP"
        }

        for pdf_path in ordered_list:
            try:
                reader = PdfReader(pdf_path)
                num_pages = len(reader.pages)
                
                # Define o nome para o Índice
                filename = os.path.basename(pdf_path)
                bookmark_title = filename # Padrão
                
                # Tenta achar um nome bonito
                for key, label in labels.items():
                    if key in filename:
                        bookmark_title = label
                        break
                
                # Adiciona o marcador (Índice) apontando para a página atual
                writer.add_outline_item(title=bookmark_title, page_number=current_page)

                # Adiciona as páginas
                for page in reader.pages:
                    writer.add_page(page)
                
                current_page += num_pages
                    
            except Exception as e:
                print(f"Erro ao mergear {pdf_path}: {e}")

        with open(final_path, "wb") as f:
            writer.write(f)