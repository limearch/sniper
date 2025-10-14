// File: src/utils.h (Corrected with print_help prototype)

#ifndef UTILS_H
#define UTILS_H

#include <sys/stat.h>
#include <sys/types.h>

// --- Color Macros for Help Screen ---
#define C_RED_HELP     "\x1B[31m"
#define C_GREEN_HELP   "\x1B[32m"
#define C_YELLOW_HELP  "\x1B[33m"
#define C_BLUE_HELP    "\x1B[34m"
#define C_MAGENTA_HELP "\x1B[35m"
#define C_CYAN_HELP    "\x1B[36m"
#define C_BOLD_HELP    "\x1B[1m"
#define C_RESET_HELP   "\x1B[0m"

// --- Prototypes for Panel Drawing ---
int get_terminal_width(void);
void print_panel_top(const char* title, const char* color, int width);
void print_panel_bottom(const char* color, int width);
void print_panel_line(const char* text, const char* color, int width);

// --- NEWLY ADDED PROTOTYPE FOR print_help ---
void print_help(const char *prog_name);
// ------------------------------------------

void log_error_with_hint(const char *error, const char *hint);
void log_system_error(const char *format, ...);
uid_t get_uid_from_name(const char *username);
mode_t parse_permissions(const char *perms_str, int *ok);
long long parse_size_string(const char *str);
time_t parse_time_string(const char *str);
void format_permissions(mode_t mode, char *buf);

#endif // UTILS_H
