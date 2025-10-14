#!/bin/bash

# ==============================================================================
# SNIPER Toolkit - Universal Installer (v1.1 - Idempotent)
#
# This script automates the full setup of the SNIPER environment, including:
# 1. Installing system and Python dependencies via setup.py.
# 2. Compiling all C-based tools via setup/build .
# 3. Changing the user's default shell to Zsh.
# 4. Injecting/Updating the 'sniper' environment activator into .zshrc.
# ==============================================================================

# --- Color Definitions ---
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'
C_MAGENTA='\033[0;35m'
C_CYAN='\033[0;36m'
C_GREY='\033[90m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

# --- Helper Functions for Output Formatting ---
print_header() {
    echo -e "${C_MAGENTA}
╭───────────────────────────────────────────────────╮
│   ${C_BOLD}SNIPER Toolkit :: Professional Setup Utility${C_RESET}${C_MAGENTA}   │
╰───────────────────────────────────────────────────╯
${C_RESET}"
}

print_stage() {
    echo -e "\n${C_BLUE}${C_BOLD}--- [ STAGE: $1 ] ---${C_RESET}"
}

print_success() {
    echo -e "  ${C_GREEN}[✔] Success:${C_RESET} $1"
}

print_error() {
    echo -e "  ${C_RED}[✘] Error:${C_RESET} $1" >&2
}

print_info() {
    echo -e "  ${C_CYAN}[i] Info:${C_RESET} $1"
}

# --- Core Installation Functions ---

run_setup() {
    print_stage "Installing Dependencies"
    if [ ! -f "setup/setup.py" ]; then
        print_error "setup/setup.py not found. Please run from the project root."
        exit 1
    fi
    
    echo -e "${C_GREY}▼▼▼ Running setup.py output ▼▼▼${C_RESET}"
    python3 setup/setup.py
    if [ $? -ne 0 ]; then
        print_error "Dependency installation failed. Please check the errors above."
        exit 1
    fi
    echo -e "${C_GREY}▲▲▲ End of setup.py output ▲▲▲${C_RESET}"
    print_success "All dependencies are installed."
}

