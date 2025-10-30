#!/bin/bash

# ==============================================================================
# SNIPER Toolkit - Universal Installer (v1.2 - With Detailed Logging)
#
# This script automates the full setup of the SNIPER environment and logs
# the entire process to config/.sniper-install.log for easy debugging.
# ==============================================================================

# --- Log File Configuration ---
LOG_FILE="config/.sniper-install.log"

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

# --- Logging Helper Function ---
# Usage: log_msg "LEVEL" "Message"
log_msg() {
    local level="$1"
    local message="$2"
    # Append formatted message with timestamp to the log file
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [$level] - $message" >> "$LOG_FILE"
}

# --- Output Formatting Helper Functions (for console) ---
print_header() {
    echo -e "${C_MAGENTA}
╭───────────────────────────────────────────────────╮
│   ${C_BOLD}SNIPER Toolkit :: Professional Setup Utility${C_RESET}${C_MAGENTA}   │
╰───────────────────────────────────────────────────╯
${C_RESET}"
}

print_stage() {
    echo -e "\n${C_BLUE}${C_BOLD}--- [ STAGE: $1 ] ---${C_RESET}"
    log_msg "INFO" "==================== START STAGE: $1 ===================="
}

print_success() {
    echo -e "  ${C_GREEN}[✔] Success:${C_RESET} $1"
    log_msg "SUCCESS" "$1"
}

print_error() {
    echo -e "  ${C_RED}[✘] Error:${C_RESET} $1" >&2
    log_msg "ERROR" "$1"
}

print_info() {
    echo -e "  ${C_CYAN}[i] Info:${C_RESET} $1"
    log_msg "INFO" "$1"
}

# --- Core Installation Functions (Modified for Logging) ---

run_setup() {
    print_stage "Installing Dependencies"
    if [ ! -f "setup/setup.py" ]; then
        print_error "setup/setup.py not found. Please run from the project root."
        exit 1
    fi
    
    local cmd="python3 setup/setup.py"
    print_info "Running dependency installer..."
    log_msg "CMD" "$cmd"
    
    echo -e "${C_GREY}▼▼▼ Running setup.py (output also in log file) ▼▼▼${C_RESET}"
    
    # Execute and redirect both stdout and stderr to the log file, and also show on screen
    if ! ($cmd 2>&1 | tee -a "$LOG_FILE"); then
        echo -e "${C_GREY}▲▲▲ End of setup.py output ▲▲▲${C_RESET}"
        print_error "Dependency installation failed. Please check the log file for details: $LOG_FILE"
        exit 1
    fi
    
    echo -e "${C_GREY}▲▲▲ End of setup.py output ▲▲▲${C_RESET}"
    print_success "All dependencies are installed."
}

