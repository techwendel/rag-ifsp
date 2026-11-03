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
question = st.text_area(
    "Sua pergunta",
    height=100,
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
