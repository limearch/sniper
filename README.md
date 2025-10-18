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
---
  <!-- Project Info -->
  <img src="https://img.shields.io/badge/Version-1.0.0-blueviolet?style=flat" alt="Version">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen?style=flat" alt="Status">
  <img src="https://img.shields.io/badge/Maintained-Yes-success?style=flat" alt="Maintained">
  <img src="https://img.shields.io/github/license/limearch/sniper?style=flat&label=License" alt="License">
</p>

<p align="center">
  <!-- Environment -->
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Termux-informational?style=flat" alt="Platform">
  <img src="https://img.shields.io/badge/Architecture-x86__64%20%7C%20ARM-informational?style=flat" alt="Architecture">
  <img src="https://img.shields.io/badge/Shell-Bash-lightgrey?style=flat" alt="Shell">
  <img src="https://img.shields.io/github/last-commit/limearch/sniper?style=flat&color=important" alt="Last Commit">
</p>

<p align="center">
  <!-- Tech Stack -->
  <img src="https://img.shields.io/badge/Made%20with-C%2C%20Python%20%26%20Shell-0078d4.svg?style=flat" alt="Made with">
  <img src="https://img.shields.io/badge/Language-C%20%7C%20Python%20%7C%20Shell-blue?style=flat" alt="Languages">
  <img src="https://img.shields.io/github/repo-size/limearch/sniper?style=flat" alt="Repo Size">
  <img src="https://img.shields.io/github/directory-file-count/limearch/sniper?style=flat&label=Files" alt="File Count">
</p>

<p align="center">
  <!-- Community -->
  <img src="https://img.shields.io/badge/Contributions-Welcome-orange.svg?style=flat" alt="Contributions Welcome">
  <img src="https://img.shields.io/github/issues/limearch/sniper?style=flat&color=yellow" alt="Issues">
  <img src="https://img.shields.io/github/forks/limearch/sniper?style=flat&color=blue" alt="Forks">
  <img src="https://img.shields.io/github/stars/limearch/sniper?style=flat&color=gold" alt="Stars">
</p>

<p align="center">
  <!-- Security & CI -->
  <img src="https://img.shields.io/badge/Security-Focused-critical?style=flat" alt="Security">
  <img src="https://img.shields.io/badge/Build-Passing-brightgreen?style=flat" alt="Build Status">
  <img src="https://img.shields.io/badge/Tests-100%25-success?style=flat" alt="Tests">
  <img src="https://img.shields.io/badge/Code%20Quality-A%2B-brightgreen?style=flat" alt="Code Quality">
</p>
</div>

 
---

**SNIPER** is not just a collection of scripts; it's a complete ecosystem that merges the power of high-performance compiled C/C++ utilities with the flexibility of robust Python scripts. It's all wrapped in a unified framework designed to deliver an unparalleled command-line experience.

---

### 📚 Table of Contents

