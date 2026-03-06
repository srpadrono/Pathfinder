# Contributing to Pathfinder

Thanks for your interest in contributing! Here's how to get started.

## How to Contribute

1. **Fork** the repository
2. **Create a branch** from `main` (`git checkout -b feature/my-feature`)
3. **Make your changes** and add tests if applicable
4. **Install dev dependencies** (`python3 -m pip install -r requirements-dev.txt`)
5. **Run the tests** (`python3 -m pytest tests/ -v`)
6. **Commit** with a clear message
7. **Open a Pull Request** against `main`

## Development Setup

```bash
git clone https://github.com/srpadrono/Pathfinder.git
cd Pathfinder
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
```

## Guidelines

- Keep PRs focused — one feature or fix per PR
- Follow existing code style and patterns
- Add tests for new scripts or functionality
- Update documentation if you change behavior

## Reporting Bugs

Open an [issue](https://github.com/srpadrono/Pathfinder/issues) with:
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, AI agent)

## Feature Requests

Open an [issue](https://github.com/srpadrono/Pathfinder/issues) describing:
- The problem you're solving
- Your proposed solution
- Any alternatives you've considered

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
