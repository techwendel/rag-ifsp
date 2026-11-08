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

## 6. Fluxo principal — Catalogação bem-sucedida

**FP01 — Iniciar catalogação**

1. O usuário acessa a interface da extensão.
2. O usuário solicita o início da catalogação.
3. O sistema identifica os endereços institucionais configurados como pontos de partida.
4. O sistema acessa as páginas elegíveis e identifica seus links.
5. O sistema percorre os links institucionais permitidos, respeitando os limites configurados de rastreamento.
6. O sistema identifica referências a documentos PDF.
7. O sistema registra os documentos identificados, evitando referências duplicadas conforme suas regras de catalogação.
8. O sistema disponibiliza o catálogo resultante para utilização posterior.

**Pós-condição de sucesso:** um catálogo de referências documentais foi produzido.

**Observação:** a identificação e a catalogação não implicam o download dos arquivos PDF.

