// File: src/search.c (FIXED with refcount for ignore_patterns)

#include "search.h"
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <time.h>
#include <fnmatch.h>
#include <sys/wait.h>
#include <ctype.h>
#include "utils.h"
#include <stdatomic.h>

#define C_RESET      "\x1B[0m"
#define C_FILE       ""
#define C_DIR        "\x1B[1;34m"
#define C_LINK       "\x1B[1;36m"
#define C_EXECUTABLE "\x1B[1;32m"
#define C_TYPE       "\x1B[90m"

// Forward declarations
static void free_ignore_patterns(ignore_patterns_t *patterns);
static void print_result(search_config_t *config, const char *path, char type_char, const struct stat *sb);
static void handle_match(search_config_t *config, const char *path, char type_char, const struct stat *sb);
static void perform_exec(const char *command_template, const char *path);
static void perform_delete(search_config_t *config, const char *path, char type_char);
static void print_long_listing(search_config_t *config, const char *path, const struct stat *sb);


void init_search_config(search_config_t *config) {
    memset(config, 0, sizeof(search_config_t));
    config->root_dir = ".";
    config->max_depth = -1;
    config->num_threads = 1;
    config->use_colors = 1;
    config->output_format = "text";
    config->out_stream = stdout;
    config->ignore_vcs = 1;
    config->no_hidden = 1;
    config->size_filter = -1;
    config->mtime_filter = -1;
    pthread_mutex_init(&config->output_lock, NULL);
    atomic_init(&config->active_tasks, 0);
    pthread_mutex_init(&config->busy_lock, NULL);
    pthread_cond_init(&config->tasks_done_cond, NULL);
    atomic_init(&config->files_scanned, 0);
    atomic_init(&config->dirs_scanned, 0);
    atomic_init(&config->matches_found, 0);
}

void cleanup_search_config(search_config_t *config) {
    free_regex(&config->name_regex);
    free_regex(&config->content_regex);
    if (config->out_stream != stdout && config->out_stream != NULL) fclose(config->out_stream);
    if (config->exclude_dirs) {
        free(config->exclude_dirs);
    }
    pthread_mutex_destroy(&config->output_lock);
    pthread_mutex_destroy(&config->busy_lock);
    pthread_cond_destroy(&config->tasks_done_cond);
}

static int ends_with(const char *str, const char *suffix, int ignore_case) {
    if (!str || !suffix) return 0;
    size_t len_str = strlen(str);
    size_t len_suffix = strlen(suffix);
    if (len_suffix > len_str) return 0;
    const char *start = str + (len_str - len_suffix);
    if (ignore_case) return strncasecmp(start, suffix, len_suffix) == 0;
    return strncmp(start, suffix, len_suffix) == 0;
}

static ignore_patterns_t* load_ignore_file(const char *dir_path) {
    char ignore_path[PATH_MAX];
    snprintf(ignore_path, sizeof(ignore_path), "%s/.gitignore", dir_path);
    FILE *fp = fopen(ignore_path, "r");
    if (!fp) return NULL;
    ignore_patterns_t *p = calloc(1, sizeof(ignore_patterns_t));
    if (!p) { fclose(fp); return NULL; }
    p->refcount = 1; /* تهيئة عداد المراجع */
    char line[1024];
    while (fgets(line, sizeof(line), fp)) {
        line[strcspn(line, "\n\r")] = 0;
        if (line[0] == '#' || line[0] == '\0') continue;
        char *end = line + strlen(line) - 1;
        while(end > line && isspace((unsigned char)*end)) end--;
        *(end + 1) = 0;
        
        p->count++;
        char **tmp = realloc(p->patterns, p->count * sizeof(char*));
        if (!tmp) { /* فشل أثناء التوسيع: نظف وانهي */
            for (int i = 0; i < p->count - 1; i++) free(p->patterns[i]);
            free(p->patterns);
            free(p);
            fclose(fp);
            return NULL;
        }
        p->patterns = tmp;
        p->patterns[p->count - 1] = strdup(line);
        if (!p->patterns[p->count - 1]) {
            /* فشل في strdup: نظف وانهي */
            for (int i = 0; i < p->count - 1; i++) free(p->patterns[i]);
            free(p->patterns);
            free(p);
            fclose(fp);
            return NULL;
        }
    }
    fclose(fp);
    return p;
}

static int is_ignored(const char *name, ignore_patterns_t *patterns) {
    if (!patterns || !name) return 0;
    for (int i = 0; i < patterns->count; i++) {
        const char *pattern = patterns->patterns[i];
        if (fnmatch(pattern, name, 0) == 0) {
            return 1;
        }
    }
    return 0;
}

