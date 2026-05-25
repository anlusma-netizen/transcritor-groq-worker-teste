# Worker de Teste - Telegram → Groq → DOCX

Versão 14.0.0.

Correção principal:
- fila controlada para múltiplos vídeos enviados ao mesmo tempo.
- por padrão processa 1 arquivo por vez (`MAX_CONCURRENT_JOBS=1`).
- evita travar o Railway e evita várias chamadas simultâneas na Groq.

Gera DOCX editável para abrir no Google Docs.

Estrutura:

```txt
HOOK
BODY
CTA
```

Sem negrito automático.
Sem timestamps.
Sem duplicar transcrição original em áudio português.

## Variável nova opcional

```txt
MAX_CONCURRENT_JOBS=1
```

Recomendado deixar 1. Depois podemos testar 2.

## Health

Abra:

```txt
/health
```

Precisa mostrar:

```json
{"version": "14.0.0", "output_format": "docx", "queue_control": true}
```
