# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-02-28

This is the first major stable release of the SNIPER toolkit, marking it as feature-complete and ready for general use.

### Added
- **New Major Tools:**
  - `run`: A universal code runner with multi-language support, performance timing, and resource limiting.
  - `format`: An automated code formatter for Python, JSON, Shell, and C/C++, featuring a `--check` mode for CI/CD.
  - `sniper-project-init`: An interactive project scaffolding tool with built-in templates.
  - `sniper-crypt`: A command-line utility for AES-256 file encryption and decryption.
- **Entertainment:**
  - `shell-game`: A terminal-based snake game built with Python's `curses` library.
- **Shell Integration:**
  - Integrated a suite of powerful Zsh plugins (`zsh-autosuggestions`, `zsh-syntax-highlighting`, `zsh-completions`, `zsh-git-prompt`).

### Changed
- **Build System:** `build.sh` is now the primary script for managing all project executables, including C tools and scripts.
- **Project Structure:** Finalized the directory structure, separating core libraries, tools, and shared resources.

## [0.4.0] - 2023-12-10

This release focuses on adding sophisticated Python-based applications to the toolkit.

### Added
- `social-dive`: A powerful, multi-threaded OSINT tool for checking usernames, with `rich` progress bars and export functionality.
- `file-info`: A detailed file and directory analyzer providing hashes, permissions, and timestamps with a rich-formatted output.
- `setup.py`: A universal dependency installer that detects the user's system (Termux/Debian) and installs all required packages and libraries.

### Changed
- Upgraded Python dependencies, adding `requests`, `cryptography`, `tqdm`, and `questionary`.

## [0.3.0] - 2023-09-05

Focus on expanding the suite of high-performance compiled utilities.

### Added
- `fastfind`: A high-performance, multi-threaded file search utility with regex, advanced filtering (size, mtime, owner), and multiple output formats (JSON, CSV).
- `compress`: A versatile compression tool supporting both ZIP (via libzip) and various TAR archives (gzip, bzip2, xz).

### Changed
- Enhanced `build.sh` to support compiling multiple C tools with individual `Makefiles`.

## [0.2.0] - 2023-06-20

Introduction of the C language toolchain and a centralized build system.

### Added
- `configer`: A C-based command-line tool for managing the central `sniper-config.json` file.
- `build.sh`: A foundational script to manage the compilation of C tools using `make`.
- `lib/system.py`: A core Python module for platform detection and path management, used across various scripts.

### Changed
- Migrated configuration management from scattered files to the `configer` tool and `sniper-config.json`.

## [0.1.0] - 2023-03-15

Initial public release of the SNIPER project.

### Added
- Initial collection of utility scripts in the `bin/` directory (`lsmap`, `iplookup`, `scan`, `timer`, etc.).
- Centralized configuration concept using `sniper-config.json`.
- Initial Python dependency list in `requirements.txt`.
- Basic interactive shell concept ("PSHMode") with `etc/intro.py` and `etc/onexit.sh`.
