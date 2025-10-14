/**
 * @file cli_handler.hpp
 * @brief Defines the main command-line interface handler class for the g-pass tool.
 *
 * This class encapsulates all logic related to parsing command-line arguments,
 * managing different execution modes (fast, crunch, smart), and orchestrating
 * the password generation process.
 */

#ifndef CLI_HANDLER_HPP
#define CLI_HANDLER_HPP

#include "generator.hpp"
#include <string>
#include <vector>
#include <map>

/**
 * @struct CliOptions
 * @brief Holds all the parsed command-line options and configuration settings.
 */
struct CliOptions {
    // Action flags
    bool show_help = false;
    bool interactive_mode = false;
    bool copy_clipboard = false;
    int count = 1;
    
    // Core password configuration
    PasswordConfig pass_config;
    
    // File output options
    std::string save_file;
    std::string split_size_str;
    unsigned long long split_size_bytes = 0;
    
    // Special modes
    std::string preset;
    std::string smart_prompt;
    
    // Crunch mode settings
    bool is_crunch_mode = false;
    int crunch_min = 0;
    int crunch_max = 0;
    std::string crunch_charset;

    // Crunch pattern mode settings
    bool is_crunch_pattern_mode = false;
    std::string crunch_pattern;
};

/**
 * @class CliHandler
 * @brief Manages the application's lifecycle based on user input.
 */
class CliHandler {
public:
    /**
     * @brief Constructor that initializes the handler with command-line arguments.
     * @param argc The argument count from main().
     * @param argv The argument vector from main().
     */
    CliHandler(int argc, char** argv);

    /**
     * @brief The main execution entry point for the handler.
     *        This function dispatches to the correct mode based on parsed arguments.
     */
    void run();

private:
    // Member variables
    int original_argc; ///< Stores the original argument count to detect no-argument runs.
    CliOptions options; ///< Stores all parsed options and configurations.
    std::map<std::string, PasswordConfig> presets; ///< Stores predefined password configurations.

    // Private helper methods
    void parse_args(int argc, char** argv);
    void setup_presets();
    void run_interactive_mode();
    void run_crunch_mode();
    void run_fast_mode();
    void apply_preset(const std::string& preset_name);
};

#endif // CLI_HANDLER_HPP
