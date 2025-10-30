/**
 * @file utils.cpp
 * @brief Implementation of utility functions for the g-pass tool.
 */

#include "utils.hpp"
#include <iostream>
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <array>
#include <cctype>
#include <unistd.h>
#include <libgen.h>
#include <climits>

// --- Function Implementations in Utils Namespace ---

std::string Utils::find_tool_root_path(const char* argv0) {
    char real_path_buf[PATH_MAX];
    char* real_path = nullptr;

    ssize_t len = readlink("/proc/self/exe", real_path_buf, sizeof(real_path_buf) - 1);
    if (len != -1) {
        real_path_buf[len] = '\0';
        real_path = real_path_buf;
    } else if (realpath(argv0, real_path_buf) != nullptr) {
        real_path = real_path_buf;
    } else {
        return ""; // Could not resolve path
    }

    // dirname can modify its argument, so we work on a copy
    char* path_copy1 = strdup(real_path);
    char* exec_dir = dirname(path_copy1); // -> .../bin
    char* path_copy2 = strdup(exec_dir);
    char* tool_root_cstr = dirname(path_copy2); // -> .../g-pass
    
    std::string tool_root_path;
    if (tool_root_cstr) {
        tool_root_path = std::string(tool_root_cstr);
    }
    
    free(path_copy1);
    free(path_copy2);
    
    return tool_root_path;
}

std::string Utils::exec_pipe(const std::string& cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    // Trim trailing newline
    if (!result.empty() && result.back() == '\n') {
        result.pop_back();
    }
    return result;
}

bool Utils::copy_to_clipboard(const std::string& text) {
    std::string command;
    // Use the central C utility to check for command existence
    if (sniper_command_exists("termux-clipboard-set")) {
        command = "echo \"" + text + "\" | termux-clipboard-set";
    } else if (sniper_command_exists("xclip")) {
        command = "echo \"" + text + "\" | xclip -selection clipboard";
    } else {
        // Use the central C logger for error reporting
        sniper_log(LOG_ERROR, "g-pass", "Clipboard utility (xclip or termux-clipboard-set) not found.");
        return false;
    }
    return system(command.c_str()) == 0;
}

bool Utils::has_extension(const std::string& filename, const std::string& ext) {
    if (filename.length() >= ext.length()) {
        return (0 == filename.compare(filename.length() - ext.length(), ext.length(), ext));
    }
    return false;
}

void Utils::print_password(int index, int total, const std::string& password) {
    // This function's formatting is specific to g-pass, so it remains here.
    // It uses the color codes defined in the central sniper_c_utils.h header.
    std::cout << C_CYAN << "[" << index << "/" << total << "] " 
              << C_RESET << C_BOLD << C_GREEN << password 
              << C_RESET << std::endl;
}

void Utils::print_password_crunch(const std::string& password) {
    // For crunch mode, performance is critical, so direct std::cout is optimal.
    std::cout << password << std::endl;
}

unsigned long long Utils::parse_size_string(const std::string& size_str) {
    if (size_str.empty()) return 0;
    
    char unit = std::toupper(size_str.back());
    std::string num_part = size_str;
    unsigned long long multiplier = 1;

    switch (unit) {
        case 'K': multiplier = 1024; num_part.pop_back(); break;
        case 'M': multiplier = 1024 * 1024; num_part.pop_back(); break;
        case 'G': multiplier = 1024 * 1024 * 1024; num_part.pop_back(); break;
    }

    try {
        return std::stoull(num_part) * multiplier;
    } catch (const std::exception&) {
        return 0; // Return 0 on parsing error
    }
}
