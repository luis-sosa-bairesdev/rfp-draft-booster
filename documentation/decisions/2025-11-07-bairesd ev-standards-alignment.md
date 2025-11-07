---
title: "BairesDev Standards Alignment"
author: "AI Assistant"
date: "2025-11-07"
version: "1.0"
status: "Approved"
---

# BairesDev Standards Alignment

## Overview

This document records the adjustments made to align the RFP Draft Booster project with official BairesDev AI-powered development standards.

## Purpose

To ensure the project follows all corporate standards and best practices as defined in the official BairesDev code-rules and documents-rules examples.

## Context

After reviewing the official BairesDev examples in `/code-rules` and `/documents-rules`, several adjustments were identified to ensure 100% compliance with corporate standards.

## Changes Made

### 1. File Renaming

**Change:** Renamed `context/config.md` to `context/context.md`

**Reason:** BairesDev standards use `@context.md` as the reference for project configuration. This aligns with the convention used across all BairesDev projects.

**Impact:** All references to the config file updated in guidelines and copilot instructions.

### 2. Documentation Structure

**Added:**
- `documentation/` folder with subfolders:
  - `architecture/` - Architecture decisions and diagrams
  - `api/` - API documentation
  - `deployment/` - Deployment guides
  - `decisions/` - Technical decision records
- `document-template.mc` - Template for all technical documentation
- README files in each documentation subfolder

**Reason:** BairesDev standard requires all technical documentation to be stored in a centralized `documentation/` folder following a specific template.

**Impact:** Future technical docs will follow consistent structure.

### 3. Versioning and Changelog

**Added:**
- `VERSION` file with current version (0.1.0)
- `CHANGELOG.md` following Keep a Changelog format
- Semantic versioning requirements in basic-guidelines.mdc

**Reason:** BairesDev mandates Semantic Versioning 2.0.0 for all projects with proper changelog maintenance.

**Impact:** 
- Version tracking centralized
- All releases will be documented
- Clear version history for stakeholders

### 4. Basic Guidelines Enhancements

**Added to `.cursor/rules/basic-guidelines.mdc`:**

#### 4.1 Language Requirements Section
- Explicit requirement: All code, JSON, docs, and deliverables in ENGLISH
- Only user-facing UI may be in other languages if requested
- Use latest released language version when unclear

#### 4.2 JSON and API Responses Section
- JSON must use **snake_case** convention
- Objects designed to be reusable
- Avoid deeply nested structures

#### 4.3 Logging Standards Section
- **DEBUG as default logging level** (BairesDev standard)
- Clear explanation of all log levels
- Example code provided

#### 4.4 Versioning and Releases Section
- Semantic Versioning 2.0.0 mandatory
- CHANGELOG.md maintenance required
- Git tagging standards (v1.2.3 format)
- Version update checklist

#### 4.5 Documentation Requirements Section
- Technical docs in `documentation/` folder
- Use `document-template.mc`
- Review docs before new tasks
- Keep synchronized with code

**Impact:** Developers have clear, comprehensive standards to follow.

### 5. PRD Guidelines Enhancements

**Added to `.cursor/rules/prd-guidelines.mdc`:**

#### Core Rules Section
- One .md file per PRD/User Story in `/deliverables`
- No grouping of stories in single file
- Use PRD template mandatory
- Document version updates required
- Use @context.md before defining requirements

#### PRD Finalization Checklist
- Comprehensive checklist added
- Domain entity updates required
- Version number mandatory

**Impact:** PRD creation process more standardized and complete.

### 6. Domain Guidelines Enhancements

**Added to `.cursor/rules/domain-guidelines.mdc`:**

#### Purpose and Core Rules
- Explicit purpose statement
- Entity file naming conventions
- Missing information handling procedures
- Inconsistency marking standards

#### Automatic Domain Update Rule
- Mandatory workflow when PRD created
- 4-step update process defined
- Example provided

**Impact:** Domain entities automatically maintained with PRD changes.

### 7. Python Practices Enhancements

**Added to `.cursor/rules/python-practices.mdc`:**

#### Memory Management Section
- Profiling tools recommendations
- Generators and streaming guidance
- `__slots__` for memory optimization
- Caching strategies
- Parallel processing guidance
- NumPy GIL release tips

