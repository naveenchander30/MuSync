# Contributing to MuSync

Thank you for your interest in contributing to MuSync! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/MuSync/issues)
2. If not, open a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, Docker version)
   - Screenshots if applicable

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/yourusername/MuSync/issues) for similar suggestions
2. Open a new issue with:
   - Clear description of the enhancement
   - Use cases and benefits
   - Possible implementation approach (optional)

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes**:
   - Ensure all existing functionality still works
   - Test both Docker and local development setups
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add: Description of your changes"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/videos for UI changes

## Development Setup

See the [Development section](README.md#development) in the README.

## Code Style

### Python

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for functions and classes
- Keep functions focused and small

### JavaScript/React

- Use functional components with hooks
- Follow Airbnb React style guide
- Use meaningful component and variable names
- Keep components focused and reusable

## Testing

While we don't currently have automated tests, please manually test:

- Both export and import operations
- Both Spotify and YouTube Music
- Error scenarios (no auth, missing files, API errors)
- UI responsiveness on different screen sizes

## Questions?

Feel free to open an issue with the `question` label!
