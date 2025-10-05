<div align="center">

```
███████╗███╗░░██╗██╗██████╗░███████╗██████╗░
██╔════╝████╗░██║██║██╔══██╗██╔════╝██╔══██╗
███████╗██╔██╗██║██║██████╔╝█████╗░░██████╔╝
╚════██║██║╚████║██║██╔═══╝░██╔══╝░░██╔══██╗
███████║██║░╚███║██║██║░░░░░███████╗██║░░██║
╚══════╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝
```

# SNIPER Toolkit

**An integrated command-line arsenal for developers, designed for precision, power, and efficiency.**

<p>
    <img src="https://img.shields.io/badge/Version-1.0.0-blueviolet?style=for-the-badge" alt="Version">
    <img src="https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge" alt="Build Status">
    <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Termux-informational?style=for-the-badge" alt="Platform">
    <img src="https://img.shields.io/github/license/mashape/apistatus?style=for-the-badge&label=License" alt="License">
    <br>
    <img src="https://img.shields.io/badge/Made%20with-C%2C%20Python%20%26%20Shell-0078d4.svg?style=for-the-badge" alt="Made with">
    <img src="https://img.shields.io/github/last-commit/google/skia?style=for-the-badge&color=important" alt="Last Commit">
    <img src="https://img.shields.io/badge/Contributions-Welcome-orange.svg?style=for-the-badge" alt="Contributions Welcome">
</p>

</div>

---

**SNIPER** is not just a collection of scripts; it's a complete ecosystem that merges the power of high-performance compiled C utilities with the flexibility of robust Python scripts. It's all wrapped in a unified framework designed to deliver an unparalleled command-line experience.

---

### 📚 Table of Contents

