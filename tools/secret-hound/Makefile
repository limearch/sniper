# Makefile for the SNIPER 'secret-hound' tool (v2.1 - Safe Clean)
# This Makefile assumes the user-facing script 'secret-hound' lives in the project's main 'sniper/bin' directory.
# The 'bin' directory created here is for compiled backends ONLY.

# --- Variables ---
SNIPER_ROOT := ../..
C_UTILS_DIR := $(SNIPER_ROOT)/lib/c_utils
C_UTILS_LIB := $(C_UTILS_DIR)/libsniper_c_utils.a

CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Isrc -I$(C_UTILS_DIR)
LDFLAGS := -L$(C_UTILS_DIR) -lsniper_c_utils -lpthread

GO := go

# --- Directories & Targets (Corrected Paths) ---
BUILD_DIR := bin
OBJS_DIR := obj

HOUND_CORE_TARGET := $(BUILD_DIR)/hound-core
GIT_ANALYZER_TARGET := $(BUILD_DIR)/git_analyzer

# --- Source Files & Objects ---
SRCS := $(wildcard src/hound_core/*.cpp) src/main.cpp
OBJS := $(patsubst src/%.cpp, $(OBJS_DIR)/%.o, $(SRCS))

# --- Default Target ---
.PHONY: all
all: build

.PHONY: build
build: $(HOUND_CORE_TARGET) $(GIT_ANALYZER_TARGET)

# --- Build Rules ---

# Rule to build the C++ core scanner
$(HOUND_CORE_TARGET): $(OBJS) $(C_UTILS_LIB)
	@echo "-> Linking C++ core scanner: $@"
	@mkdir -p $(dir $@)
	$(CXX) $(OBJS) -o $@ $(LDFLAGS)

# Rule to compile C++ object files (Handles both src/ and src/hound_core/)
$(OBJS_DIR)/%.o: src/%.cpp
	@echo "-> Compiling C++ object: $@"
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJS_DIR)/hound_core/%.o: src/hound_core/%.cpp
	@echo "-> Compiling C++ object: $@"
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Rule to build the Go git analyzer
$(GIT_ANALYZER_TARGET): src/git_analyzer/main.go
	@echo "-> Building Go git analyzer: $@"
	@mkdir -p $(dir $@)
	$(GO) build -o $@ $<

# Dependency rule for the central C utility library
$(C_UTILS_LIB):
	@echo "-> Building dependency: libsniper_c_utils.a..."
	@$(MAKE) -C $(C_UTILS_DIR) --no-print-directory

# --- Cleanup Rule (Now Safe) ---
.PHONY: clean
clean:
	@echo "-> Cleaning up secret-hound build artifacts..."
	@rm -rf $(GIT_ANALYZER_TARGET) $(HOUND_CORE_TARGET) $(OBJS_DIR)

# --- Installation Rule ---
# This rule copies the compiled backends to a central location.
# This makes them findable by the main 'secret-hound' script.
.PHONY: install
install: build
	@echo "-> Installing secret-hound backends to sniper/bin..."
	@mkdir -p $(SNIPER_ROOT)/bin
	@cp $(HOUND_CORE_TARGET) $(SNIPER_ROOT)/bin/
	@cp $(GIT_ANALYZER_TARGET) $(SNIPER_ROOT)/bin/