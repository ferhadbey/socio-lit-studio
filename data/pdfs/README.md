# Yerel PDF klasoru

Kendi hard diskindeki makaleleri buraya kopyala (`*.pdf`).

```bash
socio-lit ingest --pdf-dir data/pdfs --out outputs/local.json
```

Bu klasordeki PDF'ler `.gitignore` ile tutulur. Public GitHub'a telifli makale yukleme.
Program yalnizca burada gercekten bulunan dosyalari okur; eksik kucuk veya DOI uydurmaz.
