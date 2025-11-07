# Git Guidelines

## Overview

This document defines Git workflow, branching strategy, and commit standards for the RFP Draft Booster project.

## Branching Strategy

### Branch Types

```
main              → Production-ready code (protected)
feature/*         → New features and enhancements
fix/*             → Bug fixes
hotfix/*          → Urgent production fixes (rare)
```

### Branch Naming Conventions

**Format:** `type/short-description-ticket-number`

**Examples:**
```bash
feature/pdf-upload-RFP-123
feature/llm-integration-RFP-124
fix/file-validation-bug-RFP-125
fix/export-gdocs-error-RFP-126
```

### Workflow

1. **Create Branch from Main**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/pdf-upload-RFP-123
   ```

2. **Work on Feature**
   ```bash
   # Make changes
   git add .
   git commit -m "feat(upload): add PDF file upload component"
   
   # Continue development
   git commit -m "feat(upload): add file size validation"
   git commit -m "test(upload): add upload component tests"
   ```

3. **Keep Branch Updated**
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/pdf-upload-RFP-123
   git rebase main  # Or merge if preferred
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/pdf-upload-RFP-123
   # Create Pull Request on GitHub
   ```

5. **After PR Approval**
   ```bash
   # Merge to main (via GitHub)
   # Delete branch
   git checkout main
   git pull origin main
   git branch -d feature/pdf-upload-RFP-123
   ```

## Commit Messages

### Conventional Commits Format

```
type(scope): short description

[optional body]

[optional footer]
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)
- `perf`: Performance improvements
- `ci`: CI/CD configuration changes

### Scope Examples

- `upload`: PDF upload functionality
- `extract`: Requirement extraction
- `risk`: Risk detection
- `match`: Service matching
- `draft`: Draft generation
- `export`: Google Docs export
- `ui`: User interface components
- `api`: API integrations

### Good Commit Examples

```bash
feat(upload): add PDF file upload with validation
fix(extract): handle special characters in requirement text
docs(readme): update installation instructions
test(risk): add unit tests for risk detection
refactor(match): optimize matching algorithm performance
chore(deps): update langchain to v0.1.5
```

### Commit Message Best Practices

**Do's ✅**
- Use present tense ("add" not "added")
- Keep first line under 72 characters
- Start with lowercase (after type)
- Reference ticket number in branch name or footer
- Explain "what" and "why", not "how"

**Don'ts ❌**
- Don't use generic messages ("fix bug", "update code")
- Don't combine unrelated changes in one commit
- Don't commit commented-out code
- Don't commit secrets or credentials

### Multi-line Commit Example

```bash
git commit -m "feat(draft): implement draft generation with LLM

- Add draft generator service with Gemini integration
- Implement section-based generation (exec summary, approach, services)
- Add draft validation and word count checks
- Include retry logic for LLM failures

Closes RFP-145"
```

## Pull Requests

### PR Title Format

Same as commit message format:
```
feat(upload): add PDF file upload with validation
```

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Related Tickets
- RFP-123

## Changes Made
- Added PDF upload component
- Implemented file size validation
- Added error handling for invalid files

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots of UI changes]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] All tests passing
```

### PR Review Process

1. **Author:**
   - Ensure all tests pass
   - Self-review code changes
   - Update documentation
   - Request reviewers

2. **Reviewer:**
   - Check code quality and standards
   - Verify tests are adequate
   - Test functionality locally (if needed)
   - Provide constructive feedback

3. **Merge Requirements:**
   - At least 1 approval (for small teams)
   - All CI checks passing
   - No merge conflicts
   - Branch up to date with main

## Git Commands Reference

### Daily Workflow

```bash
# Check current status
git status

# See what changed
git diff

# Add specific files
git add src/services/pdf_processor.py

# Add all changes
git add .

# Commit with message
git commit -m "feat(pdf): add PDF text extraction"

# Push to remote
git push origin feature/pdf-processing-RFP-123

# Pull latest from main
git pull origin main

# View commit history
git log --oneline --graph --decorate
```

### Branch Management

```bash
# List all branches
git branch -a

# Switch to branch
git checkout feature/my-feature

# Create and switch to new branch
git checkout -b feature/new-feature

# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature

# Rename current branch
git branch -m new-branch-name
```

### Sync with Remote

```bash
# Fetch all remote branches
git fetch origin

# Pull and rebase
git pull --rebase origin main

# Update branch with main
git checkout feature/my-feature
git rebase main

# Abort rebase if issues
git rebase --abort
```

### Undo Changes

```bash
# Discard unstaged changes
git checkout -- filename.py

# Unstage file
git reset HEAD filename.py

# Amend last commit (not pushed yet)
git commit --amend -m "new message"

# Revert commit (creates new commit)
git revert <commit-hash>

# Reset to previous commit (dangerous!)
git reset --hard <commit-hash>
```

### Stashing

```bash
# Stash current changes
git stash

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply and remove stash
git stash pop

# Stash with message
git stash save "WIP: working on upload feature"
```

## .gitignore

Essential patterns for Python projects:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Environment
.env
.env.local
*.key
secrets.json

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# Streamlit
.streamlit/secrets.toml

# Data
*.pdf
data/uploads/
data/temp/

# Logs
logs/
*.log

# Distribution
dist/
build/
*.egg-info/
```

## Git Configuration

### Initial Setup

```bash
# Set user name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@bairesdev.com"

# Set default branch name
git config --global init.defaultBranch main

# Enable color
git config --global color.ui auto

# Set default editor
git config --global core.editor "code --wait"
```

### Useful Aliases

```bash
# Add to ~/.gitconfig or set via git config

[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --decorate
    amend = commit --amend --no-edit
```

## Best Practices

### Before Committing

- [ ] Run tests locally (`pytest`)
- [ ] Check linter (`black`, `pylint`)
- [ ] Review your changes (`git diff`)
- [ ] Ensure no debug code or console.logs
- [ ] Verify no secrets in code
- [ ] Update relevant documentation

### Branch Hygiene

- Keep branches focused and small
- Delete branches after merging
- Rebase or merge from main regularly
- Don't commit directly to main
- Use descriptive branch names

### Collaboration

- Pull before pushing
- Communicate about large refactors
- Review PRs promptly
- Provide constructive feedback
- Keep commits atomic and logical

### Security

- Never commit:
  - API keys or secrets
  - Passwords or tokens
  - Private keys or certificates
  - Environment files (.env)
  - User data or PII

- Use:
  - Environment variables
  - Secret management tools
  - .gitignore properly
  - Git hooks for validation

## Troubleshooting

### Merge Conflicts

```bash
# When conflict occurs
git status  # See conflicted files

# Edit files to resolve conflicts
# Look for <<<<<<< HEAD markers

# After resolving
git add resolved_file.py
git commit -m "fix: resolve merge conflicts"
```

### Accidentally Committed to Main

```bash
# Create branch from current state
git branch feature/my-work

# Reset main to remote state
git checkout main
git reset --hard origin/main

# Continue work on feature branch
git checkout feature/my-work
```

### Pushed Wrong Commit

```bash
# Revert the commit (safe, creates new commit)
git revert <bad-commit-hash>
git push origin main

# Or if just pushed and no one pulled yet (dangerous!)
git reset --hard HEAD~1
git push --force origin main  # Use with caution!
```

## Related Guidelines

- [Basic Guidelines](basic-guidelines.mdc)
- [Jira Guidelines](jira-guidelines.md)