static void free_ignore_patterns(ignore_patterns_t *patterns) {
    if (!patterns) return;
    /* خفض عداد المراجع: إذا بقيت مراجع لا نفرّغ */
    int prev = atomic_fetch_sub(&patterns->refcount, 1);
    if (prev > 1) {
        return;
    }
    /* إذا وصلنا هنا، prev == 1 ولذا refcount صار 0 — حرّر فعليًا */
    for (int i = 0; i < patterns->count; i++) free(patterns->patterns[i]);
    free(patterns->patterns);
    free(patterns);
}

void search_directory(void *arg) {
    search_task_arg_t *task_arg = (search_task_arg_t *)arg;
    if (!task_arg) return;
    search_config_t *config = task_arg->config;
    char *path = task_arg->path;
    int current_depth = task_arg->current_depth;

    // FIX 1: Correct max-depth logic.
    if (config->max_depth != -1 && current_depth > config->max_depth) {
        goto cleanup;
    }

    atomic_fetch_add(&config->dirs_scanned, 1);
    DIR *dir = opendir(path);
    if (!dir) goto cleanup;

    ignore_patterns_t *local_ignore = (config->ignore_vcs) ? load_ignore_file(path) : NULL;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;

        char full_path[PATH_MAX];
        snprintf(full_path, sizeof(full_path), "%s/%s", path, entry->d_name);
        struct stat sb;
        if (lstat(full_path, &sb) == -1) continue;
        
        int is_dir = S_ISDIR(sb.st_mode);
        int is_file = S_ISREG(sb.st_mode);
        int is_link = S_ISLNK(sb.st_mode);

        if (config->no_hidden && entry->d_name[0] == '.') continue;
        
        int excluded = 0;
        for (int i = 0; i < config->exclude_dirs_count; i++) {
            if (strcmp(entry->d_name, config->exclude_dirs[i]) == 0) {
                excluded = 1;
                break;
            }
        }
        if (excluded) continue;
        
        if (config->ignore_vcs) {
            if (is_ignored(entry->d_name, local_ignore) || is_ignored(entry->d_name, task_arg->parent_ignore)) {
                continue;
            }
        }

        // Start with a positive match and invalidate it if any filter fails.
        int is_match = 1;

        if (!((is_dir && (config->type_mask & TYPE_DIR)) ||
              (is_file && (config->type_mask & TYPE_FILE)) ||
              (is_link && (config->type_mask & TYPE_LINK)))) {
            is_match = 0;
        }

        if (is_match && !match_regex(&config->name_regex, entry->d_name)) {
            is_match = 0;
        }

        if (is_match && config->size_filter >= 0) {
            if (!is_file ||
                (config->size_op > 0 && sb.st_size <= config->size_filter) ||
                (config->size_op < 0 && sb.st_size >= config->size_filter) ||
                (config->size_op == 0 && sb.st_size != config->size_filter)) {
                is_match = 0;
            }
        }
        
        if (is_match && config->mtime_filter >= 0) {
            time_t now = time(NULL);
            if (!is_file ||
                (config->mtime_op < 0 && (now - sb.st_mtime) >= config->mtime_filter) ||
                (config->mtime_op > 0 && (now - sb.st_mtime) <= config->mtime_filter)) {
                is_match = 0;
            }
        }
        
        if (is_match && config->extension) {
            if (!is_file || !ends_with(entry->d_name, config->extension, config->ignore_case)) {
                is_match = 0;
            }
        }

        if (is_match && config->content_regex.compiled) {
            if (!is_file || search_file_content(config, full_path) != 1) {
                is_match = 0;
            }
        }

        if (is_match && config->owner_filter_enabled && sb.st_uid != config->owner_filter) {
            is_match = 0;
        }
        if (is_match && config->perms_filter_enabled && (sb.st_mode & 0777) != config->perms_filter) {
            is_match = 0;
        }
        
        if (is_match) {
            if (is_file) atomic_fetch_add(&config->files_scanned, 1);
            atomic_fetch_add(&config->matches_found, 1);
            char type_char = is_dir ? 'd' : (is_file ? 'f' : 'l');
            handle_match(config, full_path, type_char, &sb);
        }

        if (is_dir && (config->max_depth == -1 || current_depth < config->max_depth)) {
            search_task_arg_t *new_task = malloc(sizeof(search_task_arg_t));
            if (new_task) {
                new_task->config = config;
                new_task->path = strdup(full_path);
                new_task->current_depth = current_depth + 1;
                /* مشاركة ignore patterns: نزيد عداد المراجع إذا كنا سنشارك */
                if (local_ignore) {
                    new_task->parent_ignore = local_ignore;
                    atomic_fetch_add(&local_ignore->refcount, 1);
                } else if (task_arg->parent_ignore) {
                    new_task->parent_ignore = task_arg->parent_ignore;
                    atomic_fetch_add(&task_arg->parent_ignore->refcount, 1);
                } else {
                    new_task->parent_ignore = NULL;
                }
                atomic_fetch_add(&config->active_tasks, 1);
                if (threadpool_add(config->pool, search_directory, new_task) != 0) {
                    atomic_fetch_sub(&config->active_tasks, 1);
                    /* فشل إضافة المهمة: نظف الذاكرة ونخفض refcount الذي زدناه */
                    if (new_task->parent_ignore) free_ignore_patterns(new_task->parent_ignore);
                    free(new_task->path);
                    free(new_task);
                }
            }
        }
    }
    closedir(dir);
    if (local_ignore) {
        /* نقلنا ملكية المشاركة إلى الأطفال عن طريق refcount — الآن نخفض العداد الخاص بالمحلي */
        free_ignore_patterns(local_ignore);
    }

