/**
 * @file sniper_c_utils.c
 * @brief Implementation of the SNIPER core C utility library.
 *
 * This file contains the logic for logging, option parsing, help rendering,
 * and directory traversal functions declared in sniper_c_utils.h.
 */

#include "sniper_c_utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libgen.h>
#include <limits.h>
#include <time.h>
#include <getopt.h> // Required for sniper_parse_options

// ==============================================================================
//                              Logging Subsystem
// ==============================================================================

void sniper_log(LogLevel level, const char* tool_name, const char* format, ...) {
    va_list args;
    va_start(args, format);

    // Default to stderr for all log messages
    FILE* output_stream = stderr;

    // Select color and prefix based on log level
    const char* color = C_WHITE;
    const char* prefix = ".....";

    switch (level) {
        case LOG_DEBUG:   color = C_CYAN;    prefix = "DEBUG";   break;
        case LOG_INFO:    color = C_BLUE;    prefix = "INFO";    break;
        case LOG_SUCCESS: color = C_GREEN;   prefix = "SUCCESS"; break;
        case LOG_WARN:    color = C_YELLOW;  prefix = "WARN";    break;
        case LOG_ERROR:   color = C_RED;     prefix = "ERROR";   break;
        case LOG_UPDATE:  color = C_GREEN;   prefix = "UPDATE";  break;
    }

    // Print the formatted log message
    fprintf(output_stream, "%s%s[%s]%s %s%s[%s]%s ", C_BOLD, color, prefix, C_RESET, C_BOLD, C_CYAN, tool_name, C_RESET);
    vfprintf(output_stream, format, args);
    fprintf(output_stream, "\n");

    va_end(args);
}

void sniper_log_config_update(const char* action, const char* category, const char* key, const char* value, const char* source) {
    char root_path[PATH_MAX];
    if (sniper_get_root_path(root_path, sizeof(root_path)) != 0) {
        sniper_log(LOG_ERROR, "c_utils", "Could not determine project root to log config update.");
        return;
    }

    char log_filepath[PATH_MAX];
    snprintf(log_filepath, sizeof(log_filepath), "%s/config/sniper-config.log", root_path);

    FILE *log_file = fopen(log_filepath, "a");
    if (!log_file) return; // Fail silently if log file can't be opened

    time_t now = time(NULL);
    char time_str[20];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&now));

    if (strcmp(action, "SET") == 0 && value) {
        fprintf(log_file, "[%s] - [UPDATE] - [%s] - SET: category='%s' key='%s' value='%s'\n", time_str, source, category, key, value);
    } else if (strcmp(action, "DELETE") == 0) {
        fprintf(log_file, "[%s] - [UPDATE] - [%s] - DELETE: category='%s' key='%s'\n", time_str, source, category, key);
    }

    fclose(log_file);
}

// ==============================================================================
//                         Command-Line Option Parsing
// ==============================================================================

int sniper_parse_options(int argc, char* argv[], SniperOption options[], const char* tool_name) {
    int num_options = 0;
    while (options[num_options].long_name != NULL) {
        num_options++;
    }

    // Allocate for user options + help option + NULL terminator
    struct option* long_options = calloc(num_options + 2, sizeof(struct option));
    char* short_opts_str = malloc(num_options * 2 + 2);
    if (!long_options || !short_opts_str) {
        sniper_log(LOG_ERROR, "c_utils", "Memory allocation failed in option parser.");
        exit(1);
    }

    strcpy(short_opts_str, "h"); // Always add 'h' for help

    for (int i = 0; i < num_options; ++i) {
        long_options[i].name = options[i].long_name;
        long_options[i].has_arg = (options[i].type == OPT_FLAG) ? no_argument : required_argument;
        long_options[i].flag = NULL;
        // CRITICAL FIX: Assign a unique, non-character value for long-only options
        // We use an arbitrary range (e.g., 256+) to avoid collision with ASCII chars.
        long_options[i].val = (options[i].short_name != 0) ? options[i].short_name : (256 + i);

        if (options[i].short_name != 0) {
            char temp_short[3] = {0};
            temp_short[0] = options[i].short_name;
            if (options[i].type != OPT_FLAG) {
                temp_short[1] = ':';
            }
            strcat(short_opts_str, temp_short);
        }
    }

    long_options[num_options] = (struct option){"help", no_argument, 0, 'h'};
    long_options[num_options + 1] = (struct option){0, 0, 0, 0};

    int opt;
    optind = 1;
    while ((opt = getopt_long(argc, argv, short_opts_str, long_options, NULL)) != -1) {
        if (opt == 'h') {
            sniper_show_tool_help(tool_name);
            exit(0);
        }
        if (opt == '?') {
            // getopt_long already prints an error, so we just exit.
            exit(1);
        }

        bool found = false;
        for (int i = 0; i < num_options; ++i) {
            // Check against both the short name and the unique value for long-only options
            if (opt == options[i].short_name || opt == long_options[i].val) {
                switch (options[i].type) {
                    case OPT_FLAG:   *((bool*)options[i].value_ptr) = true; break;
                    case OPT_STRING: *((const char**)options[i].value_ptr) = optarg; break;
                    case OPT_INT:    *((int*)options[i].value_ptr) = atoi(optarg); break;
                }
                found = true;
                break;
            }
        }
    }

    free(long_options);
    free(short_opts_str);

    return optind;
}                   
// ==============================================================================
//                        Directory Traversal Subsystem
// ==============================================================================

