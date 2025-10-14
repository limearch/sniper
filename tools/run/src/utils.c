/**
 * @file utils.c
 * @brief Implementation of utility functions for the 'run' tool.
 */

#include "utils.h"
#include "sniper_c_utils.h" // For sniper_log

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libgen.h>
#include <sys/stat.h>
#include <errno.h>
#include <limits.h>

// --- Global Variable Definitions ---
bool g_use_color = true;
const char* g_temp_executable_to_cleanup = NULL;

// --- Function Implementations ---

bool check_command(const char *name) {
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

// Helper to ensure a directory exists.

char *make_output_name(const char *input_path) {
    char *input_copy = strdup(input_path);
    if (!input_copy) {
        sniper_log(LOG_ERROR, "run:util", "strdup failed in make_output_name");
        return NULL;
    }

    char *base = basename(input_copy);
    char *dot = strrchr(base, '.');
    if (dot != NULL) *dot = '\0'; // Remove extension

    // Try to create a temporary file in standard locations
    const char* temp_dirs[] = { getenv("TMPDIR"), "/tmp", "." };
    char temp_template[PATH_MAX];
    int fd = -1;

    for (size_t i = 0; i < sizeof(temp_dirs) / sizeof(temp_dirs[0]); ++i) {
        if (!temp_dirs[i]) continue;
        snprintf(temp_template, sizeof(temp_template), "%s/%s-XXXXXX", temp_dirs[i], base);
        fd = mkstemp(temp_template);
        if (fd != -1) break; // Success
    }

    free(input_copy);

    if (fd == -1) {
        sniper_log(LOG_ERROR, "run:util", "Failed to create a temporary file.");
        perror("  ↳ Last system error");
        return NULL;
    }

    close(fd);
    char *output_name = strdup(temp_template);
    if (!output_name) {
        sniper_log(LOG_ERROR, "run:util", "strdup failed for output name");
        unlink(temp_template);
        return NULL;
    }
    
    // Register for cleanup
    g_temp_executable_to_cleanup = output_name;
    atexit(cleanup_temp_file);
    
    return output_name;
}

void cleanup_temp_file(void) {
    if (g_temp_executable_to_cleanup) {
        unlink(g_temp_executable_to_cleanup);
        // The pointer is to a strdup'd string, which should be freed.
        // However, atexit handlers cannot safely free memory. We accept this small leak.
    }
}
