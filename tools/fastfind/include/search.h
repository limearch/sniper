#ifndef SEARCH_H
#define SEARCH_H

#include <sys/types.h>
#include <regex.h>
#include <stdio.h>
#include <stdatomic.h>
#include <pthread.h>
#include "threadpool.h"
#include "regex_utils.h"

#define TYPE_FILE 1
#define TYPE_DIR  2
#define TYPE_LINK 4

typedef struct {
    char **patterns;
    int count;
    _Atomic int refcount;
} ignore_patterns_t;

typedef struct search_config_s {
    const char *root_dir;
    Regex name_regex;
    Regex content_regex;
    const char *extension;
    int ignore_case;
    int max_depth;
    int type_mask;
    int use_colors;
    const char *output_format;
    const char *output_file;
    int num_threads;
    threadpool_t *pool;
    pthread_mutex_t output_lock;
    FILE* out_stream;

    // Advanced Filtering
    long long size_filter;
    int size_op; // -1 for less, 0 for equal, 1 for greater
    time_t mtime_filter;
    int mtime_op; // -1 for older, 1 for newer
    uid_t owner_filter;
    int owner_filter_enabled;
    mode_t perms_filter;
    int perms_filter_enabled;
    char **exclude_dirs;
    int exclude_dirs_count;
    int ignore_vcs;
    int no_hidden;

    // Actions
    char *exec_command;
    int delete_files;
    int interactive_delete;

    // Output
    int long_listing;
    int with_line_number;

    // Task Management
    atomic_int active_tasks;
    pthread_mutex_t busy_lock;
    pthread_cond_t tasks_done_cond;

    // Statistics
    atomic_llong files_scanned;
    atomic_llong dirs_scanned;
    atomic_llong matches_found;
} search_config_t;

typedef struct {
    search_config_t *config;
    char *path;
    int current_depth;
    ignore_patterns_t *parent_ignore;
} search_task_arg_t;

void search_directory(void *arg);
void init_search_config(search_config_t *config);
void cleanup_search_config(search_config_t *config);

#endif // SEARCH_H