# *** MODIFIED FUNCTION TO ENSURE 'bin/' DIRECTORIES EXIST ***
run_build() {
    print_stage "Building Project Tools"
    local build_script="setup/build"
    if [ ! -f "$build_script" ]; then
        print_error "$build_script not found. Cannot compile tools."
        exit 1
    fi

	local c_utils_dir="lib/c_utils"
	    if [ -d "$c_utils_dir" ]; then
	        print_info "Building central C utility library (libsniper_c_utils.a)..."
	        (cd "$c_utils_dir" && make clean && make)
	        if [ $? -ne 0 ]; then
	            print_error "Failed to build the central C utility library. Aborting build."
	            exit 1
	        fi
	        print_success "Central C library built successfully."
	    fi
    # --- START: New logic to ensure 'bin/' directories exist ---
    print_info "Ensuring output 'bin/' directories exist for all tools..."
    local tools_dir="tools" # Assuming tools are in a 'tools/' directory.
    if [ -d "$tools_dir" ]; then
        # Loop through each subdirectory in the tools folder
        for tool_path in "$tools_dir"/*; do
            if [ -d "$tool_path" ]; then
                local bin_dir="$tool_path/bin"
                # If the bin directory does not exist, create it.
                if [ ! -d "$bin_dir" ]; then
                    print_info "Creating missing directory: $bin_dir"
                    mkdir -p "$bin_dir"
                fi
            fi
        done
        print_success "All tool 'bin/' directories are confirmed to exist."
    else
        # If the main 'tools' directory doesn't exist, just inform the user.
        print_info "Main tools directory '$tools_dir' not found, skipping 'bin/' directory creation."
    fi
    # --- END: New logic ---

    chmod +x "$build_script"
    echo -e "${C_GREY}▼▼▼ Running build output ▼▼▼${C_RESET}"
    ./"$build_script"
    if [ $? -ne 0 ]; then
        print_error "Build process failed. Please check the compilation errors."
        exit 1
    fi
    echo -e "${C_GREY}▲▲▲ End of build output ▲▲▲${C_RESET}"
    print_success "All tools have been compiled and are ready."
}

change_shell_to_zsh() {
    print_stage "Configuring Shell Environment"
    if ! command -v zsh &> /dev/null; then
        print_error "Zsh is not installed. The setup script should have installed it."
        print_info "Please install it manually ('sudo apt install zsh' or 'pkg install zsh') and re-run."
        exit 1
    fi

    local zsh_path
    zsh_path=$(which zsh)

    if [[ "$SHELL" == *"/zsh"* ]]; then
        print_info "Default shell is already Zsh. Skipping change."
    else
        print_info "Changing default shell to Zsh..."
        chsh -s "$zsh_path"
        if [ $? -eq 0 ]; then
            print_success "Default shell changed to Zsh."
            print_info "You may need to log out and log back in for the change to take full effect."
        else
            print_error "Failed to change shell. You may need to do it manually."
            print_info "Command: chsh -s $zsh_path"
        fi
    fi
}

install_sniper_function() {
    print_stage "Integrating 'sniper' Command"
    local zshrc_file="$HOME/.zshrc"
    local sniper_root
    sniper_root=$(pwd) # Get the absolute path of the current directory

    # Ensure the .zshrc file exists before trying to modify it.
    touch "$zshrc_file"

    # Check if the function already exists. If so, remove the old block first.
    if grep -q "# SNIPER_TOOLKIT_FUNCTION" "$zshrc_file" 2>/dev/null; then
        print_info "Found an existing 'sniper' function. Removing it before adding the new version..."
        sed -i.bak '/# SNIPER_TOOLKIT_FUNCTION/,/# END_SNIPER_TOOLKIT_FUNCTION/d' "$zshrc_file"
        print_success "Old function block removed. A backup was created at ${zshrc_file}.bak"
    fi

    print_info "Adding/Updating the 'sniper' environment activator in $zshrc_file..."
    
    # Now, append the new, correct version of the function to the end of the file.
    cat << EOF >> "$zshrc_file"

# SNIPER_TOOLKIT_FUNCTION (Do not modify)
# Activates the SNIPER development environment.
sniper() {
    local SNIPER_ROOT="$sniper_root"

    if [[ "\$1" == "check" ]]; then
        # Special command to check dependencies without activating.
        (cd "\$SNIPER_ROOT" && python3 setup/setup.py check)
    else
        # The primary function: activate the Python virtual environment.
        # This modifies the current shell session.
        if [ -f "\$SNIPER_ROOT/bin/activate" ]; then
            source "\$SNIPER_ROOT/bin/activate"
        else
            echo -e "\033[0;31mSniper Error:\033[0m Activation script not found at \$SNIPER_ROOT/bin/activate" >&2
        fi
    fi
}
# END_SNIPER_TOOLKIT_FUNCTION

EOF
    print_success "Sniper command integrated successfully."
}

# --- Main Execution ---
main() {
    print_header
    run_setup
    run_build
    change_shell_to_zsh
    install_sniper_function

    echo -e "\n\n${C_GREEN}${C_BOLD}✅ SNIPER Toolkit installation complete!${C_RESET}"
    echo -e "--------------------------------------------------------------------------"
    echo -e "To activate the SNIPER environment, please first start a new Zsh session:"
    echo -e "  1. Close and reopen your terminal."
    echo -e "  2. Or run: ${C_YELLOW}zsh${C_RESET}"
    echo ""
    echo -e "Then, simply type the command below to activate the environment:"
    echo -e "  ${C_CYAN}sniper${C_RESET}"
    echo ""
    echo -e "After activation, all tools like 'run', 'find', 'dive' will be available."
    echo -e "--------------------------------------------------------------------------"
}

main
