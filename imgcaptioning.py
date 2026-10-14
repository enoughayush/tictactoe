"""Generate natural-language captions for images with a pretrained BLIP model.

Install dependencies with:
    py -m pip install torch transformers pillow

Usage:
    python imgcaptioning.py path/to/photo.jpg
    python imgcaptioning.py photo1.jpg photo2.png --max-new-tokens 40
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

try:
    import torch
    from PIL import Image, UnidentifiedImageError
    from transformers import BlipForConditionalGeneration, BlipProcessor
except ImportError as exc:
    missing_package = getattr(exc, "name", None) or "a required package"
    raise SystemExit(
        f"Missing dependency: {missing_package}. Install the requirements with:\n"
        "  py -m pip install torch transformers pillow"
    ) from exc

DEFAULT_MODEL = "Salesforce/blip-image-captioning-base"


def load_model(model_name: str, device_name: str | None = None):
    """Load the pretrained captioning model and its image/text processor."""
    if device_name:
        device = torch.device(device_name)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    processor = BlipProcessor.from_pretrained(model_name)
    model = BlipForConditionalGeneration.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return processor, model, device


def caption_image(
    image_path: Path,
    processor: BlipProcessor,
    model: BlipForConditionalGeneration,
    device: torch.device,
    max_new_tokens: int = 40,
) -> str:
    """Return a generated caption for one image."""
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"Cannot open image '{image_path}': {exc}") from exc

    inputs = processor(images=image, return_tensors="pt")
    inputs = {name: value.to(device) for name, value in inputs.items()}
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
        )
    return processor.decode(output[0], skip_special_tokens=True).strip()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate captions for images with a pretrained BLIP transformer."
    )
    parser.add_argument("images", nargs="+", type=Path, help="Image file(s) to caption")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Hugging Face model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--device",
        choices=("cpu", "cuda"),
        help="Inference device (default: CUDA when available, otherwise CPU)",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=40,
        help="Maximum number of new tokens in each caption (default: 40)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.max_new_tokens < 1:
        print("Error: --max-new-tokens must be at least 1.", file=sys.stderr)
        return 2
    if args.device == "cuda" and not torch.cuda.is_available():
        print("Error: CUDA was requested, but no CUDA device is available.", file=sys.stderr)
        return 2

    missing = [str(path) for path in args.images if not path.is_file()]
    if missing:
        for path in missing:
            print(f"Error: image file not found: {path}", file=sys.stderr)
        return 2

    try:
        processor, model, device = load_model(args.model, args.device)
    except Exception as exc:
        print(
            f"Error loading model '{args.model}': {exc}\n"
            "Check your network connection the first time you run this; model files "
            "are downloaded from Hugging Face and cached for later use.",
            file=sys.stderr,
        )
        return 1

    failed = False
    for image_path in args.images:
        try:
            caption = caption_image(
                image_path, processor, model, device, args.max_new_tokens
            )
            print(f"{image_path}: {caption}")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())



