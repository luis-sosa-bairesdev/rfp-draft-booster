# GitHub Copilot Instructions for RFP Draft Booster

This file configures GitHub Copilot to follow the same guidelines as Cursor AI for consistent development experience across both IDEs.

---

## Core Guidelines

All rules from `.cursor/rules/` apply to Copilot as well. Below are references to each guideline:

### Basic Guidelines (Always Apply)

[Basic Guidelines](../.cursor/rules/basic-guidelines.mdc)

**Key Principles:**
- Never assume or invent information - always ask for clarification
- Follow established coding standards and best practices
- Write self-documenting code with clear comments
- Test all new functionality
- Never hardcode secrets or sensitive information
- Use conventional commit format for version control

---

### Product Management Guidelines

[PRD Guidelines](../.cursor/rules/prd-guidelines.mdc)

[User Story Guidelines](../.cursor/rules/user-story-guidelines.mdc)

[Domain Guidelines](../.cursor/rules/domain-guidelines.mdc)

**Summary:**
- Follow standard PRD structure with all required sections
- Write user stories in "As a... I want... So that..." format
- Use Gherkin format (Given-When-Then) for acceptance criteria
- Follow INVEST principles for stories
- Reference domain entities from `/domain/` folder

---

### Development Guidelines

[Python Practices](../.cursor/rules/python-practices.mdc)

**Key Standards:**
- Python 3.10+ with type hints
- Follow PEP 8 (88 char line length for Black compatibility)
- Use dataclasses for data structures
- Google-style docstrings
- Comprehensive error handling with custom exceptions
- Test coverage minimum 80%

[Streamlit Guidelines](../.cursor/rules/streamlit-guidelines.mdc)

**Key Patterns:**
- Multi-page architecture
- Session state management
- Caching strategies (@st.cache_data, @st.cache_resource)
- Progress indicators for long operations
- Clear error messages with UI feedback

---

### Workflow Guidelines

[Git Guidelines](../.cursor/rules/git-guidelines.md)

**Branch Strategy:**
- `main` - Production (protected)
- `feature/*` - New features
- `fix/*` - Bug fixes

**Commit Format:**
```
type(scope): description

feat(upload): add PDF validation
fix(export): handle special characters
docs(readme): update installation steps
test(risk): add unit tests
```

[Jira Guidelines](../.cursor/rules/jira-guidelines.md)

**Issue Management:**
- Project Key: RFP
- Issue Types: Epic, Story, Task, Bug, Sub-task
- Link commits to Jira: `feat(upload): add validation [RFP-123]`
- Update issue status when moving between workflow stages

---

## Templates

Reference templates for consistent documentation:

- [PRD Template](../.cursor/rules/templates/prd_template.md)
- [Epic Template](../.cursor/rules/templates/epic_template.md)
- [User Story Template](../.cursor/rules/templates/user_story_template.md)

---

## Project Context

### Project Structure

```
rfp-draft-booster/
├── src/
│   ├── models/          # Data models (RFP, Requirement, Service, Risk, Draft)
│   ├── services/        # Business logic
│   ├── llm/            # LLM provider integrations
│   ├── ui/             # Streamlit UI components
│   └── utils/          # Utilities
├── tests/              # Test suite
├── domain/             # Business entity definitions
└── deliverables/       # PRDs, Epics, User Stories
```

### Domain Entities

Core business entities defined in [Domain Guidelines](../.cursor/rules/domain-guidelines.mdc):

1. **RFP** - Uploaded request for proposal documents
2. **Requirement** - Extracted requirements from RFPs
3. **Service** - Internal service offerings
4. **ServiceMatch** - Requirement-to-service mappings
5. **RiskClause** - Detected problematic clauses
6. **Draft** - Generated proposal drafts
7. **User** - System users

### Technology Stack

- **Framework:** Streamlit (Python 3.10+)
- **LLM:** Google Gemini (primary), Groq (alternative), Ollama (local)
- **PDF Processing:** PyPDF2, pdfplumber
- **AI Framework:** LangChain
- **Testing:** pytest
- **Code Quality:** Black, pylint, mypy

---

## Code Generation Rules

### When Generating Python Code