#### I/O-bound Operations Section
- Batching best practices
- Concurrent execution hierarchy (asyncio > ThreadPoolExecutor > threading)
- Request coalescing
- Error handling for batched operations

**Impact:** Performance-optimized code from the start.

### 8. Configuration Updates

**Changed in `src/config.py`:**
- `log_level` default changed from "INFO" to "DEBUG"

**Changed in `src/utils/logging_config.py`:**
- Updated docstring to reflect DEBUG default
- Fallback to DEBUG if no level specified

**Reason:** BairesDev standard mandates DEBUG as default logging level.

**Impact:** More verbose logging by default, easier debugging.

### 9. GitHub Copilot Instructions

**Updated `.github/copilot-instructions.md`:**
- Reference to `context/context.md` instead of config.md
- Note about one file per PRD/Story
- Reference to `documentation/` folder
- Semantic versioning mention
- JSON snake_case convention
- DEBUG logging default

**Impact:** Copilot users get same standards as Cursor users.

### 10. README Updates

**Updated `README.md`:**
- Added links to `documentation/` folder
- Added link to `CHANGELOG.md`

**Impact:** Complete documentation navigation for all users.

## Technical Specifications

### File Changes Summary

**Created:**
- `documentation/` folder with 4 subfolders
- `documentation/README.md`
- `documentation/architecture/README.md`
- `documentation/api/README.md`
- `documentation/deployment/README.md`
- `documentation/decisions/README.md`
- `.cursor/rules/document-template.mc`
- `CHANGELOG.md`
- `VERSION`
- `documentation/decisions/2025-11-07-bairesdev-standards-alignment.md` (this file)

**Renamed:**
- `context/config.md` → `context/context.md`

**Modified:**
- `.cursor/rules/basic-guidelines.mdc` (added ~90 lines)
- `.cursor/rules/prd-guidelines.mdc` (added ~15 lines)
- `.cursor/rules/domain-guidelines.mdc` (added ~30 lines)
- `.cursor/rules/python-practices.mdc` (added ~20 lines)
- `.github/copilot-instructions.md` (updated 1 section)
- `README.md` (added 2 links)
- `src/config.py` (changed default log level)
- `src/utils/logging_config.py` (updated docstring and default)

**Total:** 15 new files, 1 renamed file, 8 modified files

## Dependencies

None. All changes are documentation and configuration, no new code dependencies added.

## Risks and Considerations

### Minimal Risk Changes
- Documentation structure additions
- Guideline enhancements
- All backward compatible

### Potential Impacts
1. **More Verbose Logging:** DEBUG default may produce more logs
   - Mitigation: Can be overridden via .env
   
2. **Documentation Overhead:** More places to document
   - Mitigation: Templates provided, AI can help maintain

3. **Version Management:** Need to maintain VERSION and CHANGELOG
   - Mitigation: Part of standard release process

## Implementation Notes

### For Developers
1. Use `@context.md` in prompts (Cursor AI)
2. Create one .md per PRD/Story in `/deliverables`
3. Use `document-template.mc` for technical docs in `/documentation`
4. Update CHANGELOG.md with every significant change
5. JSON responses use snake_case
6. Default logging is DEBUG (override in .env if needed)

### For AI Assistants
1. Always check `context/context.md` before creating PRDs
2. Update domain entities when PRDs change
3. Create separate files for each PRD/Story
4. Use provided templates
5. Follow semantic versioning

## References

- [BairesDev Code Rules Example](/Users/luisfelipesosa/git/code-rules/)
- [BairesDev Documents Rules Example](/Users/luisfelipesosa/git/documents-rules/)
- [Semantic Versioning 2.0.0](https://semver.org)
- [Keep a Changelog](https://keepachangelog.com)

## Validation

### Compliance Checklist

- [x] Context file renamed to context.md
- [x] Documentation folder created with structure
- [x] Document template provided
- [x] CHANGELOG.md created
- [x] VERSION file created
- [x] Semantic versioning in guidelines
- [x] JSON snake_case standard documented
- [x] DEBUG logging default implemented
- [x] Language requirements explicit (English)
- [x] Performance best practices added
- [x] PRD rules enforced
- [x] Domain update workflow documented
- [x] Copilot instructions updated

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-07 | AI Assistant | Initial documentation of BairesDev standards alignment |

---

*Document created using document-template.mc*

