# OCR and document-intelligence boundary

## Ownership

`fe-reader` should own the document evidence pipeline:

1. detect media type and hash bytes;
2. extract born-digital text first;
3. assess page extraction quality;
4. render and OCR only pages/regions that need it;
5. preserve page geometry, reading order, tables, model/runtime/version/license, confidence, and warnings;
6. emit `DocumentBundle` and text blobs by stable ID.

`nlp-policy-nz` consumes `DocumentBundle` and emits evidence-anchored `DocumentSignal` records. Signals are candidates or observations; they do not autonomously certify legal outcomes.

## Important safeguards

- OCR text is stored separately from process events.
- Every segment has a source/page digest and geometry.
- Model and runtime versions are recorded for reproducibility.
- Māori language and mixed-language handling is evaluated explicitly.
- Sensitive or personal material defaults to restricted/needs-review.
- The public dashboard receives a privacy projection, not raw OCR output.
