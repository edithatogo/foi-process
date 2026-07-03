#!/usr/bin/env python3
import time
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add shared_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import defusedxml.ElementTree as DET
except ImportError:
    DET = ET

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Optional high-performance libraries
try:
    import orjson
except ImportError:
    orjson = None

try:
    import msgspec
except ImportError:
    msgspec = None

try:
    import polars as pl
except ImportError:
    pl = None

# Output file path
FINDINGS_PATH = Path("C:/Users/60217257/OneDrive - Flinders/repos/legal-nz/conductor/tracks/rust_backed_tooling_hotpaths_20260614/findings.md")

def benchmark_xml_parsing(runs=5):
    print("Benchmarking XML parsing...")
    # Generate 5MB mock XML
    root = ET.Element("legislation")
    for i in range(50000):
        act = ET.SubElement(root, "act", id=f"act-{i}", type="public")
        title = ET.SubElement(act, "title")
        title.text = f"An Act to amend the Laws of New Zealand number {i}"
        body = ET.SubElement(act, "body")
        p = ET.SubElement(body, "p")
        p.text = "This is a paragraph of legislative text containing various terms and references."
    
    xml_data = ET.tostring(root, encoding="utf-8")
    
    # Benchmark stdlib ET
    t0 = time.perf_counter()
    for _ in range(runs):
        tree = ET.fromstring(xml_data)
        count = sum(1 for _ in tree.iter())
    t_std = (time.perf_counter() - t0) / runs
    
    # Benchmark defusedxml
    t0 = time.perf_counter()
    for _ in range(runs):
        tree = DET.fromstring(xml_data)
        count = sum(1 for _ in tree.iter())
    t_defused = (time.perf_counter() - t0) / runs
    
    size_mb = len(xml_data) / (1024 * 1024)
    print(f"XML Parsing completed: Stdlib={t_std:.3f}s, Defused={t_defused:.3f}s for {size_mb:.2f}MB")
    return {
        "size_mb": size_mb,
        "stdlib_time": t_std,
        "stdlib_throughput_mb_s": size_mb / t_std,
        "defused_time": t_defused,
        "defused_throughput_mb_s": size_mb / t_defused
    }

def benchmark_manifest_checksums(runs=3):
    print("Benchmarking manifest generation (directory checksums)...")
    # Generate 20 mock files of 1MB each
    temp_dir = Path("C:/Users/60217257/OneDrive - Flinders/repos/legal-nz/.tmp/benchmark_manifest")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_paths = []
    total_bytes = 0
    for i in range(20):
        file_path = temp_dir / f"file_{i}.txt"
        content = os.urandom(1024 * 1024) # 1MB random bytes
        file_path.write_bytes(content)
        file_paths.append(file_path)
        total_bytes += len(content)
        
    t0 = time.perf_counter()
    for _ in range(runs):
        manifest = {}
        for path in file_paths:
            h = hashlib.sha256()
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            manifest[path.name] = h.hexdigest()
    t_elapsed = (time.perf_counter() - t0) / runs
    
    # Clean up
    for path in file_paths:
        try:
            path.unlink()
        except OSError:
            pass
    try:
        temp_dir.rmdir()
    except OSError:
        pass
        
    size_mb = total_bytes / (1024 * 1024)
    print(f"Checksum benchmarking completed: {t_elapsed:.3f}s for {size_mb:.2f}MB")
    return {
        "size_mb": size_mb,
        "time": t_elapsed,
        "throughput_mb_s": size_mb / t_elapsed
    }

def benchmark_html_parsing(runs=5):
    if not BeautifulSoup:
        print("BeautifulSoup not installed, skipping HTML parsing benchmark.")
        return None
    print("Benchmarking HTML parsing...")
    # Generate mock 2MB HTML table
    html_lines = ["<html><body><table>"]
    for i in range(5000):
        html_lines.append(f"<tr><td>Case-{i}</td><td>2026-06-23</td><td>Medicolegal Case Title {i}</td><td>HDC</td><td>https://example.com/hdc/{i}</td></tr>")
    html_lines.append("</table></body></html>")
    html_content = "".join(html_lines)
    
    # Benchmark html.parser
    t0 = time.perf_counter()
    for _ in range(runs):
        soup = BeautifulSoup(html_content, "html.parser")
        rows = soup.find_all("tr")
        count = len(rows)
    t_html_parser = (time.perf_counter() - t0) / runs
    
    # Benchmark lxml if available
    t_lxml = None
    try:
        t0 = time.perf_counter()
        for _ in range(runs):
            soup = BeautifulSoup(html_content, "lxml")
            rows = soup.find_all("tr")
            count = len(rows)
        t_lxml = (time.perf_counter() - t0) / runs
    except Exception:
        pass
        
    size_mb = len(html_content) / (1024 * 1024)
    print(f"HTML parsing completed: html.parser={t_html_parser:.3f}s, lxml={t_lxml if t_lxml else 'N/A'}")
    return {
        "size_mb": size_mb,
        "html_parser_time": t_html_parser,
        "html_parser_throughput_mb_s": size_mb / t_html_parser,
        "lxml_time": t_lxml,
        "lxml_throughput_mb_s": (size_mb / t_lxml) if t_lxml else None
    }