run_build() {
    print_stage "Building Project Tools"
    local build_script="setup/build"
    if [ ! -f "$build_script" ]; then
        print_error "$build_script not found. Cannot compile tools."
        exit 1
    fi
    
    # Build central C utility library first
	local c_utils_dir="lib/c_utils"
	if [ -d "$c_utils_dir" ]; then
	    print_info "Building central C utility library (libsniper_c_utils.a)..."
        local make_cmd="(cd \"$c_utils_dir\" && make clean && make)"
        log_msg "CMD" "$make_cmd"
        
        if ! (eval "$make_cmd" >> "$LOG_FILE" 2>&1); then
            print_error "Failed to build the central C utility library. Check log for details."
            exit 1
        fi
	    print_success "Central C library built successfully."
	fi

    print_info "Ensuring output 'bin/' directories exist for all tools..."
    # This part doesn't produce much output, so we just log it.
    find tools -mindepth 1 -maxdepth 1 -type d -exec mkdir -p {}/bin \;
    print_success "All tool 'bin/' directories are confirmed to exist."

    chmod +x "$build_script"
    print_info "Compiling all C/C++ tools..."
    log_msg "CMD" "./$build_script"
    
    echo -e "${C_GREY}▼▼▼ Running build script (output also in log file) ▼▼▼${C_RESET}"
    
    if ! (./"$build_script" 2>&1 | tee -a "$LOG_FILE"); then
        echo -e "${C_GREY}▲▲▲ End of build output ▲▲▲${C_RESET}"
        print_error "Build process failed. Please check the log file for details: $LOG_FILE"
        exit 1
    fi

    echo -e "${C_GREY}▲▲▲ End of build output ▲▲▲${C_RESET}"
    print_success "All tools have been compiled and are ready."
}
# ==============================================================================
# FUNCTION: install_zsh_plugins (v1.1 - Platform Aware)
# Description: Downloads and installs essential Zsh plugins and tools.
#              It now uses the native package manager for Termux for fzf/zoxide.
# ==============================================================================
# ==============================================================================
# FUNCTION: install_zsh_plugins (v2.0 - Self-Contained & Robust)
# Description: Downloads and installs essential Zsh plugins directly into the
#              SNIPER environment's 'share/zsh-plugins' directory.
#              Installs companion tools like zoxide using the system's package manager.
# ==============================================================================
install_zsh_plugins() {
    print_stage "Installing Zsh Plugins & Power Tools"
    
    # Define the target directory for plugins relative to the project root
    local plugins_dir="share/zsh-plugins"
    mkdir -p "$plugins_dir"
    log_msg "INFO" "Plugin directory ensured at: $plugins_dir"

    # --- Helper function for cloning git repositories into the plugins directory ---
    # Usage: clone_plugin "display_name" "git_url" ["target_folder_name"]
    clone_plugin() {
        local display_name="$1"
        local url="$2"
        # Use provided folder name or derive from URL
        local folder_name="${3:-$(basename "$url" .git)}"
        local target_dir="${plugins_dir}/${folder_name}"

        if [ -d "$target_dir/.git" ]; then
            print_info "Plugin '$display_name' already exists. Skipping."
            log_msg "INFO" "Skipping clone for '$display_name', directory exists: $target_dir"
        else
            print_info "Downloading plugin '$display_name'..."
            log_msg "CMD" "git clone --depth=1 $url $target_dir"
            if git clone --depth=1 "$url" "$target_dir" >> "$LOG_FILE" 2>&1; then
                print_success "Plugin '$display_name' downloaded successfully to '$target_dir'."
            else
                print_error "Failed to download plugin '$display_name'. Check log for details."
                # Clean up partially cloned directory on failure
                rm -rf "$target_dir"
            fi
        fi
    }

    # --- 1. Install ALL Zsh-based Plugins into share/zsh-plugins/ ---
    # This includes fzf, which provides zsh scripts for integration.
    # The 'activate' script will source them from this local directory.
    print_info "Cloning Zsh plugins into the local environment..."
    clone_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions.git"
    clone_plugin "zsh-syntax-highlighting" "https://github.com/zsh-users/zsh-syntax-highlighting.git"
    clone_plugin "zsh-completions" "https://github.com/zsh-users/zsh-completions.git"
    clone_plugin "Powerlevel10k" "https://github.com/romkatv/powerlevel10k.git"
    
    # fzf is treated as a plugin here because we only need its zsh integration scripts.
    # The fzf binary itself will be installed as a separate tool.
    clone_plugin "fzf-zsh-scripts" "https://github.com/junegunn/fzf.git" "fzf"


    # --- 2. Install Companion Tool Binaries (fzf & zoxide) ---
    # These are standalone programs that our zsh scripts will use.
    # We use the system's package manager for them as it's the most reliable way.
    
    # Helper function to install a package if it's not already present
    install_package() {
        local pkg_name="$1"
        if command -v "$pkg_name" &> /dev/null; then
            print_info "Tool '$pkg_name' is already installed. Skipping."
        else
            print_info "Installing tool '$pkg_name' using pkg..."
            log_msg "CMD" "pkg install -y $pkg_name"
            if pkg install -y "$pkg_name" >> "$LOG_FILE" 2>&1; then
                print_success "'$pkg_name' installed successfully via pkg."
            else
                print_error "Failed to install '$pkg_name' via pkg. Check log."
            fi
        fi
    }
    
    # We are assuming a Termux/Debian-like environment that uses 'pkg' or 'apt'
    # The logic can be expanded for other package managers if needed.
    install_package "fzf"
    install_package "zoxide"

    print_success "All Zsh plugins and tools have been processed."
}
change_shell_to_zsh() {
    print_stage "Configuring Shell Environment"
    if ! command -v zsh &> /dev/null; then
        print_error "Zsh is not installed. The setup script should have installed it."
        print_info "Please install it manually and re-run."
        exit 1
    fi

    local zsh_path
    zsh_path=$(which zsh)

    if [[ "$SHELL" == *"/zsh"* ]]; then
        print_info "Default shell is already Zsh. Skipping change."
    else
        print_info "Changing default shell to Zsh..."
        local chsh_cmd="chsh -s zsh"
        log_msg "CMD" "$chsh_cmd"
        
        # Capture output for logging
        chsh_output=$(chsh -s zsh 2>&1)
        local chsh_status=$?

        log_msg "INFO" "chsh output: $chsh_output"
        if [ $chsh_status -eq 0 ]; then
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
    sniper_root=$(pwd)

    touch "$zshrc_file"
    log_msg "INFO" "Target .zshrc file: $zshrc_file"

    if grep -q "# SNIPER_TOOLKIT_FUNCTION" "$zshrc_file" 2>/dev/null; then
        print_info "Found an existing 'sniper' function. Removing it before updating..."
        # Use a temporary file for sed to be compatible with both GNU and BSD sed
        sed -i.bak '/# SNIPER_TOOLKIT_FUNCTION/,/# END_SNIPER_TOOLKIT_FUNCTION/d' "$zshrc_file"
        log_msg "SUCCESS" "Old function block removed from .zshrc. Backup created at ${zshrc_file}.bak"
    fi

    print_info "Adding/Updating the 'sniper' environment activator in $zshrc_file..."
    
    # The new function block to be added
    local sniper_function_block
    read -r -d '' sniper_function_block << EOF

# SNIPER_TOOLKIT_FUNCTION (Do not modify)
# Activates the SNIPER development environment and handles updates.
sniper() {
    local SNIPER_ROOT="$sniper_root"

    # --- Update Commands ---
    if [[ "\$1" == "update" ]]; then
        (cd "\$SNIPER_ROOT" && ./setup/update.sh run)
        return
    fi
    if [[ "\$1" == "check-update" ]]; then
        (cd "\$SNIPER_ROOT" && python3 setup/check_update.py check-update)
        return
    fi

    # --- Automatic, silent update check ---
    (cd "\$SNIPER_ROOT" && python3 setup/check_update.py &) &>/dev/null

    # --- Original Commands ---
    if [[ "\$1" == "check" ]]; then
        (cd "\$SNIPER_ROOT" && python3 setup/setup.py check)
    else
        # Primary function: activate the environment
        if [ -d "\$SNIPER_ROOT" ]; then
            source "\$SNIPER_ROOT/bin/activate"
        else
            echo -e "\033[0;31mSniper Error:\033[0m Virtual environment not found at \$SNIPER_ROOT/.venv" >&2
        fi
    fi
}
# END_SNIPER_TOOLKIT_FUNCTION
EOF

    # Append the block to .zshrc and log it
    echo "$sniper_function_block" >> "$zshrc_file"
    log_msg "INFO" "Appended new function block to .zshrc."
    
    print_success "Sniper command integrated successfully."
    print_info "Please start a new shell session (or run 'source ~/.zshrc') for changes to take effect."
}