1.  [🎯 Philosophy and Goals](#-philosophy-and-goals)
2.  [✨ Key Features](#-key-features)
3.  [🚀 Quick Installation Guide](#-quick-installation-guide)
    *   [Prerequisites](#prerequisites)
    *   [Installation Steps](#installation-steps)
4.  [🛠️ Tools Documentation](#️-tools-documentation)
    *   [Compiled Tools](#compiled-tools)
    *   [Scripting Tools](#scripting-tools)
5.  [🗺️ Project Structure](#️-project-structure)
6.  [⚙️ Configuration](#️-configuration)
7.  [🤝 Contributing](#-contributing)
8.  [📄 License](#-license)

---

### 🎯 Philosophy and Goals

**SNIPER** is built on the principles of precision, speed, and integration. Our goal is to equip developers with a reliable arsenal of tools that work seamlessly together, focusing on:
*   **Performance**: Using C for tasks that demand maximum speed.
*   **Flexibility**: Using Python for tasks requiring API interaction or complex data processing.
*   **User Experience**: Providing beautiful, consistent, and information-rich command-line interfaces.
*   **Integration**: A unified build system that makes managing and updating the project simple.

### ✨ Key Features

-   ⚡ **High Performance**: Core utilities written in C (`fastfind`, `compress`, `run`) are designed to leverage multi-threading.
-   🌐 **Multi-Language Support**: The universal `run` tool intelligently compiles (if needed) and executes code from various languages (C, C++, Python, Java, JS, Go, Rust).
-   🎨 **Rich TUI**: Extensive use of the `rich` library to deliver colorful output, tables, progress bars, and beautiful info panels.
-   🔧 **Unified Build System**: A robust `build.sh` script to manage the compilation of C tools and grant executable permissions to all scripts.
-   🔍 **OSINT Capabilities**: The `social-dive` tool for concurrently checking username existence across dozens of websites.
-   🏗️ **Project Scaffolding**: The `sniper-project-init` tool to interactively and rapidly create new project structures.
-   🔒 **Strong Encryption**: The `sniper-crypt` tool for securely encrypting and decrypting files using AES-256.

---

### 🚀 Quick Installation Guide

The installation process is designed to be simple on **Linux (Debian/Ubuntu)** and **Termux**.

#### Prerequisites

Ensure you have these essential tools: `git`, `python`, and `pip`.

-   **On Termux:**
    ```bash
    pkg install git python
    ```
-   **On Debian/Ubuntu:**
    ```bash
    sudo apt-get install git python3 python3-pip
    ```

#### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone <URL_OF_YOUR_REPOSITORY> sniper
    cd sniper
    ```

2.  **Install All Dependencies:**
    Our smart script (`setup.py`) will automatically detect your system and install everything you need.
    ```bash
    python setup.py
    ```
    > **Note:** This will install system packages (like `clang`, `make`, `rustc`) and Python libraries (like `rich`, `cryptography`).

3.  **Build the Project:**
    The final step is to compile the C tools and set executable permissions for all tools.
    ```bash
    ./build.sh
    ```
    > **Note:** This will create the executable files in the respective `bin` directories of each tool.

**✅ Installation complete! The SNIPER arsenal is now ready for use.**

---

### 🛠️ Tools Documentation

#### Compiled Tools

| Tool | Command | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **Universal Runner** | `tools/run/bin/run` | An intelligent code runner. It detects the language, compiles if necessary, and executes the code with performance timing. | `./tools/run/bin/run --time my_program.c` |
| **Fast Find** | `tools/fastfind/bin/fastfind` | A blazing-fast, multi-threaded file search utility with Regex support and advanced filters. | `./tools/fastfind/bin/fastfind -p '\.py$' --size +10K` |
| **Compress Tool** | `tools/compress/bin/compress` | A powerful tool to compress directories into `zip` or `tar` (gz, bz2, xz) archives. | `./tools/compress/bin/compress -d ./src -o archive.zip -v` |
| **Config Manager** | `tools/config/bin/configer` | Manage the central `sniper-config.json` file directly from the command line. | `./tools/config/bin/configer set user theme dark` |
| **Size Reporter** | `tools/size/bin/size` | A simple and fast utility to calculate and display the size of files and directories in a human-readable format. | `./tools/size/bin/size ./large_directory` |

#### Scripting Tools

| Tool | Command | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **Social Dive** | `bin/social-dive` | An OSINT tool to check for the existence of usernames across dozens of websites concurrently. | `./bin/social-dive johndoe --category Gaming` |
| **Code Formatter** | `bin/format` | An automatic code formatter supporting Python, JSON, Shell, and C/C++. Ideal for standardizing code style. | `./bin/format ./my_project -f .py .c --check` |
| **File Info** | `bin/file-info` | Displays a comprehensive report on any file or directory, including size, permissions, dates, and hashes. | `./bin/file-info /path/to/my/file.zip` |
| **Project Initializer**| `bin/sniper-init` | An interactive tool to create new project structures (Python, Node.js) with a few clicks. | `./bin/sniper-init` |
| **Sniper Crypt** | `bin/sniper-crypt` | A utility for securely encrypting and decrypting files using the AES-256 algorithm. | `./bin/sniper-crypt encrypt secret-data.txt` |

---

### 🗺️ Project Structure

```
sniper/
├── bin/                 # Main executable scripts and tools
├── etc/                 # Additional config files and project intro
├── lib/                 # Shared Python libraries
├── share/               # Shared resources (e.g., Zsh plugins)
├── test/                # Test scripts for the tools
├── tools/               # Complex sub-tools (each with its own structure)
│   ├── compress/        # Compress tool (C)
│   ├── config/          # Config manager tool (C)
│   ├── fastfind/        # Fast find tool (C)
│   ├── file-info/       # File info tool (Python)
│   ├── format/          # Code formatter tool (Python)
│   ├── run/             # Universal runner (C)
│   ├── shell-game/      # Snake game (Python)
│   ├── size/            # Size reporter tool (C)
│   ├── social_dive/     # OSINT tool (Python)
│   └── sniper-project-init/ # Project initializer (Python)
├── build.sh             # Main build script
├── setup.py             # Dependency installer
├── packages.json        # List of dependencies
├── requirements.txt     # Python dependency list (reference)
└── README.md            # This file
```

---

### ⚙️ Configuration

The behavior of the SNIPER environment is controlled by the `sniper-config.json` file. You can edit it directly or use the dedicated `configer` tool.

**Example: Change the user's default shell**
```bash
./tools/config/bin/configer set user shell zsh
```

**Example: Read the configured Python version**
```bash
./tools/config/bin/configer get environment python_version
```

---

### 🤝 Contributing

We welcome all contributions to make SNIPER even better! If you wish to contribute, please follow these steps:

1.  **Fork** the repository.
2.  Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3.  Make your changes and improvements.
4.  **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Open a **Pull Request**.

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
