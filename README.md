# Minux IDE

Minux is a modern, feature-rich integrated development environment built with Python and customtkinter. It combines the power of a code editor with productivity tools and a clean, VSCode-inspired interface.

## Features

### Core Features
- **Modern UI**: Dark theme with VSCode-inspired design and customizable appearance
- **Tab-based Interface**: Multiple files can be opened in tabs
- **Activity Bar**: Quick access to different views and tools
- **Integrated Terminal**: Built-in terminal with custom logging support
- **Status Bar**: Shows application status and current time

### Development Tools
- **File Explorer**: Browse and manage your project files
- **Search**: Full-text search across your codebase
- **Source Control**: Basic Git integration
- **Debug**: Run and debug your applications
- **Extensions**: Extensible plugin system

### Productivity Tools
- **TODO Management**:
  - Create, edit, and delete tasks
  - Mark tasks as complete
  - Sort tasks by different criteria
  - Local storage using SQLite
  - Optional cloud sync with Firebase
  - View pending tasks on the welcome screen

### Special Features
- **Music Theory Tools**: 
  - Scale visualization
  - Music theory reference
  - Grand staff drawing capabilities

### User Interface
- **Welcome Screen**: 
  - Quick start actions
  - Recent files/folders
  - Pending tasks overview
- **Customizable Settings**:
  - Appearance mode (Light/Dark/System)
  - UI scaling
  - Window transparency
- **Context Menus**: Right-click menus for common actions
- **Notification System**: Error and status notifications

## Technologies Used

- **Python**: Core application language
- **customtkinter**: Modern UI framework
- **SQLite**: Local data storage
- **Firebase** (optional): Cloud synchronization
- **PIL**: Image handling
- **ttk**: Tree view components
- **logging**: Advanced logging system

## Setup and Installation

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. Install requirements:
   ```bash
   pip install -r minux_requirements.txt
   ```

4. (Optional) Firebase Setup:
   - Create a Firebase project
   - Download service account key
   - Place the key file in the application directory as `service-account-key.json`

5. Run the application:
   ```bash
   python minux.py
   ```

## Directory Structure

```
minux/
├── media/
│   ├── icons/      # Application icons
│   └── images/     # Application images
├── ui/
│   ├── widgets/    # Custom UI components
│   └── welcome.py  # Welcome screen
├── minux.py        # Main application
└── minux.db        # SQLite database
```

## Development

- The application uses a modular architecture
- Each major feature is implemented as a separate module
- Custom logging system for debugging
- SQLite database for local storage
- Optional Firebase integration for cloud features

## License

This project is licensed under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) license.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
