# Makefile for Sniper Shatter Engine
# Compiles the C++ core into a shared library for Python ctypes usage.

# Compiler definition
CXX := g++

# Compiler Flags:
# -O3: Maximize optimization (critical for cracking speed)
# -Wall -Wextra: Enable standard warnings
# -std=c++17: Use C++17 standard (required for modern threading/atomic features)
# -fPIC: Position Independent Code (required for shared libraries)
# -pthread: Enable threading support
CXXFLAGS := -O3 -Wall -Wextra -std=c++17 -fPIC -pthread

# Linker Flags:
# -shared: Produce a shared object (.so)
# -lssl -lcrypto: Link against OpenSSL (required for PBKDF2/SHA1)
LDFLAGS := -shared -lssl -lcrypto

# Directory Structure
SRC_DIR := src
LIB_DIR := lib

# Target Output File
TARGET := $(LIB_DIR)/libshatter_engine.so

# Source Files
# We strictly compile engine.cpp. If you have other cpp files, add them here.
SOURCES := $(SRC_DIR)/engine.cpp

# --- Rules ---

# Default target
all: directories $(TARGET)
	@echo "[+] Build complete. Library saved to $(TARGET)"

# Link the shared library
$(TARGET): $(SOURCES)
	@echo "[*] Compiling C++ Engine..."
	$(CXX) $(CXXFLAGS) -o $@ $(SOURCES) $(LDFLAGS)

# Ensure the output directory exists
directories:
	@mkdir -p $(LIB_DIR)

# Clean build artifacts
clean:
	@echo "[*] Cleaning up..."
	rm -f $(TARGET)
	@echo "[+] Clean complete."

# Phony targets (not actual files)
.PHONY: all clean directories
