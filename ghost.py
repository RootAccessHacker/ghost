from __future__ import annotations

import argparse
import sys
from pathlib import Path


SENSITIVE_METADATA_KEYS = (
    "/Author",
    "/Producer",
    "/Title",
    "/Subject",
    "/Creator",
    "/Keywords",
    "/CreationDate",
    "/ModDate",
    "/Trapped",
    "/PTEX.Fullbanner",
)


class SanitizationError(Exception):
    """Raised when a PDF cannot be sanitized."""


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_SANITIZED{input_path.suffix}")


def sanitize_pdf(
    input_file: str | Path,
    output_file: str | Path | None = None,
    *,
    verbose: bool = False,
    overwrite: bool = False,
) -> Path:
    """Copy a PDF to a new file with metadata values removed."""
    input_path = Path(input_file)
    output_path = Path(output_file) if output_file else default_output_path(input_path)

    if not input_path.is_file():
        raise SanitizationError(f"The file '{input_path}' does not exist.")

    if input_path.suffix.lower() != ".pdf":
        raise SanitizationError(f"The file '{input_path}' is not a PDF.")

    if output_path.suffix.lower() != ".pdf":
        raise SanitizationError(f"The output file '{output_path}' must use a .pdf extension.")

    if input_path.resolve() == output_path.resolve(strict=False):
        raise SanitizationError("The output file must be different from the input file.")

    if output_path.exists() and not overwrite:
        raise SanitizationError(
            f"The output file '{output_path}' already exists. Use --overwrite to replace it."
        )

    try:
        from PyPDF2 import PdfReader, PdfWriter
        from PyPDF2.errors import PdfReadError
    except ImportError as exc:
        raise SanitizationError(
            "Missing dependency 'PyPDF2'. Install it with: python3 -m pip install -r requirements.txt"
        ) from exc

    try:
        print("[+]\tReading the PDF file...")
        with input_path.open("rb") as source:
            reader = PdfReader(source)

            if reader.is_encrypted:
                try:
                    decrypt_result = reader.decrypt("")
                except Exception as exc:  # PyPDF2 raises several encryption-specific exceptions.
                    raise SanitizationError(
                        "The PDF is encrypted and could not be opened with an empty password."
                    ) from exc

                if decrypt_result == 0:
                    raise SanitizationError(
                        "The PDF is encrypted and could not be opened with an empty password."
                    )

            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            sanitized_metadata = {key: "" for key in SENSITIVE_METADATA_KEYS}
            if reader.metadata:
                for key, value in reader.metadata.items():
                    if verbose:
                        print(f"[i]\t{key}: {value}")
                    sanitized_metadata[str(key)] = ""
            else:
                print("[i]\tNo metadata found to sanitize.")

            writer.add_metadata(sanitized_metadata)

            print(f"[+]\tWriting sanitized PDF to '{output_path}'")
            with output_path.open("wb") as target:
                writer.write(target)
    except PdfReadError as exc:
        raise SanitizationError(f"Could not read '{input_path}' as a valid PDF.") from exc
    except OSError as exc:
        raise SanitizationError(str(exc)) from exc

    print("[+]\tSanitization complete.")
    return output_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove metadata values from a PDF by writing a sanitized copy."
    )
    parser.add_argument("input_pdf", help="Path to the PDF to sanitize.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path for the sanitized PDF. Defaults to '<name>_SANITIZED.pdf'.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output file if it already exists.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print metadata keys and values before they are removed.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        sanitize_pdf(
            args.input_pdf,
            args.output,
            verbose=args.verbose,
            overwrite=args.overwrite,
        )
    except SanitizationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
