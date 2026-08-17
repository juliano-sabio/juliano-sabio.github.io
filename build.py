"""Gera as duas saídas do portfólio a partir de portfolio.html.

  index.html    — página completa, imagens em img/. É esta que você hospeda.
  _artifact.html — fragmento com as imagens embutidas em base64, para publicar
                   como artifact (lá o CSP bloqueia arquivo externo).

Uso: python build.py
"""
import base64
import mimetypes
import pathlib
import re

AQUI = pathlib.Path(__file__).parent
FONTE = AQUI / 'portfolio.html'

TITULO = 'Juliano Sabio — Desenvolvedor mobile'
DESCRICAO = (
    'Desenvolvedor Flutter. Aplicativos que funcionam offline, '
    'com número que não pode errar.'
)


def embutir(html: str) -> str:
    """Troca src/poster="img/x" pelo data: URI correspondente.

    O artifact roda sob CSP que bloqueia arquivo externo, entao imagem e video
    precisam viajar dentro do proprio HTML."""
    def troca(m):
        atributo, rel = m.group(1), m.group(2)
        caminho = AQUI / rel
        if not caminho.exists():
            raise SystemExit(f'ERRO: arquivo nao encontrado: {caminho}')
        tipo = mimetypes.guess_type(caminho.name)[0] or 'application/octet-stream'
        dados = base64.b64encode(caminho.read_bytes()).decode('ascii')
        return f'{atributo}="data:{tipo};base64,{dados}"'
    return re.sub(r'\b(src|poster)="(img/[^"]+)"', troca, html)


def main():
    html = FONTE.read_text(encoding='utf-8')

    # 1. página completa, para hospedar
    pagina = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{DESCRICAO}">
<meta name="color-scheme" content="light dark">
<meta property="og:title" content="{TITULO}">
<meta property="og:description" content="{DESCRICAO}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>📱</text></svg>">
<style>*,*::before,*::after{{box-sizing:border-box}}body{{margin:0}}</style>
{html}
</body>
</html>
"""
    (AQUI / 'index.html').write_text(pagina, encoding='utf-8')

    # 2. fragmento com imagens embutidas, para o artifact
    (AQUI / '_artifact.html').write_text(embutir(html), encoding='utf-8')

    for nome in ('index.html', '_artifact.html'):
        kb = (AQUI / nome).stat().st_size // 1024
        print(f'  {nome}: {kb} KB')


if __name__ == '__main__':
    main()
