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

## 7. Fluxos alternativos e de exceção

### FA01 — Página sem documentos PDF

**Ponto de ocorrência:** etapa 6 do fluxo principal.

1. O sistema examina uma página elegível.
2. Nenhum link para documento PDF é identificado.
3. O sistema prossegue com as demais páginas elegíveis, quando houver.
4. A ausência de PDFs nessa página não é tratada como erro.

### FA02 — Referência duplicada

**Ponto de ocorrência:** etapa 7 do fluxo principal.

1. O sistema identifica uma URL de documento já registrada na catalogação.
2. O sistema reconhece a duplicidade conforme suas regras de comparação.
3. O sistema evita criar uma segunda entrada para a mesma referência.
4. A catalogação prossegue normalmente.

### FA03 — Limite de rastreamento atingido

**Ponto de ocorrência:** etapa 5 do fluxo principal.

1. O sistema atinge um dos limites configurados de rastreamento.
2. O sistema interrompe a expansão da coleta correspondente.
3. Os documentos identificados até aquele momento são preservados no catálogo.

### EX01 — Página inacessível

**Ponto de ocorrência:** etapa 4 do fluxo principal.

1. O sistema tenta acessar uma página institucional.
2. O acesso falha por indisponibilidade, erro de rede ou outra condição técnica.
3. O sistema registra a ocorrência, quando houver mecanismo de registro disponível.
4. O sistema prossegue com outras páginas elegíveis, sempre que possível.

### EX02 — Link inválido ou não processável

**Ponto de ocorrência:** etapas 4 a 6 do fluxo principal.

1. O sistema encontra um link inválido ou que não consegue processar.
2. O link é desconsiderado ou a falha é registrada, conforme as regras implementadas.
3. O sistema continua o processamento dos demais links.

**Nota de validação:** os comportamentos descritos constituem a especificação proposta. Sua correspondência com a implementação v0.3.0 deverá ser confirmada por inspeção do código e execução dos testes.

## 8. Regras de negócio e restrições operacionais

**RN01 — Escopo institucional**

O rastreamento deve considerar apenas páginas pertencentes aos endereços institucionais autorizados e às regras de escopo configuradas.

**RN02 — Pontos de partida**

A catalogação deve iniciar pelos endereços previamente configurados na extensão. Na versão 0.3.0, foram identificados cinco pontos de partida.

**RN03 — Profundidade de rastreamento**

A extensão deve respeitar o limite de profundidade configurado. Na versão 0.3.0, o limite identificado é de três níveis.

**RN04 — Quantidade máxima de páginas**

A extensão deve respeitar o limite máximo de páginas processadas. Na versão 0.3.0, o limite identificado é de 120 páginas.

**RN05 — Identificação de documentos**

A catalogação deve aplicar as regras de reconhecimento de links para documentos PDF implementadas no sistema.

**RN06 — Controle de duplicidade**

Uma mesma referência documental não deve produzir registros duplicados no catálogo, conforme os critérios de comparação de URLs adotados.

**RN07 — Separação entre catalogação e download**

A operação de catalogação não deve iniciar automaticamente o download dos arquivos identificados.

**RN08 — Preservação da origem**

Os registros catalogados devem permitir identificar o endereço de origem dos documentos, favorecendo sua rastreabilidade.

### Observação sobre a implementação

Os valores de profundidade e quantidade máxima de páginas correspondem à configuração identificada na versão 0.3.0.

As demais regras expressam comportamentos a serem confrontados com a implementação e os testes existentes. Esta especificação não constitui, isoladamente, evidência de conformidade.

