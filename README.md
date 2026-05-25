# Worker de Teste - v18 Tradução Rápida Corrigida

Versão 18.0.0.

Correção:
- Corrige erro `clean_transcript_text is not defined` da v17.
- Mantém tradução/adaptação rápida para áudio em inglês/outros idiomas.
- Português continua rápido.

## Variável nova

```txt
FAST_TRANSLATION_MODEL=llama-3.1-8b-instant
```

Mantenha:

```txt
GROQ_TRANSLATION_MODEL=llama-3.3-70b-versatile
```

## Saída para criativos curtos

```txt
HOOK
BODY
CTA
TRANSCRIÇÃO LIMPA COMPLETA
```

## Saída para VSL / copy longa

```txt
ABERTURA / HOOK
PROBLEMA / DOR
PROMESSA / TRANSFORMAÇÃO
MECANISMO / SOLUÇÃO
PROVAS / AUTORIDADE
OFERTA / BENEFÍCIO CENTRAL
OBJEÇÕES / GARANTIA / RISCO
CTA / FECHAMENTO
TRANSCRIÇÃO LIMPA COMPLETA
```

## Health

Precisa mostrar:

```json
{
  "version": "18.0.0",
  "fast_translation": true,
  "fast_translation_model": "llama-3.1-8b-instant"
}
```
