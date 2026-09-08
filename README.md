# socio-lit-studio

Sosyoloji ve yakin alanlarda makale tarama, dergi eslestirme ve arastirma **iskeleti**.

Kaynak havuzu: [OpenAlex](https://openalex.org) + senin lokal PDF klasorun.

## Sert kural

- Uydurma kaynak yok
- Uydurma metin ici referans yok
- Taslak, yalnizca `scan` ve `ingest` ile fiilen bulunan kayitlari kataloglar
- Katalogda yoksa atif dusulmez

## Bu ne yapmaz

Sahte veri, sahte bulgu, dergiye gonderilmeye hazir nihai makale, Grok ile kaynak uydurma.

## Kurulum

```bash
git clone https://github.com/ferhadbey/socio-lit-studio.git
cd socio-lit-studio
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env
```

`.env` icine `OPENALEX_MAILTO=sen@eposta.com` yaz.

## Lokal PDF

Public GitHub'a telifli makale yukleme. PDF'leri kendi diskinde tut:

1. Dosyalari `data/pdfs/` icine kopyala
2. `socio-lit ingest --pdf-dir data/pdfs --out outputs/local.json`

`*.pdf` gitignore'dadir. Repo sadece cikarilan ozet katalogunu (`outputs/local.json`) kullanir.

## Kullanim

```bash
socio-lit scan --query queries/example.yaml --out outputs/scan.json
socio-lit ingest --pdf-dir data/pdfs --out outputs/local.json
socio-lit journals --query queries/example.yaml --out outputs/journals.json
socio-lit draft --query queries/example.yaml --scan outputs/scan.json --local outputs/local.json --out outputs/draft.md
socio-lit bibtex --scan outputs/scan.json --local outputs/local.json --out outputs/refs.bib
```
