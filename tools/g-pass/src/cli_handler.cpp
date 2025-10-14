/**
 * @file cli_handler.cpp
 * @brief Implementation of the command-line interface logic for g-pass.
 */

#include "cli_handler.hpp"
#include "utils.hpp" // Includes sniper_c_utils.h for logging and help

#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <stdexcept>

/**
 * @brief Constructs the CliHandler, setting up presets and parsing arguments.
 * @param argc The argument count from main().
 * @param argv The argument vector from main().
 */
CliHandler::CliHandler(int argc, char** argv) : original_argc(argc) {
    setup_presets();
    parse_args(argc, argv);
}

/**
 * @brief Initializes the map of predefined password configurations.
 */
void CliHandler::setup_presets() {
    presets["human"] = {16, true, false, true, false, false, ""}; 
    presets["human"].use_symbols = true;
    presets["email"] = {18, true, true, true, true, false, ""};
    presets["wifi"] = {12, true, true, true, false, false, "Il1O0"};
    presets["random"] = {24, true, true, true, true, false, ""};
}

/**
 * @brief Parses command-line arguments and populates the `options` struct.
 */
void CliHandler::parse_args(int argc, char** argv) {
    std::vector<std::string> args(argv + 1, argv + argc);
    for (size_t i = 0; i < args.size(); ++i) {
        const std::string& arg = args[i];

        auto has_next_arg = [&](const std::string& option) {
            if (i + 1 < args.size()) return true;
            sniper_log(LOG_ERROR, "g-pass", "Option '%s' requires an argument.", option.c_str());
            options.show_help = true;
            return false;
        };

        if (arg == "-h" || arg == "--help") { options.show_help = true; break; }
        else if (arg == "-i" || arg == "--interactive") options.interactive_mode = true;
        else if (arg == "-c" || arg == "--copy") options.copy_clipboard = true;
        else if ((arg == "-l" || arg == "--length") && has_next_arg(arg)) options.pass_config.length = std::stoi(args[++i]);
        else if ((arg == "-n" || arg == "--count") && has_next_arg(arg)) options.count = std::stoi(args[++i]);
        else if ((arg == "--save") && has_next_arg(arg)) options.save_file = args[++i];
        else if ((arg == "--split-size") && has_next_arg(arg)) options.split_size_str = args[++i];
        else if ((arg == "-p" || arg == "--preset") && has_next_arg(arg)) options.preset = args[++i];
        else if ((arg == "-e" || arg == "--exclude") && has_next_arg(arg)) options.pass_config.exclude_chars = args[++i];
        else if (arg == "--no-lower") options.pass_config.use_lower = false;
        else if (arg == "--no-upper") options.pass_config.use_upper = false;
        else if (arg == "--no-numbers") options.pass_config.use_numbers = false;
        else if (arg == "--no-symbols") options.pass_config.use_symbols = false;
        else if (arg == "--unicode") options.pass_config.use_unicode = true;
        else if (arg == "--smart" && has_next_arg(arg)) options.smart_prompt = args[++i];
        else if (arg == "--crunch" && i + 2 < args.size()) {
            options.is_crunch_mode = true;
            options.crunch_min = std::stoi(args[++i]);
            options.crunch_max = std::stoi(args[++i]);
            options.crunch_charset = args[++i];
        } else if (arg == "--crunch-pattern" && has_next_arg(arg)) {
            options.is_crunch_pattern_mode = true;
            options.crunch_pattern = args[++i];
        } else {
            sniper_log(LOG_ERROR, "g-pass", "Unknown or invalid argument: %s", arg.c_str());
            options.show_help = true;
            break;
        }
    }
    if (!options.split_size_str.empty()) {
        options.split_size_bytes = Utils::parse_size_string(options.split_size_str);
    }
}

void CliHandler::run_interactive_mode() {
    sniper_log(LOG_WARN, "g-pass", "Interactive mode is not yet fully implemented. Please use CLI arguments.");
}

void CliHandler::apply_preset(const std::string& preset_name) {
    if (presets.count(preset_name)) {
        options.pass_config = presets[preset_name];
        sniper_log(LOG_INFO, "g-pass", "Applied preset '%s'.", preset_name.c_str());
    } else {
        sniper_log(LOG_ERROR, "g-pass", "Unknown preset: '%s'.", preset_name.c_str());
        options.show_help = true;
    }
}

