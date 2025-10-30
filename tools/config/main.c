/**
 * @file main.c
 * @brief Main entry point for the 'configer' utility.
 *
 * This file handles command-line argument parsing and dispatches actions
 * to the appropriate functions defined in config.c. It has been refactored
 * to rely entirely on the sniper_c_utils library for its core functionality.
 */

#include "config.h"
#include "sniper_c_utils.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

int main(int argc, char *argv[]) {
    // Determine the absolute path to the sniper-config.json file
    char root_path[PATH_MAX];
    if (sniper_get_root_path(root_path, sizeof(root_path)) != 0) {
        sniper_log(LOG_ERROR, "configer", "Could not determine the SNIPER project root directory.");
        sniper_log(LOG_WARN, "configer", "Please run this tool from within the 'sniper' project structure.");
        return 1;
    }
    
    char config_filepath[PATH_MAX];
    snprintf(config_filepath, sizeof(config_filepath), "%s/config/sniper-config.json", root_path);

    // Show help if no command is provided
    if (argc < 2) {
        sniper_show_tool_help("configer");
        return 1;
    }

    // --- Command Dispatcher ---
    const char* command = argv[1];

    if (strcmp(command, "help") == 0) {
        sniper_show_tool_help("configer");
        return 0;
    
    } else if (strcmp(command, "set") == 0 && argc == 5) {
        int result = set_value(config_filepath, argv[2], argv[3], argv[4]);
        if (result == 0) {
            sniper_log(LOG_SUCCESS, "configer", "Value set successfully.");
        }
        return result;
    
    } else if (strcmp(command, "get") == 0 && argc == 4) {
        return get_value(config_filepath, argv[2], argv[3]);
    
    } else if (strcmp(command, "delete") == 0 && argc == 4) {
        int result = delete_value(config_filepath, argv[2], argv[3]);
        if (result == 0) {
            sniper_log(LOG_SUCCESS, "configer", "Value deleted successfully.");
        }
        return result;
    
    } else {
        // Handle any other invalid command structure
        sniper_log(LOG_ERROR, "configer", "Invalid command or number of arguments.");
        sniper_show_tool_help("configer");
        return 1;
    }
}
