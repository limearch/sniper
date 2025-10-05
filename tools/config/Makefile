CC = gcc
CFLAGS = -Wall -Wextra -std=c99
OBJ = main.o config.o cJSON.o
TARGET = bin/configer

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

main.o: main.c config.h cJSON.h
config.o: config.c config.h cJSON.h
cJSON.o: cJSON.c cJSON.h

clean:
	rm -f $(OBJ) $(TARGET)
