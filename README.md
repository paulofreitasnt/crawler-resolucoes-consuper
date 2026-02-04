# Crawler de Resoluções (CONSUPER)

Este repositório contém crawlers desenvolvidos para coletar e organizar resoluções publicadas no site do IFPB.

## Descrição

Coletores em Python que baixam PDFs de resoluções e os organizam na pasta `pdfs_ifpb_completos/` por ano e tipo (padrão, ad_referendum, aprovadas, etc.).

## Motivação

O site alvo não segue um padrão consistente para as páginas de publicações. Por isso foi necessário desenvolver um crawler específico — `crawler-ad-referendum.py` — para lidar com as variações e exceções encontradas nas resoluções *ad referendum*.

## Conteúdo principal

- `crawler-geral.py`: Crawler geral para resoluções com estrutura mais padronizada.
- `crawler-ad-referendum.py`: Crawler especializado para resoluções *ad referendum* (tratamento de padronizações inconsistentes).
- `pdfs_ifpb_completos/`: Diretório onde os PDFs baixados são armazenados, organizado por ano.
- `myenv/`: Ambiente virtual usado no desenvolvimento (opcional — pode usar seu próprio ambiente).

## Requisitos

- Python 3.10+ (recomendado 3.13).
- Dependências: `requests`, `beautifulsoup4` e outras bibliotecas usuais para scraping. Se preferir, ative o ambiente virtual `myenv` fornecido.

## Uso

1. (Opcional) Ativar o ambiente virtual incluído:

```bash
source myenv/bin/activate
```

2. Executar o crawler geral:

```bash
python crawler-geral.py
```

3. Executar o crawler específico para *ad referendum*:

```bash
python crawler-ad-referendum.py
```

## Saída

Os PDFs são salvos em `pdfs_ifpb_completos/` organizados por ano e subpastas indicativas (por exemplo `ad_referendum/` e `aprovadas/`).

## Observações técnicas

- O `crawler-ad-referendum.py` contém lógica adicional para lidar com páginas que fogem do padrão (seletores diferentes, links em formatos variados e metadados inconsistentes).
- Em caso de falhas por mudanças no site, verifique os seletores e atualize os tratamentos de exceção no crawler.

## Contribuições

Contribuições são bem-vindas. Abra uma *issue* para discutir mudanças maiores antes de submeter um *pull request*.