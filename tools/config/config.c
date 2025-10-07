// File: config.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <libgen.h> // Required for dirname()
#include <unistd.h> // Required for readlink()
#include "cJSON.h"
#include "config.h"

// تعريفات الألوان
#define C_RED "\x1B[31m"
#define C_GREEN "\x1B[32m"
#define C_YELLOW "\x1B[33m"
#define C_BLUE "\x1B[34m"
#define C_WHITE "\x1B[37m"
#define C_RESET "\x1B[0m"
#define C_BOLD "\x1B[1m"

// --- NEW Hybrid Help Function ---
void print_help(const char* prog_name) {
    // Check if Python and Rich are available
    if (system("python3 -c 'import rich' >/dev/null 2>&1") == 0) {
        char command[1024];
        char executable_path[1024];
        char* dir_name;
        
        // Find the directory of the currently running C executable
        ssize_t len = readlink("/proc/self/exe", executable_path, sizeof(executable_path) - 1);
        if (len != -1) {
            executable_path[len] = '\0';
            dir_name = dirname(executable_path);
            // Assume help_printer.py is in the same directory as the executable
            snprintf(command, sizeof(command), "python3 %s/help_printer.py %s", dir_name, prog_name);
            system(command);
        } else {
            // Fallback if readlink fails (less reliable, assumes script is in current dir)
            snprintf(command, sizeof(command), "python3 help_printer.py %s", prog_name);
            system(command);
        }
    } else {
        // --- Simple Text Fallback Help ---
        printf("\n%sSniper Config Manager%s - A simple tool to manage JSON configuration.\n", C_BOLD, C_RESET);
        printf("%sNOTE:%s For a better help screen, please install Python3 and the 'rich' library (pip install rich)\n\n", C_YELLOW, C_RESET);
        
        printf("%sUSAGE:\n%s", C_YELLOW, C_RESET);
        printf("  %s <command> [category] [key] [value]\n\n", prog_name);
        
        printf("%sCOMMANDS:\n%s", C_YELLOW, C_RESET);
        printf("  %s%-10s%s <category> <key> <value>    Set or update a configuration value.\n", C_GREEN, "set", C_RESET);
        printf("  %s%-10s%s <category> <key>            Retrieve a specific value.\n", C_GREEN, "get", C_RESET);
        printf("  %s%-10s%s <category> <key>            Delete a key-value pair.\n", C_GREEN, "delete", C_RESET);
        printf("  %s%-10s%s                            Show this help message.\n\n", C_GREEN, "help", C_RESET);
        
        printf("%sEXAMPLE:\n%s", C_YELLOW, C_RESET);
        printf("  %s set user prompt_text \"Hello Sniper\"\n", prog_name);
    }
}

void log_change(const char *base_path, const char *action, const char *category, const char *key, const char *value) {
    char log_filepath[1024];
    snprintf(log_filepath, sizeof(log_filepath), "%s/sniper-config.log", base_path);

    FILE *log_file = fopen(log_filepath, "a");
    if (!log_file) {
        return; // Silent fail
    }

    time_t now = time(NULL);
    char time_str[20];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&now));

    if (strcmp(action, "SET") == 0 && value) {
        fprintf(log_file, "[%s] SET: category='%s' key='%s' value='%s'\n", time_str, category, key, value);
    } else if (strcmp(action, "DELETE") == 0) {
        fprintf(log_file, "[%s] DELETE: category='%s' key='%s'\n", time_str, category, key);
    }

    fclose(log_file);
}

char* read_file(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        return NULL;
    }
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);
    char *content = malloc(length + 1);
    if (!content) { fclose(file); return NULL; }
    size_t read_len = fread(content, 1, length, file);
    content[read_len] = '\0';
    fclose(file);
    return content;
}

int write_file(const char *filename, const char *data) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Could not write to file %s.\n" C_RESET, filename);
        return 1;
    }
    fputs(data, file);
    fclose(file);
    return 0;
}

int set_value(const char *filepath, const char *base_path, const char *category, const char *key, const char *value) {
    char *data = read_file(filepath);
    cJSON *json = NULL;

    if (data) {
        json = cJSON_Parse(data);
        free(data);
    }
    
    if (!json) {
        json = cJSON_CreateObject();
    }

    cJSON *cat = cJSON_GetObjectItem(json, category);
    if (!cat) {
        cat = cJSON_CreateObject();
        cJSON_AddItemToObject(json, category, cat);
    }

    cJSON_ReplaceItemInObject(cat, key, cJSON_CreateString(value));
    
    char *out = cJSON_Print(json);
    if (!out) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Failed to generate JSON string.\n" C_RESET);
        cJSON_Delete(json);
        return 1;
    }

    int result = write_file(filepath, out);
    if (result == 0) {
        log_change(base_path, "SET", category, key, value);
    }
    
    free(out);
    cJSON_Delete(json);
    return result;
}

int get_value(const char *filepath, const char *category, const char *key) {
    char *data = read_file(filepath);
    if (!data) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Configuration file not found at %s.\n" C_RESET, filepath);
        fprintf(stderr, C_YELLOW "  Tip:" C_WHITE " Create it by running a 'set' command first.\n" C_RESET);
        return 1;
    }

    cJSON *json = cJSON_Parse(data);
    if (!json) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Failed to parse JSON. Check the file format.\n" C_RESET);
        free(data);
        return 1;
    }

    cJSON *cat = cJSON_GetObjectItem(json, category);
    if (!cat) {
        printf(C_YELLOW "⚠ Warning:" C_WHITE " Category '%s' not found.\n" C_RESET, category);
    } else {
        cJSON *item = cJSON_GetObjectItem(cat, key);
        if (item && cJSON_IsString(item)) {
            printf(C_BLUE "%s\n" C_RESET, item->valuestring);
        } else {
            printf(C_YELLOW "⚠ Warning:" C_WHITE " Key '%s' not found in category '%s'.\n" C_RESET, key, category);
        }
    }

    cJSON_Delete(json);
    free(data);
    return 0;
}

int delete_value(const char *filepath, const char *base_path, const char *category, const char *key) {
    char *data = read_file(filepath);
    if (!data) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Configuration file not found. Nothing to delete.\n" C_RESET);
        return 1;
    }

    cJSON *json = cJSON_Parse(data);
    if (!json) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Failed to parse JSON.\n" C_RESET);
        free(data);
        return 1;
    }

    cJSON *cat = cJSON_GetObjectItem(json, category);
    if (cat && cJSON_HasObjectItem(cat, key)) {
        cJSON_DeleteItemFromObject(cat, key);
    } else {
        printf(C_YELLOW "⚠ Warning:" C_WHITE " Key or category not found. Nothing to delete.\n" C_RESET);
        cJSON_Delete(json);
        free(data);
        return 0;
    }

    char *out = cJSON_Print(json);
    if (!out) {
        fprintf(stderr, C_RED "✖ Error:" C_WHITE " Failed to generate JSON string for writing.\n" C_RESET);
        cJSON_Delete(json);
        free(data);
        return 1;
    }

    int result = write_file(filepath, out);
    if (result == 0) {
        log_change(base_path, "DELETE", category, key, NULL);
    }

    free(out);
    cJSON_Delete(json);
    free(data);

    return result;
}