1.  [🎯 Philosophy and Goals](#-philosophy-and-goals)
2.  [✨ Key Features](#-key-features)
3.  [🚀 Quick Installation Guide](#-quick-installation-guide)
    *   [Prerequisites](#prerequisites)
    *   [Installation Steps](#installation-steps)
4.  [🛠️ Tools Documentation](#️-tools-documentation)
    *   [Compiled Tools (C/C++)](#compiled-tools-cc)
    *   [Scripting Tools (Python/Shell)](#scripting-tools-pythonshell)
5.  [🗺️ Project Structure](#️-project-structure)
6.  [⚙️ Configuration](#️-configuration)
7.  [🤝 Contributing](#-contributing)
8.  [📄 License](#-license)

---

### 🎯 Philosophy and Goals

**SNIPER** is built on the principles of precision, speed, and integration. Our goal is to equip developers with a reliable arsenal of tools that work seamlessly together, focusing on:
*   **Performance**: Using C/C++ for tasks that demand maximum speed and efficiency.
*   **Flexibility**: Using Python for tasks requiring API interaction, complex data processing, or rapid development.
*   **User Experience**: Providing beautiful, consistent, and information-rich command-line interfaces.
*   **Integration**: A unified build system that makes managing and updating the project simple.

### ✨ Key Features

-   ⚡ **High Performance**: Core utilities written in C (`fastfind`, `compress`, `run`) or C++ (`g-pass`) are designed to leverage multi-threading and low-level optimizations.
-   🌐 **Universal Code Runner**: The `run` tool intelligently compiles (if needed) and executes code from various languages (C, C++, Python, Java, JS, Go, Rust) with performance timing.
-   🎨 **Rich TUI**: Extensive use of the `rich` library to deliver colorful output, tables, progress bars, and beautiful info panels for a modern CLI experience.
-   🔧 **Unified Build System**: A robust `install.sh` script to manage system dependencies, compile all C/C++ tools, and set up the shell environment.
-   🔍 **OSINT Capabilities**: The `social-dive` tool for concurrently checking username existence across dozens of websites.
-   🏗️ **Advanced Project Scaffolding**: The `sniper-init` tool to interactively and rapidly create new project structures from dynamic templates.
-   🔒 **Strong Encryption**: The `sniper-crypt` tool for securely encrypting and decrypting files and folders using AES-256-GCM.
-   🛡️ **Code Obfuscation**: The `py-shroud` tool to protect Python source code through multi-level obfuscation, including string encryption and name mangling.
-   ✍️ **Automatic Code Formatting**: The `format` tool to enforce a consistent code style across Python, JSON, Shell, and C/C++ files, with a check mode for CI/CD.

---

### 🚀 Quick Installation Guide

The installation process is designed to be simple on **Linux (Debian/Ubuntu)** and **Termux**.

#### Prerequisites

Ensure you have these essential tools: `git` and `python`.

-   **On Debian/Ubuntu:**
    ```bash
    sudo apt-get update && sudo apt-get install -y git python3 python3-pip
    ```
-   **On Termux:**
    ```bash
    pkg install git python -y
    ```

#### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/limearch/sniper.git sniper
    cd sniper
    ```

2.  **Run the Universal Installer:**
    Our smart script (`install.sh`) will automatically detect your system, install all required packages, compile all tools, and set up your shell environment.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    > **Note:** This will install system packages (like `clang`, `make`, `rustc`, `zsh`) and Python libraries (like `rich`, `cryptography`, `questionary`). It will also change your default shell to Zsh for full integration.

**✅ Installation complete! Start a new terminal session, then type `sniper` to activate the environment.**

---

### 🛠️ Tools Documentation

#### Compiled Tools (C/C++)

| Tool | Command | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **Universal Runner** | `run` | An intelligent code runner. Detects language, compiles if necessary, and executes with performance timing and resource limiting. | `run --time my_program.c` |
| **Fast Find** | `fastfind` | A blazing-fast, multi-threaded file search utility with Regex support and advanced filters (size, mtime, owner). | `fastfind -p '\.py$' --size +10K` |
| **Compress Tool** | `compress` | A powerful tool to compress directories into `zip` or various `tar` (gz, bz2, xz) archives. | `compress -d ./src -o archive.zip -v` |
| **Password Generator** | `g-pass` | Advanced hybrid C++/Python password generator with random, "smart", and high-performance "crunch" modes. | `g-pass --smart "strong wifi pass"` |
| **Config Manager** | `configer` | A C-based utility to manage the central `sniper-config.json` file directly from the command line. | `configer set user theme dark` |
| **Size Reporter** | `size` | A simple and fast utility to calculate and display the size of files and directories in a human-readable format. | `size ./large_directory` |

#### Scripting Tools (Python/Shell)

| Tool | Command | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **Social Dive** | `social-dive` | An OSINT tool to check for the existence of usernames across dozens of websites concurrently. | `social-dive johndoe --category Gaming` |
| **Code Formatter** | `format` | An automatic code formatter supporting Python, JSON, Shell, and C/C++. Ideal for standardizing code style. | `format ./my_project --check -p` |
| **Project Initializer**| `sniper-init` | An interactive tool to create new project structures from dynamic templates (Python, Go, React, etc.). | `sniper-init` |
| **Sniper Crypt** | `sniper-crypt` | A utility for securely encrypting and decrypting files and folders using AES-256. | `sniper-crypt encrypt secrets.txt -r` |
| **Python Shroud** | `py-shroud` | Obfuscates Python source code to make it difficult to reverse-engineer, with multiple protection levels. | `py-shroud main.py -o dist.py -l 3` |
| **File Info** | `file-info` | Displays a comprehensive, multi-panel report on any file or directory, including size, permissions, and hashes. | `file-info /path/to/my/file.zip` |
| **Shell Game** | `shell-game` | A simple terminal-based snake game for entertainment, built with Python's `curses` library. | `shell-game` |

---

### 🗺️ Project Structure

```
sniper/
├── config/              # Central configuration files (sniper-config.json)
├── etc/                 # Additional scripts (intro animation, on-exit cleanup)
├── lib/                 # Shared libraries (c_utils for C, sniper_env.py for Python)
├── setup/               # Installation and build scripts (setup.py, packages.json)
├── share/               # Shared resources (help content in share/readme/)
├── test/                # Test scripts for the tools
├── tools/               # Complex sub-tools (each with its own structure)
│   ├── compress/        # Compress tool (C)
│   ├── config/          # Config manager tool (C)
│   ├── fastfind/        # Fast find tool (C)
│   ├── file-info/       # File info tool (Python)
│   ├── format/          # Code formatter tool (Python)
│   ├── g-pass/          # Password generator (C++/Python)
│   ├── py-shroud/       # Python obfuscator (C/Python)
│   ├── run/             # Universal runner (C)
│   ├── shell-game/      # Snake game (Python)
│   ├── size/            # Size reporter tool (C)
│   ├── sniper-crypt/    # Encryption tool (Python)
│   ├── sniper-project-init/ # Project initializer (Python)
│   └── social_dive/     # OSINT tool (Python)
├── install.sh           # Main universal installer
└── README.md            # This file
```

---

### ⚙️ Configuration

The behavior of the SNIPER environment is controlled by the `config/sniper-config.json` file. You can edit it directly or use the dedicated `configer` tool.

**Example: Change the user's default shell**
```bash
configer set user shell zsh
```

**Example: Read the configured Python version**
```bash
configer get environment python_version
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

This project is licensed under the **Apache License 2.0**. See the `LICENSE` file for more details.
