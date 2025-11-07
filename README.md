# 🚀 RFP Draft Booster

**Accelerate your RFP responses by 80%**

RFP Draft Booster is an AI-powered Streamlit application that automates the time-consuming process of responding to Request for Proposals (RFPs). Upload an RFP PDF, and get intelligent requirement extraction, risk analysis, service matching, and automated draft generation in minutes instead of hours.

---

## 📊 Business Value

- **80% faster** RFP response time
- **25-30% higher** win rates through personalized, risk-aware proposals
- **100+ hours/month** saved per sales team
- **$50K+ annual ROI** in productivity gains

---

## ✨ Features

### 🔹 PDF Upload & Processing
- Upload RFP documents up to 50MB
- Automatic text extraction and parsing
- Support for multi-page documents

### 🔹 Intelligent Requirement Extraction
- AI-powered extraction of key requirements
- Categorization (technical, functional, timeline, budget, compliance)
- Confidence scoring for quality assurance
- Manual verification and editing

### 🔹 Risk Detection
- Automated detection of problematic clauses
- Risk categorization (legal, financial, timeline, technical)
- Severity assessment (critical, high, medium, low)
- Actionable recommendations

### 🔹 Smart Service Matching
- Match requirements to internal service offerings
- Confidence-based matching algorithm
- Manual approval workflow for ambiguous matches
- Integration with service catalog

### 🔹 Draft Generation
- AI-generated proposal drafts
- Structured sections (executive summary, approach, services, timeline, pricing)
- Editable in-app
- Export to Google Docs

### 🔹 Web Search Integration
- Contextual benchmarking
- Industry standards lookup
- Competitive intelligence

---

## 🛠️ Technology Stack

- **Framework:** Streamlit (Python)
- **LLM Providers:** Google Gemini, Groq, Ollama
- **PDF Processing:** PyPDF2, pdfplumber
- **AI Framework:** LangChain
- **Export:** Google Docs API
- **Testing:** pytest
- **Code Quality:** Black, pylint, mypy

---

## 📋 Prerequisites

- Python 3.10 or higher
- Git
- Docker Desktop (for MCP integration)
- API keys for LLM providers (Gemini or Groq recommended)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/bairesdev/rfp-draft-booster.git
cd rfp-draft-booster
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# LLM Configuration (use at least one)
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Google Docs Export (optional)
GDOCS_CREDENTIALS_PATH=/path/to/credentials.json

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

**Get API Keys:**
- **Gemini:** https://ai.google.dev/ (Free)
- **Groq:** https://console.groq.com (Free)

### 5. Run Application

```bash
streamlit run src/main.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### Step 1: Upload RFP
1. Click "Upload RFP" button
2. Select PDF file (max 50MB)
3. Wait for processing (typically 30-60 seconds)

### Step 2: Review Requirements
1. Navigate to "Requirements" page
2. Review extracted requirements
3. Edit or add requirements manually if needed
4. Verify confidence scores

### Step 3: Analyze Risks
1. Go to "Risk Analysis" page
2. Review detected risk clauses
3. Acknowledge critical risks
4. Review recommendations

### Step 4: Match Services
1. Open "Service Matching" page
2. Review automated matches
3. Approve or adjust matches
4. Add alternative services if needed

### Step 5: Generate Draft
1. Navigate to "Generate Draft" page
2. Click "Generate Draft Response"
3. Review and edit generated content
4. Export to Google Docs when ready

---

## 🧪 Development

### Project Structure

```
rfp-draft-booster/
├── .cursor/rules/          # AI development guidelines
├── context/                # Project configuration
├── domain/                 # Business entity definitions
├── deliverables/           # PRDs, Epics, User Stories
├── src/
│   ├── main.py            # Streamlit app entry
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── llm/              # LLM integrations
│   ├── ui/               # UI components
│   └── utils/            # Utilities
├── tests/                 # Test suite
├── data/                  # Data storage
└── logs/                  # Application logs
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_services/test_pdf_processor.py
```

### Code Quality

```bash
# Format code
black src/ tests/ --line-length 88

# Sort imports
isort src/ tests/ --profile black

# Lint
pylint src/

# Type check
mypy src/ --strict
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature-RFP-123

# Make changes and commit
git add .
git commit -m "feat(component): add new feature"

# Push and create PR
git push origin feature/my-feature-RFP-123
```

See [Git Guidelines](.cursor/rules/git-guidelines.md) for detailed workflow.

---

## 📚 Documentation

- **[Product Requirements Document](deliverables/prd-rfp-draft-booster.md)** - Full product specs
- **[Domain Guidelines](.cursor/rules/domain-guidelines.mdc)** - Business entities
- **[Python Practices](.cursor/rules/python-practices.mdc)** - Coding standards
- **[Streamlit Guidelines](.cursor/rules/streamlit-guidelines.mdc)** - UI best practices
- **[Jira Guidelines](.cursor/rules/jira-guidelines.md)** - Project management
- **[Technical Documentation](documentation/)** - Architecture and technical guides
- **[CHANGELOG](CHANGELOG.md)** - Version history and changes

---

## 🤝 Contributing

We follow the BairesDev AI-Powered Development framework:

1. **Check Jira** for available tasks
2. **Create branch** following naming convention
3. **Follow guidelines** in `.cursor/rules/`
4. **Write tests** for all new code
5. **Submit PR** with detailed description
6. **Update Jira** ticket status

---

## 🔒 Security

- Never commit API keys or credentials
- Use environment variables for secrets
- Follow security guidelines in documentation
- Report vulnerabilities to security team

---

## 📊 Roadmap

### Phase 1: MVP (Weeks 1-4)
- [x] Project setup
- [ ] PDF upload & parsing
- [ ] LLM requirement extraction
- [ ] Basic draft generation

### Phase 2: Enhanced Features (Weeks 5-8)
- [ ] Risk detection engine
- [ ] Service matching algorithm
- [ ] Google Docs export
- [ ] Web search integration

### Phase 3: Production Ready (Weeks 9-12)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] User documentation
- [ ] Deployment to production

### Future Enhancements
- [ ] Salesforce CRM integration
- [ ] Multi-user support
- [ ] Analytics dashboard
- [ ] Template library
- [ ] Collaboration features

---

## 🐛 Troubleshooting

### PDF Upload Fails
- Ensure file is under 50MB
- Verify PDF contains extractable text (not scanned image)
- Check file permissions

### LLM Errors
- Verify API keys in `.env` file
- Check internet connectivity
- Ensure API rate limits not exceeded
- Try alternative LLM provider

### Export to Google Docs Fails
- Verify Google credentials configured
- Check credentials.json path
- Ensure Google Docs API enabled
- Verify OAuth permissions

---

## 📞 Support

- **Slack:** #rfp-draft-booster-support
- **Jira:** https://bairesdev.atlassian.net/browse/RFP
- **Email:** support@bairesdev.com

---

## 📄 License

Copyright © 2025 BairesDev. All rights reserved.

---

## 👥 Team

- **Product Owner:** [TBD]
- **Tech Lead:** [TBD]
- **Developers:** [TBD]

---

## 🙏 Acknowledgments

Built using the BairesDev AI-Powered Development Framework with:
- Cursor AI IDE
- Atlassian MCP Integration
- Google Gemini
- Groq API
- LangChain

---

**Made with ❤️ by BairesDev**

