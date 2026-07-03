#!/usr/bin/env node

/**
 * Document Validator — legal-nz
 * 
 * Validates documents in the legal-nz knowledge base against defined quality standards.
 * Checks: formatting, citations, metadata, and structure.
 * 
 * Usage: node scripts/validate-documents.js [path]
 */

const fs = require('fs');
const path = require('path');

// --- Configuration ---
const WARN = 'WARN';
const ERROR = 'ERROR';
const PASS = 'PASS';

const NZ_CITATION_PATTERN = /\[\d{4}\]\s+(NZHC|NZCA|NZSC|NZLR|NZFLR|NZCCLR|NZBORR|NZEnvC|NZEmpC|NZFC|NZDC)\s+\d+/g;

const REQUIRED_DOC_METADATA = ['title', 'source', 'date', 'jurisdiction'];
const VALID_JURISDICTIONS = ['nz', 'NZ', 'New Zealand'];

let totalChecks = 0;
let passedChecks = 0;
let failures = [];

function check(condition, message, severity = WARN) {
  totalChecks++;
  if (condition) {
    passedChecks++;
    console.log(`  ${PASS} ${message}`);
  } else {
    failures.push({ severity, message });
    console.log(`  ${severity} ${message}`);
  }
}

function validateFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (!['.md', '.json', '.yaml', '.yml'].includes(ext)) return;

  console.log(`\n📄 ${path.relative(process.cwd(), filePath)}`);

  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    if (ext === '.md') {
      validateMarkdown(filePath, content, lines);
    } else if (ext === '.json') {
      validateJSON(filePath, content);
    }
  } catch (err) {
    check(false, `Cannot read file: ${err.message}`, ERROR);
  }
}

function validateMarkdown(filePath, content, lines) {
  // Check for required metadata (look for top-level heading)
  const hasTitle = lines.some(l => l.startsWith('# '));
  check(hasTitle, 'Document has a title (H1 heading)', ERROR);

  // Check for NZ legal citations
  const citations = content.match(NZ_CITATION_PATTERN);
  if (citations) {
    check(true, `Contains ${citations.length} NZ legal citation(s)`);
  } else {
    check(content.includes('[1]') || content.includes('(') && content.includes(')'),
      'No NZ citations found — acceptable if document is not a legal reference');
  }

  // Check line length (markdown body)
  const longLines = lines.filter(l => l.length > 120 && !l.startsWith('|') && !l.startsWith('```'));
  check(longLines.length === 0, `No lines exceed 120 chars (found ${longLines.length} long line(s))`, WARN);

  // Check for trailing whitespace
  const trailing = lines.filter(l => l !== l.trimEnd());
  check(trailing.length === 0, `No trailing whitespace (${trailing.length} line(s) affected)`, WARN);
}

function validateJSON(filePath, content) {
  try {
    const data = JSON.parse(content);
    check(true, 'JSON is syntactically valid', ERROR);

    // Check for required metadata if it looks like a document
    if (typeof data === 'object' && data !== null) {
      const missingMeta = REQUIRED_DOC_METADATA.filter(f => !(f in data));
      check(missingMeta.length === 0,
        missingMeta.length > 0
          ? `Missing metadata fields: ${missingMeta.join(', ')}`
          : 'All required metadata fields present',
        missingMeta.length > 0 ? ERROR : PASS);

      if (data.jurisdiction) {
        check(VALID_JURISDICTIONS.includes(data.jurisdiction),
          `Jurisdiction "${data.jurisdiction}" is a valid NZ jurisdiction`,
          ERROR);
      }
    }
  } catch (e) {
    check(false, `Invalid JSON: ${e.message}`, ERROR);
  }
}

function walkDirectory(dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
        walkDirectory(fullPath);
      }
    } else {
      validateFile(fullPath);
    }
  }
}

// --- Main ---
console.log('═══════════════════════════════════════════');
console.log('  legal-nz Document Validator');
console.log('═══════════════════════════════════════════');

const startPath = process.argv[2] || '.';
const targetPath = path.resolve(startPath);

if (fs.statSync(targetPath).isDirectory()) {
  walkDirectory(targetPath);
} else {
  validateFile(targetPath);
}

// --- Summary ---
console.log('\n═══════════════════════════════════════════');
console.log('  Validation Summary');
console.log('═══════════════════════════════════════════');
console.log(`  Total checks: ${totalChecks}`);
console.log(`  Passed:       ${passedChecks}`);
console.log(`  Failures:     ${failures.length}`);

const errors = failures.filter(f => f.severity === ERROR);
const warnings = failures.filter(f => f.severity === WARN);
if (errors.length > 0) {
  console.log(`  ⛔ Errors:     ${errors.length}`);
}
if (warnings.length > 0) {
  console.log(`  ⚠️  Warnings:   ${warnings.length}`);
}

console.log('═══════════════════════════════════════════\n');

// Exit with error code if any ERROR-level failures
process.exit(errors.length > 0 ? 1 : 0);
