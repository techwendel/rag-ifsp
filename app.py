"""MVP de consulta documental institucional, com métricas e cache de uploads."""
import hashlib
import os
import time
from pathlib import Path

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Consulta documental IFSP", page_icon="📄", layout="wide")
BASE = Path(__file__).parent
DOCS = BASE / "documentos"
MODEL = "gpt-4.1"
INSTRUCTIONS = """Você é um assistente de consulta documental institucional.
Responda exclusivamente com base nos PDFs fornecidos.
REGRAS:
1. Não invente informações ausentes dos documentos.
2. Identifique o documento e a página que fundamentam cada informação relevante.
3. Ao relacionar informações sobre pessoas, verifique cuidadosamente a correspondência entre os nomes.
4. Pessoas com o mesmo primeiro nome não devem ser consideradas a mesma pessoa.
5. Quando encontrar nomes abreviados, avalie sua compatibilidade com os nomes completos disponíveis. Diferencie correspondências confirmadas, prováveis, ambíguas e incompatíveis.
6. Não atribua a uma pessoa disciplinas, cargos, candidaturas ou responsabilidades pertencentes a outra pessoa.
7. Quando uma correspondência for plausível, mas não comprovada, apresente a informação como possibilidade, identificando claramente a incerteza. Não descarte registros relevantes nem atribua automaticamente informações a uma pessoa.
8. Diferencie atribuições formalmente designadas de atividades identificadas em outros documentos."""


def api_key():
    try:
        return st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    except Exception:
        return os.environ.get("OPENAI_API_KEY")


@st.cache_resource(show_spinner=False)
def client_for_key(key_fingerprint: str, _key: str):
    return OpenAI(api_key=_key)


@st.cache_resource(show_spinner=False)
def upload_pdf(key_fingerprint: str, file_hash: str, _content: bytes, filename: str, _client):
    """Cache em memória do processo; file_id reutilizado para mesmo conteúdo."""
    import io
    stream = io.BytesIO(_content)
    stream.name = filename
    result = _client.files.create(file=stream, purpose="user_data")
    return result.id


st.title("Consulta documental institucional")
st.caption("MVP experimental • PDF original • GPT-4.1 • latência e cache observáveis")
key = api_key()
if not key:
    st.error("Configure OPENAI_API_KEY em .streamlit/secrets.toml ou nas variáveis de ambiente.")
    st.stop()

client = client_for_key(hashlib.sha256(key.encode()).hexdigest()[:16], key)
files = sorted(DOCS.rglob("*.pdf")) if DOCS.exists() else []
if not files:
    st.warning("Nenhum PDF encontrado em documentos/.")
    st.stop()

with st.sidebar:
    st.subheader("Documentos disponíveis")
    selected = st.multiselect("PDFs da consulta", [str(f.relative_to(DOCS)) for f in files], default=[str(f.relative_to(DOCS)) for f in files])
    st.caption("Uploads são reaproveitados enquanto o cache do processo estiver ativo. Alterar o conteúdo do PDF gera novo upload.")
    if st.button("Limpar cache de uploads"):
        upload_pdf.clear()
        st.success("Cache local limpo. IDs remotos anteriores não são excluídos.")

question = st.text_area("Sua pergunta", height=100, placeholder="Ex.: Quem foi designado pela Portaria nº 159/2026?")
if st.button("Consultar", type="primary", disabled=not selected or not question.strip()):
    t0 = time.perf_counter()
    docs_content = []
    stats = []
    try:
        for rel in selected:
            p = DOCS / rel
            b = p.read_bytes()
            digest = hashlib.sha256(b).hexdigest()
            t_upload = time.perf_counter()
            file_id = upload_pdf(hashlib.sha256(key.encode()).hexdigest()[:16], digest, b, p.name, client)
            stats.append({"documento": rel, "sha256": digest[:12], "tempo_preparacao_upload_s": round(time.perf_counter()-t_upload, 3), "file_id": file_id})
            docs_content.extend([{"type": "input_text", "text": f"Documento: {rel}"}, {"type": "input_file", "file_id": file_id}])
        t_api = time.perf_counter()
        response = client.responses.create(model=MODEL, instructions=INSTRUCTIONS,
            input=[{"role": "user", "content": docs_content + [{"type": "input_text", "text": question.strip()}]}])
        api_seconds = time.perf_counter() - t_api
        total_seconds = time.perf_counter() - t0
        st.subheader("Resposta")
        st.write(response.output_text)
        c1, c2, c3 = st.columns(3)
        c1.metric("Tempo total", f"{total_seconds:.2f} s")
        c2.metric("Tempo da API", f"{api_seconds:.2f} s")
        c3.metric("Preparação + uploads", f"{total_seconds-api_seconds:.2f} s")
        with st.expander("Diagnóstico da consulta"):
            st.json({"modelo": MODEL, "documentos": stats, "response_id": response.id,
                "usage": response.usage.model_dump() if response.usage else None})
    except Exception as exc:
        st.error(f"Falha na consulta: {exc}")

st.divider()
st.caption("O cache evita reenviar arquivos idênticos; não elimina o custo de processar os PDFs a cada pergunta. Não armazena respostas.")
