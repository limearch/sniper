#
# Makefile for the 'run' tool
#

# --- Compiler and Flags ---
CC = clang
# Include directories: current (I.), headers (Iinclude), and the central C utils library
CFLAGS = -Wall -Wextra -I. -Iinclude -I../../lib/c_utils

# Linker flags: Specify library path and link against sniper_c_utils and math library
LDFLAGS = -L../../lib/c_utils -lsniper_c_utils -lm

# --- Project Structure ---
TARGET_DIR := bin
OBJ_DIR    := object
SRC_DIR    := src

# Executable name
TARGET := $(TARGET_DIR)/run

# --- Source Files ---
# Find all .c files in the source directory
SRC := $(wildcard $(SRC_DIR)/*.c)

# --- Object Files ---
# Generate object file paths by replacing src/ with object/ and .c with .o
OBJ := $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC))

# --- Phony Targets (commands that are not files) ---
.PHONY: all clean c_utils_lib

# --- Main Rules ---

# Default target: build everything
all: c_utils_lib $(TARGET)

# Rule to build the central C utility library first
c_utils_lib:
	@echo "--- [run] Building dependency: libsniper_c_utils.a ---"
	@$(MAKE) -s -C ../../lib/c_utils

# Rule to link the final executable
# This depends on all object files being created.
$(TARGET): $(OBJ)
	@echo "--- [run] Linking executable: $@"
	@mkdir -p $(TARGET_DIR)
	$(CC) $(OBJ) -o $@ $(LDFLAGS)

# --- Pattern Rule for Compilation ---
# This rule tells make how to build an object file from a source file.
# It creates the object directory if it doesn't exist.
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(OBJ_DIR)
	@echo "--- [run] Compiling: $< -> $@"
	$(CC) $(CFLAGS) -c $< -o $@

# --- Cleanup Rule ---
clean:
	@echo "--- [run] Cleaning object files and executable ---"
	rm -rf $(OBJ_DIR) $(TARGET_DIR)
	@$(MAKE) -s -C ../../lib/c_utils clean
	