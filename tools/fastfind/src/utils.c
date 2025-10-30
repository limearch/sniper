// File: src/utils.c (REFACTORED - Complete Code)
// Description: Implements utility functions for the fastfind tool,
// including the centralized help caller, error logging, and parsers
// for command-line arguments.

#include "utils.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <pwd.h>
#include <ctype.h>
#include <time.h>
#include <unistd.h>
#include <libgen.h>
#include <limits.h>

// --- ANSI Color Macros for Fallback Help and Error Messages ---
#define BOLD     "\x1B[1m"
#define YELLOW   "\x1B[33m"
#define CYAN     "\x1B[36m"
#define GREEN    "\x1B[32m"
#define BOLD_RED "\x1B[1;31m"
#define GREY     "\x1B[90m"
#define RESET    "\x1B[0m"

// --- START: Centralized Help System Integration ---

/**
 * @brief Prints the help screen for the fastfind tool.
 *
 * This function first checks if Python and the 'rich' library are available.
 * If they are, it calls the centralized Python help renderer script (`lib/help_renderer.py`),
 * passing its own tool name (`fastfind`) to load the correct content.
 * If Python/rich is not available, it prints a simplified, plain-text fallback help message.
 *
 * @param prog_name The name of the executable (argv[0]), used for the fallback message.
 */
void print_help(const char* prog_name) {
    // Check for Python and Rich library by attempting a silent import.
    if (system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        // --- Rich Help (Python Call) ---
        char command[PATH_MAX * 2];
        char executable_path[PATH_MAX];

        // Find the absolute path of the currently running executable on Linux.
        ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
        if (len != -1) {
            executable_path[len] = '\0';
            
            // To get the project root, we need to traverse up the directory tree.
            // The path is expected to be: .../sniper/tools/fastfind/bin/fastfind
            // We need to call dirname() multiple times to get to .../sniper/
            // Note: dirname can modify its argument, so we must use copies or be careful.
            char* path_copy1 = strdup(executable_path);
            char* p1 = dirname(path_copy1);      // -> .../tools/fastfind/bin
            char* path_copy2 = strdup(p1);
            char* p2 = dirname(path_copy2);      // -> .../tools/fastfind
            char* path_copy3 = strdup(p2);
            char* p3 = dirname(path_copy3);      // -> .../tools
            char* project_root = dirname(p3);    // -> .../sniper
            
            // Construct the full command to execute the central help renderer script.
            snprintf(command, sizeof(command),
                     "python3 %s/lib/help_renderer.py --tool fastfind",
                     project_root);
            
            free(path_copy1);
            free(path_copy2);
            free(path_copy3);

            system(command);
        } else {
            // Fallback if readlink fails. This assumes the CWD is the project root.
            system("python3 lib/help_renderer.py --tool fastfind");
        }
    } else {
        // --- Simple Text Fallback Help ---
        printf(BOLD "fastfind" RESET " - A smart, fast, and feature-rich file search utility.\n");
        printf(YELLOW "NOTE:" RESET " For a rich help screen, please install Python3 and the 'rich' library (pip install rich).\n\n");
        printf(YELLOW "USAGE:\n" RESET);
        printf("    fastfind " GREEN "[OPTIONS]" RESET " " CYAN "-p <regex>" RESET " [directory]\n\n");
        printf(YELLOW "KEY OPTIONS:\n" RESET);
        printf("    " GREEN "-p, --pattern <regex>" RESET "      (Required) Regex to match filenames.\n");
        printf("    " GREEN "-d, --directory <path>" RESET "       Directory to start from (Default: .).\n");
        printf("    " GREEN "-h, --help" RESET "                Show this help message.\n");
        printf("    " GREEN "--size <[+|-]N>" RESET "          Filter by size (e.g., +10M, -1K).\n");
        printf("    " GREEN "--content <regex>" RESET "      Search inside file contents.\n");
    }
}

// --- END: Centralized Help System Integration ---


/**
 * @brief Prints a formatted error message with an optional hint.
 * @param error The main error message string.
 * @param hint  An optional hint string to guide the user, or NULL.
 */
