// File: main.c
// Entry point for the 'configer' utility.
// This file handles command-line argument parsing and dispatches actions
// to the appropriate functions defined in config.c.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libgen.h> // Required for dirname()
#include <unistd.h> // Required for readlink(), getcwd()
#include "config.h"

// Color definitions for status messages
#define C_GREEN "\x1B[32m"
#define C_WHITE "\x1B[37m"
#define C_RESET "\x1B[0m"

/**
 * @brief  Gets the absolute path of the 'sniper' project's root directory.
 * @note   It intelligently finds the root by traversing up from the executable's path.
 *         This makes the tool location-independent.
 * @param  executable_path The path the program was called with (argv[0]).
 * @param  buffer          A buffer to store the resulting path.
 * @param  buffer_size     The size of the buffer.
 * @retval 0 on success, 1 on failure.
 */
int get_sniper_base_path(const char* executable_path, char* buffer, size_t buffer_size) {
    char real_path[1024];
    char* final_path = NULL;

    // The most reliable method on Linux/Termux is to use /proc/self/exe
    ssize_t len = readlink("/proc/self/exe", real_path, sizeof(real_path) - 1);
    if (len != -1) {
        real_path[len] = '\0';
        final_path = real_path;
    } else if (realpath(executable_path, real_path) != NULL) {
        // Fallback method using realpath
        final_path = real_path;
    } else {
        // Last resort fallback (less reliable if called via symlink)
        final_path = strdup(executable_path);
        if (!final_path) return 1;
    }
    
    // Now that we have the full path to the executable,
    // traverse up the directory tree until we find the 'sniper' root folder.
    char* current_path = strdup(final_path);
    if (final_path != real_path) free(final_path); // Free only if allocated by strdup
    
    char* temp_path = current_path;
    while (temp_path != NULL && strcmp(temp_path, "/") != 0) {
        char* base = basename(temp_path);
        if (strcmp(base, "sniper") == 0) {
            strncpy(buffer, temp_path, buffer_size - 1);
            buffer[buffer_size - 1] = '\0';
            free(current_path);
            return 0; // Success: Found the path
        }
        // Go up one directory level
        temp_path = dirname(temp_path);
    }

    free(current_path);
    
    // If the loop fails, maybe the user is already inside the sniper dir.
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        if (strstr(cwd, "sniper") != NULL) {
             strncpy(buffer, cwd, buffer_size - 1);
             buffer[buffer_size - 1] = '\0';
             return 0;
        }
    }
    
    return 1; // Failure: Could not find the 'sniper' root directory
}

int main(int argc, char *argv[]) {
    char base_path[1024];
    // Determine the base path of the sniper project dynamically
    if (get_sniper_base_path(argv[0], base_path, sizeof(base_path)) != 0) {
        fprintf(stderr, "Error: Could not determine the SNIPER base directory.\n");
        fprintf(stderr, "Please run this tool from within the 'sniper' project directory.\n");
        // As a last resort, use the current directory
        strcpy(base_path, ".");
    }
    
    // Construct the full path to the configuration and log files
    char config_filepath[2048];
    // We assume a 'config' subdirectory in the project root for config files
    snprintf(config_filepath, sizeof(config_filepath), "%s/config/sniper-config.json", base_path);

    // If no arguments are provided, or 'help' is the command, show the help screen.
    if (argc < 2 || strcmp(argv[1], "help") == 0) {
        print_help(argv[0]);
        return (argc < 2); // Return 1 if no args, 0 if 'help' was explicit
    }

    // --- Command Dispatcher ---
    
    // Handle 'set' command
    if (strcmp(argv[1], "set") == 0 && argc == 5) {
        int result = set_value(config_filepath, base_path, argv[2], argv[3], argv[4]);
        if (result == 0) {
            printf(C_GREEN "✔ Success:" C_WHITE " Value was set successfully.\n" C_RESET);
        }
        return result;
    
    // Handle 'get' command
    } else if (strcmp(argv[1], "get") == 0 && argc == 4) {
        // The get_value function prints the output on its own
        return get_value(config_filepath, argv[2], argv[3]);
    
    // Handle 'delete' command
    } else if (strcmp(argv[1], "delete") == 0 && argc == 4) {
        int result = delete_value(config_filepath, base_path, argv[2], argv[3]);
        if (result == 0) {
            printf(C_GREEN "✔ Success:" C_WHITE " Value was deleted successfully.\n" C_RESET);
        }
        return result;
    
    // Handle any other invalid command structure
    } else {
        print_help(argv[0]);
        return 1;
    }
}
