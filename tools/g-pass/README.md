<div align="center">

<h1 align="center">
  SNIPER: g-pass
</h1>

<p align="center">
  An advanced, hybrid C++/Python password generation tool designed for performance, security, and intelligence.
</p>

<p align="center">
  <a href="https://github.com/limearch/sniper">
    <img src="https://img.shields.io/badge/Part%20of-SNIPER%20Toolkit-magenta?style=for-the-badge" alt="Part of SNIPER Toolkit">
  </a>
  <img src="https://img.shields.io/badge/Language-C%2B%2B%20%26%20Python-blue?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge" alt="License">
</p>

</div>

---

**`g-pass`** is a powerful password generator and a core component of the **SNIPER Toolkit**. It embodies the SNIPER philosophy by merging the raw performance of a C++ core with the flexibility and intelligence of a Python engine. It's designed to be a comprehensive solution for everything from generating a simple random password to creating massive wordlists for security testing.

### 📚 Table of Contents

1.  [🎯 Core Philosophy](#-core-philosophy)
2.  [✨ Key Features](#-key-features)
3.  [🚀 Build & Installation](#-build--installation)
4.  [⚙️ Usage and Modes](#️-usage-and-modes)
    *   [Fast Mode (Default)](#fast-mode-default)
    *   [Interactive Mode](#interactive-mode)
    *   [Smart Mode](#smart-mode)
    *   [Crunch Mode](#crunch-mode)
    *   [Output & Saving](#output--saving)
5.  [💡 Examples](#-examples)

---

### 🎯 Core Philosophy

-   **Hybrid Performance**: Leverage the extreme speed of C++ for computationally intensive tasks like generating millions of password permutations (`Crunch Mode`).
-   **Intelligent Flexibility**: Use Python for complex logic, natural language processing (`Smart Mode`), and handling various file formats (`.json`, `.csv`).
-   **Unified User Experience**: Provide a consistent, rich, and intuitive command-line interface that aligns with the entire SNIPER ecosystem.
-   **Power & Simplicity**: Offer simple commands for common tasks while providing deep customization for advanced users and security professionals.

---

### ✨ Key Features

-   ⚡ **High-Performance C++ Core**: The `Crunch Mode` is implemented in C++ for maximum speed when generating all possible password combinations.
-   🧠 **Intelligent Python Engine**:
    -   **Smart Mode**: Generate passwords based on natural language descriptions (e.g., `"a strong and memorable password for my bank"`).
    -   **Advanced File Handling**: Save output to `.txt`, `.json`, or `.csv`, with automatic file splitting for massive wordlists.
-   🎛️ **Multiple Generation Modes**:
    -   **Fast Mode**: Generate customizable random passwords instantly.
    -   **Interactive Mode**: A guided wizard to build your perfect password generation profile step-by-step.
    -   **Crunch Mode**: A powerful engine to create comprehensive wordlists based on character sets, length ranges, and patterns.
-   📋 **Presets & Customization**: Quickly generate passwords for common use-cases (`wifi`, `email`) or fine-tune every parameter, including length, character sets, and exclusions.
-   📤 **Versatile Output**: Print to the console, save to a file, or copy directly to the clipboard (supports `xclip` on Linux and `termux-clipboard-set` on Termux).
-   🎨 **Rich TUI**: A beautiful, panel-based help screen and clear, colored output that matches the SNIPER aesthetic.

---

### 🚀 Build & Installation

`g-pass` is designed to be built as part of the main SNIPER Toolkit. Ensure the necessary build tools are installed by the main `install.sh` script.

**Prerequisites:**
- A C++ compiler (`g++` or `clang`)
- `make`
- `python3` and the `rich` library (`pip install rich`)

**Build Steps:**

1.  Navigate to the `g-pass` tool directory:
    ```bash
    cd /path/to/sniper/tools/g-pass
    ```

2.  Run `make` to compile the tool. This will create the executable in the `bin/` directory.
    ```bash
    make
    ```

3.  (Optional) Install it to a system-wide path for easy access, or ensure the `g-pass/bin` directory is in your `$PATH`.
    ```bash
    sudo make install
    ```

---

### ⚙️ Usage and Modes

Run `g-pass --help` at any time to see a detailed, rich-formatted guide.

#### Fast Mode (Default)

For generating one or more random passwords with specific rules.

```bash
# Generate a default 16-character password
g-pass

# Generate a 24-character password with no symbols
g-pass -l 24 --no-symbols

# Generate 5 passwords of length 32
g-pass -l 32 -n 5

# Generate a password excluding ambiguous characters
g-pass -l 12 -e "Il1O0"
```

#### Interactive Mode

For a step-by-step guided experience. The tool will ask you for each parameter.

```bash
g-pass -i
```

#### Smart Mode

Let the Python engine interpret your needs and generate a suitable password.

```bash
# Generate a strong but memorable password
g-pass --smart "an easy to remember but secure password for my email"

# Generate a highly secure password for a sensitive account
g-pass --smart "a very strong and complex password for a crypto wallet"
```

#### Crunch Mode

For generating wordlists by creating every possible combination of characters within a given length.

```bash
# Generate all combinations of 'abc1' from length 3 to 4
g-pass --crunch 3 4 abc1

# Generate all 8-character passwords using only lowercase letters and numbers
g-pass --crunch 8 8 "abcdefghijklmnopqrstuvwxyz0123456789"

# Generate passwords based on a pattern.
# Placeholders: @ (lower), , (upper), % (number), ^ (symbol)
# Any other character is treated as a literal.
g-pass --crunch-pattern "SNIPER-@@%%"
# Output example: SNIPER-ab12, SNIPER-ac13, ...
```
> **⚠️ Warning:** Crunch mode can generate extremely large files. The tool will warn you before starting large jobs.

#### Output & Saving

Control where the generated passwords go.

```bash
# Copy the first generated password to the clipboard
g-pass -l 20 -c

# Save 10 passwords to a text file
g-pass -n 10 --save passwords.txt

# Save passwords from Smart Mode to a JSON file
g-pass --smart "passwords for my team" -n 5 --save team_pass.json

# Generate a large wordlist and split it into 10MB chunks
g-pass --crunch 1 6 abcdef012345 --save wordlist.txt --split-size 10M
# This will create: wordlist.txt, wordlist_part2.txt, etc.
```

---

### 💡 Examples

Here are some practical command combinations:

**1. Secure Wi-Fi Password**
Use the `wifi` preset, which generates an easy-to-type password by excluding symbols and ambiguous characters.
```bash
g-pass -p wifi
```

**2. Human-Readable Passphrase**
Use the `human` preset for a memorable, XKCD-style passphrase.
```bash
g-pass -p human
# Output example: Tango-Silver-Whiskey-42!
```

**3. Generating PIN Codes**
Use crunch mode to generate all possible 4-digit PIN codes and save them to a file.
```bash
g-pass --crunch 4 4 0123456789 --save pins.txt
```

**4. Complex Scripting**
Generate a list of potential passwords for a user named 'alex' born in '95' and pipe it to another tool.
```bash
g-pass --crunch-pattern "alex%%^^" | john --stdin
# This generates passwords like: alex00!@, alex01!#, ...
```
```
