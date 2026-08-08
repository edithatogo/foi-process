PYTHON ?= python
BUILD ?= build

.PHONY: pdf source-package clean

pdf:
	mkdir -p $(BUILD)
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory $(BUILD) foi-process.tex
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory $(BUILD) foi-process.tex

source-package:
	rm -rf $(BUILD)/arxiv-source
	mkdir -p $(BUILD)/arxiv-source
	cp foi-process.tex references.bib README.md $(BUILD)/arxiv-source/
	tar -czf $(BUILD)/foi-process-arxiv-source.tar.gz -C $(BUILD)/arxiv-source .
	sha256sum $(BUILD)/foi-process-arxiv-source.tar.gz > $(BUILD)/SHA256SUMS

clean:
	rm -rf $(BUILD)