# --- Main Execution ---
main() {
    # Ensure config directory exists
    mkdir -p config
    # Start with a clean log file
    echo "" > "$LOG_FILE"
    
    log_msg "INFO" "SNIPER Toolkit Installation Started"
    log_msg "INFO" "Installer Version: 1.2"
    log_msg "INFO" "Timestamp: $(date)"
    log_msg "INFO" "--------------------------------------"
    
    print_header
    
    run_setup
    run_build
    install_zsh_plugins
    change_shell_to_zsh
    install_sniper_function

    log_msg "INFO" "==================== INSTALLATION COMPLETE ===================="
    
    echo -e "\n\n${C_GREEN}${C_BOLD}✅ SNIPER Toolkit installation complete!${C_RESET}"
    echo -e "--------------------------------------------------------------------------"
    echo -e "A detailed installation report has been saved to:${C_YELLOW} $LOG_FILE ${C_RESET}"
    echo -e "To activate the SNIPER environment, please first start a new Zsh session:"
    echo -e "  1. Close and reopen your terminal."
    echo -e "  2. Or run: ${C_YELLOW}zsh${C_RESET}"
    echo ""
    echo -e "Then, simply type the command below to activate the environment:"
    echo -e "  ${C_CYAN}sniper${C_RESET}"
    echo -e "--------------------------------------------------------------------------"
}

# Run the main function and handle Ctrl+C
trap 'echo -e "\n${C_YELLOW}Installation aborted by user.${C_RESET}"; log_msg "WARN" "Installation aborted by user."; exit 1' INT
main
trap - INT # Disable trap on normal exit
