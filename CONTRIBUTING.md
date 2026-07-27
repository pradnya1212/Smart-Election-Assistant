# 🤝 Contributing to Smart Election Assistant (CivicMate)

Thank you for your interest in contributing to **CivicMate / VoteGuide AI**! This document provides everything you need to make meaningful, well-structured contributions. Please read it carefully before opening a Pull Request.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started — Fork & Setup](#-getting-started--fork--setup)
- [Branch Naming Conventions](#-branch-naming-conventions)
- [Making Changes](#-making-changes)
- [Writing a Good PR Description](#-writing-a-good-pr-description)
- [Code Style Expectations](#-code-style-expectations)
- [Running Tests](#-running-tests)
- [Commit Message Guidelines](#-commit-message-guidelines)
- [Review Process](#-review-process)
- [Reporting Issues](#-reporting-issues)

---

## 🧭 Code of Conduct

By contributing, you agree to be respectful and inclusive. This project follows the principle: **be kind, be constructive**. Discrimination, harassment, or disrespectful communication of any kind will not be tolerated.

---

## 🚀 Getting Started — Fork & Setup

### Step 1 — Fork the repository

Click the **Fork** button at the top-right of the [GitHub repository page](https://github.com/pradnya1212/Smart-Election-Assistant). This creates your personal copy of the project.

### Step 2 — Clone your fork

```bash
git clone https://github.com/<your-username>/Smart-Election-Assistant.git
cd Smart-Election-Assistant
```

### Step 3 — Add the upstream remote

This keeps your fork in sync with the main repository:

```bash
git remote add upstream https://github.com/pradnya1212/Smart-Election-Assistant.git
```

### Step 4 — Install dependencies

```bash
cd vote_ai
pip install -r requirements.txt
```

### Step 5 — Configure environment variables

Create a `.env` file inside the `vote_ai/` directory:

```env
DATABASE_URL=postgresql://postgres:root@localhost:5432/voting_system
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```

> **Note:** Never commit your `.env` file or any secrets to the repository. The `.gitignore` already excludes it.

### Step 6 — Run the application locally

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser to verify everything is working.

---

## 🌿 Branch Naming Conventions

All work must happen on a dedicated branch — **never commit directly to `main`**.

Use the following naming patterns:

| Type | Pattern | Example |
|---|---|---|
| New feature | `feat/<short-description>` | `feat/multilanguage-voter-search` |
| Bug fix | `fix/<short-description>` | `fix/double-vote-prevention-bug` |
| Documentation | `docs/<short-description>` | `docs/add-contributing-guide` |
| Refactor / cleanup | `refactor/<short-description>` | `refactor/simplify-vote-routes` |
| Tests | `test/<short-description>` | `test/add-admin-portal-tests` |
| Hotfix (urgent) | `hotfix/<short-description>` | `hotfix/broken-ai-endpoint` |

**Rules:**
- Use **lowercase letters** and **hyphens** (no underscores, no spaces).
- Keep names short but descriptive (3–5 words max).
- Always branch off from an up-to-date `main`.

```bash
# Sync your fork with upstream before branching
git fetch upstream
git checkout main
git merge upstream/main

# Create your feature branch
git checkout -b feat/your-feature-name
```

---

## ✏️ Making Changes

1. Make your changes in small, logical commits (see [Commit Message Guidelines](#-commit-message-guidelines)).
2. Ensure all existing tests still pass before pushing.
3. Add new tests for any new functionality you introduce.
4. Update documentation (including `README.md` if needed) if your change affects the public interface or setup steps.

---

## 📝 Writing a Good PR Description

When you open a Pull Request, use the following template. A well-written PR description makes the review process faster for everyone.

```markdown
## Summary
<!-- One or two sentences describing what this PR does and why. -->

## Changes Made
<!-- A bullet list of the specific changes. Be specific. -->
- 
- 

## Type of Change
<!-- Put an x in the boxes that apply. -->
- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📖 Documentation update
- [ ] ♻️ Refactor (no functional changes)
- [ ] 🧪 Tests (adding or updating tests)

## How to Test
<!-- Step-by-step instructions for a reviewer to verify your changes. -->
1. 
2. 

## Related Issue
<!-- Link the issue this PR addresses, e.g., "Closes #2" -->
Closes #

## Screenshots (if applicable)
<!-- For UI changes, add before/after screenshots. -->
```

**PR Checklist before submitting:**
- [ ] My branch is up-to-date with `main`.
- [ ] All existing tests pass (`python -m pytest test_app.py`).
- [ ] I have added tests for my new functionality.
- [ ] I have not committed any secrets, API keys, or `.env` files.
- [ ] My code follows the style guide below.
- [ ] I have updated documentation where necessary.

---

## 🎨 Code Style Expectations

### Python (Backend — `vote_ai/`)

- Follow **PEP 8** conventions for all Python code.
- Use **4 spaces** for indentation (no tabs).
- Maximum line length: **100 characters**.
- Use descriptive variable and function names (e.g., `get_voter_by_id` not `gvbi`).
- Add **docstrings** to all new functions and classes:

```python
def cast_vote(voter_id: int, candidate_id: int) -> dict:
    """
    Records a vote for a candidate after validating the voter's eligibility.

    Args:
        voter_id: The unique ID of the voter.
        candidate_id: The unique ID of the candidate.

    Returns:
        A dict with keys 'success' (bool) and 'message' (str).
    """
```

- Avoid bare `except:` clauses — always catch specific exceptions.
- Keep Flask route handlers thin; delegate logic to helper functions or model methods.

### HTML / CSS / JavaScript (Frontend — `index.html`)

- Use **2 spaces** for indentation in HTML and CSS.
- Use **4 spaces** for indentation in JavaScript.
- JavaScript variable declarations should use `const` or `let` (never `var`).
- Use semantic HTML5 elements (`<section>`, `<nav>`, `<article>`, etc.) where appropriate.
- CSS class names should use `kebab-case` (e.g., `.vote-card`, `.ai-response`).
- Avoid inline styles — use classes defined in the `<style>` block or a separate CSS file.

### General Rules

- Do not leave commented-out dead code in your PR.
- Remove `print()` debug statements before submitting.
- Keep functions short and focused on a single responsibility.
- Prefer clarity over cleverness.

---

## 🧪 Running Tests

The project uses **Pytest** for backend testing. Always run the full test suite before submitting a PR.

```bash
# From the vote_ai/ directory
python -m pytest test_app.py -v
```

Expected output: **14/14 tests passing**.

If you are adding new features, add corresponding test cases to `test_app.py`. Follow the existing test structure for consistency.

---

## 💬 Commit Message Guidelines

Use the **Conventional Commits** format:

```
<type>(<scope>): <short summary>
```

| Type | When to use |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, missing semicolons, etc. (no logic change) |
| `refactor` | Code change that is neither a fix nor a feature |
| `test` | Adding or correcting tests |
| `chore` | Maintenance tasks (dependency updates, config changes) |

**Examples:**

```
feat(ai): add Hindi language support to Gemini prompt builder
fix(vote): prevent duplicate votes when request is retried
docs(readme): update setup instructions for PostgreSQL 15
test(admin): add tests for reset-votes admin endpoint
```

**Rules:**
- Use the **imperative mood** in the summary ("add", not "added" or "adds").
- Keep the summary under **72 characters**.
- Reference the issue number in the footer if applicable: `Closes #2`.

---

## 🔍 Review Process

1. Once you open a PR, a maintainer will review it within a few days.
2. Address all review comments by pushing new commits to your branch — **do not force-push** once a PR is open.
3. Once approved, a maintainer will merge it using **Squash and Merge** to keep the history clean.
4. After merge, delete your feature branch.

---

## 🐛 Reporting Issues

Before opening an issue, please search existing issues to avoid duplicates. When filing a new bug report, include:

- **A clear title** summarising the problem.
- **Steps to reproduce** the issue.
- **Expected vs. actual behaviour**.
- **Environment details** (OS, Python version, Browser if frontend).
- **Screenshots or error logs** if applicable.

For feature requests, describe:
- The problem you are trying to solve.
- Your proposed solution.
- Why this would benefit the project.

---

## 🙏 Thank You

Every contribution — no matter how small — makes CivicMate better for voters everywhere. We appreciate your time and effort!

> *"Democracy is not just an event. It is a daily practice."*
