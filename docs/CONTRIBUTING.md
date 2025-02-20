# Contributing Guidelines

## How to Contribute

1. **Fork the Repository**: Fork the repository to your GitHub account.
2. **Clone the Repository**: Clone the repository to your local machine.
    ```bash
    git clone https://github.com/yourusername/TarkovCultistCircle.git
    cd TarkovCultistCircle
    ```

3. **Create a Branch**: Create a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/your-feature-name
    ```

4. **Make Changes**: Make your changes in the codebase.

5. **Run Tests**: Run the tests to ensure your changes do not break existing functionality.
    ```bash
    python -m unittest discover tests
    ```

6. **Commit Changes**: Commit your changes with a descriptive commit message.
    ```bash
    git add .
    git commit -m "Add feature/your-feature-name"
    ```

7. **Push Changes**: Push your changes to your forked repository.
    ```bash
    git push origin feature/your-feature-name
    ```

8. **Create a Pull Request**: Create a pull request to merge your changes into the main repository.

## Code Review

1. **Review Process**: All pull requests must be reviewed by at least one other developer before being merged.
2. **Feedback**: Provide constructive feedback and suggestions for improvement.
3. **Approval**: Once the pull request is approved, it can be merged into the main branch.

## Coding Standards

1. **PEP 8**: Follow the PEP 8 style guide for Python code.
2. **Docstrings**: Use docstrings to document all functions and classes.
3. **Comments**: Add comments to explain complex logic and important sections of the code.

## Best Practices

1. **Modularity**: Keep the code modular by using blueprints and separating concerns.
2. **Configuration**: Use environment variables for configuration and keep sensitive information out of the codebase.
3. **Logging**: Use logging to capture important events and errors.
4. **Testing**: Write unit tests for all functions and classes to ensure code quality and reliability.
