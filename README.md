# 📑 Consolidador Fiscal Automatizado (Fiscal PDF Automator)

Este sistema foi desenvolvido para automatizar o processo de consolidação de documentos tributários federais (DCTFWeb, PER/DCOMP, Resumos). Ele elimina a necessidade de somas manuais, reduz erros humanos e gera um relatório executivo padronizado para a contabilidade.

---

## 🎯 O que o sistema faz?

O software lê múltiplos arquivos PDF de guias fiscais "sujos" (com formatação complexa), identifica automaticamente o tipo de documento (Recibo, Comprovante de Compensação, etc.), extrai os valores monetários corretos (Patronal, Segurados, Terceiros) e realiza o cálculo matemático exato da compensação.

Ao final, ele gera uma **Capa Executiva Profissional** e une todos os documentos originais em um único arquivo PDF organizado, pronto para envio/arquivamento.

---

## 🛠️ Requisitos Técnicos

O projeto foi construído em **Python 3** utilizando bibliotecas específicas para garantir precisão e estabilidade:

* **`pdfplumber`**: Escolhido pela sua capacidade superior de extrair dados de tabelas e textos "sujos" (onde letras e números estão misturados), essencial para os layouts da Receita Federal.
* **`reportlab`**: Utilizado para desenhar a Capa do Relatório "do zero", permitindo um design corporativo (Cores, Logos, Tabelas) que não seria possível apenas editando PDFs existentes.
* **`pypdf2`**: Responsável pela manipulação final, unindo a capa gerada com os documentos originais e criando índices de navegação.

---

## 📂 Estrutura do Sistema (Arquivos .py)

Cada arquivo dentro da pasta `src/` tem uma responsabilidade única, seguindo o princípio de responsabilidade única (SOLID):

1.  **`main.py` (O Maestro):**
    É o ponto de entrada. Ele coordena o fluxo: manda ler a pasta, chama o processamento, pede para gerar a capa e finaliza com o merge.

2.  **`extractor.py` (O Leitor):**
    Contém a lógica de "Inteligência". Ele abre o PDF, limpa caracteres estranhos (aspas, erros de formatação) e usa Expressões Regulares (Regex) para identificar CNPJ, Data e Valores, diferenciando um Recibo de um Comprovante.

3.  **`processor.py` (O Contador):**
    Armazena e organiza os dados. Sua função principal é a **Segurança Matemática**: ele recalcula o total compensado somando as partes (*Patronal + Segurados + Terceiros*) para garantir que o valor final bata exatamente com os impostos, corrigindo eventuais discrepâncias de multas/juros.

4.  **`generator.py` (O Designer):**
    Cria a capa visual. Possui lógica para ajustar automaticamente nomes de empresas muito grandes (quebra de linha) e formata os valores para o padrão moeda brasileiro (R$).

5.  **`merger.py` (O Encadernador):**
    Pega a capa nova e "grampeia" junto com os PDFs originais na ordem correta, gerando o arquivo final.

---

## 🚀 Como Usar (Guia Rápido)

O sistema conta com um arquivo `executar.bat` para facilitar o uso no Windows, sem precisar abrir terminais de comando.

### Passo a Passo:

1.  **Prepare os Arquivos:**
    Copie todos os PDFs da competência (Recibos, Resumos, PER/DCOMP) e cole dentro da pasta **`input`**.

2.  **Execute:**
    Dê um duplo clique no arquivo **`executar.bat`**. Uma tela preta aparecerá processando os dados e fechará automaticamente ao terminar.

3.  **Resultado:**
    Vá até a pasta **`output`**. O arquivo consolidado estará lá com o nome:
    `CONSOLIDADO - NOME DA EMPRESA - MES-ANO.pdf`

---

### ⚠️ Regras de Ouro para Operação

* **Limpeza da Pasta `input`:**
    Sempre que for processar uma **nova empresa** ou um **novo mês**, você deve **apagar os arquivos antigos da pasta `input`** e colocar apenas os novos. Se não fizer isso, o sistema vai ler os arquivos velhos junto com os novos.

* **Pasta `output`:**
    **Não é necessário limpar a pasta `output`.**
    Como o sistema gera o nome do arquivo final baseado na Empresa e no Mês (ex: `12-2025`), não há risco de um arquivo sobrescrever o outro (a menos que você processe a mesma empresa e mês duas vezes). Você pode manter o histórico dos arquivos gerados lá sem problemas.

---
*Desenvolvido por [zSevens7](https://github.com/zSevens7)*
