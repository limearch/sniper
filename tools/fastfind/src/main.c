// File: src/main.c (Corrected with ALL options restored)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <sys/stat.h>
#include <time.h>
#include <stdatomic.h>
#include <libgen.h>
#include "search.h"
#include "regex_utils.h"
#include "utils.h"

// Original Color Macros
#define BOLD     "\x1B[1m"
#define YELLOW   "\x1B[33m"
#define CYAN     "\x1B[36m"
#define GREEN    "\x1B[32m"
#define GREY     "\x1B[90m"
#define RESET    "\x1B[0m"

// Forward declaration from utils.c
void print_help(const char* prog_name);

void print_version(void) { printf("fastfind 1.5.0\n"); }

int main(int argc, char *argv[]) {
    search_config_t config;
    init_search_config(&config);
    char *name_pattern = NULL;
    char *content_pattern = NULL;

    // --- ALL LONG OPTIONS ARE RESTORED HERE ---
    struct option long_options[] = {
        {"pattern",   required_argument, 0, 'p'}, {"directory", required_argument, 0, 'd'},
        {"ext",       required_argument, 0, 'e'}, {"type",      required_argument, 0, 't'},
        {"ignore-case", no_argument,   0, 'i'},   {"max-depth", required_argument, 0, 'm'},
        {"output",    required_argument, 0, 'o'}, {"help",      no_argument,       0, 'h'},
        {"version",   no_argument,       0, 'v'}, {"long-listing", no_argument,   0, 'l'},
        {"show-hidden", no_argument,     0, 's'},
        {"content",   required_argument, 0, 1000},{"size",      required_argument, 0, 1001},
        {"mtime",     required_argument, 0, 1002},{"owner",     required_argument, 0, 1003},
        {"perms",     required_argument, 0, 1004},{"no-hidden", no_argument,       0, 1005},
        {"ignore-vcs",  no_argument,   0, 1006},{"no-ignore", no_argument,       0, 1007},
        {"exclude",   required_argument, 0, 1008},{"exec",      required_argument, 0, 1009},
        {"delete",    no_argument,       0, 1010},{"interactive", no_argument,   0, 1011},
        {"with-line-number", no_argument,0,1012},{"format",    required_argument, 0, 1013},
        {"threads",   required_argument, 0, 1014},{0, 0, 0, 0}
    };
    int opt;
    while ((opt = getopt_long(argc, argv, "p:d:e:t:im:lo:vhs", long_options, NULL)) != -1) {
        switch (opt) {
            case 'p': name_pattern = optarg; break;
            case 'd': config.root_dir = optarg; break;
            case 'e': config.extension = optarg; break;
            case 't':
                config.type_mask = 0;
                for (char *c = optarg; *c; c++) {
                    if (*c == 'f') config.type_mask |= TYPE_FILE;
                    else if (*c == 'd') config.type_mask |= TYPE_DIR;
                    else if (*c == 'l') config.type_mask |= TYPE_LINK;
                }
                break;
            case 'i': config.ignore_case = 1; break;
            case 'm': config.max_depth = atoi(optarg); break;
            case 'l': config.long_listing = 1; break;
            case 'o': config.output_file = optarg; break;
            case 'h': print_help(argv[0]); return 0;
            case 'v': print_version(); return 0;
            case 's': config.no_hidden = 0; break;
            // --- ALL LONG OPTION CASES ARE RESTORED HERE ---
            case 1000: content_pattern = optarg; break;
            case 1001:
                if (*optarg=='+'||*optarg=='-') { config.size_op=(*optarg++=='+')?1:-1; } else { config.size_op=0; }
                config.size_filter = parse_size_string(optarg);
                if(config.size_filter < 0) {log_error_with_hint("Invalid size format.", "Use N, NK, NM, NG.");return 1;}
                break;
            case 1002:
                if (*optarg=='+'||*optarg=='-') { config.mtime_op=(*optarg++=='+')?1:-1; } else { config.mtime_op=0; }
                config.mtime_filter = parse_time_string(optarg);
                if(config.mtime_filter < 0) {log_error_with_hint("Invalid mtime format.", "Use Nd (e.g., 7d).");return 1;}
                break;
            case 1003:
                config.owner_filter = get_uid_from_name(optarg);
                if (config.owner_filter == (uid_t)-1) { log_error_with_hint("User not found.", "Check username."); return 1; }
                config.owner_filter_enabled = 1;
                break;
            case 1004: {
                int ok;
                config.perms_filter = parse_permissions(optarg, &ok);
                if (!ok) { log_error_with_hint("Invalid permission format.", "Use a 3-digit octal number."); return 1; }
                config.perms_filter_enabled = 1;
                break;
            }
            case 1005: config.no_hidden = 1; break;
            case 1006: config.ignore_vcs = 1; break;
            case 1007: config.ignore_vcs = 0; break;
            case 1008:
                config.exclude_dirs_count++;
                config.exclude_dirs = realloc(config.exclude_dirs, config.exclude_dirs_count * sizeof(char*));
                if (!config.exclude_dirs) { log_system_error("realloc failed"); return 1; }
                config.exclude_dirs[config.exclude_dirs_count - 1] = optarg;
                break;
            case 1009: config.exec_command = optarg; break;
            case 1010: config.delete_files = 1; break;
            case 1011: config.interactive_delete = 1; break;
            case 1012: config.with_line_number = 1; break;
            case 1013: config.output_format = optarg; break;
            case 1014: config.num_threads = atoi(optarg); break;
            default: return 1;
        }
    }

    if (optind < argc) config.root_dir = argv[optind];
    if (!name_pattern) {
        // If no pattern is given, maybe the user just wanted help.
        print_help(argv[0]);
        return 1;
    }
    if (config.type_mask == 0) config.type_mask = TYPE_FILE | TYPE_DIR | TYPE_LINK;
    if (!isatty(fileno(stdout)) || config.output_file) config.use_colors = 0;
    
    if (config.output_file) {
        config.out_stream = fopen(config.output_file, "w");
        if (!config.out_stream) { log_system_error("Could not open file '%s'", config.output_file); return 1; }
    }
    if (compile_regex(&config.name_regex, name_pattern, config.ignore_case) != 0) return 1;
    if (content_pattern && compile_regex(&config.content_regex, content_pattern, config.ignore_case) != 0) return 1;
    
    config.pool = threadpool_create(config.num_threads > 0 ? config.num_threads : sysconf(_SC_NPROCESSORS_ONLN), 4096);
    if (!config.pool) { log_error_with_hint("Failed to create thread pool.", NULL); return 1; }

    if (strcmp(config.output_format, "json") == 0) fprintf(config.out_stream, "[\n");
    if (strcmp(config.output_format, "csv") == 0) fprintf(config.out_stream, "path,type,size,mtime\n");

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    search_task_arg_t *initial_task = malloc(sizeof(search_task_arg_t));
    if (!initial_task) { log_system_error("malloc failed"); return 1; }
    initial_task->config = &config;
    initial_task->path = strdup(config.root_dir);
    initial_task->current_depth = 0;
    initial_task->parent_ignore = NULL;
    atomic_store(&config.active_tasks, 1);
    threadpool_add(config.pool, search_directory, initial_task);

    pthread_mutex_lock(&config.busy_lock);
    while (atomic_load(&config.active_tasks) > 0) {
        pthread_cond_wait(&config.tasks_done_cond, &config.busy_lock);
    }
    pthread_mutex_unlock(&config.busy_lock);

    threadpool_destroy(config.pool);
    clock_gettime(CLOCK_MONOTONIC, &end);

    if (strcmp(config.output_format, "json") == 0) {
        if (atomic_load(&config.matches_found) > 0) {
            fseek(config.out_stream, -2L, SEEK_CUR); 
            fprintf(config.out_stream, "\n");
        }
        fprintf(config.out_stream, "]\n");
    }
    
    double time_spent = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    fprintf(stderr, "\n" GREY "Searched %lld directories and %lld files. Found %lld matches in %.2f seconds." RESET "\n",
            atomic_load(&config.dirs_scanned), atomic_load(&config.files_scanned), atomic_load(&config.matches_found), time_spent);

    cleanup_search_config(&config);
    return 0;
}
