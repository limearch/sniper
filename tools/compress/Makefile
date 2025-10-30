#
# Makefile for the 'compress' tool
#

# --- Compiler and Flags ---
CC = clang
# Include directories: current directory (.), tool headers, and the central C utils library
CFLAGS = -Wall -Wextra -I. -I../../lib/c_utils

# Linker flags: Link against the required 'libzip' for ZIP functionality,
# and our central 'libsniper_c_utils' for logging, parsing, and help.
LDFLAGS = -lzip -L../../lib/c_utils -lsniper_c_utils

# --- Project Structure ---
TARGET_DIR := bin
OBJ_DIR    := object

# Final executable path
TARGET := $(TARGET_DIR)/compress

# --- Source Files ---
# Automatically find all .c files in the current directory.
SRC := $(wildcard *.c)

# --- Object Files ---
# Generate object file paths by placing them in the OBJ_DIR.
# e.g., "main.c" becomes "object/main.o"
OBJ := $(patsubst %.c, $(OBJ_DIR)/%.o, $(SRC))

# --- Phony Targets (commands that are not files) ---
.PHONY: all clean c_utils_lib

# --- Main Rules ---

# Default target: build the library dependency, then the main executable.
all: c_utils_lib $(TARGET)

# Dependency Rule: Ensures the central C utility library is built before this tool.
# This makes the build process self-contained. The '-s' flag silences the make output.
c_utils_lib:
	@echo "--- [compress] Building dependency: libsniper_c_utils.a ---"
	@$(MAKE) -s -C ../../lib/c_utils

# Linking Rule: Links all object files to create the final executable.
$(TARGET): $(OBJ)
	@echo "--- [compress] Linking executable: $@"
	@mkdir -p $(TARGET_DIR)
	$(CC) $(OBJ) -o $@ $(LDFLAGS)

# --- Pattern Rule for Compilation ---
# This generic rule tells 'make' how to build any .o file from its corresponding .c file.
$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(OBJ_DIR)
	@echo "--- [compress] Compiling: $< -> $@"
	$(CC) $(CFLAGS) -c $< -o $@

# --- Cleanup Rule ---
# Removes generated object files and the final executable. Also cleans the dependency library.
clean:
	@echo "--- [compress] Cleaning object files and executable ---"
	rm -rf $(OBJ_DIR) $(TARGET_DIR)
	@$(MAKE) -s -C ../../lib/c_utils clean
