# arXiv manuscript package

This directory contains the first submission-oriented manuscript for `foi-process`.
It is a software/resource paper, not a claim of full FYI archive coverage or statutory validation.

## Local build

From this directory, with a TeX installation available:

```text
make pdf
make source-package
```

The source package contains only the manuscript source and bibliography. Do not add raw requests,
attachments, OCR text, embeddings, tokens, or local absolute paths to the arXiv package.

## Review records

- `authentext-review.md` records the prose-quality pass and remaining human edits.
- `sourceright-review.json` records the source/provenance and rights checks applied to the manuscript.

These records are repository evidence and are not included in the arXiv upload archive.
