# socio-lit-studio

Sosyoloji ve yakın alanlarda **makale tarama**, **dergi eşleştirme** ve **araştırma taslağı** üreten yardımcı program.

Kaynak havuzu: [OpenAlex](https://openalex.org) (ücretsiz akademik grafik). Anahtar gerekmez; nezaket için e-posta önerilir.

## Bu ne yapar, ne yapmaz

Yapar:
- Anahtar kelime ve cümlelerle makale arar
- Sosyoloji + yakın dergileri (kaynak / journal) puanlar
- Boşluk notu çıkarır (gap: literatürde az işlenen kesişim)
- Gerçek özetlerden literatür taslağı ve IMRaD iskeleti üretir
- BibTeX dışa aktarır

Yapmaz:
- Sahte veri, sahte anket, sahte bulgu
- Uydurma kaynak
- Dergiye gönderilmeye hazır nihaî makale iddiası

Program **asistan**. Yöntem, veri ve argüman sana ait. Her DOI kontrol edilmeli.

## Kurulum

```bash
git clone https://github.com/ferhadbey/socio-lit-studio.git
cd socio-lit-studio
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env
```

`.env` içine `OPENALEX_MAILTO=sen@eposta.com` yaz.

## Kullanım

`queries/example.yaml` dosyasını kendi anahtarlarınla düzenle.

```bash
# Makale + dergi tarama
socio-lit scan --query queries/example.yaml --out outputs/scan.json

# Dergi önerisi
socio-lit journals --query queries/example.yaml --out outputs/journals.json

# Taslak (yalnızca bulunan kaynaklara dayanır)
socio-lit draft --query queries/example.yaml --scan outputs/scan.json --out outputs/draft.md

# Kaynakça
socio-lit bibtex --scan outputs/scan.json --out outputs/refs.bib
```

İsteğe bağlı: `XAI_API_KEY` varsa taslak dilini Grok ile düzeltir; yoksa şablonla yazar. Anahtar yokken de tarama çalışır.
