// File: config.c (Corrected and Complete Version)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "cJSON.h"
#include "config.h"

// تعريفات الألوان
#define C_RED "\x1B[31m"
#define C_GREEN "\x1B[32m"
#define C_YELLOW "\x1B[33m"
#define C_BLUE "\x1B[34m"
#define C_MAGENTA "\x1B[35m"
#define C_CYAN "\x1B[36m"
#define C_WHITE "\x1B[37m"
#define C_RESET "\x1B[0m"
#define C_BOLD "\x1B[1m"

// --- دوال رسم الصناديق الديناميكية (كاملة) ---

int get_terminal_width() {
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0 && w.ws_col > 0) {
        return w.ws_col;
    }
    return 80;
}

void print_char_repeat(const char* c, int times) {
    if (times < 0) return;
    for (int i = 0; i < times; ++i) {
        printf("%s", c);
    }
}

void print_panel_top(const char* title, const char* color, int width) {
    printf("%s┌", color);
    if (title && strlen(title) > 0) {
        int title_len = strlen(title);
        // Approximation for color codes length
        int non_visible_len = 15; 
        int line_len = (width - title_len - 4) / 2; // 4 for " [] "
        if (line_len < 1) line_len = 1;
        
        print_char_repeat("─", line_len);
        printf("[ %s%s%s %s %s%s ]", C_RESET, C_BOLD, color, title, C_RESET, color);
        
        // This calculation is complex due to invisible ANSI codes.
        // We will simplify and just fill some space. A perfect calculation is tricky.
        int remaining_width = width - line_len - title_len - 5;
        print_char_repeat("─", remaining_width > 0 ? remaining_width : 0);

    } else {
        print_char_repeat("─", width - 2);
    }
    printf("┐%s\n", C_RESET);
}

void print_panel_bottom(const char* color, int width) {
    printf("%s└", color);
    print_char_repeat("─", width - 2);
    printf("┘%s\n", C_RESET);
}

void print_panel_line(const char* text, const char* color, int width) {
    int text_len = 0;
    int in_escape = 0;
    for (const char* p = text; *p; ++p) {
        if (*p == '\x1B') in_escape = 1;
        else if (in_escape && *p == 'm') in_escape = 0;
        else if (!in_escape) text_len++;
    }
    int padding = width - text_len - 4;
    if (padding < 0) padding = 0;
    printf("%s│%s %s%*s %s│%s\n", color, C_RESET, text, padding, "", color, C_RESET);
}

// --- دالة المساعدة (كاملة) ---
void print_help(void) {
    int width = get_terminal_width();
    char title_buffer[256];
    snprintf(title_buffer, sizeof(title_buffer), "%sSNIPER: Config Manager%s", C_BOLD, C_RESET);
    print_panel_top("", C_MAGENTA, width);
    print_panel_line(title_buffer, C_MAGENTA, width);
    print_panel_line("A tool to manage the main `sniper-config.json` file.", C_MAGENTA, width);
    print_panel_bottom(C_MAGENTA, width);
    
    char usage_buffer[256];
    snprintf(usage_buffer, sizeof(usage_buffer), "  %sUsage:%s %sconfiger%s %s<command>%s %s[args...]%s",
           C_BOLD, C_RESET, C_YELLOW, C_RESET, C_GREEN, C_RESET, C_CYAN, C_RESET);
    printf("\n%s\n\n", usage_buffer);

    print_panel_top("Commands", C_BLUE, width);
    print_panel_line("  set    <category> <key> <value>    Set or update a configuration value.", C_BLUE, width);
    print_panel_line("  get    <category> <key>            Retrieve a specific value.", C_BLUE, width);
    print_panel_line("  delete <category> <key>            Delete a key-value pair.", C_BLUE, width);
    print_panel_line("  help                               Show this help message.", C_BLUE, width);
    print_panel_bottom(C_BLUE, width);

    print_panel_top("Examples", C_GREEN, width);
    print_panel_line("  # Set a custom prompt text for a user", C_GREEN, width);
    print_panel_line("  configer set user prompt_text \"Hello Sniper\"", C_GREEN, width);
    print_panel_line(" ", C_GREEN, width);
    print_panel_line("  # Retrieve the user's prompt text", C_GREEN, width);
    print_panel_line("  configer get user prompt_text", C_GREEN, width);
    print_panel_bottom(C_GREEN, width);
}

// --- دالة السجل (مكتملة الآن) ---
void log_change(const char *base_path, const char *action, const char *category, const char *key, const char *value) {
    char log_filepath[1024];
    snprintf(log_filepath, sizeof(log_filepath), "%s/sniper-config.log", base_path);

    FILE *log_file = fopen(log_filepath, "a");
    if (!log_file) {
        return; // فشل صامت
    }

    time_t now = time(NULL);
    char time_str[20];
    // كتابة الوقت بصيغة ISO 8601
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", localtime(&now));

    if (strcmp(action, "SET") == 0 && value) {
        fprintf(log_file, "[%s] SET: category='%s' key='%s' value='%s'\n", time_str, category, key, value);
    } else if (strcmp(action, "DELETE") == 0) {
        fprintf(log_file, "[%s] DELETE: category='%s' key='%s'\n", time_str, category, key);
    }

    fclose(log_file);
}

// --- باقي الدوال (كاملة ومصححة) ---
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

// --- دالة delete_value (مكتملة الآن) ---
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
        // لا يعتبر خطأ فادحًا، بل مجرد عملية لم تتم
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
