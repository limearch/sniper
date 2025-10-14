# File: lib/c_utils/Makefile

CC = clang
CFLAGS = -Wall -Wextra -fPIC
AR = ar
ARFLAGS = rcs

TARGET_LIB = libsniper_c_utils.a
SRC = sniper_c_utils.c
OBJ = $(SRC:.c=.o)

.PHONY: all clean

all: $(TARGET_LIB)

$(TARGET_LIB): $(OBJ)
	$(AR) $(ARFLAGS) $@ $^

%.o: %.c sniper_c_utils.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET_LIB)
