# Worker de Teste - Telegram → Groq → DOCX

Versão 12.0.0.

Gera arquivo DOCX editável para abrir no Google Docs.

Estrutura:

```txt
HOOK
BODY
CTA
```

Sem negrito automático.
Sem timestamps.
Sem duplicar transcrição original em áudio português.

## Health

Abra:

```txt
/health
```

Precisa mostrar:

```json
{"version": "12.0.0", "output_format": "docx"}
```
