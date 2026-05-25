import os
import re
import json
import shutil
import tempfile
import time
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs

import requests
import gdown
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from groq import Groq

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE


VERSION = "15.0.0"

app = FastAPI(title="Worker Telegram → Groq → DOCX", version=VERSION)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_TRANSCRIPTION_MODEL = os.getenv("GROQ_TRANSCRIPTION_MODEL", "whisper-large-v3-turbo")
GROQ_TRANSLATION_MODEL = os.getenv("GROQ_TRANSLATION_MODEL", "llama-3.3-70b-versatile")
MAX_AUDIO_MB = int(os.getenv("MAX_AUDIO_MB", "24"))
TARGET_AUDIO_BITRATE = os.getenv("TARGET_AUDIO_BITRATE", "24k")
TARGET_AUDIO_FORMAT = os.getenv("TARGET_AUDIO_FORMAT", "mp3")
TRANSLATION_CHUNK_CHARS = int(os.getenv("TRANSLATION_CHUNK_CHARS", "3000"))
TRANSLATION_DELAY_SECONDS = int(os.getenv("TRANSLATION_DELAY_SECONDS", "12"))
TRANSLATION_RETRY_WAIT_SECONDS = int(os.getenv("TRANSLATION_RETRY_WAIT_SECONDS", "70"))
INCLUDE_ORIGINAL_FOR_NON_PT = os.getenv("INCLUDE_ORIGINAL_FOR_NON_PT", "true").lower() in {"1", "true", "yes", "sim"}

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "version": VERSION,
            "error": str(exc),
            "type": exc.__class__.__name__,
        },
    )


@app.get("/")
def root():
    return {
        "ok": True,
        "service": "transcritor-groq-worker-teste",
        "version": VERSION,
        "output_format": "docx",
        "copy_structure": "hook_body_cta_fast",
        "fast_mode": true,
        "routes": ["/health", "/process-source", "/process-telegram-media"],
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "version": VERSION,
        "groq_key_configured": bool(GROQ_API_KEY),
        "telegram_token_configured": bool(TELEGRAM_BOT_TOKEN),
        "transcription_model": GROQ_TRANSCRIPTION_MODEL,
        "translation_model": GROQ_TRANSLATION_MODEL,
        "translation_chunk_chars": TRANSLATION_CHUNK_CHARS,
        "translation_delay_seconds": TRANSLATION_DELAY_SECONDS,
        "output_format": "docx",
        "copy_structure": "hook_body_cta_fast",
        "fast_mode": true,
        "include_original_for_non_pt": INCLUDE_ORIGINAL_FOR_NON_PT,
    }


def run_cmd(cmd: List[str]):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Erro no comando: {' '.join(cmd)}\nSTDERR:\n{result.stderr}")
    return result


def safe_filename(name: str, fallback: str = "arquivo") -> str:
    name = name or fallback
    name = re.sub(r"[^\w\-. ]+", "_", name, flags=re.UNICODE).strip()
    return name[:120] or fallback


def download_url(url: str, output_path: Path):
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def extract_google_drive_file_id(url: str) -> Optional[str]:
    if "drive.google.com" not in url:
        return None

    m = re.search(r"/file/d/([^/]+)", url)
    if m:
        return m.group(1)

    qs = parse_qs(urlparse(url).query)
    if "id" in qs:
        return qs["id"][0]

    return None


def download_google_drive_or_url(url: str, output_path: Path):
    file_id = extract_google_drive_file_id(url)

    if file_id:
        gdown_url = f"https://drive.google.com/uc?id={file_id}"
        result = gdown.download(gdown_url, str(output_path), quiet=False, fuzzy=True)
        if not result or not output_path.exists() or output_path.stat().st_size < 1024:
            raise RuntimeError(
                "Não consegui baixar o arquivo do Google Drive. "
                "Confirme que está em 'Qualquer pessoa com o link pode visualizar'."
            )
        return

    download_url(url, output_path)
    if not output_path.exists() or output_path.stat().st_size < 1024:
        raise RuntimeError("Download falhou ou retornou arquivo vazio.")


def download_telegram_file(file_id: str, output_path: Path):
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não configurado no Railway de teste.")

    info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    info = requests.get(info_url, params={"file_id": file_id}, timeout=60).json()

    if not info.get("ok"):
        raise RuntimeError(f"Telegram getFile falhou: {info}")

    file_path = info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    download_url(file_url, output_path)


def convert_to_audio(input_path: Path, output_path: Path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-b:a", TARGET_AUDIO_BITRATE,
        str(output_path),
    ]
    run_cmd(cmd)


def file_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def split_audio(input_audio: Path, chunks_dir: Path, chunk_seconds: int = 600) -> List[Path]:
    chunks_dir.mkdir(parents=True, exist_ok=True)
    pattern = chunks_dir / f"chunk_%03d.{TARGET_AUDIO_FORMAT}"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_audio),
        "-f", "segment",
        "-segment_time", str(chunk_seconds),
        "-c", "copy",
        str(pattern),
    ]
    run_cmd(cmd)
    return sorted(chunks_dir.glob(f"chunk_*.{TARGET_AUDIO_FORMAT}"))


