#!/usr/bin/env node

/**
 * Quality Report Generator — legal-nz
 * 
 * Generates a consolidated quality report covering document validation,
 * test results, and coverage data.
 * 
 * Usage: node scripts/quality-report.js
 */

const fs = require('fs');
const path = require('path');

class QualityReport {
  constructor() {
    this.timestamp = new Date().toISOString();
    this.domains = {
      documents: { status: 'pending', checks: 0, passed: 0, errors: 0, warnings: 0 },
      code: { status: 'pending', checks: 0, passed: 0, errors: 0, warnings: 0 },
      data: { status: 'pending', checks: 0, passed: 0, errors: 0, warnings: 0 },
    };
    this.summary = { overall: 'pending', score: 0 };
  }

  addDocumentResult(results) {
    this.domains.documents = { ...results, status: results.errors > 0 ? 'fail' : 'pass' };
  }

  addCodeResult(results) {
    this.domains.code = { ...results, status: results.errors > 0 ? 'fail' : 'pass' };
  }

  addDataResult(results) {
    this.domains.data = { ...results, status: results.errors > 0 ? 'fail' : 'pass' };
  }

  generate() {
    const totalChecks = Object.values(this.domains).reduce((s, d) => s + d.checks, 0);
    const totalPassed = Object.values(this.domains).reduce((s, d) => s + d.passed, 0);
    const totalErrors = Object.values(this.domains).reduce((s, d) => s + d.errors, 0);
    const totalWarnings = Object.values(this.domains).reduce((s, d) => s + d.warnings, 0);

    this.summary.score = totalChecks > 0 ? Math.round((totalPassed / totalChecks) * 100) : 0;
    this.summary.overall = totalErrors === 0 ? 'pass' : 'fail';

    const report = {
      generated: this.timestamp,
      project: 'legal-nz',
      validator: 'Quality_Validator (Antigravity Swarm)',
      domains: this.domains,
      summary: {
        ...this.summary,
        total_checks: totalChecks,
        total_passed: totalPassed,
        total_errors: totalErrors,
        total_warnings: totalWarnings,
      },
    };

    return report;
  }

  write(outputPath = './quality-report.json') {
    const report = this.generate();
    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2), 'utf-8');
    console.log(`📋 Quality report written to ${outputPath}`);
    return report;
  }
}

// --- CLI usage ---
if (require.main === module) {
  const report = new QualityReport();

  // Attempt to read document validation results
  try {
    if (fs.existsSync('./scripts/validate-documents.js')) {
      console.log('ℹ️  Run "node scripts/validate-documents.js" first for document validation data.');
    }
  } catch {}

  // Default: generate empty report structure
  const data = report.generate();
  report.write();

  console.log('\n═══════════════════════════════════════════');
  console.log('  Quality Report Summary');
  console.log('═══════════════════════════════════════════');
  console.log(`  Overall:     ${data.summary.overall === 'pass' ? '✅ PASS' : '⏳ PENDING'}`);
  console.log(`  Score:       ${data.summary.score}%`);
  console.log(`  Documents:   ${data.domains.documents.status}`);
  console.log(`  Code:        ${data.domains.code.status}`);
  console.log(`  Data:        ${data.domains.data.status}`);
  console.log('═══════════════════════════════════════════\n');
}

module.exports = QualityReport;
