// File: main.c (Corrected Version)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libgen.h>
#include <unistd.h>
#include "config.h"

#define C_GREEN "\x1B[32m"
#define C_WHITE "\x1B[37m"
#define C_RESET "\x1B[0m"

/**
 * @brief يحصل على المسار المطلق للمجلد الذي يحتوي على الملف التنفيذي،
 * ثم يصعد إلى المجلد الرئيسي 'sniper'.
 */
int get_sniper_base_path(const char* executable_path, char* buffer, size_t buffer_size) {
    char real_path[1024];
    char* final_path = NULL;

    // الطريقة الأكثر موثوقية على لينكس/Termux
    ssize_t len = readlink("/proc/self/exe", real_path, sizeof(real_path) - 1);
    if (len != -1) {
        real_path[len] = '\0';
        final_path = real_path;
    } else if (realpath(executable_path, real_path) != NULL) {
        // طريقة احتياطية
        final_path = real_path;
    } else {
        // طريقة احتياطية أخيرة
        final_path = strdup(executable_path);
        if (!final_path) return 1;
    }
    
    // الآن لدينا المسار الكامل للملف التنفيذي.
    // لنصعد في شجرة المجلدات حتى نجد مجلد 'sniper'.
    char* current_path = strdup(final_path);
    if (final_path != real_path) free(final_path); // Free if allocated by strdup
    
    char* temp_path = current_path;
    while (strcmp(temp_path, "/") != 0 && temp_path != NULL) {
        char* base = basename(temp_path);
        if (strcmp(base, "sniper") == 0) {
            strncpy(buffer, temp_path, buffer_size - 1);
            buffer[buffer_size - 1] = '\0';
            free(current_path);
            return 0; // وجدنا المسار
        }
        // اصعد مجلدًا واحدًا
        temp_path = dirname(temp_path);
    }

    free(current_path);
    // إذا فشلنا، ربما يكون المستخدم في مجلد sniper بالفعل
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        if (strstr(cwd, "sniper") != NULL) {
             strncpy(buffer, cwd, buffer_size -1);
             buffer[buffer_size - 1] = '\0';
             return 0;
        }
    }
    
    return 1; // فشل في العثور على مجلد sniper
}

int main(int argc, char *argv[]) {
    char base_path[1024];
    if (get_sniper_base_path(argv[0], base_path, sizeof(base_path)) != 0) {
        fprintf(stderr, "Error: Could not determine the SNIPER base directory.\n");
        fprintf(stderr, "Please run this tool from within the 'sniper' project directory.\n");
        // كحل احتياطي، استخدم المجلد الحالي
        strcpy(base_path, ".");
    }
    
    char config_filepath[2048];
    snprintf(config_filepath, sizeof(config_filepath), "%s/config/sniper-config.json", base_path);

    if (argc < 2 || strcmp(argv[1], "help") == 0) {
        print_help();
        return (argc < 2);
    }

    if (strcmp(argv[1], "set") == 0 && argc == 5) {
        int result = set_value(config_filepath, base_path, argv[2], argv[3], argv[4]);
        if (result == 0) {
            printf(C_GREEN "✔ Success:" C_WHITE " Value was set successfully.\n" C_RESET);
        }
        return result;
    } else if (strcmp(argv[1], "get") == 0 && argc == 4) {
        return get_value(config_filepath, argv[2], argv[3]);
    } else if (strcmp(argv[1], "delete") == 0 && argc == 4) {
        int result = delete_value(config_filepath, base_path, argv[2], argv[3]);
        if (result == 0) {
            printf(C_GREEN "✔ Success:" C_WHITE " Value was deleted successfully.\n" C_RESET);
        }
        return result;
    } else {
        print_help();
        return 1;
    }
}