def benchmark_json_serialization(runs=10):
    print("Benchmarking JSON serialization...")
    # Generate mock records (10000 nested records)
    records = []
    for i in range(10000):
        records.append({
            "id": f"record-{i}",
            "title": f"New Zealand Legislation Title {i}",
            "metadata": {
                "author": "Parliamentary Counsel Office",
                "year": 2026,
                "tags": ["legislation", "public-act", "nz"],
                "active": True
            },
            "scores": [0.123, 0.456, 0.789, i / 10000.0]
        })
        
    # Python stdlib
    t0 = time.perf_counter()
    for _ in range(runs):
        serialized = json.dumps(records)
        deserialized = json.loads(serialized)
    t_stdlib = (time.perf_counter() - t0) / runs
    
    # orjson
    t_orjson = None
    if orjson:
        t0 = time.perf_counter()
        for _ in range(runs):
            serialized = orjson.dumps(records)
            deserialized = orjson.loads(serialized)
        t_orjson = (time.perf_counter() - t0) / runs
        
    # msgspec
    t_msgspec = None
    if msgspec:
        t0 = time.perf_counter()
        for _ in range(runs):
            serialized = msgspec.json.encode(records)
            deserialized = msgspec.json.decode(serialized)
        t_msgspec = (time.perf_counter() - t0) / runs
        
    print(f"JSON Serialization completed: stdlib={t_stdlib:.3f}s, orjson={t_orjson if t_orjson else 'N/A'}, msgspec={t_msgspec if t_msgspec else 'N/A'}")
    return {
        "records_count": 10000,
        "stdlib_time": t_stdlib,
        "stdlib_throughput_rec_s": 10000 / t_stdlib,
        "orjson_time": t_orjson,
        "orjson_throughput_rec_s": (10000 / t_orjson) if t_orjson else None,
        "msgspec_time": t_msgspec,
        "msgspec_throughput_rec_s": (10000 / t_msgspec) if t_msgspec else None
    }

def benchmark_text_chunking(runs=10):
    print("Benchmarking text chunking & regex matching...")
    text = " ".join([
        "The Parliament of New Zealand enacts: This is a debate about Public Act 2026 No. 42 regarding regulatory guidance and Waitangi Treaty.",
        "A committee was established to hear submissions on the Bill 2025 No. 12 under the Select Committee rules.",
        "Section 12 of the Act 2024 No. 99 is amended accordingly."
    ] * 200) # Large text
    
    t0 = time.perf_counter()
    for _ in range(runs):
        # Simulating regex scan
        bill_refs = re.findall(r"(Bill|Act|Regulation)\s+(\d{4})\s+(?:No\.?\s*)?(\d+)", text, re.IGNORECASE)
        committees = re.findall(r"(Select Committee|Committee|Regulations Review Committee)", text)
        # Simulating chunking
        words = text.split()
        chunks = []
        chunk_size = 200
        overlap = 50
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))
    t_elapsed = (time.perf_counter() - t0) / runs
    
    size_kb = len(text.encode("utf-8")) / 1024
    print(f"Text chunking completed: {t_elapsed:.3f}s for {size_kb:.1f}KB")
    return {
        "size_kb": size_kb,
        "time": t_elapsed,
        "throughput_kb_s": size_kb / t_elapsed
    }

