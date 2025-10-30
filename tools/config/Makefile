#
# Makefile for the 'configer' tool
#

# --- Compiler and Flags ---
CC = clang
# Include directories for the tool's headers and the central C utils library
CFLAGS = -Wall -Wextra -I. -I../../lib/c_utils

# Linker flags: Link against the central utility library
LDFLAGS = -L../../lib/c_utils -lsniper_c_utils

# --- Project Structure ---
TARGET_DIR := bin
OBJ_DIR    := object

# Final executable path
TARGET := $(TARGET_DIR)/configer

# --- Source Files ---
# Automatically find all .c files in the current directory
SRC := $(wildcard *.c)

# --- Object Files ---
OBJ := $(patsubst %.c, $(OBJ_DIR)/%.o, $(SRC))

# --- Phony Targets ---
.PHONY: all clean c_utils_lib

# --- Main Rules ---

# Default target: build dependency then the main executable
all: c_utils_lib $(TARGET)

# Dependency Rule: Build the central C utility library first
c_utils_lib:
	@echo "--- [configer] Building dependency: libsniper_c_utils.a ---"
	@$(MAKE) -s -C ../../lib/c_utils

# Linking Rule: Link all object files to create the final executable
$(TARGET): $(OBJ)
	@echo "--- [configer] Linking executable: $@"
	@mkdir -p $(TARGET_DIR)
	$(CC) $(OBJ) -o $@ $(LDFLAGS)

# --- Pattern Rule for Compilation ---
$(OBJ_DIR)/%.o: %.c
	@echo "--- [configer] Compiling: $< -> $@"
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# --- Cleanup Rule ---
clean:
	@echo "--- [configer] Cleaning object files and executable ---"
	rm -rf $(OBJ_DIR) $(TARGET_DIR)
	@$(MAKE) -s -C ../../lib/c_utils clean
