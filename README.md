# Worker de Teste - v16 VSL + Tradução PT-BR

Versão 16.0.0.

Objetivo:
- Criativos curtos continuam rápidos.
- VSL/copy longa sai em formato de mapa de copy.
- Áudios em inglês/outros idiomas geram versão traduzida/adaptada em PT-BR.
- A transcrição original entra no final quando o áudio não for português.

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

Abra:

```txt
/health
```

Precisa mostrar:

```json
{
  "version": "16.0.0",
  "output_format": "docx",
  "vsl_mode": true,
  "translation_for_non_pt": true
}
```

## Observação

Português é processado rápido, sem etapa extra de tradução.
Áudio em inglês/outro idioma usa IA de texto para traduzir/adaptar, então demora mais.