1. **Always include type hints:**
```python
def extract_requirements(rfp_text: str, min_confidence: float = 0.7) -> List[Requirement]:
    pass
```

2. **Use dataclasses for models:**
```python
@dataclass
class Requirement:
    id: str
    rfp_id: str
    category: str
    description: str
    confidence_score: float
```

3. **Add comprehensive docstrings:**
```python
def match_services(requirements: List[Requirement]) -> Dict[str, List[ServiceMatch]]:
    """Match requirements to service offerings.
    
    Args:
        requirements: List of extracted requirements
        
    Returns:
        Dictionary mapping requirement IDs to matched services
        
    Raises:
        LLMException: If embedding generation fails
    """
```

4. **Handle errors properly:**
```python
try:
    result = process_rfp(file_path)
except PDFProcessingError as e:
    logger.error(f"PDF processing failed: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise RFPDraftBoosterException(f"Processing failed: {e}") from e
```

### When Generating Streamlit UI

1. **Initialize session state:**
```python
if "current_rfp" not in st.session_state:
    st.session_state.current_rfp = None
```

2. **Use caching:**
```python
@st.cache_data(ttl=3600)
def load_services() -> List[Service]:
    return Service.load_all()
```

3. **Show progress:**
```python
with st.spinner("Processing RFP..."):
    rfp = process_rfp(uploaded_file)
st.success("✅ Processing complete!")
```

4. **Handle errors gracefully:**
```python
try:
    result = risky_operation()
except Exception as e:
    st.error(f"❌ Error: {e}")
    with st.expander("Details"):
        st.exception(e)
```

### When Writing Tests

1. **Use pytest fixtures:**
```python
@pytest.fixture
def sample_rfp():
    return RFP(id="test-1", title="Test RFP")

def test_extract_requirements(sample_rfp):
    requirements = extract_requirements(sample_rfp.text)
    assert len(requirements) > 0
```

2. **Test edge cases:**
```python
def test_empty_input():
    with pytest.raises(InvalidRFPError):
        extract_requirements("")
```

3. **Parameterized tests:**
```python
@pytest.mark.parametrize("confidence,expected", [
    (0.95, True),
    (0.65, False),
])
def test_confidence_threshold(confidence, expected):
    assert meets_threshold(confidence, 0.7) == expected
```

---

## Security Rules

### Never Generate

- Hardcoded API keys or credentials
- Passwords or tokens in code
- Production database credentials
- User PII without encryption
- Commented-out sensitive data

### Always Use

- Environment variables for secrets (`.env`)
- Type validation for inputs
- Error messages without sensitive data
- Logging without PII
- OAuth for authentication

---

## Quality Standards

### Before Suggesting Code

- [ ] Follows type hints
- [ ] Has docstrings
- [ ] Handles errors
- [ ] Includes logging
- [ ] No hardcoded values
- [ ] Follows project structure
- [ ] Matches coding style (Black format)

### Before Completing Feature

- [ ] Unit tests written
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] No linter errors
- [ ] Type checking passes
- [ ] Comments for complex logic

---

## Jira Integration

When suggesting commits or PRs, include Jira references:

```bash
# Commit message
git commit -m "feat(upload): add PDF validation

Implements file size and type validation for uploads.

RFP-123"

# Branch name
feature/pdf-upload-RFP-123
fix/export-error-RFP-156
```

---

## Additional Context

- All configuration in `context/context.md` (use @context.md)
- Domain entities in `domain/` folder
- Deliverables in `deliverables/` folder (one file per PRD/Story)
- Technical documentation in `documentation/` folder
- Guidelines take precedence over defaults
- When in doubt, ask for clarification
- Human approval required for destructive operations
- Follow Semantic Versioning (see VERSION file and CHANGELOG.md)
- JSON uses snake_case convention
- Logging default level is DEBUG

---

## Summary

This project follows the **BairesDev AI-Powered Development Framework**. All code generation should:

1. Follow established guidelines in `.cursor/rules/`
2. Reference domain entities from `domain/`
3. Include comprehensive tests
4. Use proper error handling
5. Have clear documentation
6. Link to Jira tickets
7. Follow Git workflow
8. Maintain high code quality standards

**When uncertain, reference the specific guideline document or ask for clarification.**