def transcribe_one(audio_path: Path) -> Dict[str, Any]:
    if not client:
        raise RuntimeError("GROQ_API_KEY não configurada no Railway.")

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(audio_path.name, f.read()),
            model=GROQ_TRANSCRIPTION_MODEL,
            response_format="verbose_json",
            temperature=0,
        )

    if hasattr(result, "model_dump"):
        return result.model_dump()

    if isinstance(result, dict):
        return result

    return json.loads(result.json())


def transcribe_audio(audio_path: Path, workdir: Path) -> Dict[str, Any]:
    if file_mb(audio_path) <= MAX_AUDIO_MB:
        return transcribe_one(audio_path)

    chunks = split_audio(audio_path, workdir / "chunks", chunk_seconds=600)
    all_text = []
    language = None

    for index, chunk in enumerate(chunks, start=1):
        print(f"Transcrevendo chunk {index}/{len(chunks)}: {chunk.name}")
        res = transcribe_one(chunk)

        if not language:
            language = res.get("language")

        text = res.get("text", "")
        if text:
            all_text.append(text.strip())

    return {
        "text": "\n\n".join(all_text).strip(),
        "language": language,
    }


def is_portuguese_language(language: Optional[str]) -> bool:
    if not language:
        return False
    lang = str(language).lower().strip()
    return lang in {"pt", "por", "portuguese", "português", "portugues", "pt-br", "pt_br"} or "portugu" in lang


def split_text_for_llm(text: str, max_chars: int) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    parts = []
    current = []
    current_len = 0

    for paragraph in paragraphs:
        chunks = [paragraph[i:i + max_chars] for i in range(0, len(paragraph), max_chars)] if len(paragraph) > max_chars else [paragraph]

        for chunk in chunks:
            if current and current_len + len(chunk) + 1 > max_chars:
                parts.append("\n".join(current).strip())
                current = []
                current_len = 0

            current.append(chunk)
            current_len += len(chunk) + 1

    if current:
        parts.append("\n".join(current).strip())

    return [p for p in parts if p]


