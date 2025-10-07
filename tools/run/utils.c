// File: utils.c

#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <libgen.h>
#include <sys/stat.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/ioctl.h> // Required for TIOCGWINSZ

// --- Global Options Definition ---
bool g_use_color = true; // Enabled by default
const char* g_temp_executable_to_cleanup = NULL;

// --- Formatted Printing (Unchanged) ---
void print_error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    fprintf(stderr, "%s%s[ERROR]%s ", C_BOLD, C_RED, C_RESET);
    vfprintf(stderr, format, args);
    fprintf(stderr, "\n");
    va_end(args);
}

void print_warning(const char* format, ...) {
    va_list args;
    va_start(args, format);
    fprintf(stdout, "%s%s[WARN]%s  ", C_BOLD, C_YELLOW, C_RESET);
    vfprintf(stdout, format, args);
    fprintf(stdout, "\n");
    va_end(args);
}

void print_info(const char* format, ...) {
    va_list args;
    va_start(args, format);
    fprintf(stdout, "%s%s[INFO]%s  ", C_BOLD, C_CYAN, C_RESET);
    vfprintf(stdout, format, args);
    fprintf(stdout, "\n");
    va_end(args);
}

void print_stage(const char* stage, const char* format, ...) {
    va_list args;
    va_start(args, format);
    fprintf(stdout, "%s%s[%s]%s ", C_BOLD, C_BLUE, stage, C_RESET);
    vfprintf(stdout, format, args);
    fprintf(stdout, "\n");
    va_end(args);
}

// --- NEW & UPDATED HELP-RELATED FUNCTIONS ---

int get_terminal_width(void) {
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0 && w.ws_col > 0) {
        return w.ws_col;
    }
    return 80; // Default fallback width
}

void print_panel_top(const char* title, const char* color, int width) {
    if (g_use_color) {
        int title_len = title ? strlen(title) : 0;
        printf("%s┌", color);
        if (title && title_len > 0) {
            printf("─[ %s%s %s %s%s ]", C_RESET, C_BOLD, color, title, C_RESET);
            printf("%s", color);
            // Adjust for multi-byte characters in title (simple approximation)
            int visual_title_len = title_len + 12; // Approximation for color codes
            for (int i = 0; i < width - visual_title_len - 2 && i < 200; ++i) {
                printf("─");
            }
        } else {
            for (int i = 0; i < width - 2; ++i) printf("─");
        }
        printf("┐%s\n", C_RESET);
    } else {
        printf("+");
        for (int i = 0; i < width - 2; ++i) printf("-");
        printf("+\n");
    }
}

void print_panel_bottom(const char* color, int width) {
    if (g_use_color) {
        printf("%s└", color);
        for (int i = 0; i < width - 2; ++i) printf("─");
        printf("┘%s\n", C_RESET);
    } else {
        printf("+");
        for (int i = 0; i < width - 2; ++i) printf("-");
        printf("+\n");
    }
}

void print_panel_line(const char* text, const char* color, int width) {
    int text_len = 0;
    bool in_escape = false;
    for (const char* p = text; *p; ++p) {
        if (*p == '\x1B') {
            in_escape = true;
        } else if (in_escape && *p == 'm') {
            in_escape = false;
        } else if (!in_escape) {
            text_len++;
        }
    }

    int padding = width - text_len - 4;
    if (padding < 0) padding = 0;

    if (g_use_color) {
        printf("%s│%s %s%*s %s│%s\n", color, C_RESET, text, padding, "", color, C_RESET);
    } else {
        // Simple fallback for no color
        char plain_text[256] = {0};
        int j = 0;
        in_escape = false;
        for (const char* p = text; *p && j < 255; ++p) {
             if (*p == '\x1B') in_escape = true;
             else if (in_escape && *p == 'm') in_escape = false;
             else if (!in_escape) plain_text[j++] = *p;
        }
        printf("| %s%*s |\n", plain_text, padding + (text_len - (int)strlen(plain_text)), "");
    }
}

void print_panel_separator(const char* color, int width) {
    if (g_use_color) {
        printf("%s├", color);
        for (int i = 0; i < width - 2; ++i) printf("─");
        printf("┤%s\n", C_RESET);
    } else {
        printf("+");
        for (int i = 0; i < width - 2; ++i) printf("-");
        printf("+\n");
    }
}

// --- Command and File Utilities (Unchanged) ---

int check_command(const char *name) {
    char command[PATH_MAX];
    snprintf(command, sizeof(command), "command -v %s >/dev/null 2>&1", name);
    return system(command) == 0;
}

double get_time_diff(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) / 1e9;
}

time_t get_file_mtime(const char* filepath) {
    struct stat statbuf;
    if (stat(filepath, &statbuf) != 0) {
        return (time_t)-1;
    }
    return statbuf.st_mtime;
}

int ensure_dir_exists(const char* path) {
    struct stat st = {0};
    if (stat(path, &st) == -1) {
        if (mkdir(path, 0755) != 0) {
            if (errno != EEXIST) {
                return -1;
            }
        }
    }
    return 0;
}

char *make_output_name(const char *input_path) {
    char *input_copy = strdup(input_path);
    if (!input_copy) { print_error("strdup failed"); return NULL; }

    char *base = basename(input_copy);
    char *dot = strrchr(base, '.');
    if (dot != NULL) *dot = '\0';

    char home_cache_path[PATH_MAX] = {0};
    const char* home_dir = getenv("HOME");
    if (home_dir) {
        snprintf(home_cache_path, sizeof(home_cache_path), "%s/.cache", home_dir);
        if (ensure_dir_exists(home_cache_path) == 0) {
             strncat(home_cache_path, "/run", sizeof(home_cache_path) - strlen(home_cache_path) - 1);
             if (ensure_dir_exists(home_cache_path) != 0) {
                 home_cache_path[0] = '\0';
             }
        } else {
            home_cache_path[0] = '\0';
        }
    }

    const char* temp_dirs[] = {
        getenv("TMPDIR"),
        "/tmp",
        home_dir && home_cache_path[0] != '\0' ? home_cache_path : NULL,
        "."
    };
    
    char temp_template[PATH_MAX];
    int fd = -1;

    for (size_t i = 0; i < sizeof(temp_dirs) / sizeof(temp_dirs[0]); ++i) {
        const char* dir = temp_dirs[i];
        if (!dir) continue;

        snprintf(temp_template, sizeof(temp_template), "%s/%s-XXXXXX", dir, base);
        fd = mkstemp(temp_template);
        if (fd != -1) {
            break; 
        }
    }

    free(input_copy);

    if (fd == -1) {
        print_error("Failed to create a temporary file in any available location.");
        perror("  ↳ Last system error was");
        return NULL;
    }

    close(fd);
    char *output_name = strdup(temp_template);
    if (!output_name) {
        print_error("strdup failed");
        unlink(temp_template);
        return NULL;
    }
    
    g_temp_executable_to_cleanup = output_name;
    atexit(cleanup_temp_file);
    
    return output_name;
}

void cleanup_temp_file(void) {
    if (g_temp_executable_to_cleanup) {
        unlink(g_temp_executable_to_cleanup);
    }
}
