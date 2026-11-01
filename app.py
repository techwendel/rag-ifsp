"""Consulta documental: PDFs do Google Drive, cache e tempos por etapa."""
import hashlib
import io
import os
import time

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from openai import OpenAI

st.set_page_config(page_title="Consulta documental IFSP", page_icon="📄", layout="wide")
MODEL = "gpt-4.1"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
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


def openai_key():
    return st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")


@st.cache_resource(show_spinner=False)
def openai_client(key_digest, _key):
    return OpenAI(api_key=_key)


@st.cache_resource(show_spinner=False)
def drive_client():
    credentials = service_account.Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def drive_list(service, query, fields="nextPageToken,files(id,name,mimeType,modifiedTime,size)"):
    results = []
    token = None
    while True:
        response = service.files().list(
            q=query, fields=fields, pageSize=1000, pageToken=token,
            supportsAllDrives=True, includeItemsFromAllDrives=True
        ).execute()
        results.extend(response.get("files", []))
        token = response.get("nextPageToken")
        if not token:
            return results


@st.cache_data(ttl=60, show_spinner=False)
def list_documents():
    """Reconsulta Drive a cada 60 s; encontra Documentos e percorre subpastas."""
    service = drive_client()
    roots = drive_list(service, "name = 'Documentos' and mimeType = 'application/vnd.google-apps.folder' and trashed = false")
    if not roots:
        raise RuntimeError("Pasta 'Documentos' não encontrada para a conta de serviço.")
    # Se houver mais de uma pasta com esse nome, o usuário deverá especificar o ID.
    if len(roots) != 1:
        raise RuntimeError("Há mais de uma pasta 'Documentos' acessível. Defina DRIVE_FOLDER_ID nos Secrets.")
    root_id = st.secrets.get("DRIVE_FOLDER_ID", roots[0]["id"])
    stack = [(root_id, "")]
    found = []
    while stack:
        folder_id, prefix = stack.pop()
        for item in drive_list(service, f"'{folder_id}' in parents and trashed = false"):
            rel = f"{prefix}{item['name']}"
            if item["mimeType"] == "application/vnd.google-apps.folder":
                stack.append((item["id"], rel + "/"))
            elif item["mimeType"] == "application/pdf":
                found.append({"id": item["id"], "nome": rel,
                              "modificado": item.get("modifiedTime", ""), "tamanho": item.get("size", "")})
    return sorted(found, key=lambda x: x["nome"].casefold())


@st.cache_data(show_spinner=False)
def download_pdf(file_id, modified_time):
    """Versão do arquivo participa da chave de cache."""
    service = drive_client()
    request = service.files().get_media(fileId=file_id)
    stream = io.BytesIO()
    downloader = MediaIoBaseDownload(stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return stream.getvalue()


@st.cache_resource(show_spinner=False)
def upload_pdf(key_digest, content_hash, filename, _content, _client):
    stream = io.BytesIO(_content)
    stream.name = filename
    return _client.files.create(file=stream, purpose="user_data").id


st.title("Consulta documental institucional")
st.caption("MVP experimental • PDFs no Google Drive • GPT-4.1 • cache e latência observáveis")
key = openai_key()
if not key:
    st.error("OPENAI_API_KEY não configurada nos Secrets.")
    st.stop()
if "gcp_service_account" not in st.secrets:
    st.error("Seção [gcp_service_account] não configurada nos Secrets.")
    st.stop()
client = openai_client(hashlib.sha256(key.encode()).hexdigest()[:16], key)

try:
    t_listing = time.perf_counter()
    docs = list_documents()
    listing_seconds = time.perf_counter() - t_listing
except Exception as exc:
    st.error(f"Não foi possível listar documentos no Google Drive: {exc}")
    st.stop()
if not docs:
    st.warning("Nenhum PDF encontrado na pasta Documentos e suas subpastas.")
    st.stop()

by_name = {d["nome"]: d for d in docs}
with st.sidebar:
    st.subheader("Documentos do Google Drive")
    st.caption(f"{len(docs)} PDF(s) • listagem: {listing_seconds:.3f} s • atualização até 60 s")
    selected = st.multiselect("PDFs da consulta", list(by_name), default=list(by_name))
    if st.button("Atualizar lista agora"):
        list_documents.clear()
        st.rerun()
    if st.button("Limpar caches de documentos"):
        download_pdf.clear()
        upload_pdf.clear()
        st.success("Caches locais de download e upload limpos; arquivos remotos não excluídos.")

question = st.text_area("Sua pergunta", height=100, placeholder="Ex.: Quem foi designado pela Portaria nº 159/2026?")
if st.button("Consultar", type="primary", disabled=not selected or not question.strip()):
    t0 = time.perf_counter()
    parts, stats = [], []
    try:
        for name in selected:
            doc = by_name[name]
            td = time.perf_counter()
            content = download_pdf(doc["id"], doc["modificado"])
            download_s = time.perf_counter() - td
            digest = hashlib.sha256(content).hexdigest()
            tu = time.perf_counter()
            fid = upload_pdf(hashlib.sha256(key.encode()).hexdigest()[:16], digest, name.split("/")[-1], content, client)
            upload_s = time.perf_counter() - tu
            stats.append({"documento": name, "download_cache_ou_rede_s": round(download_s, 3),
                          "upload_cache_ou_rede_s": round(upload_s, 3),
                          "sha256": digest[:12], "file_id": fid})
            parts.extend([{"type": "input_text", "text": f"Documento: {name}"},
                          {"type": "input_file", "file_id": fid}])
        t_api = time.perf_counter()
        response = client.responses.create(
            model=MODEL, instructions=INSTRUCTIONS,
            input=[{"role": "user", "content": parts + [{"type": "input_text", "text": question.strip()}]}]
        )
        api_s = time.perf_counter() - t_api
        total_s = time.perf_counter() - t0
        st.subheader("Resposta")
        st.write(response.output_text)
        c1, c2, c3 = st.columns(3)
        c1.metric("Tempo total da consulta", f"{total_s:.2f} s")
        c2.metric("Tempo da OpenAI", f"{api_s:.2f} s")
        c3.metric("Preparação (Drive + uploads)", f"{total_s-api_s:.2f} s")
        with st.expander("Diagnóstico da consulta"):
            st.json({"modelo": MODEL, "listagem_drive_s": round(listing_seconds, 3),
                     "documentos": stats, "response_id": response.id,
                     "usage": response.usage.model_dump() if response.usage else None})
    except Exception as exc:
        st.error(f"Falha na consulta: {exc}")

st.divider()
st.caption("Cache local não garante persistência após reinícios. A listagem é atualizada em até 60 s; downloads são invalidados pela data de modificação. Reutilizar file_id não elimina o processamento dos PDFs na OpenAI.")
