# RFP Draft Booster - Configuration

## Project Information

- **Project Name:** RFP Draft Booster
- **Project Key (Jira):** RFP
- **Repository:** https://github.com/bairesdev/rfp-draft-booster
- **Atlassian URL:** https://bairesdev.atlassian.net

## Branch Strategy

### Branch Types

- **main:** Production-ready code (protected branch)
- **feature/*:** New features and enhancements
- **fix/*:** Bug fixes

### Default Base Branch

```
main
```

### Branch Naming Convention

```
feature/[description]-RFP-[ticket-number]
fix/[description]-RFP-[ticket-number]
```

**Examples:**
```
feature/pdf-upload-RFP-123
feature/llm-integration-RFP-124
fix/file-validation-bug-RFP-125
```

## Development Environment

### Python Version

- **Required:** Python 3.10+
- **Recommended:** Python 3.11 or 3.12

### Required Tools

- Git
- Docker Desktop (for MCP integration)
- Streamlit
- pytest

## Jira Configuration

### Project Details

- **Project Key:** RFP
- **Project Name:** RFP Draft Booster
- **Jira URL:** https://bairesdev.atlassian.net/browse/RFP

### Issue Types

- **Epic:** Large features spanning multiple sprints
- **Story:** User-facing features
- **Task:** Technical work
- **Bug:** Defects
- **Sub-task:** Story/Task breakdown

### Sprint Configuration

- **Sprint Duration:** 2 weeks
- **Sprint Capacity (per developer):** 30-40 story points

## LLM Configuration

### Supported Providers

1. **Google Gemini** (Primary - Free)
   - API Endpoint: https://ai.google.dev/
   - Models: gemini-1.5-flash, gemini-1.5-pro
   - Rate Limits: 60 requests/min (free tier)

2. **Groq** (Alternative - Free)
   - API Endpoint: https://console.groq.com
   - Models: llama-3.2, mixtral-8x7b
   - Rate Limits: High throughput

3. **Ollama** (Local - Free)
   - Models: llama-3.2, mistral
   - No rate limits, requires local resources

### Default Settings

```python
LLM_PROVIDER = "gemini"  # gemini | groq | ollama
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000
MIN_CONFIDENCE_SCORE = 0.7
```

## File Upload Configuration

```python
MAX_FILE_SIZE = 52428800  # 50MB in bytes
ALLOWED_EXTENSIONS = [".pdf"]
UPLOAD_DIRECTORY = "data/uploads/"
```

## Service Matching Configuration

```python
MATCH_THRESHOLD = 0.7  # Minimum match score (0.0-1.0)
AUTO_APPROVE_THRESHOLD = 0.85  # Auto-approve matches above this
MANUAL_REVIEW_THRESHOLD = 0.70  # Manual review between 0.70-0.84
```

## Risk Detection Configuration

```python
CRITICAL_RISKS_BLOCK_DRAFT = True  # Block draft generation if critical risks not acknowledged
RISK_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for risk detection
```

## Draft Generation Configuration

```python
MIN_DRAFT_WORD_COUNT = 500
MAX_DRAFT_WORD_COUNT = 10000
DEFAULT_DRAFT_SECTIONS = [
    "executive_summary",
    "approach",
    "services",
    "timeline",
    "pricing"
]
```

## Testing Configuration

```python
TEST_COVERAGE_MINIMUM = 80  # Percentage
PYTEST_VERBOSE = True
RUN_INTEGRATION_TESTS = True
```

## Environment Variables

### Required

```bash
# LLM API Keys (at least one required)
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here

# Google Docs Export (optional)
GDOCS_CREDENTIALS_PATH=/path/to/credentials.json
```

### Optional

```bash
# Application Settings
DEBUG=False
LOG_LEVEL=INFO

# Database (if needed in future)
DATABASE_URL=sqlite:///data/rfp_booster.db

# Web Search (optional)
SERP_API_KEY=your_serp_api_key
```

## Deployment Configuration

### Development

```bash
streamlit run src/main.py --server.port 8501
```

### Production (Future)

- Platform: TBD (Streamlit Cloud, AWS, GCP, Azure)
- CI/CD: GitHub Actions
- Monitoring: TBD

## Code Quality Standards

### Linting & Formatting

```bash
# Black formatter
black src/ tests/ --line-length 88

# isort (import sorting)
isort src/ tests/ --profile black

# pylint
pylint src/ --max-line-length 88

# mypy (type checking)
mypy src/ --strict
```

### Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_services/test_pdf_processor.py
```

## Directory Structure

```
rfp-draft-booster/
├── .cursor/
│   └── rules/              # AI assistant rules
├── .github/
│   └── copilot-instructions.md
├── context/
│   └── config.md          # This file
├── domain/
│   └── [entity].md        # Domain entity definitions
├── deliverables/
│   └── [prd-stories].md   # PRDs, Epics, User Stories
├── src/
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── llm/              # LLM integrations
│   ├── ui/               # Streamlit UI components
│   └── utils/            # Utilities
├── tests/
│   ├── test_models/
│   ├── test_services/
│   └── test_integration/
├── data/
│   ├── uploads/          # Uploaded RFP files
│   └── temp/            # Temporary files
├── logs/                 # Application logs
├── .env                 # Environment variables (not in git)
├── .gitignore
├── requirements.txt
└── README.md
```

## Confluence Documentation

### Main Pages

- **Project Overview:** [Link TBD]
- **Architecture Docs:** [Link TBD]
- **API Documentation:** [Link TBD]
- **User Guide:** [Link TBD]

## Team Contacts

### Product Owner

- **Name:** [TBD]
- **Email:** [TBD]
- **Slack:** [TBD]

### Tech Lead

- **Name:** [TBD]
- **Email:** [TBD]
- **Slack:** [TBD]

### Development Team

- **Developer 1:** [TBD]
- **Developer 2:** [TBD]

## Slack Channels

- **#rfp-draft-booster-dev** - Development discussions
- **#rfp-draft-booster-support** - User support
- **#ai-powered-software-development** - AI development community

## Additional Notes

- This configuration file should be updated as the project evolves
- All sensitive information (API keys, credentials) must be stored in `.env` file, never committed to Git
- Team should review configuration quarterly or when major changes occur
- Configuration changes should be communicated via Slack and documented in Confluence

## Configuration Change Log

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-07 | Initial Setup | Created initial configuration |

