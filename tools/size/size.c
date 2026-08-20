#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>

#define BLOCK_SIZE 1024
#define MAX_PATH_LEN 4096

/* Color definitions */
#define C_RESET   "\033[0m"
#define C_RED     "\033[1;31m"
#define C_GREEN   "\033[1;32m"
#define C_YELLOW  "\033[1;33m"
#define C_CYAN    "\033[1;36m"
#define C_BOLD    "\033[1m"

/* Function prototypes */
unsigned long long calculate_path_size(const char *path);
void format_human_readable(unsigned long long size, char *out_buf, size_t buf_size);

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, C_YELLOW "Usage: %s <path>\n" C_RESET, argv[0]);
        return EXIT_FAILURE;
    }

    const char *target_path = argv[1];
    unsigned long long total_bytes = calculate_path_size(target_path);

    char human_size[64];
    format_human_readable(total_bytes, human_size, sizeof(human_size));

    /* Direct one-line colored output */
    printf(C_CYAN "%s" C_RESET " => " C_GREEN C_BOLD "%s" C_RESET C_YELLOW " (%llu bytes)\n" C_RESET, 
           target_path, human_size, total_bytes);

    return EXIT_SUCCESS;
}

/**
 * Calculates total size recursively skipping symlinks
 */
unsigned long long calculate_path_size(const char *path) {
    struct stat st;

    if (lstat(path, &st) == -1) {
        fprintf(stderr, C_RED "[!] Error accessing %s: %s\n" C_RESET, path, strerror(errno));
        return 0;
    }

    if (S_ISLNK(st.st_mode)) return 0;
    if (S_ISREG(st.st_mode)) return st.st_size;

    if (S_ISDIR(st.st_mode)) {
        DIR *dir = opendir(path);
        if (!dir) {
            fprintf(stderr, C_RED "[!] Permission denied: %s\n" C_RESET, path);
            return 0;
        }

        unsigned long long dir_total = 0;
        struct dirent *entry;
        char sub_path[MAX_PATH_LEN];

        while ((entry = readdir(dir)) != NULL) {
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }

            snprintf(sub_path, sizeof(sub_path), "%s/%s", path, entry->d_name);
            dir_total += calculate_path_size(sub_path);
        }

        closedir(dir);
        return dir_total + st.st_size;
    }

    return 0;
}

/**
 * Converts size to human readable units
 */
void format_human_readable(unsigned long long size, char *out_buf, size_t buf_size) {
    const char *units[] = {"B", "KiB", "MiB", "GiB", "TiB", "PiB"};
    int i = 0;
    double friendly_size = (double)size;

    while (friendly_size >= BLOCK_SIZE && i < 5) {
        friendly_size /= BLOCK_SIZE;
        i++;
    }

    snprintf(out_buf, buf_size, "%.2f %s", friendly_size, units[i]);
}
