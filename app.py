"""MVP RAG IFSP: busca documental e respostas fundamentadas no Vector Store."""

import hashlib
import os
import time

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI

st.set_page_config(page_title="Consulta documental IFSP", page_icon="📄", layout="wide")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DEFAULT_VECTOR_STORE_ID = "vs_6aea5a97694c819195b1cc430262b7f3"
DEFAULT_MODEL = "gpt-5.1"

INSTRUCTIONS = """Você é um assistente de consulta documental do IFSP Campus Itaquaquecetuba.
Seu objetivo é orientar servidores a encontrar informações em documentos institucionais.
Responda em português brasileiro, de forma objetiva, exclusivamente com base nos documentos recuperados.
Não invente fatos, nomes, cargos, datas, páginas ou documentos.
Indique os documentos que fundamentam as afirmações e preserve as citações fornecidas pela ferramenta.
Se não houver evidência suficiente, diga isso claramente.
Ao relacionar pessoas, não confunda nomes semelhantes ou abreviados.
Diferencie informações confirmadas, possibilidades e ambiguidades.
Não trate editais que autorizam uma temática como prova de que um projeto específico foi executado.
Não afirme que a pesquisa foi exaustiva.
Seu papel é orientar a consulta: a documentação original é a referência final.
"""


def setting(name, default=None):
    return st.secrets.get(name) or os.environ.get(name) or default


@st.cache_resource(show_spinner=False)
def get_openai_client(key_hash, _key):
    return OpenAI(api_key=_key)