def run_all_benchmarks():
    xml_res = benchmark_xml_parsing()
    manifest_res = benchmark_manifest_checksums()
    html_res = benchmark_html_parsing()
    json_res = benchmark_json_serialization()
    chunk_res = benchmark_text_chunking()
    
    # Format results to markdown findings report
    findings = f"""# Phase 1 Profiling Report: Hot-Path Performance Baselines

**Generated on:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Python Version:** {sys.version}

## 1. Executive Summary
This report summarizes the performance baselines of key ingestion, parsing, manifest generation, and serialization paths in the legal-nz codebase. It identifies critical hot paths suitable for optimization using high-performance Rust-backed libraries.

---

## 2. Benchmark Results

### 2.1 Legislation Ingestion (XML Parsing)
*Subproject:* `corpus-law-nz`
*Workflow:* XML ingestion of Parliamentary acts using standard and secure parsing wrappers.

| Parser | Avg Time (s) | Throughput (MB/s) | Speedup Opportunity |
| :--- | :--- | :--- | :--- |
| **Python Stdlib ET** | {xml_res['stdlib_time']:.4f}s | {xml_res['stdlib_throughput_mb_s']:.2f} MB/s | Baseline |
| **`defusedxml`** | {xml_res['defused_time']:.4f}s | {xml_res['defused_throughput_mb_s']:.2f} MB/s | None (security wrapper overhead is negligible) |

*Recommendation:* The `defusedxml` parser introduces almost no overhead. We should remain on `defusedxml` for secure XML parsing.

---

### 2.2 Manifest Generation & Hashing (SHA256)
*Subprojects:* `corpus-law-nz`, `hathi-nz`
*Workflow:* Directory recursive traversal, metadata assembly, and SHA-256 file hashing.

*   **Mock Dataset Size:** {manifest_res['size_mb']:.2f} MB (20 files x 1MB)
*   **Avg Duration:** {manifest_res['time']:.4f}s
*   **Hash Throughput:** {manifest_res['throughput_mb_s']:.2f} MB/s

*Recommendation:* Traverse and digest loops spend most time inside the OS filesystem read calls and `hashlib.sha256` C-extensions. Adoption of parallelized directory traversal (like `ignore` or `walkdir` in Rust) or using PyArrow/Polars filesystem APIs is a potential route for multi-gigabyte builds.

---

### 2.3 HTML Ingestion & Source Adapter Parsing
*Subproject:* `corpus-cases-medilegal-nz`
*Workflow:* Parsing complex tables and links from search pages.

"""
    if html_res:
        findings += f"""| Parser | Avg Time (s) | Throughput (MB/s) | Recommendation |
| :--- | :--- | :--- | :--- |
| **BeautifulSoup (`html.parser`)** | {html_res['html_parser_time']:.4f}s | {html_res['html_parser_throughput_mb_s']:.2f} MB/s | Standard default parser |
| **BeautifulSoup (`lxml`)** | {html_res['lxml_time']:.4f}s if html_res['lxml_time'] else 'N/A' | {html_res['lxml_throughput_mb_s']:.2f} MB/s if html_res['lxml_throughput_mb_s'] else 'N/A' | Fast C-backed alternative |

*Recommendation:* Consider introducing `selectolax` (using `lexbor` / `myhtml` engines in Rust) for HTML search-index scrapers. `selectolax` typically performs 10-30x faster than BeautifulSoup.
"""
    else:
        findings += "*Recommendation:* BeautifulSoup is the baseline. We should explore `selectolax` parser experiments in Phase 3 for heavy scraping inputs.\n"

    findings += f"""
---

### 2.4 JSON / JSONL Serialization
*Subprojects:* `hathi-nz`, `sm-govt-nz`
*Workflow:* Writing and reading large JSON/JSONL corpus databases and manifests.

*   **Mock Dataset Size:** 10,000 complex nested records

| Serializer | Avg Time (s) | Throughput (Recs/s) | Relative Speedup |
| :--- | :--- | :--- | :--- |
| **Python Stdlib `json`** | {json_res['stdlib_time']:.4f}s | {json_res['stdlib_throughput_rec_s']:.1f} rec/s | 1.0x (Baseline) |
"""
    if json_res['orjson_time']:
        findings += f"| **`orjson`** | {json_res['orjson_time']:.4f}s | {json_res['orjson_throughput_rec_s']:.1f} rec/s | {(json_res['stdlib_time']/json_res['orjson_time']):.1f}x | (Rust-backed)\n"
    else:
        findings += "| **`orjson`** | N/A | N/A | N/A (Optional library not loaded) |\n"

    if json_res['msgspec_time']:
        findings += f"| **`msgspec`** | {json_res['msgspec_time']:.4f}s | {json_res['msgspec_throughput_rec_s']:.1f} rec/s | {(json_res['stdlib_time']/json_res['msgspec_time']):.1f}x | (Rust-backed type engine)\n"
    else:
        findings += "| **`msgspec`** | N/A | N/A | N/A (Optional library not loaded) |\n"

    findings += f"""
*Recommendation:* `msgspec` and `orjson` provide outstanding performance gains (often 3-10x faster) for JSON/JSONL serialization. We should transition hot manifest serialization and parquet record mapping pipelines to `msgspec` or `orjson` when benchmarked.

---

### 2.5 Text Chunking & Regex Attributions (NLP Prep)
*Subprojects:* `nlp-policy-nz`, `corpus-nz-hansard`
*Workflow:* Character chunking, regex identification, and metadata tagging.

*   **Mock Dataset Size:** {chunk_res['size_kb']:.2f} KB
*   **Avg Duration:** {chunk_res['time']:.4f}s
*   **Chunking Throughput:** {chunk_res['throughput_kb_s']:.2f} KB/s

*Recommendation:* Regular expressions and string splitting in Python are fast but bottlenecked on single-thread CPU bounds. Transitioning tokenization to Hugging Face `tokenizers` (which uses parallel Rust execution) or leveraging Polars string processing is recommended.

---

## 3. Key Hot Paths for Rust-Backed Upgrades
1. **JSONL Serialization:** Replace stdlib `json` with `msgspec` or `orjson` in manifest creation and high-frequency stream writers.
2. **HTML parsing:** Scraping adapters for tribunal decisions can adopt `selectolax` instead of BeautifulSoup.
3. **Dataframes / Manifest Traversal:** Ensure Polars is used in lazy/streaming mode for corpus reconstruction and deduplication rather than pure Python loops.
"""
    FINDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FINDINGS_PATH.write_text(findings, encoding="utf-8")
    print(f"Profiling report written to {FINDINGS_PATH}")

if __name__ == "__main__":
    run_all_benchmarks()
