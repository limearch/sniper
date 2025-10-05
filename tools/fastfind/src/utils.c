// File: src/utils.c

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
#include <libgen.h> // For dirname()

// Color macros for fallback help and error messages
#define BOLD     "\x1B[1m"
#define YELLOW   "\x1B[33m"
#define CYAN     "\x1B[36m"
#define GREEN    "\x1B[32m"
#define BOLD_RED "\x1B[1;31m"
#define GREY     "\x1B[90m"
#define RESET    "\x1B[0m"

// --- The actual implementation of the help function ---
void print_help(const char* prog_name) {
    // Check if Python and Rich are available
    if (system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        // --- Rich Help (Python Call) ---
        char command[1024];
        char executable_path[1024];
        char* dir_name;
        
        // Find the directory of the currently running C executable
        ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
        if (len != -1) {
            executable_path[len] = '\0';
            dir_name = dirname(executable_path);
            // Construct the path to the python script relative to the C executable's directory
            snprintf(command, sizeof(command), "python3 %s/../help_printer.py %s", dir_name, prog_name);
            system(command);
        } else {
             // Fallback if readlink fails (less reliable, assumes script is in current dir)
            snprintf(command, sizeof(command), "python3 help_printer.py %s", prog_name);
            system(command);
        }
    } else {
        // --- Simple Text Fallback Help ---
        printf(BOLD "fastfind" RESET " - A smart, fast, and feature-rich file search utility.\n");
        printf(YELLOW "NOTE:" RESET " For a better help screen, please install Python3 and the 'rich' library (pip install rich).\n\n");
        
        printf(YELLOW "USAGE:\n" RESET);
        printf("    fastfind " GREEN "[OPTIONS]" RESET " " CYAN "-p <regex>" RESET " [directory]\n\n");
        
        printf(YELLOW "KEY OPTIONS:\n" RESET);
        printf("    " GREEN "-p, --pattern <regex>" RESET "      (Required) Regex to match filenames.\n");
        printf("    " GREEN "-d, --directory <path>" RESET "       Directory to start from (Default: .).\n");
        printf("    " GREEN "-h, --help" RESET "                Show this help message.\n");
        printf("    " GREEN "-i, --ignore-case" RESET "          Enable case-insensitive matching.\n");
        printf("    " GREEN "--size <[+|-]N>" RESET "          Filter by size (e.g., +10M, -1K, 0).\n");
        printf("    " GREEN "--content <regex>" RESET "      Search inside file contents.\n");
    }
}


void log_error_with_hint(const char *error, const char *hint) {
    fprintf(stderr, BOLD_RED "fastfind error: " RESET "%s\n", error);
    if (hint) {
        fprintf(stderr, GREY "-> HINT: %s" RESET "\n", hint);
    }
}

void log_system_error(const char *format, ...) {
    int errnum = errno;
    va_list args;
    va_start(args, format);
    fprintf(stderr, BOLD_RED "fastfind error: " RESET);
    vfprintf(stderr, format, args);
    fprintf(stderr, ": %s\n", strerror(errnum));
    va_end(args);
}

uid_t get_uid_from_name(const char *username) {
    if (username == NULL || *username == '\0') {
         return geteuid();
    }
    struct passwd *pw = getpwnam(username);
    return (pw == NULL) ? (uid_t)-1 : pw->pw_uid;
}

mode_t parse_permissions(const char *perms_str, int *ok) {
    char *endptr;
    long perms = strtol(perms_str, &endptr, 8);
    if (*endptr != '\0' || perms < 0 || perms > 0777) {
        *ok = 0;
        return 0;
    }
    *ok = 1;
    return (mode_t)perms;
}

long long parse_size_string(const char *str) {
    char *endptr;
    long long size = strtoll(str, &endptr, 10);
    if (endptr == str) return -1;
    char suffix = toupper((unsigned char)*endptr);
    switch (suffix) {
        case 'G': size *= 1024;
        case 'M': size *= 1024;
        case 'K': size *= 1024; break;
        case '\0': break;
        default: return -1;
    }
    return size;
}

time_t parse_time_string(const char *str) {
    char *endptr;
    long days = strtol(str, &endptr, 10);
    if (endptr == str || (toupper((unsigned char)*endptr) != 'D' && *endptr != '\0')) return -1;
    return days * 24 * 60 * 60;
}

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
