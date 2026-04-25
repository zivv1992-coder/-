#!/usr/bin/env python3
import click
from tqdm import tqdm

from bookvoice.extractor import extract
from bookvoice.chunker import chunk_text
from bookvoice.synthesizer import synthesize_chunks, get_tmp_dir
from bookvoice.merger import merge_mp3s, cleanup_tmp_dir

VOICE_DEFAULTS = {
    "en": "en-US-GuyNeural",
    "he": "he-IL-AvriNeural",
}

VOICE_OPTIONS = {
    "en": ["en-US-GuyNeural", "en-GB-SoniaNeural"],
    "he": ["he-IL-AvriNeural", "he-IL-HilaNeural"],
}


@click.command()
@click.option("--input", "-i", "input_path", required=True,
              help="Path to the PDF or EPUB file.")
@click.option("--output", "-o", "output_path", required=True,
              help="Output MP3 file path.")
@click.option("--language", "-l",
              type=click.Choice(["en", "he"]), default="en", show_default=True,
              help="Book language.")
@click.option("--voice", "-v", default=None,
              help="Voice name override. Defaults by language.")
@click.option("--chunk-size", default=8000, show_default=True,
              help="Max characters per audio chunk.")
def main(input_path, output_path, language, voice, chunk_size):
    """BookVoice: convert a PDF or EPUB book into an MP3 audiobook."""
    if voice is None:
        voice = VOICE_DEFAULTS[language]

    if voice not in VOICE_OPTIONS[language]:
        available = ", ".join(VOICE_OPTIONS[language])
        raise click.BadParameter(
            f"Voice '{voice}' not available for language '{language}'. "
            f"Choose from: {available}"
        )

    click.echo(f"Reading: {input_path}")
    text = extract(input_path)

    chunks = chunk_text(text, max_size=chunk_size)
    click.echo(f"Extracted {len(text):,} characters → {len(chunks)} chunks.")
    click.echo(f"Voice: {voice}")

    tmp_dir = get_tmp_dir()
    try:
        with tqdm(total=len(chunks), desc="Synthesizing", unit="chunk") as bar:
            chunk_paths = synthesize_chunks(chunks, voice, tmp_dir, progress_bar=bar)

        click.echo(f"Merging {len(chunk_paths)} audio chunks...")
        merge_mp3s(chunk_paths, output_path)
    finally:
        cleanup_tmp_dir(tmp_dir)

    click.echo(f"Done! Audiobook saved to: {output_path}")


if __name__ == "__main__":
    main()
