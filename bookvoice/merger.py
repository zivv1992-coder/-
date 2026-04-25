import os
import shutil


def merge_mp3s(chunk_paths: list, output_path: str) -> None:
    """Merge a list of MP3 files into a single output MP3 using pydub."""
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub is required: pip install pydub")

    if not chunk_paths:
        raise ValueError("No audio chunks to merge.")

    combined = AudioSegment.empty()
    for path in chunk_paths:
        segment = AudioSegment.from_mp3(path)
        combined += segment

    combined.export(output_path, format="mp3")


def cleanup_tmp_dir(tmp_dir: str) -> None:
    """Remove the temporary directory and all chunk files."""
    shutil.rmtree(tmp_dir, ignore_errors=True)
