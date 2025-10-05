// File: tools/compress/zip_tool.h (Corrected)

#ifndef ZIP_TOOL_H
#define ZIP_TOOL_H

#include <zip.h>
#include <time.h> // For clock_t

#define MAX_THREADS 4

// Struct for passing data to each thread
typedef struct {
    zip_t *archive;
    const char *folder_path;
    const char *base_path;
    int verbose;
    int skip_hidden;
    const char *exclude_ext;
    const char *filter_ext;
} thread_data;

// Function declarations
void zip_folder(zip_t *archive, const char *folder_path, const char *base_path, int verbose, int skip_hidden, const char *exclude_ext, const char *filter_ext);
void* zip_thread(void* arg);
int exclude_file(const char *filename, const char *exclude_ext);
int filter_file(const char *filename, const char *filter_ext);
int compress_folder(const char *folder_path, const char *output_file, int level, int verbose, int test_archive, int num_threads, const char *exclude_ext, const char *password, const char *filter_ext, int skip_hidden);

// --- CORRECTED PROTOTYPE ---
void print_help(const char *prog_name);
// ---------------------------

#endif // ZIP_TOOL_H
