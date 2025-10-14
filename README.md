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
  <img src="https://img.shields.io/badge/Version-1.0.1-blueviolet?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Status-Actively%20Developed-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Termux-informational?style=for-the-badge" alt="Platform">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-C%2C%20C%2B%2B%2C%20Python%20%26%20Shell-0078d4.svg?style=for-the-badge" alt="Made with">
  <img src="https://img.shields.io/github/directory-file-count/limearch/sniper?style=for-the-badge&label=Files" alt="File Count">
  <img src="https://img.shields.io/github/repo-size/limearch/sniper?style=for-the-badge" alt="Repo Size">
</p>
</div>

---

**SNIPER** is not just a collection of scripts; it's a complete ecosystem that merges the power of high-performance compiled C/C++ utilities with the flexibility of robust Python scripts. It's all wrapped in a unified, dynamic framework designed to deliver an unparalleled command-line experience.

---

### 📚 Table of Contents

1.  [🎯 Philosophy](#-philosophy)
2.  [✨ Key Features](#-key-features)
3.  [🚀 Quick Installation](#-quick-installation)
4.  [🛠️ The Arsenal: Tools Overview](#️-the-arsenal-tools-overview)
    *   [Core & Performance Tools (C/C++)](#core--performance-tools-cc)
    *   [Development & Code Tools](#development--code-tools)
    *   [OSINT & Network Tools](#osint--network-tools)
    *   [File & System Utilities](#file--system-utilities)
5.  [⚙️ Configuration](#️-configuration)
6.  [🤝 Contributing](#-contributing)
7.  [📄 License](#-license)

---

### 🎯 Philosophy

**SNIPER** is built on the principles of precision, speed, and integration. Our goal is to equip developers with a reliable arsenal of tools that work seamlessly together, focusing on:
*   **Performance**: Using C/C++ for tasks that demand maximum speed and efficiency (e.g., `fastfind`, `run`).
*   **Flexibility**: Using Python for tasks requiring API interaction, complex data processing, or rich UIs (e.g., `social-dive`, `sniper-init`).
*   **User Experience**: Providing beautiful, consistent, and information-rich command-line interfaces powered by a centralized `rich` rendering engine.
*   **Integration**: A unified, dynamic build system that makes managing and updating the project simple and error-free.

---

### ✨ Key Features

-   ⚡ **High-Performance Core**: Core utilities like `fastfind`, `compress`, and `run` are written in C/C++ and leverage multi-threading for maximum speed.
-   🌐 **Universal Code Runner**: The `run` tool intelligently compiles (if needed) and executes code from various languages, with performance timing, resource limiting, and a `--watch` mode for live-reloading.
-   🏗️ **Intelligent Project Scaffolding**: The `sniper-init` tool interactively creates new, professional project structures from dynamic templates for Flask, React, Go, C++, and more.
-   🎨 **Rich & Centralized UI**: Extensive use of Python's `rich` library through a centralized JSON-driven help engine, delivering beautiful, consistent, and dynamic help screens for all tools.
-   🔍 **OSINT Capabilities**: The multi-threaded `social-dive` tool for concurrently checking username existence across hundreds of websites with rich progress bars.
-   🔒 **Strong Encryption**: The `sniper-crypt` tool for securely encrypting and decrypting files and folders using AES-256-GCM.
-   🔧 **Dynamic Build System**: A robust `setup/build` script that automatically discovers and compiles all C/C++ tools and sets permissions for all scripts, eliminating manual configuration.

---

### 🚀 Quick Installation

The installation process is designed to be simple and idempotent on **Linux (Debian/Ubuntu)** and **Termux**.

#### Prerequisites

Ensure you have these essential tools: `git`, `python3`, and `pip`.

-   **On Termux:** `pkg install git python`
-   **On Debian/Ubuntu:** `sudo apt-get install git python3 python3-pip`

#### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/limearch/sniper.git
    cd sniper
    ```

2.  **Run the Universal Installer:**
    Our smart script (`install.sh`) will automatically detect your system (Debian/Termux), install all required compilers and libraries, build all C/C++ tools, and configure your shell.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    > **Note:** This script will set **Zsh** as your default shell and configure `~/.zshrc` to activate the SNIPER environment.

3.  **Start a New Shell Session:**
    Close and reopen your terminal, or simply run `zsh`.

4.  **Activate SNIPER:**
    ```bash
    sniper
    ```

**✅ Installation complete! All SNIPER tools are now available in your path.**

---

### 🛠️ The Arsenal: Tools Overview

Run `readme <tool_name>` for a detailed guide on any tool (e.g., `readme fastfind`).

#### Core & Performance Tools (C/C++)

| Tool | Command | Description |
| :--- | :--- | :--- |
| **Universal Runner** | `run` | An intelligent code runner with performance timing, resource limiting, and watch mode. |
| **Fast Find** | `fastfind` | A blazing-fast, multi-threaded file search utility with Regex and advanced filters. |
| **Compress Tool** | `compress` | A powerful tool to compress directories into `zip` or `tar` (gz, bz2, xz) archives. |
| **Config Manager** | `configer` | Manage the central `sniper-config.json` file directly from the command line. |
| **Password Gen** | `g-pass` | Hybrid C++/Python password generator with crunch, smart, and preset modes. |
| **Size Reporter** | `size` | A simple and fast utility to calculate and display file/directory size. |

#### Development & Code Tools

| Tool | Command | Description |
| :--- | :--- | :--- |
| **Project Initializer**| `sniper-init` | An interactive tool to create new project structures from professional templates. |
| **Code Formatter** | `format` | An automatic code formatter supporting Python, JSON, Shell, and C/C++. |
| **Python Obfuscator**| `py-shroud` | Protects Python source code with multi-level obfuscation. |
| **Source Viewer** | `view-source` | Displays source code with syntax highlighting and themes in the terminal. |
| **Context Combiner** | `combined` | Combines project source files into a single context file for LLMs. |

#### OSINT & Network Tools

| Tool | Command | Description |
| :--- | :--- | :--- |
| **Social Dive** | `social-dive` | An OSINT tool to check for usernames across hundreds of websites concurrently. |
| **GeoIP Lookup** | `iplookup` | Finds geolocation and network information for an IP address or domain. |
| **Net Discover** | `net-discover` | Scans the local network to discover connected devices. |
| **Net Listener** | `listen` | A versatile TCP listener and simple HTTP file server. |

#### File & System Utilities

| Tool | Command | Description |
| :--- | :--- | :--- |
| **File Info** | `file-info` | Displays a comprehensive report on any file or directory (metadata, hashes). |
| **Sniper Crypt** | `sniper-crypt` | A utility for AES-256 file and folder encryption/decryption. |
| **Directory Mapper** | `lsmap` | A powerful `tree`-like command with advanced filtering and analysis reports. |
| **Lib Installer** | `lib-installer` | An enhanced wrapper around `pip` for managing Python packages. |
| **Shell Game** | `shell-game` | A classic terminal-based snake game for when you need a break. |

---

### ⚙️ Configuration

The behavior of the SNIPER environment is controlled by the `config/sniper-config.json` file. You can edit it directly or use the dedicated `configer` tool for safe and easy modifications.

**Example: Change the user's default prompt text**
```bash
configer set user.prompt_text "HACKERMODE"
```

**Example: Read the configured Python version**
```bash
configer get environment.python_version
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
```
