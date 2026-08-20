
<div align="center">

```
 __                 __           __  __         __
/  |               /  |         /  |/  |       /  |
$$ |____    ______ $$/   ______ $$ |$$ |____  _$$ |_     ______
$$      \  /      \/  | /      \$$ |$$      \/ $$   |   /      \
$$$$$$$  |/$$$$$$/ $$ |/$$$$$$  |$$ |$$$$$$$  |$$$$$$/  /$$$$$$  |
$$ |  $$ |$$ |     $$ |$$ |  $$ |$$ |$$ |  $$ |$$ | __  $$    $$ |
$$ |__$$ |$$ |     $$ |$$ \__$$ |$$ |$$ |__$$ |$$ |/  |/$$$$$$$$/
$$    $$/ $$ |     $$ |$$    $$/ $$ |$$    $$/ $$  $$/ $$       |
$$$$$$$/  $$/      $$/  $$$$$$/  $$/ $$$$$$$/   $$$$/   $$$$$$$/
```

# SNIPER: secret-hound

**A silent guardian for your codebase. An advanced, hybrid-engine tool for hunting down secrets in your filesystem and Git history.**

<p align="center">
  <a href="https://github.com/limearch/sniper">
    <img src="https://img.shields.io/badge/Part%20of-SNIPER%20Toolkit-magenta?style=for-the-badge" alt="Part of SNIPER Toolkit">
  </a>
  <img src="https://img.shields.io/badge/Engine-C%2B%2B%2C%20Go%2C%20Python-blue?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge" alt="License">
</p>

</div>

---

**`secret-hound`** is a high-performance secret scanner and a core security component of the **SNIPER Toolkit**. It embodies the SNIPER philosophy by leveraging the right technology for the right job: a blazing-fast C++ core for regex and entropy analysis, a powerful Go engine for deep Git history traversal, and a flexible Python frontend for a superior user experience.

It's designed to be a developer's first line of defense against accidentally committing sensitive information like API keys, private tokens, and credentials.

### 📚 Table of Contents

