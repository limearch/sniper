# File: tools/py-shroud/Makefile

# --- Configuration ---
PROJECT_NAME = py-shroud
SRC_DIR = src
BIN_DIR = bin
CC = gcc
CFLAGS = -Wall -Wextra -O2

# --- Source and Target ---
SRC = $(SRC_DIR)/main.c
TARGET = $(BIN_DIR)/$(PROJECT_NAME)

# --- Build Targets ---

all: $(TARGET)

$(TARGET): $(SRC)
	@echo "CC   => Compiling C source for $(PROJECT_NAME)..."
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $^
	@echo "DONE => Created executable: '$@'"

# Install the final executable into the main SNIPER bin directory
install: all
	@echo "INSTALL => Copying '$(TARGET)' to root 'bin/' directory..."
	@mkdir -p ../../bin
	@cp $(TARGET) ../../bin/
	@echo "         Installation complete. Run '$(PROJECT_NAME)' from anywhere."

clean:
	@echo "CLEAN => Removing build artifacts..."
	@rm -rf $(BIN_DIR)

.PHONY: all install clean
