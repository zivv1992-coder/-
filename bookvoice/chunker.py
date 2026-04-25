import re


def chunk_text(text: str, max_size: int = 8000) -> list:
    """
    Split text into chunks no larger than max_size characters.

    Splits first on paragraph boundaries (double newlines), then on sentence
    boundaries if a paragraph is still too large, so TTS output sounds natural.
    """
    paragraphs = re.split(r"\n{2,}", text)
    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        segments = _split_paragraph(para, max_size)
        for seg in segments:
            if current_len + len(seg) + 1 > max_size and current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(seg)
            current_len += len(seg) + 1

    if current:
        chunks.append("\n\n".join(current))

    return [c for c in chunks if c.strip()]


def _split_paragraph(para: str, max_size: int) -> list:
    """Split a single paragraph into sentence-sized pieces if it exceeds max_size."""
    if len(para) <= max_size:
        return [para]

    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", para)
    pieces = []
    current = []
    current_len = 0

    for sentence in sentences:
        if current_len + len(sentence) + 1 > max_size and current:
            pieces.append(" ".join(current))
            current = []
            current_len = 0
        # If a single sentence is longer than max_size, hard-split it
        if len(sentence) > max_size:
            for i in range(0, len(sentence), max_size):
                pieces.append(sentence[i : i + max_size])
        else:
            current.append(sentence)
            current_len += len(sentence) + 1

    if current:
        pieces.append(" ".join(current))

    return pieces
