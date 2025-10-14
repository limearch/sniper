/**
 * @file main.cpp
 * @brief The main entry point for the g-pass executable.
 */

#include "cli_handler.hpp"
#include "utils.hpp" // This now includes sniper_c_utils.h for logging

#include <iostream>
#include <exception>

// Define the global variable that will hold the tool's root path.
// It is declared as 'extern' in utils.hpp.
std::string G_TOOL_ROOT_PATH;

int main(int argc, char* argv[]) {
    // Determine and set the tool's root path at the very beginning.
    G_TOOL_ROOT_PATH = Utils::find_tool_root_path(argv[0]);
    if (G_TOOL_ROOT_PATH.empty()) {
        // Use the new central logger for critical startup errors.
        sniper_log(LOG_ERROR, "g-pass:init", "Critical: Could not determine the tool's installation directory.");
        sniper_log(LOG_ERROR, "g-pass:init", "Please ensure the executable is correctly placed or run from a standard location.");
        return 1;
    }

    try {
        // The CliHandler now only needs argc and argv for parsing.
        CliHandler handler(argc, argv);
        handler.run();
    } catch (const std::exception& e) {
        // Use the central logger for catching top-level exceptions.
        sniper_log(LOG_ERROR, "g-pass:main", "A critical error occurred: %s", e.what());
        return 1;
    }
    
    return 0;
}
