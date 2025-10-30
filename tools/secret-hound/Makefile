# File: tools/secret-hound/Makefile
# Description: Makefile for building the C++ core and Go git_analyzer for secret-hound. (FIXED)

# --- Compiler and Flags ---
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -I../../lib/c_utils -Isrc/hound_core
LDFLAGS = -L../../lib/c_utils -lsniper_c_utils -lpthread

# --- Go Compiler ---
GC = go

# --- Directories ---
SRC_DIR = src
CORE_DIR = src/hound_core
GO_DIR = src/git_analyzer
BIN_DIR = bin
OBJ_DIR = obj

# --- Source Files ---
# Find all .cpp files in the source directories
CXX_SOURCES = $(wildcard $(SRC_DIR)/*.cpp) $(wildcard $(CORE_DIR)/*.cpp)
# Get corresponding object file names
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(CXX_SOURCES))

# --- Target Executables ---
# The C++ binary is the "core" worker.
CORE_EXEC = $(BIN_DIR)/hound-core
# The Go binary is the git analyzer.
GO_EXEC = $(BIN_DIR)/git_analyzer
# The user-facing executable is the Python script, which is already in the bin/ directory.
PYTHON_EXEC = $(BIN_DIR)/secret-hound


# --- Main Build Rule ---
all: $(CORE_EXEC) $(GO_EXEC) $(PYTHON_EXEC)

# --- Rule to build the C++ core executable ---
$(CORE_EXEC): $(OBJECTS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(OBJECTS) -o $@ $(LDFLAGS)
	@echo "✓ C++ core scanner created: $@"

# --- Rule to build the Go executable ---
$(GO_EXEC): $(GO_DIR)/main.go
	@mkdir -p $(BIN_DIR)
	$(GC) build -o $@ $(GO_DIR)/main.go
	@echo "✓ Go git analyzer created: $@"

# --- START OF FIX ---
# This rule now ensures the Python entrypoint is executable.
# It no longer copies a file, but assumes the entrypoint script is already in place.
# We will create the `bin` directory if it doesn't exist.
$(PYTHON_EXEC):
	@mkdir -p $(BIN_DIR)
	@chmod +x $(PYTHON_EXEC)
	@echo "✓ Python entrypoint is executable: $@"
# --- END OF FIX ---


# --- Rule to compile .cpp files into .o object files ---
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(OBJ_DIR) $(OBJ_DIR)/hound_core
	$(CXX) $(CXXFLAGS) -c $< -o $@

# --- Phony Targets ---
.PHONY: all clean install

clean:
	@rm -rf $(OBJ_DIR)
	@echo "🧹 Cleaned up build artifacts."

install: all
	@mkdir -p ../../bin
	cp $(CORE_EXEC) ../../bin/hound-core
	cp $(GO_EXEC) ../../bin/git_analyzer
	cp $(PYTHON_EXEC) ../../bin/secret-hound
	@echo "✓ secret-hound and its components installed to main SNIPER bin directory."