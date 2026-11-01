# rag-ifsp
# Consulta documental IFSP — Streamlit

1. Instale: `pip install -r requirements.txt`
2. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e informe sua chave (não publique esse arquivo).
3. Execute: `streamlit run app.py`
4. Para publicar no Streamlit Community Cloud, coloque os arquivos em um repositório GitHub **privado** e configure `OPENAI_API_KEY` nas Secrets do app. Avalie as regras institucionais de compartilhamento dos PDFs antes de publicar.

Os três PDFs de teste estão na pasta `documentos/`. O app seleciona PDFs dessa pasta e os envia à API na primeira consulta; os IDs de upload ficam em cache enquanto o processo estiver ativo. O cache é invalidado quando os bytes mudam. Limpar o cache não exclui arquivos remotos. A latência total inclui leitura dos arquivos, upload quando necessário e chamada da API. A API ainda processa o conteúdo dos PDFs em cada pergunta; não há cache de respostas.

Para comparação Colab × Streamlit, use a mesma pergunta, o mesmo conjunto de PDFs e as mesmas instruções. Execute cada consulta em sessões independentes e compare as respostas e tempos. A aplicação usa o mesmo modelo, mas não fixa temperatura nem seed.
