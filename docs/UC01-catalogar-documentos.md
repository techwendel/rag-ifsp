# UC01 — Catalogar documentos PDF institucionais

## 1. Identificação

**Código:** UC01  
**Nome:** Catalogar documentos PDF institucionais  
**Sistema:** Coletor IFSP Extensão  
**Versão de referência:** 0.3.0  
**Situação:** Em documentação

## 2. Objetivo

Permitir a identificação e catalogação de documentos PDF disponibilizados em páginas institucionais relacionadas à Extensão do IFSP, por meio de rastreamento automatizado de links.

## 3. Ator principal

Usuário responsável pela operação da extensão de coleta documental.

## 4. Descrição geral

O usuário inicia a operação de catalogação por meio da extensão instalada no navegador.

O sistema percorre páginas institucionais elegíveis, identifica links para documentos PDF e organiza as informações encontradas em um catálogo.

A catalogação constitui uma etapa distinta do download dos arquivos, permitindo que os documentos identificados sejam posteriormente processados.

## 5. Escopo

Este caso de uso contempla:

- Identificação de páginas institucionais elegíveis.
- Rastreamento de links dentro dos limites configurados.
- Identificação de referências a documentos PDF.
- Registro das informações dos documentos identificados.
- Tratamento de referências duplicadas conforme as regras implementadas.

**Fora do escopo:** download, armazenamento no Google Drive e indexação no Vector Store.

