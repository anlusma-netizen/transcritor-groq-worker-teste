# Worker de Teste - v21 Tradução Universal para Análise PT-BR

Versão 21.0.0.

Objetivo:
- Cópia crua, sem Hook/Body/CTA.
- Tradução adaptada para análise em português brasileiro.
- Funciona para qualquer nicho: saúde, emagrecimento, diabetes, beleza, financeiro, sexualidade, negócios, espiritualidade, tecnologia etc.
- Preserva tom, intensidade, promessa, dados, provas, termos técnicos, termos sensíveis e ordem das ideias.
- Não censura, não suaviza, não resume e não moraliza.
- Parágrafos maiores e mais legíveis.

## Saída em português

```txt
CÓPIA DIAGRAMADA
```

## Saída em inglês/outros idiomas

```txt
CÓPIA TRADUZIDA PARA ANÁLISE EM PT-BR
TRANSCRIÇÃO ORIGINAL
```

## Variáveis recomendadas

```txt
RAW_TRANSLATION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
TRANSLATE_NON_PT=true
PARAGRAPH_SENTENCES=5
PARAGRAPH_MAX_CHARS=1400
```

## Health

Precisa mostrar:

```json
{
  "version": "21.0.0",
  "raw_copy_mode": true,
  "translation_style": "universal_ptbr_copy_analysis"
}
```