@st.cache_resource(show_spinner=False)
def get_drive_client():
    credentials = service_account.Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def drive_list(service, query):
    items, token = [], None
    while True:
        result = service.files().list(
            q=query,
            fields="nextPageToken,files(id,name,mimeType,webViewLink)",
            pageSize=1000,
            pageToken=token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        items.extend(result.get("files", []))
        token = result.get("nextPageToken")
        if not token:
            return items


@st.cache_data(ttl=300, show_spinner=False)
def list_drive_pdfs():
    """Consulta apenas metadados para oferecer links; não baixa PDFs."""
    service = get_drive_client()
    folder_id = setting("DRIVE_FOLDER_ID")
    if not folder_id:
        roots = drive_list(
            service,
            "name = 'Documentos' and "
            "mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        )
        if len(roots) != 1:
            raise RuntimeError(
                "Não foi possível identificar uma única pasta 'Documentos'. "
                "Configure DRIVE_FOLDER_ID nos Secrets."
            )
        folder_id = roots[0]["id"]

    stack = [(folder_id, "")]
    found = []
    while stack:
        current_id, prefix = stack.pop()
        for item in drive_list(service, f"'{current_id}' in parents and trashed = false"):
            path = prefix + item["name"]
            if item["mimeType"] == "application/vnd.google-apps.folder":
                stack.append((item["id"], path + "/"))
            elif item["mimeType"] == "application/pdf":
                found.append({
                    "name": item["name"],
                    "path": path,
                    "id": item["id"],
                    "url": item.get("webViewLink") or
                           f"https://drive.google.com/file/d/{item['id']}/view",
                })
    return sorted(found, key=lambda doc: doc["path"].casefold())


def citation_files(response):
    """Retorna os nomes citados pela API, sem inventar correspondências."""
    names = []
    for item in response.output:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", []):
            for annotation in getattr(content, "annotations", []):
                if getattr(annotation, "type", None) == "file_citation":
                    name = getattr(annotation, "filename", None)
                    if name and name not in names:
                        names.append(name)
    return names


def show_sources(filenames, drive_docs):
    """Associa por nome exato; nomes duplicados são mostrados como ambíguos."""
    lookup = {}
    for doc in drive_docs:
        lookup.setdefault(doc["name"], []).append(doc)

    if not filenames:
        st.info("Nenhuma fonte identificada nesta consulta.")
        return

    for filename in filenames:
        matches = lookup.get(filename, [])
        if len(matches) == 1:
            doc = matches[0]
            st.markdown(f"📄 [{filename}]({doc['url']})")
            st.caption(doc["path"])
        elif len(matches) > 1:
            st.write(f"📄 **{filename}** — mais de um arquivo com esse nome no Drive:")
            for doc in matches:
                st.markdown(f"- [{doc['path']}]({doc['url']})")
        else:
            st.write(f"📄 {filename}")
            st.caption("Link não localizado na listagem do Google Drive.")


st.title("📄 Consulta documental IFSP")
st.caption("MVP experimental • 85 PDFs indexados • busca semântica e respostas com fontes")

api_key = setting("OPENAI_API_KEY")
vector_store_id = setting("VECTOR_STORE_ID", DEFAULT_VECTOR_STORE_ID)
model = setting("OPENAI_MODEL", DEFAULT_MODEL)

if not api_key:
    st.error("Configure OPENAI_API_KEY nos Secrets do Streamlit.")
    st.stop()

client = get_openai_client(hashlib.sha256(api_key.encode()).hexdigest()[:16], api_key)

# Falhas de acesso ao Drive não impedem a consulta ao índice.
drive_docs = []
drive_error = None
if "gcp_service_account" in st.secrets:
    try:
        drive_docs = list_drive_pdfs()
    except Exception as exc:
        drive_error = str(exc)
else:
    drive_error = "Credenciais gcp_service_account não configuradas."

with st.sidebar:
    st.subheader("Acervo")
    st.write("Índice: RAG_IFSP_Documentos")
    st.caption(f"Modelo de respostas: {model}")
    st.caption(f"PDFs localizados no Drive: {len(drive_docs)}")
    if drive_error:
        st.warning(f"Links do Drive indisponíveis: {drive_error}")
    if st.button("Atualizar links do Drive"):
        list_drive_pdfs.clear()
        st.rerun()
    st.caption("A consulta utiliza o índice da OpenAI. Nenhum PDF é baixado ou reenviado.")

mode = st.radio(
    "O que você deseja fazer?",
    ["Localizar documentos", "Consultar conteúdo"],
    horizontal=True,
)
question = st.text_input(
    "Sua pergunta",
    placeholder=(
        "Ex.: Projetos de extensão relacionados ao meio ambiente"
        if mode == "Localizar documentos"
        else "Ex.: Quais iniciativas ambientais aparecem nos documentos do campus?"
    ),
)

if st.button("Consultar", type="primary", disabled=not question.strip()):
    start = time.perf_counter()
    try:
        if mode == "Localizar documentos":
            with st.spinner("Procurando documentos relevantes..."):
                result = client.vector_stores.search(
                    vector_store_id=vector_store_id,
                    query=question.strip(),
                    max_num_results=20,
                )
            elapsed = time.perf_counter() - start
            st.subheader("Documentos encontrados")
            # A busca retorna trechos; agrupar evita repetir o mesmo PDF.
            grouped = {}
            for item in result.data:
                name = item.filename
                if name not in grouped:
                    grouped[name] = {"score": item.score, "snippets": []}
                for part in item.content:
                    if getattr(part, "type", None) == "text" and part.text.strip():
                        if len(grouped[name]["snippets"]) < 2:
                            grouped[name]["snippets"].append(part.text.strip())
                        break

            if not grouped:
                st.info("Nenhum documento foi encontrado para esta consulta.")
            else:
                st.caption(
                    f"{len(grouped)} documento(s) distinto(s) encontrado(s) "
                    f"em {elapsed:.2f} segundos. Busca por relevância, não exaustiva."
                )
                for number, (name, data) in enumerate(grouped.items(), 1):
                    with st.container(border=True):
                        st.markdown(f"**{number}. {name}**")
                        show_sources([name], drive_docs)
                        if data["snippets"]:
                            with st.expander("Ver trecho recuperado"):
                                st.write(data["snippets"][0][:1200])

        else:
            with st.spinner("Consultando o conteúdo dos documentos..."):
                response = client.responses.create(
                    model=model,
                    instructions=INSTRUCTIONS,
                    input=question.strip(),
                    tools=[{
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id],
                    }],
                )
            elapsed = time.perf_counter() - start
            st.subheader("Resposta")
            st.write(response.output_text or "Não foi possível elaborar uma resposta.")
            st.subheader("Documentos citados")
            show_sources(citation_files(response), drive_docs)
            st.caption(f"Tempo da consulta: {elapsed:.2f} segundos")
            with st.expander("Diagnóstico"):
                st.json({
                    "modelo": model,
                    "tempo_s": round(elapsed, 3),
                    "response_id": response.id,
                    "usage": response.usage.model_dump() if response.usage else None,
                })

    except Exception as exc:
        st.error(f"Não foi possível concluir a consulta: {exc}")

st.divider()
st.caption(
    "Esta ferramenta orienta a consulta documental. "
    "Confira as informações e as permissões de acesso nos PDFs originais."
)
