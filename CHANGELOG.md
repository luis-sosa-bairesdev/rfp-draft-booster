# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with AI-powered development framework
- Comprehensive guidelines for development and documentation
- Domain entity definitions (RFP, Requirement, Service, Risk, Draft)
- PRD and Epic documentation
- Python scaffolding with models and configuration
- Test infrastructure with pytest fixtures

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2025-11-07

### Added
- Project initialization
- AI-powered development guidelines
  - Basic guidelines (always apply)
  - PRD guidelines
  - User story guidelines
  - Domain guidelines
  - Python practices
  - Streamlit guidelines
  - Git guidelines
  - Jira guidelines
- Templates for PRD, Epic, and User Story
- Configuration management with Pydantic
- Domain entities in `/domain/`
  - RFP entity
  - Requirement entity
  - Service catalog entity
  - Risk clause entity
  - Draft entity
- Deliverables
  - Complete PRD for RFP Draft Booster
  - Epic 1: Project Setup
  - Epic 2: PDF Processing
  - Epic 3: LLM Requirement Extraction
  - Epic summary
- Source code structure
  - Models (RFP, Requirement, Service, Risk, Draft)
  - Config management
  - Custom exceptions
  - Session state management
  - Logging configuration
  - Main Streamlit application
- Test infrastructure
  - pytest configuration
  - Test fixtures
  - Folder structure for unit and integration tests
- Documentation
  - Comprehensive README
  - Context configuration
  - .env.example for environment variables

### Technical Details
- Python 3.10+ with type hints
- Streamlit for UI
- Pydantic for configuration
- Support for multiple LLM providers (Gemini, Groq, Ollama)
- Modular architecture with clear separation of concerns

---

## Version Format

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
  - MAJOR: Incompatible API changes
  - MINOR: Backward-compatible functionality additions
  - PATCH: Backward-compatible bug fixes
  
- **Pre-release qualifiers:**
  - `-alpha`: Early development
  - `-beta`: Feature complete, testing
  - `-rc1`: Release candidate

## How to Update This File

When making changes:

1. Add entries under `[Unreleased]` section
2. Group changes by type: Added, Changed, Deprecated, Removed, Fixed, Security
3. Use present tense ("Add feature" not "Added feature")
4. Link to relevant PRs or issues when applicable
5. On release, move `[Unreleased]` content to new version section with date

## Links

- [GitHub Repository](https://github.com/bairesdev/rfp-draft-booster)
- [Jira Project](https://bairesdev.atlassian.net/browse/RFP)
- [Documentation](./documentation/)

