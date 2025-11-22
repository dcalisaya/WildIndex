# Contributing to WildIndex

Thank you for your interest in contributing to WildIndex! We welcome contributions from the community to help make this the best open-source tool for wildlife photographers and researchers.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs
- **Check existing issues** to see if the bug has already been reported.
- **Open a new issue** with a clear title and description. Include steps to reproduce, expected behavior, and logs if possible.

### Suggesting Enhancements
- Open an issue describing the feature you'd like to see.
- Explain *why* this feature would be useful to you and others.

### Pull Requests
1.  **Fork the repository** and create your branch from `master`.
2.  **Install dependencies** and ensure the project runs locally (see Development Setup).
3.  **Make your changes**. Ensure your code follows the project's style (Python, Type Hinting).
4.  **Test your changes**. Run the QA script (`scripts/qa_validation.py`) to verify everything works.
5.  **Submit a Pull Request**. Provide a clear description of your changes and link to any relevant issues.

## Development Setup

1.  **Clone your fork:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/WildIndex.git
    cd WildIndex
    ```

2.  **Set up environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

3.  **Run with Docker:**
    ```bash
    docker compose up -d --build
    ```

## Coding Standards

- **Python:** We use Python 3.11+.
- **Type Hinting:** Please use type hints for function arguments and return values.
- **Logging:** Use the project's logging configuration, do not use `print()`.
- **Documentation:** Add docstrings to classes and methods.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