void CliHandler::run_crunch_mode() {
    PasswordGenerator generator;
    
    unsigned long long total = 0;
    if (options.is_crunch_mode) {
        total = generator.calculate_crunch_total(options.crunch_min, options.crunch_max, options.crunch_charset);
    }

    if (total > 1000000) {
        sniper_log(LOG_WARN, "g-pass", "This operation will generate %llu passwords.", total);
        std::cout << "This may take a long time and produce a very large file. Continue? [y/N]: ";
        char confirm = 'n';
        std::cin >> confirm;
        if (confirm != 'y' && confirm != 'Y') {
            sniper_log(LOG_INFO, "g-pass", "Operation cancelled.");
            return;
        }
    }
    
    bool use_python_handler = !options.save_file.empty() && 
                              (Utils::has_extension(options.save_file, ".json") || 
                               Utils::has_extension(options.save_file, ".csv") || 
                               options.split_size_bytes > 0);

    if (use_python_handler) {
        sniper_log(LOG_INFO, "g-pass", "Piping output to Python file handler for advanced formatting/splitting...");
        
        std::string format = "txt";
        if (Utils::has_extension(options.save_file, ".json")) format = "json";
        if (Utils::has_extension(options.save_file, ".csv")) format = "csv";

        std::string python_cmd = "python3 " + G_TOOL_ROOT_PATH + "/src/file_handler.py --output \"" + options.save_file + "\" --format " + format;
        if (options.split_size_bytes > 0) {
            python_cmd += " --split-size " + std::to_string(options.split_size_bytes);
        }

        FILE* pipe = popen(python_cmd.c_str(), "w");
        if (!pipe) {
            sniper_log(LOG_ERROR, "g-pass", "Failed to open pipe to Python script.");
            return;
        }

        auto callback = [&](const std::string& pwd) { fprintf(pipe, "%s\n", pwd.c_str()); };
        
        if (options.is_crunch_mode) generator.generate_crunch(options.crunch_min, options.crunch_max, options.crunch_charset, callback);
        else if (options.is_crunch_pattern_mode) generator.generate_crunch_pattern(options.crunch_pattern, callback);
        
        pclose(pipe);
        sniper_log(LOG_SUCCESS, "g-pass", "File generation complete.");

    } else {
        std::ofstream outfile;
        if (!options.save_file.empty()) {
            outfile.open(options.save_file);
            if (!outfile.is_open()) {
                sniper_log(LOG_ERROR, "g-pass", "Failed to open output file: %s", options.save_file.c_str());
                return;
            }
        }
        
        auto& out_stream = options.save_file.empty() ? std::cout : outfile;
        auto callback = [&](const std::string& pwd) { out_stream << pwd << std::endl; };

        if (options.is_crunch_mode) generator.generate_crunch(options.crunch_min, options.crunch_max, options.crunch_charset, callback);
        else if (options.is_crunch_pattern_mode) generator.generate_crunch_pattern(options.crunch_pattern, callback);
        
        if(outfile.is_open()) {
            outfile.close();
            sniper_log(LOG_SUCCESS, "g-pass", "Passwords saved to %s", options.save_file.c_str());
        }
    }
}

void CliHandler::run_fast_mode() {
    PasswordGenerator generator;
    std::vector<std::string> passwords;
    
    for (int i = 0; i < options.count; ++i) {
        passwords.push_back(generator.generate(options.pass_config));
    }
    
    std::cout << std::endl;
    for (size_t i = 0; i < passwords.size(); ++i) {
        Utils::print_password(i + 1, passwords.size(), passwords[i]);
    }
    std::cout << std::endl;

    if (options.copy_clipboard && !passwords.empty()) {
        if(Utils::copy_to_clipboard(passwords[0])) {
            sniper_log(LOG_SUCCESS, "g-pass", "First password copied to clipboard.");
        }
    }
    
    if (!options.save_file.empty()) {
        std::string cmd = "python3 " + G_TOOL_ROOT_PATH + "/src/file_handler.py --output \"" + options.save_file + "\"";
        if (Utils::has_extension(options.save_file, ".json")) cmd += " --format json";
        else if (Utils::has_extension(options.save_file, ".csv")) cmd += " --format csv";
        
        FILE* pipe = popen(cmd.c_str(), "w");
        if (!pipe) { sniper_log(LOG_ERROR, "g-pass", "Failed to open pipe to Python script."); return; }
        for(const auto& pwd : passwords) { fprintf(pipe, "%s\n", pwd.c_str()); }
        pclose(pipe);
        sniper_log(LOG_SUCCESS, "g-pass", "Passwords saved to %s", options.save_file.c_str());
    }
}

void CliHandler::run() {
    // If --help is passed, or if the program is run with no arguments, show help.
    if (options.show_help || original_argc == 1) {
        sniper_show_tool_help("g-pass");
        return;
    }

    if (options.interactive_mode) {
        run_interactive_mode();
    }
    
    if (!options.preset.empty()) {
        apply_preset(options.preset);
        if (options.show_help) return; // Exit if preset was invalid
    }

    // Dispatch to the correct generation mode
    if (options.is_crunch_mode || options.is_crunch_pattern_mode) {
        run_crunch_mode();
    } else if (!options.smart_prompt.empty()) {
        sniper_log(LOG_INFO, "g-pass", "Engaging smart generator for prompt: \"%s\"", options.smart_prompt.c_str());
        std::string cmd = "python3 " + G_TOOL_ROOT_PATH + "/smart_generator/smart_generator.py \"" + options.smart_prompt + "\"";
        try {
            std::string password = Utils::exec_pipe(cmd);
            if (!password.empty()) {
                 std::cout << std::endl;
                 Utils::print_password(1, 1, password);
                 std::cout << std::endl;
                 if (options.copy_clipboard && Utils::copy_to_clipboard(password)) {
                     sniper_log(LOG_SUCCESS, "g-pass", "Password copied to clipboard.");
                 }
                 // Logic for saving smart password...
            } else {
                sniper_log(LOG_ERROR, "g-pass", "Smart generator failed to produce a password.");
            }
        } catch (const std::runtime_error& e) {
            sniper_log(LOG_ERROR, "g-pass", "Failed to execute smart generator: %s", e.what());
        }
    } else {
        run_fast_mode();
    }
}
