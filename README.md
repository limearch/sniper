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

<p align="center">
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
    git clone https://github.com/limearch/sniper.git sniper
    cd sniper
    ```

2.  **Install All Dependencies And Build:**
    Our smart script (`install.sh`) will automatically detect your system and install everything you need.
    ```bash
    bash install.sh
    ```
    > **Note:** This will install system packages (like `clang`, `make`, `rustc`) and Python libraries (like `rich`, `cryptography`).

    > **Note:** This will create the executable files in the respective `bin` directories of each tool.

**✅ Installation complete! The SNIPER arsenal is now ready for use.**

---

### 🛠️ Tools Documentation

#### Compiled Tools

| Tool | Command | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **Universal Runner** | `run` | An intelligent code runner. It detects the language, compiles if necessary, and executes the code with performance timing. | `run --time my_program.c` |
| **Fast Find** | `fastfind` | A blazing-fast, multi-threaded file search utility with Regex support and advanced filters. | `fastfind -p '\.py$' --size +10K` |
| **Compress Tool** | `compress` | A powerful tool to compress directories into `zip` or `tar` (gz, bz2, xz) archives. | `compress -d ./src -o archive.zip -v` |
| **Config Manager** | `configer` | Manage the central `sniper-config.json` file directly from the command line. | `configer set user theme dark` |
| **Size Reporter** | `size` | A simple and fast utility to calculate and display the size of files and directories in a human-readable format. | `size ./large_directory` |

#### Scripting Tools

| Tool | Command | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| **Social Dive** | `social-dive` | An OSINT tool to check for the existence of usernames across dozens of websites concurrently. | `social-dive johndoe --category Gaming` |
| **Code Formatter** | `format` | An automatic code formatter supporting Python, JSON, Shell, and C/C++. Ideal for standardizing code style. | `format ./my_project -f .py .c --check` |
| **File Info** | `file-info` | Displays a comprehensive report on any file or directory, including size, permissions, dates, and hashes. | `file-info /path/to/my/file.zip` |
| **Project Initializer**| `sniper-init` | An interactive tool to create new project structures (Python, Node.js) with a few clicks. | `sniper-init` |
| **Sniper Crypt** | `sniper-crypt` | A utility for securely encrypting and decrypting files using the AES-256 algorithm. | `sniper-crypt encrypt secret-data.txt` |

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