1.  [🎯 Core Philosophy](#-core-philosophy)
2.  [✨ Key Features](#-key-features)
3.  [🚀 Build & Installation](#-build--installation)
4.  [⚙️ Usage and Modes](#️-usage-and-modes)
    *   [Filesystem Scan Mode (Default)](#filesystem-scan-mode-default)
    *   [Git History Scan Mode](#git-history-scan-mode)
5.  [🔧 Filtering and Configuration](#-filtering-and-configuration)
6.  [💡 Examples](#-examples)
7.  [🔬 How It Works](#-how-it-works)

---

### 🎯 Core Philosophy

-   **Hybrid Performance**: Use a multi-threaded C++ engine for the CPU-intensive task of scanning file content. Use Go for its excellent concurrency and ecosystem for interacting with Git. Use Python for its rich CLI capabilities and flexible orchestration.
-   **Intelligence over Brute Force**: The scanner is not just a simple regex matcher. It employs Shannon entropy analysis to validate findings and a "smart scan" mode that applies stricter rules to high-risk files like `.env` or `.pem`.
-   **Developer-First Experience**: Provide clear, actionable output. The tool should be easy to integrate into local development workflows and CI/CD pipelines.
-   **Extensibility**: A simple JSON-based rule system allows users to easily add their own secret detection patterns without recompiling the tool.

---

### ✨ Key Features

-   ⚡ **High-Performance C++ Core**: A multi-threaded engine that scans files using optimized regex and Shannon entropy calculations.
-   📜 **Deep Git History Analysis**: A Go-based backend (`git_analyzer`) that efficiently traverses the entire Git history, commit by commit, to find secrets that were committed and later removed.
-   🧠 **Smart Scanning**: Automatically identifies high-risk files (e.g., `.env`, `.pem`, `.key`) and applies more aggressive scanning logic to them, reducing false negatives.
-   🎯 **Fine-Grained Control**: Filter scan results by confidence level (`low`, `medium`, `high`) or include only specific rule IDs to reduce noise.
-   🌐 **Extensible Rule Engine**: Comes with a robust set of default rules for common services (AWS, GitHub, Slack, etc.) and allows users to provide their own custom rule files in JSON format.
-   🖥️ **Clean & Consistent UI**: A simple, colored, and easy-to-parse command-line output that aligns with the SNIPER toolkit's aesthetic, with findings grouped by file.
-   📦 **Flexible Output**: Print results to the console or save them to a structured JSON file for programmatic use or integration with other tools.

---

### 🚀 Build & Installation

`secret-hound` is built and installed automatically as part of the main SNIPER Toolkit's `install.sh` or `make` command.

To build the tool manually, navigate to its directory and use `make`:

```bash
# Navigate to the tool's directory
cd /path/to/sniper/tools/secret-hound/

# Build the C++ and Go backends
make

# Install the backends to the central sniper/bin directory
make install
```

**Dependencies:**
-   **Build-time:** A C++ compiler (`g++` or `clang`), `make`, and the `go` toolchain.
-   **Run-time:** `git` (for Git scanning mode).
These are all handled by the main SNIPER installer.

---

### ⚙️ Usage and Modes

#### Filesystem Scan Mode (Default)

This is the standard mode. It scans a given file or recursively scans a directory. By default, it includes hidden files.

```bash
# Scan the current directory
secret-hound .

# Scan a specific project folder
secret-hound ~/projects/my-app

# Scan a single configuration file
secret-hound /etc/nginx/nginx.conf
```

#### Git History Scan Mode

This powerful mode ignores the current state of files and instead looks at every version of every file committed to the repository.

```bash
# Switch to Git mode (must be inside a Git repository)
secret-hound --scan-git

# Scan the last 500 commits in the repository's history
secret-hound --scan-git --depth 500
```
> **Note:** The `<PATH>` argument is ignored when `--scan-git` is used.

---

### 🔧 Filtering and Configuration

Control the scanner's behavior and output with these flags.

| Flag | Alias | Description |
| :--- | :--- | :--- |
| **`--confidence <lvl>`** | `-c` | Sets the minimum confidence level to report. Choices: `low`, `medium`, `high`. Default is `low`. |
| **`--include <IDs>`** | | A comma-separated list of rule IDs to run exclusively (e.g., `AWS_KEY,GITHUB_TOKEN`). |
| **`--rules <FILE>`** | `-r` | Path to a custom JSON file containing detection rules. |
| **`--no-hidden`** | | Excludes hidden files and directories (those starting with a `.`) from the scan. |
| **`--output <FILE>`** | `-o` | Saves the full report to a file in JSON format. |
| **`--help`** | `-h` | Shows the detailed help screen. |

---

### 💡 Examples

**1. Quick Scan on a Project**
Perform a default scan on the current directory, showing all findings.
```bash
secret-hound .
```

**2. CI/CD Pipeline Check**
Scan a project for only high-confidence secrets. The command will exit with a non-zero status code if secrets are found.
```bash
secret-hound ~/project --confidence high
```

**3. Deep Git History Audit**
Scan the entire history of the current repository and save the findings to a JSON file for later analysis.
```bash
secret-hound --scan-git --depth 99999 -o git-secrets-report.json
```

**4. Focused Scan for Specific Keys**
Scan a directory for only AWS and GitHub tokens.
```bash
secret-hound /path/to/app --include AWS_KEY,AWS_SECRET_KEY,GITHUB_TOKEN
```

---

### 🔬 How It Works

`secret-hound` uses a three-stage pipeline to deliver fast and accurate results:

1.  **Orchestration (Python)**: The user-facing script parses your command.
    *   If it's a **filesystem scan**, it invokes the C++ backend directly, passing the path and filter options.
    *   If it's a **Git scan**, it invokes the Go backend.

2.  **Discovery (Go or C++)**:
    *   **Git Mode**: The Go `git_analyzer` traverses the Git log. For each file in each commit, it retrieves the file's content (blob) and pipes it to the C++ core's `stdin`.
    *   **Filesystem Mode**: The C++ core's `sniper_directory_walk` function efficiently finds all files to be scanned in parallel.

3.  **Analysis (C++)**: The `hound-core` engine receives either a file path or content from `stdin`.
    *   It reads the content line by line.
    *   Each line is checked against all active regex rules.
    *   If a rule requires entropy analysis, the Shannon entropy of the match is calculated.
    *   If a rule is triggered, a JSON object representing the finding is printed to `stdout`.

4.  **Reporting (Python)**: The main Python script captures the continuous stream of JSON objects from the backend, groups them by location, and prints a clean, human-readable report to the console.
