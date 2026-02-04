import requests
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

class IFPBCrawlerUnificado:

    def __init__(self):
        self.base_url = "https://www.ifpb.edu.br"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
        })

        self.ano_urls = {
            2016: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2016/ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2016/resolucoes-aprovadas-pelo-colegiado'
            },
            2017: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2017/ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2017/resolucoes-aprovadas-pelo-colegiado'
            },
            2018: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2018/ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2018/resolucoes-aprovadas-pelo-colegiado'
            },
            2019: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2019/resolucoes-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2019/resolucoes-aprovadas-pelo-colegiado'
            },
            2020: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2020/aprovadas-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2020/aprovadas-pelo-colegiado'
            },
            2021: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2021/resolucoes-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2021/resolucoes-aprovadas-pelo-colegiado'
            },
            2022: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2022/resolucoes-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2022/resolucoes-aprovadas-pelo-colegiado'
            },
            2023: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2023/resolucoes-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2023/resolucoes-aprovadas-pelo-colegiado'
            },
            2024: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2024/resolucoes-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2024/resolucoes-aprovadas-pelo-colegiado'
            },
            2025: {
                'ad_referendum': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2025/resolucoes-ad-referendum',
                'aprovadas': 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2025/resolucoes-aprovadas-pelo-colegiado'
            }
        }

        self.url_cache = {}

    def verificar_url_pdf(self, url):
        if url in self.url_cache:
            return self.url_cache[url]

        try:
            r = self.session.head(url, timeout=10, allow_redirects=True)
            if r.status_code == 200 and 'pdf' in r.headers.get('content-type', '').lower():
                self.url_cache[url] = True
                return True

            headers = {'Range': 'bytes=0-4'}
            r = self.session.get(url, headers=headers, timeout=10)
            ok = r.content[:4] == b'%PDF'
            self.url_cache[url] = ok
            return ok
        except:
            self.url_cache[url] = False
            return False

    def buscar_resolucoes_2009_2015(self, ano):
        base = f"{self.base_url}/orgaoscolegiados/consuper/resolucoes/{ano}"
        resolucoes = []

        estimativas = {
            2009: 65, 2010: 113, 2011: 102, 2012: 153,
            2013: 196, 2014: 259, 2015: 236
        }

        max_resolutions = estimativas.get(ano, 100)

        for num in range(1, max_resolutions + 1):
            patterns = [
                f"{base}/resolucao-no-{num:02d}/@@download/file",
                f"{base}/resolucao-no-{num:03d}/@@download/file",
                f"{base}/resolucao-no-{num}/@@download/file",
                f"{base}/resolucao-{num:02d}/@@download/file",
                f"{base}/resolucao-{num}/@@download/file",
                f"{base}/resolucao-no-{num:02d}.pdf",
                f"{base}/resolucao-no-{num}.pdf",
            ]

            for url in patterns:
                if self.verificar_url_pdf(url):
                    resolucoes.append({
                        'ano': ano,
                        'numero': str(num),
                        'categoria': 'padrao',
                        'titulo': f"Resolução Nº {num}/{ano}",
                        'url_download': url
                    })
                    break

            time.sleep(0.1)

        return resolucoes

    def extrair_links_da_pagina(self, url, ano, categoria):
        try:
            html = self.session.get(url, timeout=30).text
        except:
            return []

        resolucoes = []

        padrao_paginas = r'href=["\']([^"\']*/resolucao[^"\']*/\d{1,4})["\']'
        paginas = re.findall(padrao_paginas, html, re.IGNORECASE)

        for pagina_rel in paginas[:100]:
            pagina_abs = urljoin(url, pagina_rel)
            num_match = re.search(r'resolucao[_-](?:no-|n-|)(\d{1,4})', pagina_abs, re.IGNORECASE)
            if not num_match:
                continue

            numero = num_match.group(1)
            url_download = f"{pagina_abs}/@@download/file"

            if self.verificar_url_pdf(url_download):
                resolucoes.append({
                    'ano': ano,
                    'numero': numero,
                    'categoria': categoria,
                    'titulo': f"Resolução Nº {numero} ({categoria} {ano})",
                    'url_download': url_download
                })

        padrao_pdfs = r'href=["\']([^"\']*\.pdf)["\']'
        pdfs = re.findall(padrao_pdfs, html, re.IGNORECASE)

        for pdf_rel in pdfs[:50]:
            if 'resolucao' in pdf_rel.lower() and str(ano) in pdf_rel:
                pdf_abs = urljoin(url, pdf_rel)
                num_match = re.search(r'resolucao[_-](?:no-|n-|)(\d{1,4})', pdf_rel, re.IGNORECASE)
                numero = num_match.group(1) if num_match else "0"

                if self.verificar_url_pdf(pdf_abs):
                    resolucoes.append({
                        'ano': ano,
                        'numero': numero,
                        'categoria': categoria,
                        'titulo': f"Resolução Nº {numero} ({categoria} {ano})",
                        'url_download': pdf_abs
                    })

        unicas = {}
        for r in resolucoes:
            unicas[r['url_download']] = r

        return list(unicas.values())

    def buscar_por_padroes_2022_2025(self, url_base, ano, categoria):
        resolucoes = []
        max_scan = 400 if ano >= 2023 else 300

        if categoria == 'ad_referendum':
            padroes = [
                lambda n: f"{url_base}/resolucao-{n:03d}/@@download/file",
                lambda n: f"{url_base}/resolucao-{n:04d}/@@download/file",
                lambda n: f"{url_base}/resolucao-no-{n:03d}/@@download/file",
                lambda n: f"{url_base}/resolucao-no-{n:04d}/@@download/file",
                lambda n: f"{url_base}/resolucao-n-{n:03d}/@@download/file",
                lambda n: f"{url_base}/resolucao-{n:02d}/@@download/file",
                lambda n: f"{url_base}/resolucao-no-{n:02d}/@@download/file",
                lambda n: f"{url_base}/resolucao-{n}/@@download/file",
                lambda n: f"{url_base}/resolucao-no-{n}/@@download/file",
            ]
        else:
            padroes = [
                lambda n: f"{url_base}/resolucao-no-{n:02d}/@@download/file",
                lambda n: f"{url_base}/resolucao-{n:02d}/@@download/file",
                lambda n: f"{url_base}/resolucao-no-{n}/@@download/file",
            ]

        def testar(num):
            for gerar in padroes:
                url = gerar(num)
                if self.verificar_url_pdf(url):
                    return num, url
            return None

        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(testar, n) for n in range(1, max_scan + 1)]
            for f in as_completed(futures):
                if f.result():
                    num, url = f.result()
                    resolucoes.append({
                        'ano': ano,
                        'numero': str(num),
                        'categoria': categoria,
                        'titulo': f"Resolução Nº {num} ({categoria} {ano})",
                        'url_download': url
                    })

        return resolucoes

    def buscar_resolucoes_2016_2025(self, ano):
        todas = []

        for categoria, url in self.ano_urls[ano].items():
            res_pagina = self.extrair_links_da_pagina(url, ano, categoria)

            if (ano >= 2022 and categoria == 'ad_referendum') or len(res_pagina) < 5:
                res_padroes = self.buscar_por_padroes_2022_2025(url, ano, categoria)
            else:
                res_padroes = []

            urls = {}
            for r in res_pagina + res_padroes:
                urls[r['url_download']] = r

            todas.extend(sorted(urls.values(), key=lambda x: int(x['numero']) if x['numero'].isdigit() else 0))
            time.sleep(1)

        return todas

    def baixar_pdf(self, resolucao, output_base='pdfs_ifpb_completos'):
        ano = resolucao['ano']
        categoria = resolucao['categoria']
        cat_dir = categoria.replace('-', '_')
        output_dir = os.path.join(output_base, str(ano), cat_dir)
        os.makedirs(output_dir, exist_ok=True)

        numero = resolucao['numero'].zfill(4)
        filename = f"{ano}_{cat_dir}_{numero}.pdf"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            return

        r = self.session.get(resolucao['url_download'], timeout=60)
        if r.content[:4] != b'%PDF':
            return

        with open(filepath, 'wb') as f:
            f.write(r.content)

    def processar_ano(self, ano):
        if 2009 <= ano <= 2015:
            resolucoes = self.buscar_resolucoes_2009_2015(ano)
        else:
            resolucoes = self.buscar_resolucoes_2016_2025(ano)

        with ThreadPoolExecutor(max_workers=5) as ex:
            for res in resolucoes:
                ex.submit(self.baixar_pdf, res)

    def executar(self):
        for ano in range(2009, 2026):
            print(f"Processando {ano}")
            self.processar_ano(ano)
            time.sleep(5)

if __name__ == "__main__":
    IFPBCrawlerUnificado().executar()
