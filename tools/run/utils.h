// File: utils.h

#ifndef UTILS_H
#define UTILS_H

#include <stdbool.h>
#include <time.h>

// --- Global Options ---
extern bool g_use_color;
extern const char* g_temp_executable_to_cleanup;

// --- ANSI Color Macros ---
#define C_RESET   (g_use_color ? "\x1B[0m" : "")
#define C_RED     (g_use_color ? "\x1B[31m" : "")
#define C_GREEN   (g_use_color ? "\x1B[32m" : "")
#define C_YELLOW  (g_use_color ? "\x1B[33m" : "")
#define C_BLUE    (g_use_color ? "\x1B[34m" : "")
#define C_MAGENTA (g_use_color ? "\x1B[35m" : "")
#define C_CYAN    (g_use_color ? "\x1B[36m" : "")
#define C_BOLD    (g_use_color ? "\x1B[1m" : "")

// --- Function Prototypes ---

// Formatted printing helpers
void print_error(const char* format, ...);
void print_warning(const char* format, ...);
void print_info(const char* format, ...);
void print_stage(const char* stage, const char* format, ...);

// --- HELP PROTOTYPE ---
void show_rich_help(const char *prog_name);
// ----------------------

// Other utility functions
int check_command(const char *name);
char *make_output_name(const char *input_path);
double get_time_diff(struct timespec *start, struct timespec *end);
time_t get_file_mtime(const char* filepath);
void cleanup_temp_file(void);
int ensure_dir_exists(const char* path);

#endif // UTILS_H