cleanup:
    if (path) free(path);
    free(task_arg);
    if (atomic_fetch_sub(&config->active_tasks, 1) == 1) {
        pthread_mutex_lock(&config->busy_lock);
        pthread_cond_broadcast(&config->tasks_done_cond);
        pthread_mutex_unlock(&config->busy_lock);
    }
}

static void print_long_listing(search_config_t *config, const char *path, const struct stat *sb) {
    char perms[11];
    format_permissions(sb->st_mode, perms);
    char time_buf[20];
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M", localtime(&sb->st_mtime));
    fprintf(config->out_stream, "%s %4ld %-8d %-8d %8lld %s %s\n", perms, (long)sb->st_nlink, (int)sb->st_uid, (int)sb->st_gid, (long long)sb->st_size, time_buf, path);
}

static void print_result(search_config_t *config, const char *path, char type_char, const struct stat *sb) {
    if (config->long_listing) {
        print_long_listing(config, path, sb);
        return;
    }
    if (config->output_format && strcmp(config->output_format, "json") == 0) {
        if (atomic_load(&config->matches_found) > 1) {
           fprintf(config->out_stream, ",\n");
        }
        fprintf(config->out_stream, "{\"path\":\"%s\",\"type\":\"%c\",\"size\":%lld,\"mtime\":%ld}", path, type_char, (long long)sb->st_size, (long)sb->st_mtime);
    } else if (config->output_format && strcmp(config->output_format, "csv") == 0) {
        fprintf(config->out_stream, "\"%s\",%c,%lld,%ld\n", path, type_char, (long long)sb->st_size, (long)sb->st_mtime);
    } else {
        const char *color = C_FILE;
        if (config->use_colors) {
            if (type_char == 'd') color = C_DIR;
            else if (type_char == 'l') color = C_LINK;
            else if (sb->st_mode & S_IXUSR) color = C_EXECUTABLE;
        }
        fprintf(config->out_stream, "%s%s%s %s[%c]%s\n", color, path, C_RESET, C_TYPE, type_char, C_RESET);
    }
}

static void perform_exec(const char *command_template, const char *path) {
    pid_t pid = fork();
    if (pid == -1) { log_system_error("fork failed"); return; }
    if (pid == 0) {
        char *cmd_copy = strdup(command_template);
        if (!cmd_copy) exit(127);
        char final_cmd[PATH_MAX * 2] = {0};
        char *placeholder = strstr(cmd_copy, "{}");
        if (placeholder) {
            *placeholder = '\0';
            snprintf(final_cmd, sizeof(final_cmd), "%s'%s'%s", cmd_copy, path, placeholder + 2);
        } else {
            snprintf(final_cmd, sizeof(final_cmd), "%s '%s'", cmd_copy, path);
        }
        free(cmd_copy);
        execl("/bin/sh", "sh", "-c", final_cmd, (char *)NULL);
        log_system_error("execl failed for command");
        exit(127);
    } else {
        wait(NULL);
    }
}

static void perform_delete(search_config_t *config, const char *path, char type_char) {
    int should_delete = 1;
    if (config->interactive_delete) {
        printf("delete %s? [y/N] ", path);
        fflush(stdout);
        int c = getchar();
        should_delete = (c == 'y' || c == 'Y');
        while (c != '\n' && c != EOF) { c = getchar(); }
    }
    if (should_delete) {
        int ret = (type_char == 'd') ? rmdir(path) : remove(path);
        if (ret != 0) log_system_error("Failed to delete '%s'", path);
    }
}

static void handle_match(search_config_t *config, const char *path, char type_char, const struct stat *sb) {
    if (config->with_line_number && config->content_regex.compiled) {
        return;
    }

    pthread_mutex_lock(&config->output_lock);
    if (config->exec_command) {
        perform_exec(config->exec_command, path);
    } else if (config->delete_files) {
        perform_delete(config, path, type_char);
    } else {
        print_result(config, path, type_char, sb);
    }
    fflush(config->out_stream);
    pthread_mutex_unlock(&config->output_lock);
}
