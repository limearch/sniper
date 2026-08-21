/**
 * @file main.cpp
 * @brief The C++ core scanner for secret-hound (CORRECTED).
 * - Fixes missing <sstream> header.
 * - Moves the directory_walk_callback function into this file where it is used.
 */

#include "hound_core/scanner.hpp"
#include "hound_core/rule_parser.hpp"
#include <iostream>
#include <string>
#include <cstring>
#include <vector>
#include <stdexcept>
#include <unistd.h>
#include <libgen.h>
#include <climits>
#include <sys/stat.h>
#include <algorithm>
#include <sstream> // <<< FIX 1: Added missing header for stringstream

extern "C" {
    #include "sniper_c_utils.h"
}

// Data structure to pass the scanner instance to the callback.
struct WalkData {
    Scanner* scanner_instance;
};

// <<< FIX 2: Moved the callback function from scanner.cpp to main.cpp >>>
// This function is called by `sniper_directory_walk` for every file system entry.
int directory_walk_callback(const WalkInfo* info, void* user_data) {
    if (!S_ISREG(info->stat_info.st_mode)) {
        return 0; // Continue walking, skip non-regular files.
    }
    
    WalkData* data = (WalkData*)user_data;
    Scanner* scanner = data->scanner_instance;
    
    // Create task arguments on the heap for the thread pool.
    ScanTaskArgs* task_args = new ScanTaskArgs{
        scanner,
        std::string(info->full_path)
    };

    // Add the file scanning task to the pool.
    scanner->add_scan_task(task_args);
    
    return 0; // Signal to continue the walk.
}

// Helper to split a C-style string by a delimiter
std::vector<std::string> split_string(const char* str, char delimiter) {
    std::vector<std::string> result;
    if (!str) return result;
    std::stringstream ss(str);
    std::string item;
    while (std::getline(ss, item, delimiter)) {
        result.push_back(item);
    }
    return result;
}

int main(int argc, char* argv[]) {
    // --- Argument Parsing (remains the same) ---
    const char* target_path = NULL;
    const char* rules_file_path = NULL;
    bool scan_stdin = false;
    const char* min_confidence_str = "low";
    const char* include_ids_str = NULL;
    bool no_hidden = false;

    SniperOption options[] = {
        {0,   "rules",      OPT_STRING, &rules_file_path,    "Path to a custom JSON rules file."},
        {0,   "scan-stdin", OPT_FLAG,   &scan_stdin,         "Scan content piped from standard input."},
        {'c', "confidence", OPT_STRING, &min_confidence_str, "Minimum confidence level (low, medium, high)."},
        {0,   "include",    OPT_STRING, &include_ids_str,    "Comma-separated rule IDs to include."},
        {0,   "no-hidden",  OPT_FLAG,   &no_hidden,          "Exclude hidden files and directories."},
        {0,   NULL,         (OptionType)0, NULL,             NULL}
    };
    
    int first_arg_idx = sniper_parse_options(argc, argv, options, "hound-core");

    if (!scan_stdin && first_arg_idx < argc) {
        target_path = argv[first_arg_idx];
    }
    
    if (!target_path && !scan_stdin) {
        sniper_log(LOG_ERROR, "hound-core", "No target path specified.");
        sniper_show_tool_help("hound-core");
        return 1;
    }

    try {
        // --- Rule Loading and Filtering (remains the same) ---
        std::string final_rules_path;
        if (rules_file_path) {
            final_rules_path = rules_file_path;
        } else {
            char root_path[PATH_MAX];
            if (sniper_get_root_path(root_path, sizeof(root_path)) == 0) {
                final_rules_path = std::string(root_path) + "/tools/secret-hound/rules/default.json";
            } else {
                sniper_log(LOG_ERROR, "hound-core", "Cannot find project root to load default rules.");
                return 1;
            }
        }
        
        auto all_rules = RuleParser::parse_rules_from_file(final_rules_path);
        std::vector<DetectionRule> filtered_rules;

        int min_confidence_level = (strcmp(min_confidence_str, "high") == 0) ? 2 :
                                   (strcmp(min_confidence_str, "medium") == 0) ? 1 : 0;
        
        std::vector<std::string> include_ids = split_string(include_ids_str, ',');

        for (const auto& rule : all_rules) {
            bool confidence_ok = rule.confidence_level >= min_confidence_level;
            bool id_ok = include_ids.empty() || (std::find(include_ids.begin(), include_ids.end(), rule.id) != include_ids.end());
            
            if (confidence_ok && id_ok) {
                filtered_rules.push_back(rule);
            }
        }
        
        if (filtered_rules.empty() && !all_rules.empty()) {
            sniper_log(LOG_WARN, "hound-core", "No rules match the specified filters. Scan will find nothing.");
        }
        
        // --- Scanner Initialization and Dispatch (remains the same, but with corrected walk logic) ---
        int num_threads = sysconf(_SC_NPROCESSORS_ONLN);
        Scanner scanner(filtered_rules, num_threads);
        
        if (scan_stdin) {
            std::string content((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
            scanner.scan_content(content, "stdin");
        } else {
            WalkOptions walk_opts = {.follow_symlinks = false, .skip_hidden = no_hidden, .max_depth = -1};
            
            struct stat s;
            if (stat(target_path, &s) == 0) {
                if (S_ISDIR(s.st_mode)) {
                    // --- FIX 2 (continued): Pass the correct user_data struct ---
                    WalkData walk_data = {&scanner};
                    sniper_directory_walk(target_path, &walk_opts, directory_walk_callback, &walk_data);
                } else if (S_ISREG(s.st_mode)) {
                    ScanTaskArgs* task_args = new ScanTaskArgs{&scanner, std::string(target_path)};
                    scanner.add_scan_task(task_args);
                }
                scanner.wait_for_completion();
            } else {
                sniper_log(LOG_ERROR, "hound-core", "Target path not found: %s", target_path);
                return 1;
            }
        }
    } catch (const std::exception& e) {
        sniper_log(LOG_ERROR, "hound-core", "A critical exception occurred: %s", e.what());
        return 1;
    }

    return 0;
}
