import re
import unicodedata
from collections import Counter
from pathlib import Path


def extract(path: str) -> str:
    """Extract and clean text from a PDF or EPUB file."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        raw = _extract_pdf(path)
    elif suffix == ".epub":
        raw = _extract_epub(path)
    else:
        raise ValueError(f"Unsupported file type: '{suffix}'. Use .pdf or .epub.")
    return _clean_text(raw)


def _extract_pdf(path: str) -> str:
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber is required: pip install pdfplumber")

    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                pages.append(text)

    if not pages:
        raise ValueError(
            f"No extractable text found in '{path}'. "
            "The PDF may be scanned/image-based."
        )
    return "\n\n".join(pages)


def _extract_epub(path: str) -> str:
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "ebooklib and beautifulsoup4 are required: "
            "pip install ebooklib beautifulsoup4"
        )

    book = epub.read_epub(path)
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html = item.get_content().decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        # Drop script/style noise
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        if text.strip():
            chapters.append(text)

    if not chapters:
        raise ValueError(f"No readable content found in '{path}'.")
    return "\n\n\n".join(chapters)


def _clean_text(text: str) -> str:
    # Normalize Unicode (handles ligatures, non-breaking spaces, etc.)
    text = unicodedata.normalize("NFKC", text)

    lines = text.splitlines()

    # Count frequency of short lines to identify repeated headers/footers
    short_lines = [ln.strip() for ln in lines if 0 < len(ln.strip()) <= 60]
    freq = Counter(short_lines)
    repeated = {ln for ln, count in freq.items() if count >= 5}

    cleaned = []
    for line in lines:
        stripped = line.strip()

        # Drop standalone page numbers (bare integers, possibly with whitespace)
        if re.fullmatch(r"\d{1,4}", stripped):
            continue

        # Drop repeated headers/footers
        if stripped in repeated:
            continue

        cleaned.append(stripped)

    # Collapse runs of 3+ blank lines into 2 blank lines
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned))

    return result.strip()