// This is a private helper function for the public-facing sniper_directory_walk.
static int walk_recursive(const char* base_path, char* current_path, int depth, const WalkOptions* options, WalkCallback callback, void* user_data) {
    DIR *dir = opendir(current_path);
    if (!dir) {
        sniper_log(LOG_WARN, "c_utils:walk", "Could not open directory: %s", current_path);
        return 0; // Don't stop the whole walk, just skip this directory
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        // Skip '.' and '..' directories
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        // Skip hidden files if requested
        if (options->skip_hidden && entry->d_name[0] == '.') {
            continue;
        }
        
        WalkInfo info;
        char full_path_buf[PATH_MAX];
        snprintf(full_path_buf, sizeof(full_path_buf), "%s/%s", current_path, entry->d_name);

        if (lstat(full_path_buf, &info.stat_info) != 0) {
            sniper_log(LOG_WARN, "c_utils:walk", "Could not stat: %s", full_path_buf);
            continue;
        }

        info.root_path = base_path;
        info.full_path = full_path_buf;
        // Calculate relative path. Handle the root case where it would be empty.
        if (strcmp(base_path, current_path) == 0) {
            info.relative_path = (char*)entry->d_name;
        } else {
            info.relative_path = full_path_buf + strlen(base_path) + 1; // +1 for the '/'
        }
        info.filename = entry->d_name;
        info.depth = depth;

        int callback_result = callback(&info, user_data);
        if (callback_result != 0) {
            closedir(dir);
            return callback_result; // Propagate stop signal
        }

        // --- Recurse into subdirectories ---
        bool is_dir = S_ISDIR(info.stat_info.st_mode);
        bool is_link = S_ISLNK(info.stat_info.st_mode);
        
        // Recurse if it's a directory, and it's not a symlink we're supposed to ignore
        if (is_dir && !(is_link && !options->follow_symlinks)) {
            if (options->max_depth == -1 || depth < options->max_depth) {
                int result = walk_recursive(base_path, full_path_buf, depth + 1, options, callback, user_data);
                if (result != 0) {
                    closedir(dir);
                    return result; // Propagate stop signal
                }
            }
        }
    }

    closedir(dir);
    return 0;
}

int sniper_directory_walk(const char* root_path, const WalkOptions* options_in, WalkCallback callback, void* user_data) {
    // Use default options if none are provided
    WalkOptions default_options = { .follow_symlinks = false, .skip_hidden = true, .max_depth = -1 };
    const WalkOptions* options = (options_in) ? options_in : &default_options;
    
    char path_buf[PATH_MAX];
    strncpy(path_buf, root_path, sizeof(path_buf) -1);
    path_buf[sizeof(path_buf) -1] = '\0';
    
    // Start the recursive walk
    return walk_recursive(root_path, path_buf, 0, options, callback, user_data);
}

// ==============================================================================
//                              General Utilities
// ==============================================================================

int sniper_get_root_path(char* buffer, size_t buffer_size) {
    char executable_path[PATH_MAX];
    // /proc/self/exe is a reliable way to get the true path of the executable on Linux/Termux
    ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
    
    if (len != -1) {
        executable_path[len] = '\0';
        // dirname can modify the string, so we work on a copy
        char* path_copy = strdup(executable_path);
        if (!path_copy) return 1;
        
        // Assumed structure: /.../sniper/tools/TOOL/bin/EXECUTABLE
        // We need to go up 4 levels from the executable's path.
        char* p1 = dirname(path_copy);      // -> .../bin
        char* p2 = dirname(p1);             // -> .../TOOL
        char* p3 = dirname(p2);             // -> .../tools
        char* root = dirname(p3);           // -> .../sniper

        strncpy(buffer, root, buffer_size - 1);
        buffer[buffer_size - 1] = '\0';
        free(path_copy);
        return 0; // Success
    }
    return 1; // Failure
}

int sniper_command_exists(const char* command_name) {
    char command[512];
    // Using `command -v` is a POSIX-compliant way to check for an executable in PATH
    snprintf(command, sizeof(command), "command -v %s >/dev/null 2>&1", command_name);
    return system(command) == 0;
}

void sniper_show_tool_help(const char* tool_name) {
    // Check for python3 and rich before attempting to call the script
    if (sniper_command_exists("python3") && system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        char root_path[PATH_MAX];
        if (sniper_get_root_path(root_path, sizeof(root_path)) == 0) {
            char command[PATH_MAX * 2];
            snprintf(command, sizeof(command), "python3 %s/lib/help_renderer.py --tool %s", root_path, tool_name);
            system(command);
        } else {
            sniper_log(LOG_ERROR, tool_name, "Could not determine project root to display help.");
        }
    } else {
        // Provide a simple, standard fallback help message
        sniper_log(LOG_INFO, tool_name, "A command-line tool within the SNIPER toolkit.");
        sniper_log(LOG_INFO, tool_name, "Usage: %s [OPTIONS]", tool_name);
        sniper_log(LOG_WARN, tool_name, "For a rich, detailed help screen, please ensure Python3 and the 'rich' library are installed (`pip install rich`).");
    }
}