void log_error_with_hint(const char *error, const char *hint) {
    fprintf(stderr, BOLD_RED "fastfind error: " RESET "%s\n", error);
    if (hint) {
        fprintf(stderr, GREY "-> HINT: %s" RESET "\n", hint);
    }
}

/**
 * @brief Prints a formatted error message based on a format string and the global `errno`.
 * @param format A printf-style format string.
 * @param ...    Variable arguments for the format string.
 */
void log_system_error(const char *format, ...) {
    int errnum = errno; // Capture errno immediately
    va_list args;
    va_start(args, format);
    fprintf(stderr, BOLD_RED "fastfind error: " RESET);
    vfprintf(stderr, format, args);
    fprintf(stderr, ": %s\n", strerror(errnum));
    va_end(args);
}


/**
 * @brief Converts a username string to a user ID (uid_t).
 * @param username The username to look up. If NULL or empty, returns the current effective UID.
 * @return The uid_t of the user, or (uid_t)-1 if the user is not found.
 */
uid_t get_uid_from_name(const char *username) {
    if (username == NULL || *username == '\0') {
         return geteuid(); // Default to the current user
    }
    struct passwd *pw = getpwnam(username);
    return (pw == NULL) ? (uid_t)-1 : pw->pw_uid;
}

/**
 * @brief Parses a string representing octal permissions (e.g., "755").
 * @param perms_str The string to parse.
 * @param ok        A pointer to an integer that will be set to 1 on success or 0 on failure.
 * @return The parsed mode_t value on success, 0 on failure.
 */
mode_t parse_permissions(const char *perms_str, int *ok) {
    char *endptr;
    long perms = strtol(perms_str, &endptr, 8); // Base 8 for octal
    if (*endptr != '\0' || perms < 0 || perms > 0777) {
        *ok = 0;
        return 0;
    }
    *ok = 1;
    return (mode_t)perms;
}

/**
 * @brief Parses a size string (e.g., "10K", "20M", "1G") into a long long of bytes.
 * @param str The size string to parse.
 * @return The size in bytes, or -1 on parsing error.
 */
long long parse_size_string(const char *str) {
    char *endptr;
    long long size = strtoll(str, &endptr, 10);
    if (endptr == str) return -1; // No numbers were found
    
    char suffix = toupper((unsigned char)*endptr);
    switch (suffix) {
        case 'G': size *= 1024; // Fall-through
        case 'M': size *= 1024; // Fall-through
        case 'K': size *= 1024; break;
        case '\0': break; // No suffix
        default: return -1; // Invalid suffix
    }
    return size;
}

/**
 * @brief Parses a time string (e.g., "7d") into a time_t value in seconds.
 * @param str The time string to parse.
 * @return The duration in seconds, or -1 on parsing error.
 */
time_t parse_time_string(const char *str) {
    char *endptr;
    long days = strtol(str, &endptr, 10);
    if (endptr == str || (toupper((unsigned char)*endptr) != 'D' && *endptr != '\0')) {
        return -1; // Invalid format
    }
    return days * 24 * 60 * 60; // Convert days to seconds
}

/**
 * @brief Formats a file mode into a standard symbolic permission string (e.g., "drwxr-xr-x").
 * @param mode The mode_t value from stat.
 * @param buf  A character buffer of at least 11 bytes to store the result.
 */
void format_permissions(mode_t mode, char *buf) {
    strcpy(buf, "----------");
    if (S_ISDIR(mode)) buf[0] = 'd';
    if (S_ISLNK(mode)) buf[0] = 'l';
    
    if (mode & S_IRUSR) buf[1] = 'r';
    if (mode & S_IWUSR) buf[2] = 'w';
    if (mode & S_IXUSR) buf[3] = 'x';
    
    if (mode & S_IRGRP) buf[4] = 'r';
    if (mode & S_IWGRP) buf[5] = 'w';
    if (mode & S_IXGRP) buf[6] = 'x';
    
    if (mode & S_IROTH) buf[7] = 'r';
    if (mode & S_IWOTH) buf[8] = 'w';
    if (mode & S_IXOTH) buf[9] = 'x';
}
