# Worker de Teste - Telegram → Groq → DOCX

Versão 13.0.0.

Correção principal:
- melhora processamento de múltiplos vídeos enviados ao mesmo tempo.
- rota `/process-source` agora roda em thread separada no FastAPI, evitando travar todas as requisições quando uma conversão/transcrição está em andamento.

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

## Health

Abra:

```txt
/health
```

Precisa mostrar:

```json
{"version": "13.0.0", "output_format": "docx", "concurrency_fix": true}
```
