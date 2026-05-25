# Worker de Teste - Telegram → Groq → DOCX Rápido

Versão 15.0.0.

Modo rápido:
- transcreve com Groq Whisper
- gera DOCX imediatamente
- não usa IA extra para organizar
- divide em HOOK / BODY / CTA por posição do texto
- muito mais rápido que a versão com análise inteligente

Observação:
- A estrutura Hook/Body/CTA é aproximada.
- Para máxima precisão de copy, use a versão inteligente.
- Para velocidade, use esta.

## Health

Abra:

```txt
/health
```

Precisa mostrar:

```json
{"version": "15.0.0", "output_format": "docx", "fast_mode": true}
```
