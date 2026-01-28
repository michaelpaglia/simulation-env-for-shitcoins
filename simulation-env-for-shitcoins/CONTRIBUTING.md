# Contributing to Shitcoin Simulation Environment

Thanks for your interest in contributing. This project is open to improvements and new ideas.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies: `pip install -r requirements.txt`
4. Create a branch for your changes

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy env file and add your API key
cp .env.example .env
```

## What We're Looking For

- **New agent personas**: Different CT archetypes (KOLs, traders, maxis, etc.)
- **Better viral modeling**: More realistic spread patterns
- **UI contributions**: Web interface for the simulator
- **Data integrations**: Twitter API, on-chain data, etc.
- **Bug fixes**: Always welcome

## Code Style

- Use type hints
- Keep functions focused and small
- Add docstrings for public functions
- Run tests before submitting

## Pull Requests

1. Keep PRs focused on a single change
2. Update README if adding new features
3. Add tests for new functionality
4. Describe what and why in the PR description

## Issues

Feel free to open issues for:
- Bug reports
- Feature requests
- Questions about the codebase

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
