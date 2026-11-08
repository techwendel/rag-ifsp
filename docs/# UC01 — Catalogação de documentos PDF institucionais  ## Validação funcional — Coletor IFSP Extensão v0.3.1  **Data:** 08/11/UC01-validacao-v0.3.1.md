# UC01 — Catalogação de documentos PDF institucionais

## Validação funcional — Coletor IFSP Extensão v0.3.1

**Data:** 08/11/2026  
**Status:** Aprovado

### 1. Problema identificado

Durante os testes da versão v0.3.0, constatou-se que a página **Cursos 2025**, do portal IFSP Itaquaquecetuba, não era percorrida pelo coletor, embora estivesse acessível e contivesse documentos PDF.

A análise do arquivo `core.js` identificou uma restrição na função `scopeLink()`, responsável por determinar quais páginas são elegíveis para navegação.

### 2. Correção implementada

A versão v0.3.1 passou a reconhecer a estrutura de URL utilizada pela página Cursos 2025, preservando as restrições de navegação para outras áreas do portal.

### 3. Resultados dos testes

| Indicador | v0.3.0 | v0.3.1 | Variação |
|---|---:|---:|---:|
| Páginas percorridas | 16 | 17 | +1 |
| PDFs identificados | 89 | 97 | +8 |
| Outros links e arquivos | 17 | 18 | +1 |
| Páginas pendentes | 0 | 0 | 0 |

### 4. Validação dos catálogos

A comparação dos arquivos JSON confirmou:

- Inclusão da página Cursos 2025.
- Identificação de oito documentos PDF adicionais.
- Preservação dos 89 documentos anteriormente catalogados.
- Ausência de páginas pendentes ao final da execução.

### 5. Conclusão

A correção foi validada por meio de testes funcionais no navegador e comparação dos catálogos gerados.

A versão **v0.3.1 está aprovada para a funcionalidade de catalogação**, dentro do escopo testado.

A identificação de links PDF não garante que os arquivos possam ser baixados ou que estejam íntegros.

### 6. Próxima etapa — Download dos documentos

Verificar o funcionamento do mecanismo de download, utilizando o catálogo de 97 documentos PDF.

**Critérios de verificação:**
- Download efetivo dos arquivos.
- Identificação de falhas e links indisponíveis.
- Conferência da quantidade de arquivos obtidos.
- Verificação básica de integridade dos PDFs.
- Tratamento de erros sem interromper indevidamente a operação.
