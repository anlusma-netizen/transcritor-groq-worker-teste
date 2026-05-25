# Worker de Teste - v20 Tradução para Análise PT-BR

Versão 20.0.0.

Objetivo:
- Cópia crua, sem Hook/Body/CTA.
- Parágrafos maiores e mais enxutos.
- Tradução adaptada para análise de copy em português brasileiro.
- Preserva intenção, promessa, agressividade, ordem das ideias, dados, nomes e termos sensíveis.
- Mantém transcrição original no final quando o áudio não for português.

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

## Modelos para testar em RAW_TRANSLATION_MODEL

```txt
meta-llama/llama-4-scout-17b-16e-instruct
llama-3.3-70b-versatile
openai/gpt-oss-20b
openai/gpt-oss-120b
```

## Health

Precisa mostrar:

```json
{
  "version": "20.0.0",
  "raw_copy_mode": true,
  "translation_style": "ptbr_copy_analysis"
}
```
