## Contributing to JeevanQR

Thanks for your interest in contributing! This project follows a lightweight workflow — please follow the steps below to make it easy to review and land your changes.

1. Fork the repository and create a feature branch from `main`:

```bash
git checkout -b feature/short-description
```

2. Run tests and lint locally before opening a PR.

- Install dependencies (project uses the Python backend in `backend/`):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # Windows
# or: source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

- Run linter (Ruff):

```bash
python -m ruff check app
# or run across the backend folder: python -m ruff check .
```

- Run tests:

```bash
python -m pytest -q
```

3. Commit messages

- Write clear, concise commit messages. Use present-tense and reference the issue when relevant.

4. Open a Pull Request

- Push your branch to your fork and open a PR against `main`.
- Describe the change, the motivation, and any testing you performed.

5. Style & Review

- Small, focused PRs are easier to review. If your change affects the API or data format, mention migration or compatibility notes.

Thank you — your contributions help make JeevanQR more reliable and useful.
