#
# Makefile for the 'g-pass' C++/Python hybrid tool
#

# --- Compiler and Flags ---
CXX = g++
# Use modern C++ standard, enable warnings, and include necessary directories
CXXFLAGS = -Wall -Wextra -std=c++17 -Iinclude -I../../lib/c_utils

# Linker flags: Link against the central C utility library
LDFLAGS = -L../../lib/c_utils -lsniper_c_utils

# --- Project Structure ---
TARGET_DIR := bin
OBJ_DIR    := object
SRC_DIR    := src

# Executable name
TARGET := $(TARGET_DIR)/g-pass

# --- Source Files ---
# Find all .cpp files in the source directory
SRC := $(wildcard $(SRC_DIR)/*.cpp)

# --- Object Files ---
OBJ := $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRC))

# --- Phony Targets ---
.PHONY: all clean c_utils_lib

# --- Main Rules ---

# Default target: build everything
all: c_utils_lib $(TARGET)

# Dependency: Ensure the central C utility library is built first
c_utils_lib:
	@echo "--- [g-pass] Building dependency: libsniper_c_utils.a ---"
	@$(MAKE) -s -C ../../lib/c_utils

# Rule to link the final executable
$(TARGET): $(OBJ)
	@echo "--- [g-pass] Linking executable: $@"
	@mkdir -p $(TARGET_DIR)
	$(CXX) $(OBJ) -o $@ $(LDFLAGS)

# --- Pattern Rule for Compilation (for .cpp files) ---
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(OBJ_DIR)
	@echo "--- [g-pass] Compiling: $< -> $@"
	$(CXX) $(CXXFLAGS) -c $< -o $@

# --- Cleanup Rule ---
clean:
	@echo "--- [g-pass] Cleaning object files and executable ---"
	rm -rf $(OBJ_DIR) $(TARGET_DIR)
	@$(MAKE) -s -C ../../lib/c_utils clean
