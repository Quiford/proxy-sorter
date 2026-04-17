# Contributing Guide

Thanks for your interest in contributing to Quiford Proxy Sorter.

## Setup

1. Fork the repo
2. Create a feature branch
3. Install dependencies

```bash
pip install -r requirements.txt
```

## Development flow

1. Make focused changes
2. Add or update tests in `tests/`
3. Run tests locally:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

4. Open a pull request with:
- Clear title
- What changed
- Why it changed
- Test evidence

## Code style

- Keep code readable and documented
- Use descriptive function names
- Avoid breaking existing CLI/GUI behavior without discussion

## Reporting issues

When opening an issue, include:

- OS and Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Logs or screenshot (if available)
