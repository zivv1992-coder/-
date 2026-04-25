#!/usr/bin/env python3
import click
from bookvoice.extractor import extract
from bookvoice.chunker import chunk_text

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
def main(input_path, output_path, language, voice):
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

    chunks = chunk_text(text)
    click.echo(f"Extracted {len(text):,} characters → {len(chunks)} chunks.")
    click.echo(f"Voice: {voice}")
    click.echo("\n--- Text preview (first 500 chars) ---")
    click.echo(text[:500])
    click.echo("--------------------------------------")
    click.echo("\nSynthesis not yet wired up. Next step: edge-tts integration.")


if __name__ == "__main__":
    main()
