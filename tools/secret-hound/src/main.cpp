/**
 * @file main.cpp
 * @brief The high-performance C++ core scanner for secret-hound.
 *
 * This executable is designed to be a silent worker. It accepts a path
 * as an argument, scans it for secrets based on rules, and prints any
 * findings as raw, line-delimited JSON to stdout. It is not intended
 * to be called directly by the user, but by a wrapper script.
 */

#include "hound_core/scanner.hpp"
#include "hound_core/rule_parser.hpp"
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <unistd.h>
#include <libgen.h>
#include <climits>
#include <sys/stat.h>

extern "C" {
    #include "sniper_c_utils.h"
}

// Prototypes
std::string find_tool_root_path(const char* argv0);

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <path_to_scan> [--rules /path/to/rules.json]\n", argv[0]);
        return 1;
    }

    const char* target_path = argv[1];
    const char* rules_file_path = NULL;

    // Manual, simple argument parsing for this internal tool.
    for (int i = 2; i < argc; ++i) {
        if (strcmp(argv[i], "--rules") == 0 && i + 1 < argc) {
            rules_file_path = argv[++i];
        }
    }

    try {
        std::string final_rules_path;
        if (rules_file_path) {
            final_rules_path = rules_file_path;
        } else {
            std::string tool_root = find_tool_root_path(argv[0]);
            if (!tool_root.empty()) {
                final_rules_path = tool_root + "/rules/default.json";
            } else {
                sniper_log(LOG_ERROR, "hound-core", "Cannot find default rules file without tool root path.");
                return 1;
            }
        }
        
        auto rules = RuleParser::parse_rules_from_file(final_rules_path);
        int num_threads = sysconf(_SC_NPROCESSORS_ONLN);
        
        Scanner scanner(rules, num_threads);
        
        struct stat s;
        if (stat(target_path, &s) == 0) {
            if (S_ISDIR(s.st_mode)) {
                scanner.scan_directory(target_path);
            } else if (S_ISREG(s.st_mode)) {
                ScanTaskArgs* task_args = new ScanTaskArgs{&scanner, std::string(target_path)};
                scanner.add_scan_task(task_args);
            }
            scanner.wait_for_completion();
        } else {
            sniper_log(LOG_ERROR, "hound-core", "Target path not found: %s", target_path);
            return 1;
        }
    } catch (const std::exception& e) {
        sniper_log(LOG_ERROR, "hound-core", "An exception occurred: %s", e.what());
        return 1;
    }

    return 0;
}

std::string find_tool_root_path(const char* argv0) {
    char real_path_buf[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", real_path_buf, sizeof(real_path_buf) - 1);
    if (len != -1) {
        real_path_buf[len] = '\0';
    } else if (realpath(argv0, real_path_buf) == nullptr) {
        return "";
    }
    char* path_copy1 = strdup(real_path_buf);
    if (!path_copy1) return "";
    char* exec_dir = dirname(path_copy1);
    
    char* path_copy2 = strdup(exec_dir);
    if (!path_copy2) { free(path_copy1); return ""; }
    char* tool_root_cstr = dirname(path_copy2);
    
    std::string tool_root_path(tool_root_cstr);
    
    free(path_copy1);
    free(path_copy2);
    
    return tool_root_path;
}