# Makefile for compress tool

CC = gcc
# Note: You need to link against libzip. The exact flags can vary.
# On Debian/Ubuntu: -lzip
# On Termux, you might need to specify paths.
CFLAGS = -Wall -Wextra -std=c11 -O2 -I.
LDFLAGS = -lzip
SRC = main.c compress_folder.c zip_folder.c zip_thread.c utils.c tar_compress.c
OBJS = $(SRC:.c=.o)
TARGET = bin/compress
HELP_SCRIPT = help_printer.py

all: $(TARGET) copy_helper

$(TARGET): $(OBJS)
	@mkdir -p bin
	$(CC) $(OBJS) -o $@ $(LDFLAGS)
	@echo "Build successful! Executable is at $(TARGET)"

# --- NEW RULE ---
copy_helper:
	@cp $(HELP_SCRIPT) bin/
	@echo "Copied Python helper to bin/"
# ----------------

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o $(TARGET) bin/$(HELP_SCRIPT)

.PHONY: all clean copy_helper