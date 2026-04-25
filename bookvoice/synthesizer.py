import asyncio
import os
import tempfile

import edge_tts


async def synthesize_chunk(text: str, voice: str, output_path: str) -> None:
    """Convert a single text chunk to an MP3 file using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def synthesize_chunks(chunks: list, voice: str, tmp_dir: str, progress_bar=None) -> list:
    """
    Synthesize a list of text chunks to individual MP3 files.

    Returns a list of file paths in chunk order.
    """
    paths = []
    for i, chunk in enumerate(chunks):
        out_path = os.path.join(tmp_dir, f"chunk_{i:04d}.mp3")
        asyncio.run(synthesize_chunk(chunk, voice, out_path))
        paths.append(out_path)
        if progress_bar is not None:
            progress_bar.update(1)
    return paths


def get_tmp_dir() -> str:
    """Create and return a temporary directory for intermediate MP3 chunks."""
    return tempfile.mkdtemp(prefix="bookvoice_")
