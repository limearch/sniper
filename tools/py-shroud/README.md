<div align="center">

```
 _________   ____    __   _________   __    __
/________/\ /___/\  /_/\ /________/\ /_/\  /_/\
\__.::.__\/ \::\ \ \ \:\ \\__.::.__\/ \ \ \ \ \:\ \
   \::\ \    \::\/_/ /_\:\ \   \::\ \    \:\_\/.:\ \
    \::\ \    \::\ \ \::\ \ \   \::\ \    \ ..::/ /
     \::\ \    \::\_\/ \::\ \ \   \::\ \    \::\ \ /
      \__\/     \_____\/ \__\/     \__\/     \__\/ \/
```

# SNIPER: py-shroud

**An advanced, multi-level Python source code obfuscator designed for security and distribution.**

</div>

---

**py-shroud** is a powerful utility within the **SNIPER Toolkit** that transforms human-readable Python code into a protected, difficult-to-reverse-engineer format. It goes beyond simple bytecode compilation by employing multiple layers of obfuscation, including string encryption and name mangling, to significantly increase the complexity of your distributed scripts.

The tool is built with a hybrid C-Python architecture, providing a fast native command-line interface that invokes a sophisticated Python engine for Abstract Syntax Tree (AST) manipulation.

### ✨ Key Features

-   🛡️ **Multi-Level Obfuscation**: Choose from three levels of protection, from basic bytecode conversion to maximum-strength name mangling.
-   🔒 **String Encryption**: Automatically finds and encrypts all string literals in your code, decrypting them only at runtime.
-   ✍️ **Name Mangling**: Renames variables, functions, and classes to meaningless, unreadable names (`_O`, `_I`, `_IO`, etc.).
-   🚀 **Fast Native Interface**: Built with a C wrapper for instant startup and seamless integration with shell environments and the SNIPER `build.sh` system.
-   🎨 **Rich User Experience**: Features a beautifully formatted, panel-based help screen and a detailed summary report after each operation, powered by `rich`.
-   📎 **Banner Support**: Easily prepend a custom copyright or informational banner to your shrouded files.

---

### 📚 Table of Contents

1.  [🚀 Quick Start](#-quick-start)
2.  [🛠️ Installation & Build](#️-installation--build)
3.  [⚙️ Usage and Options](#️-usage-and-options)
    *   [Command Syntax](#command-syntax)
    *   [Obfuscation Levels](#obfuscation-levels)
4.  [💡 Examples](#-examples)
5.  [🔬 How It Works](#-how-it-works)

---

### 🚀 Quick Start

To shroud a Python script with the default (and recommended) protection level:

```bash
py-shroud my_script.py -o my_shrouded_script.py
```

This will create `my_shrouded_script.py`, which is functionally identical to the original but with its source code protected.

---

### 🛠️ Installation & Build

`py-shroud` is installed automatically as part of the main SNIPER Toolkit's `install.sh` script.

To build or rebuild the tool manually, navigate to its directory and use `make`:

```bash
# Navigate to the tool's directory
cd tools/py-shroud/

# Compile the C wrapper to create the executable
make

# Optional: Install the executable to the main SNIPER bin/ directory
make install
```

**Dependencies:**
*   **Build-time:** `gcc` (or `clang`), `make`, `python3-dev`, `python3-pip`.
*   **Run-time (for the Python engine):** `rich`.

These dependencies are handled by the main SNIPER `install.sh` script.

---

### ⚙️ Usage and Options

#### Command Syntax

```
Usage: py-shroud <INPUT_FILE> -o <OUTPUT_FILE> [OPTIONS]
```

**Required Arguments:**
*   `<INPUT_FILE>`: The path to the Python source file you want to obfuscate.
*   `-o, --output <FILE>`: The path where the final shrouded file will be saved.

**Options:**
*   `-l, --level <1|2|3>`: Sets the obfuscation level. Defaults to `2`.
*   `--banner <FILE>`: Path to a text file to prepend as a header/comment.
*   `-h, --help`: Displays the detailed, rich-formatted help screen.

#### Obfuscation Levels

| Level | Name      | Description                                                                                                                              |
| :---: | :-------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
|   **1**   | `Basic`   | Converts the source code into marshalled bytecode. This is fast but provides minimal protection against simple decompilation.             |
|   **2**   | `Standard`| **(Default)** Includes Level 1 protection and adds robust string encryption. All string literals are hidden and decrypted at runtime. |
|   **3**   | `Maximum` | Includes all previous levels and adds name mangling. Renames variables, functions, and classes to unreadable, non-descriptive names. |

---

### 💡 Examples

**1. Basic Obfuscation (Level 2)**
Shroud a script with default protection (string encryption + bytecode).
```bash
py-shroud sensitive_api.py -o protected_api.py
```

**2. Maximum Obfuscation (Level 3)**
Apply the strongest protection, including name mangling.
```bash
py-shroud main_app.py -o dist/main.py -l 3
```

**3. Adding a Copyright Banner**
Prepend the contents of `copyright.txt` to the final output file.
```bash
py-shroud my_tool.py -o my_tool.shrouded.py --banner copyright.txt
```
The resulting file will look like this:
```python
"""
My Awesome Tool v1.0
(c) 2024 Your Name. All rights reserved.
"""

# ==============================================================================
#  This file was obfuscated by SNIPER: py-shroud
#
#  Timestamp:        2024-05-21 12:00:00 UTC
#  Source File:      my_tool.py
#  Protection Level: 2 (Standard (String Encryption))
#
#  WARNING: DO NOT EDIT THIS FILE MANUALLY.
# ==============================================================================

import marshal, base64; exec(marshal.loads(base64.b64decode(b'eJz...')))
```

---

### 🔬 How It Works

`py-shroud` does not simply compile your code to `.pyc`. It follows a more sophisticated, multi-stage process:

1.  **Parsing**: The Python source code is parsed into an **Abstract Syntax Tree (AST)**, which is a tree-like representation of the code's structure.
2.  **Transformation**: The tool walks through this tree and applies transformations based on the chosen obfuscation level:
    *   **String Encryption (Lvl 2+):** It finds every string literal (`"hello"`) and replaces it with a function call that decrypts the string at runtime (e.g., `_d(b'aGVsbG8=')`). A small decryption function is injected into the code.
    *   **Name Mangling (Lvl 3):** It finds all user-defined names (variables, functions, etc.) and replaces them with generated, non-descriptive names, keeping a map to ensure consistency.
3.  **Unparsing**: The modified AST is converted back into Python source code. This new code is functionally identical but structurally obfuscated.
4.  **Marshalling**: The obfuscated source code is compiled into Python bytecode, which is then serialized using the `marshal` module.
5.  **Encoding & Wrapping**: The marshalled bytecode is encoded in Base64 and embedded into a simple loader stub (`import marshal, base64; exec(...)`). This final string is written to the output file, along with the informational banners.

This AST-based approach is extremely powerful as it allows for deep, structural modifications to the code before it is ever executed.
