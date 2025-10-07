CC = gcc; CFLAGS = -Iinclude -Wall -Wextra -g; SRCS = $(wildcard src/*.c); OBJS = $(SRCS:.c=.o); TARGET = build/app
all: $(TARGET); $(TARGET): $(OBJS); @mkdir -p build; $(CC) $(CFLAGS) -o $@ $^
%.o: %.c; $(CC) $(CFLAGS) -c -o $@ $<
clean:; rm -rf build $(OBJS)
.PHONY: all clean
