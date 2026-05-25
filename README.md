# Worker de Teste - v19 Cópia Crua + Tradução

Versão 19.0.0.

Objetivo:
- Não separar em Hook, Body, CTA, Promessa, Oferta etc.
- Apenas transcrever/traduzir e diagramar em parágrafos legíveis.
- Português continua rápido.
- Inglês/outros idiomas são traduzidos/adaptados para PT-BR e a transcrição original vai ao final.

## Saída

```txt
CÓPIA DIAGRAMADA
```

ou, se o áudio não for português:

```txt
CÓPIA TRADUZIDA E DIAGRAMADA EM PT-BR
TRANSCRIÇÃO ORIGINAL
```

## Variáveis novas

```txt
RAW_TRANSLATION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
TRANSLATE_NON_PT=true
PARAGRAPH_SENTENCES=2
PARAGRAPH_MAX_CHARS=650
```

Modelos para testar em `RAW_TRANSLATION_MODEL`:

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
  "version": "19.0.0",
  "raw_copy_mode": true,
  "raw_translation_model": "meta-llama/llama-4-scout-17b-16e-instruct"
}
```
