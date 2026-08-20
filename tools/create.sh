#!/bin/bash
#
# Bash script to create the simplified 'shatter' project structure.
# This structure emphasizes a Python interface over a C/C++ core engine.

# Define the root directory name
PROJECT_ROOT="shatter"

echo "📝 Creating simplified project structure for: $PROJECT_ROOT/"
echo "---------------------------------------------------------"

# 1. Create the main project directory and its subdirectories
echo "📁 Creating main directories..."

mkdir -p "$PROJECT_ROOT/bin"
mkdir -p "$PROJECT_ROOT/src"
mkdir -p "$PROJECT_ROOT/lib"
mkdir -p "$PROJECT_ROOT/rules"

echo "---------------------------------------------------------"
echo "📄 Creating files..."

# 2. Create files in the root directory
touch "$PROJECT_ROOT/README.md"
touch "$PROJECT_ROOT/Makefile"

# 3. Create files in 'bin'
touch "$PROJECT_ROOT/bin/shatter" # Python Entry Script

# 4. Create files in 'src' (C/C++ Core)
touch "$PROJECT_ROOT/src/engine.cpp"
touch "$PROJECT_ROOT/src/engine.hpp"
touch "$PROJECT_ROOT/src/loaders.cpp"
touch "$PROJECT_ROOT/src/crypto_utils.c"

# 5. Create files in 'lib' (Python Modules)
touch "$PROJECT_ROOT/lib/shatter_core.py" # Python Wrapper for C++ Library
touch "$PROJECT_ROOT/lib/parser.py"
touch "$PROJECT_ROOT/lib/session.py"

# 6. Create files in 'rules'
touch "$PROJECT_ROOT/rules/best64.rule"

# 7. Add comments/content to key files for clarity and functionality hints

# Add hint for C++ header
echo "// Core C++ Hashing Engine Declarations" > "$PROJECT_ROOT/src/engine.hpp"

# Add hint for the Python wrapper
echo "# Python interface to the compiled C++ core (shatter_core.so or similar)" > "$PROJECT_ROOT/lib/shatter_core.py"

# Add placeholder Makefile content
echo "# Simple Makefile for building the C/C++ core into a shared library (.so)" > "$PROJECT_ROOT/Makefile"
echo "TARGET = shatter_core.so" >> "$PROJECT_ROOT/Makefile"
echo "CXX = g++" >> "$PROJECT_ROOT/Makefile"
echo "CFLAGS = -Wall -fPIC" >> "$PROJECT_ROOT/Makefile"
echo "LDFLAGS = -shared" >> "$PROJECT_ROOT/Makefile"
echo "" >> "$PROJECT_ROOT/Makefile"
echo "\$(TARGET):" >> "$PROJECT_ROOT/Makefile"
echo "\t\$(CXX) \$(CFLAGS) src/engine.cpp src/loaders.cpp src/crypto_utils.c \$(LDFLAGS) -o \$(TARGET)" >> "$PROJECT_ROOT/Makefile"


echo "---------------------------------------------------------"
echo "✅ File structure for '$PROJECT_ROOT/' created successfully, including basic Makefile content."
