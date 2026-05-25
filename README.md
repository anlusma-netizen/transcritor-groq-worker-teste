# Worker de Teste - v17 Tradução Rápida

Versão 17.0.0.

Correção principal:
- Português continua rápido.
- Inglês/outros idiomas usam modelo rápido para tradução/adaptação PT-BR.
- Remove delay fixo entre blocos de tradução.
- Se o modelo rápido falhar, tenta fallback no modelo principal.

## Variável nova

```txt
FAST_TRANSLATION_MODEL=llama-3.1-8b-instant
```

Mantenha:

```txt
GROQ_TRANSLATION_MODEL=llama-3.3-70b-versatile
```

Assim o rápido traduz primeiro, e o 70B fica como reserva.

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
  "version": "17.0.0",
  "fast_translation": true,
  "fast_translation_model": "llama-3.1-8b-instant"
}
```
