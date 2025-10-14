/**
 * @file utils.hpp
 * @brief Utility function declarations for the g-pass tool.
 *
 * This header defines the public interface for g-pass specific helper functions
 * and integrates the central SNIPER C utility library for common tasks like logging.
 */

#ifndef UTILS_HPP
#define UTILS_HPP

#include <string>

// --- C Utility Library Integration ---
// This block tells the C++ compiler that the functions declared in the included
// header use the C calling convention. This is crucial for linking C code with C++.
extern "C" {
    #include "sniper_c_utils.h"
}

// This global variable holds the absolute path to the tool's root directory.
// It is defined in main.cpp and used throughout the application to find resources.
extern std::string G_TOOL_ROOT_PATH;

// --- C++ Namespace for g-pass specific utilities ---
namespace Utils {

    /**
     * @brief Finds the absolute path of the tool's root directory (e.g., ".../sniper/tools/g-pass").
     * @param argv0 The first argument from main (the executable path).
     * @return A std::string containing the resolved absolute path.
     */
    std::string find_tool_root_path(const char* argv0);

    /**
     * @brief Executes a shell command and captures its standard output.
     * @param cmd The command to execute.
     * @return The standard output of the command as a std::string.
     * @throws std::runtime_error if popen() fails.
     */
    std::string exec_pipe(const std::string& cmd);

    /**
     * @brief Copies a string to the system clipboard.
     *        Supports `xclip` on Linux and `termux-clipboard-set` on Termux.
     * @param text The string to copy.
     * @return True on success, false on failure (e.g., no clipboard utility found).
     */
    bool copy_to_clipboard(const std::string& text);
    
    /**
     * @brief Checks if a filename ends with a specific extension.
     * @param filename The full filename.
     * @param ext The extension to check for (e.g., ".json").
     * @return True if the filename has the extension, false otherwise.
     */
    bool has_extension(const std::string& filename, const std::string& ext);

    /**
     * @brief Prints a formatted password line for standard/fast mode.
     * @param index The current password number.
     * @param total The total number of passwords being generated.
     * @param password The password string to print.
     */
    void print_password(int index, int total, const std::string& password);

    /**
     * @brief Prints a password for crunch mode (simple, for performance).
     * @param password The password string to print.
     */
    void print_password_crunch(const std::string& password);
    
    /**
     * @brief Parses a size string (e.g., "100M", "2G") into bytes.
     * @param size_str The string to parse.
     * @return The size in bytes as an unsigned long long.
     */
    unsigned long long parse_size_string(const std::string& size_str);

} // namespace Utils

#endif // UTILS_HPP
