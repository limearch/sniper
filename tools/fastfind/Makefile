# Makefile (Updated)

CC = gcc
CFLAGS = -Wall -Wextra -pedantic -std=c11 -O2 -Isrc
LDFLAGS = -pthread
SRC_DIR = src
BIN_DIR = bin
OBJS = $(SRC_DIR)/main.o $(SRC_DIR)/regex_utils.o $(SRC_DIR)/search.o $(SRC_DIR)/threadpool.o $(SRC_DIR)/utils.o
TARGET = $(BIN_DIR)/fastfind
HELP_SCRIPT = help_printer.py # <-- NEW

all: $(TARGET) copy_helper

$(TARGET): $(OBJS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)
	@echo "Build successful! Executable is at $(TARGET)"

# --- NEW RULE ---
copy_helper:
	@cp $(HELP_SCRIPT) $(BIN_DIR)/
	@echo "Copied Python helper to $(BIN_DIR)/"
# ----------------

$(SRC_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(SRC_DIR)/*.o $(TARGET) $(BIN_DIR)/$(HELP_SCRIPT)

.PHONY: all clean copy_helper