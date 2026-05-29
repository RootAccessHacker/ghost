# Ghost

<img src="assets/logo.png" alt="logo" style="width:50%; height:auto;">

Ghost writes a copy of a PDF with metadata values removed.

The default output path is the original filename with `_SANITIZED` appended before the
`.pdf` extension.

## Metadata fields

Ghost removes values for the following common metadata fields:

* /Author
* /Producer
* /Title  
* /Subject
* /Creator
* /Keywords
* /CreationDate
* /ModDate
* /Trapped
* /PTEX.Fullbanner

Any other metadata keys found in the PDF are also blanked in the sanitized copy.

## Requirements

This project was written for Python 3.12 and uses `PyPDF2`.

Install dependencies with:

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```bash
python3 ghost.py path/to/file.pdf
```

Choose an explicit output path:

```bash
python3 ghost.py path/to/file.pdf --output path/to/clean.pdf
```

Print metadata before sanitizing:

```bash
python3 ghost.py path/to/file.pdf --verbose
```

Ghost will not overwrite an existing output file unless `--overwrite` is supplied.
