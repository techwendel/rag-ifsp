# Validação funcional — Downloads v0.3.2

**Projeto:** Coletor IFSP Extensão  
**Caso de uso:** UC02 — Baixar documentos PDF catalogados  
**Versão validada:** v0.3.2  
**Data:** 08/11/2026  
**Situação:** Aprovado

## 1. Objetivo

Validar a funcionalidade de download dos documentos PDF identificados pelo UC01, verificando a automação do processo, o salvamento dos arquivos e o tratamento de falhas.

## 2. Problemas identificados na versão anterior

Durante os testes da versão v0.3.1, foram observados:

- Necessidade de intervenção manual para salvar os documentos.
- Ausência de seleção única da pasta de destino.
- Elevado número de falhas HTTP 405.

**Resultado inicial:** 58 downloads concluídos, 38 falhas e 1 pendente.

## 3. Correções implementadas

Na versão v0.3.2, foram introduzidas as seguintes melhorias:

- Seleção da pasta de destino pelo usuário.
- Salvamento automático dos documentos na pasta escolhida.
- Processamento sequencial dos downloads.
- Alteração do mecanismo de obtenção e validação dos arquivos PDF.
- Possibilidade de recolocar downloads malsucedidos na fila.

## 4. Resultados dos testes

| Indicador | v0.3.1 | v0.3.2 |
|---|---:|---:|
| PDFs catalogados | 97 | 97 |
| Downloads concluídos | 58 | 96 |
| Falhas | 38 | 1 |
| Pendentes | 1 | 0 |
| Taxa de conclusão | 59,8% | 99,0% |

A versão v0.3.2 apresentou aumento expressivo na quantidade de downloads concluídos, eliminando a necessidade de intervenção manual para cada arquivo.

## 5. Análise da falha remanescente

**Documento:** Portaria 2.968, de 24/08/2015.

**Erro registrado:** Resposta não é um PDF (assinatura inválida).

O endereço institucional fornecido não retornou um documento com assinatura PDF válida na verificação realizada.

A extensão identificou a incompatibilidade e registrou a falha, evitando salvar conteúdo inválido como PDF.

A ocorrência foi considerada uma limitação da fonte consultada, não sendo necessária uma nova alteração no mecanismo de download.

## 6. Conclusão

O UC02 foi considerado **funcionalmente validado** na versão v0.3.2.

Foram concluídos 96 dos 97 downloads, com uma falha identificada e nenhuma operação pendente.

A validação confirma o funcionamento observado do processo automatizado de download e do tratamento da falha remanescente. Não representa uma verificação criptográfica ou uma auditoria integral dos arquivos obtidos.

**Decisão:** UC02 aprovado e encerrado para o escopo desta versão.