def run_llm_with_retry(prompt: str, index: int, total: int) -> str:
    if not client:
        raise RuntimeError("GROQ_API_KEY não configurada no Railway.")

    last_error = None

    for attempt in range(1, 6):
        try:
            completion = client.chat.completions.create(
                model=GROQ_TRANSLATION_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você organiza transcrições de anúncios, VSLs e cartas de vendas com fidelidade, sem reescrever criativamente.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            return completion.choices[0].message.content.strip()

        except Exception as exc:
            last_error = exc
            error_text = str(exc)

            if (
                "rate_limit_exceeded" in error_text
                or "Request too large" in error_text
                or "tokens per minute" in error_text
                or "TPM" in error_text
                or "Rate limit" in error_text
            ):
                print(f"Rate limit no bloco {index}/{total}. Tentativa {attempt}/5. Esperando {TRANSLATION_RETRY_WAIT_SECONDS}s.")
                time.sleep(TRANSLATION_RETRY_WAIT_SECONDS)
                continue

            raise

    raise RuntimeError(f"Falha ao processar bloco {index}/{total}: {last_error}")



def prepare_structured_text(text: str, source_is_portuguese: bool) -> str:
    """
    Modo rápido: não usa LLM depois da transcrição.
    Para ganhar velocidade, só limpa timestamps simples e divide o texto em HOOK/BODY/CTA por posição.
    Não traduz. Para idioma estrangeiro, retorna a transcrição original estruturada rapidamente.
    """
    text = (text or "").strip()
    if not text:
        return "HOOK:\n[não identificado]\n\nBODY:\n[não identificado]\n\nCTA:\n[não identificado]"

    # Remove timestamps comuns se aparecerem: [00:01], 00:01, 00:01:20
    text = re.sub(r"\[?\b\d{1,2}:\d{2}(?::\d{2})?\b\]?", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Quebra em frases, preservando a ordem.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        sentences = [text]

    n = len(sentences)

    if n <= 3:
        hook = sentences[:1]
        body = sentences[1:2] if n >= 2 else []
        cta = sentences[2:] if n >= 3 else []
    else:
        hook_end = max(1, round(n * 0.18))
        cta_start = max(hook_end + 1, round(n * 0.82))
        hook = sentences[:hook_end]
        body = sentences[hook_end:cta_start]
        cta = sentences[cta_start:]

    if not body:
        body = ["[não identificado neste trecho]"]
    if not cta:
        cta = ["[não identificado neste trecho]"]

    return (
        "HOOK:\n" + " ".join(hook).strip() +
        "\n\nBODY:\n" + " ".join(body).strip() +
        "\n\nCTA:\n" + " ".join(cta).strip()
    )


def parse_hook_body_cta(structured_text: str) -> Dict[str, List[str]]:
    sections = {"HOOK": [], "BODY": [], "CTA": []}
    current = "BODY"

    for raw_line in structured_text.splitlines():
        line = raw_line.strip()
        upper = line.upper().strip()

        if upper in {"HOOK", "HOOK:"}:
            current = "HOOK"
            continue
        if upper in {"BODY", "BODY:"}:
            current = "BODY"
            continue
        if upper in {"CTA", "CTA:"}:
            current = "CTA"
            continue

        if line:
            sections[current].append(line)

    return sections


def setup_docx_styles(doc: Document):
    styles = doc.styles

    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(11)

    for style_name in ["Title", "Heading 1", "Heading 2"]:
        style = styles[style_name]
        style.font.name = "Arial"

    styles["Title"].font.size = Pt(20)
    styles["Title"].font.bold = True

    styles["Heading 1"].font.size = Pt(16)
    styles["Heading 1"].font.bold = True
    styles["Heading 1"].font.color.rgb = RGBColor(0, 0, 0)

    styles["Heading 2"].font.size = Pt(13)
    styles["Heading 2"].font.bold = True
    styles["Heading 2"].font.color.rgb = RGBColor(0, 0, 0)


def add_paragraphs(doc: Document, lines: List[str]):
    text = "\n".join(lines).strip()
    if not text:
        text = "[não identificado neste trecho]"

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    for paragraph_text in paragraphs:
        p = doc.add_paragraph(style="Normal")
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(paragraph_text)


def create_docx(original_name: str, transcription: Dict[str, Any], structured_text: str, output_path: Path, include_original: bool):
    doc = Document()
    setup_docx_styles(doc)

    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Transcrição - Estrutura Rápida da Copy")

    meta = doc.add_paragraph(style="Normal")
    meta.add_run("Arquivo: ").bold = True
    meta.add_run(original_name)

    meta2 = doc.add_paragraph(style="Normal")
    meta2.add_run("Idioma detectado: ").bold = True
    meta2.add_run(str(transcription.get("language") or "não identificado"))

    doc.add_paragraph("")

    sections = parse_hook_body_cta(structured_text)

    for heading in ["HOOK", "BODY", "CTA"]:
        doc.add_heading(heading, level=1)
        add_paragraphs(doc, sections.get(heading, []))

    if include_original:
        original_text = transcription.get("text", "") or ""
        if original_text.strip():
            doc.add_page_break()
            doc.add_heading("TRANSCRIÇÃO ORIGINAL", level=1)
            for p_text in [x.strip() for x in original_text.split("\n\n") if x.strip()]:
                p = doc.add_paragraph(style="Normal")
                p.paragraph_format.space_after = Pt(8)
                p.paragraph_format.line_spacing = 1.15
                p.add_run(p_text)

    doc.save(output_path)


def process_file(input_path: Path, original_name: str, workdir: Path) -> Path:
    audio_path = workdir / f"audio_convertido.{TARGET_AUDIO_FORMAT}"
    convert_to_audio(input_path, audio_path)

    transcription = transcribe_audio(audio_path, workdir)
    source_is_portuguese = is_portuguese_language(transcription.get("language"))

    structured_text = prepare_structured_text(
        transcription.get("text", ""),
        source_is_portuguese=source_is_portuguese,
    )

    include_original = False

    output_name = safe_filename(Path(original_name).stem or "transcricao") + "_hook_body_cta.docx"
    output_path = workdir / output_name
    create_docx(original_name, transcription, structured_text, output_path, include_original=include_original)
    return output_path


def persistent_file_response(output_path: Path) -> FileResponse:
    final_path = Path(tempfile.gettempdir()) / output_path.name
    shutil.copy(output_path, final_path)
    return FileResponse(
        final_path,
        filename=output_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.post("/process-telegram-media")
async def process_telegram_media(request: Request, file: Optional[UploadFile] = File(default=None)):
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)

        if file is None:
            body = await request.body()
            if not body:
                raise HTTPException(status_code=400, detail="Nenhum arquivo recebido.")
            original_name = request.headers.get("x-file-name", "arquivo_telegram")
            input_path = workdir / safe_filename(original_name, "input.bin")
            input_path.write_bytes(body)
        else:
            original_name = request.headers.get("x-file-name", file.filename or "arquivo_telegram")
            input_path = workdir / safe_filename(original_name, "input.bin")
            with open(input_path, "wb") as f:
                f.write(await file.read())

        output_path = process_file(input_path, original_name, workdir)
        return persistent_file_response(output_path)


@app.post("/process-source")
async def process_source(payload: Dict[str, Any]):
    source_type = payload.get("sourceType")
    original_name = payload.get("fileName") or "arquivo"

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        input_path = workdir / safe_filename(original_name, "input.bin")

        if source_type == "url":
            url = payload.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="URL não enviada.")
            download_google_drive_or_url(url, input_path)

        elif source_type == "telegram_file_id":
            file_id = payload.get("fileId")
            if not file_id:
                raise HTTPException(status_code=400, detail="fileId do Telegram não enviado.")
            download_telegram_file(file_id, input_path)

        else:
            raise HTTPException(status_code=400, detail="Envie arquivo ou link público.")

        output_path = process_file(input_path, original_name, workdir)
        return persistent_file_response(output_path)
