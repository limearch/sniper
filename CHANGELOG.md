# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-28

This is the first major stable release of the SNIPER toolkit, marking it as feature-complete and ready for general use. This release introduces a powerful suite of new tools for development, security, and productivity.

### Added
- **New Major Tools:**
  - `run`: A universal code runner with multi-language support, performance timing, and resource limiting.
  - `format`: An automated code formatter for Python, JSON, Shell, and C/C++, featuring a `--check` mode for CI/CD.
  - `sniper-project-init`: An interactive project scaffolding tool with built-in templates for modern frameworks.
  - `sniper-crypt`: A command-line utility for AES-256 file and folder encryption and decryption.
  - `g-pass`: An advanced hybrid C++/Python password generator with "smart" (NLP-based) and high-performance "crunch" modes.
  - `py-shroud`: A multi-level Python source code obfuscator that uses AST transformation for string encryption and name mangling.

- **Entertainment:**
  - `shell-game`: A terminal-based snake game built with Python's `curses` library.

- **Shell Integration:**
  - Integrated a suite of powerful Zsh plugins (`zsh-autosuggestions`, `zsh-syntax-highlighting`, `zsh-completions`).

### Changed
- **Build System:** `install.sh` is now the primary universal script for managing all dependencies, compilations, and shell integration.
- **Project Structure:** Finalized the directory structure, separating core libraries (`lib`), tools (`tools`), and shared resources (`share`).
- **Configuration:** Centralized all user and environment settings into `config/sniper-config.json`.

## [0.4.0] - 2024-12-10

This release focuses on adding sophisticated Python-based applications to the toolkit.

### Added
- `social-dive`: A powerful, multi-threaded OSINT tool for checking usernames, with `rich` progress bars and export functionality.
- `file-info`: A detailed file and directory analyzer providing hashes, permissions, and timestamps with a rich-formatted output.
- `setup.py`: A universal dependency installer that detects the user's system (Termux/Debian) and installs all required packages and libraries.

### Changed
- Upgraded Python dependencies, adding `requests`, `cryptography`, `tqdm`, and `questionary`.

## [0.3.0] - 2024-09-05

Focus on expanding the suite of high-performance compiled utilities.

### Added
- `fastfind`: A high-performance, multi-threaded file search utility with regex, advanced filtering (size, mtime, owner), and multiple output formats (JSON, CSV).
- `compress`: A versatile compression tool supporting both ZIP (via libzip) and various TAR archives (gzip, bzip2, xz).

### Changed
- Enhanced build system to support compiling multiple C tools with individual `Makefiles` via a central script.

## [0.2.0] - 2024-06-20

Introduction of the C language toolchain and a centralized build system.

### Added
- `configer`: A C-based command-line tool for managing the central `sniper-config.json` file.
- `build.sh`: A foundational script to manage the compilation of C tools.
- `lib/system.py`: A core Python module for platform detection and path management, used across various scripts.

### Changed
- Migrated configuration management from scattered files to the `configer` tool and `sniper-config.json`.

## [0.1.0] - 2024-03-15

Initial public release of the SNIPER project.

### Added
- Initial collection of utility scripts (`lsmap`, `iplookup`, `scan`, `timer`, etc.).
- Centralized configuration concept using `sniper-config.json`.
- Initial Python dependency list in `requirements.txt`.
- Basic interactive shell concept with `etc/intro.py` and `etc/onexit.sh`.
