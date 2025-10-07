CXX = g++; CXXFLAGS = -std=c++17 -Iinclude -Wall -Wextra -g; SRCS = $(wildcard src/*.cpp); OBJS = $(SRCS:.cpp=.o); TARGET = build/app
all: $(TARGET); $(TARGET): $(OBJS); @mkdir -p build; $(CXX) $(CXXFLAGS) -o $@ $^
%.o: %.cpp; $(CXX) $(CXXFLAGS) -c -o $@ $<
clean:; rm -rf build $(OBJS)
.PHONY: all clean
