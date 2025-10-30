#
# Original Makefile for the 'fastfind' tool
#

# --- Compiler and Flags ---
CC = clang
# Include the 'include' directory and enable pthread support
CFLAGS = -Wall -Wextra -Iinclude -pthread
# Link with the pthread library for the threadpool
LDFLAGS = -pthread

# --- Project Structure ---
TARGET_DIR := bin
OBJ_DIR    := object
SRC_DIR    := src

# Final executable path
TARGET := $(TARGET_DIR)/fastfind

# --- Source Files & Object Files ---
SRC := $(wildcard $(SRC_DIR)/*.c)
OBJ := $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC))

# --- Phony Targets ---
.PHONY: all clean

# --- Main Rules ---

# Default target: build the executable
all: $(TARGET)

# Rule to link the final executable from its object files
$(TARGET): $(OBJ)
	@echo "--- [fastfind] Linking executable: $@"
	@mkdir -p $(TARGET_DIR)
	$(CC) $(OBJ) -o $@ $(LDFLAGS)

# --- Pattern Rule for Compilation ---
# This rule builds any .o file in object/ from its corresponding .c file in src/
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(OBJ_DIR)
	@echo "--- [fastfind] Compiling: $< -> $@"
	$(CC) $(CFLAGS) -c $< -o $@

# --- Cleanup Rule ---
clean:
	@echo "--- [fastfind] Cleaning object files and executable ---"
	rm -rf $(OBJ_DIR) $(TARGET_DIR)
