# FastRenamer

## Overview

FastRenamer is a Tkinter-based file renaming application that provides an intuitive graphical interface for batch file renaming operations. The application allows users to select a directory, view files, and apply various renaming operations with user confirmation before execution.

## Features

- **Directory Selection**: Easy browsing and selection of target directories
- **File List Display**: Clear view of files in the selected directory with multiple selection capability
- **Multiple Renaming Options**:
  - Sequential numbering
  - Add prefix or suffix to filenames
  - Replace text within filenames
  - Add folder name to filenames
- **User Confirmation**: Preview and confirm changes before applying them
- **Operation Feedback**: Clear success or failure messages for all operations
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6 or higher
- Tkinter (included with standard Python distributions)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dadebr/FastRenamer.git
   cd FastRenamer
   ```

2. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python renamer_app.py
   ```

## Usage

1. **Launch the Application**: Run `python renamer_app.py`
2. **Select Directory**: Click "Browse" to choose the directory containing files to rename
3. **View Files**: The file list will populate with files from the selected directory
4. **Select Files**: Choose one or more files from the list for renaming
5. **Choose Renaming Option**: Select from the available renaming methods:
   - Sequential: Number files sequentially
   - Prefix/Suffix: Add text before or after the filename
   - Replace: Replace specific text within filenames
   - Folder Name: Add the parent folder name to filenames
6. **Preview Changes**: Review the proposed changes in the confirmation dialog
7. **Apply Changes**: Confirm to execute the renaming operation

## Development

### Project Structure
```
FastRenamer/
├── README.md
├── LICENSE
├── requirements.txt
└── renamer_app.py    # Main application file
```

### Contributing to Development

To set up the development environment:

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Packaging

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create the executable:
   ```bash
   pyinstaller --onefile --windowed renamer_app.py
   ```

The executable will be created in the `dist/` directory.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Include comments for complex logic
- Write descriptive commit messages

### Testing
- Test the application on multiple platforms if possible
- Verify all renaming operations work correctly
- Test edge cases (empty directories, special characters, etc.)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
