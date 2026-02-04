import requests
import os
import re
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class IFPBCrawlerAdReferendum:

    def __init__(self):
        self.base_url = "https://www.ifpb.edu.br"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0'
        })

        self.paginas = {
            2022: 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2022/resolucoes-ad-referendum',
            2023: 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2023/resolucoes-ad-referendum',
            2024: 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2024/resolucoes-ad-referendum',
            2025: 'https://www.ifpb.edu.br/orgaoscolegiados/consuper/resolucoes/2025/resolucoes-ad-referendum'
        }

    def verificar_pdf(self, url):
        try:
            r = self.session.head(url, timeout=5, allow_redirects=True)
            return "pdf" in r.headers.get("content-type", "").lower()
        except:
            return False

    def buscar_intervalo(self, ano, max_num=150):
        base = self.paginas[ano]
        resolucoes = []

        for n in range(1, max_num + 1):
            for fmt in [f"{n:02d}", f"{n}"]:
                urls = [
                    f"{base}/resolucao-ar-no-{fmt}/@@download/file",
                    f"{base}/resolucao-no-{fmt}/@@download/file"
                ]

                for url in urls:
                    if self.verificar_pdf(url):
                        resolucoes.append((n, url))
                        break

        return resolucoes

    def baixar(self, ano, numero, url):
        pasta = f"pdfs_ifpb_completos/{ano}/ad_referendum"
        os.makedirs(pasta, exist_ok=True)

        nome = f"{ano}_ad_referendum_{str(numero).zfill(4)}.pdf"
        path = os.path.join(pasta, nome)

        if os.path.exists(path):
            return True

        r = self.session.get(url, timeout=20)
        if r.content[:4] != b"%PDF":
            return False

        with open(path, "wb") as f:
            f.write(r.content)

        return True

    def executar(self):
        for ano in self.paginas:
            print(f"\nAno {ano}")
            resolucoes = self.buscar_intervalo(ano)

            with ThreadPoolExecutor(max_workers=3) as ex:
                futures = [
                    ex.submit(self.baixar, ano, num, url)
                    for num, url in resolucoes
                ]
                for _ in as_completed(futures):
                    pass

            print(f"Total: {len(resolucoes)}")


if __name__ == "__main__":
    IFPBCrawlerAdReferendum().executar()
