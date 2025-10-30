#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>

#define BIT 1024
const char *SIZES[] = {"B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"};

// حساب حجم الملف
unsigned long long get_file_size(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0) {
        return st.st_size;
    }
    return 0;
}

// حساب حجم المجلد
unsigned long long get_dir_size(const char *path) {
    unsigned long long total_size = 0;
    struct dirent *entry;
    char fullpath[4096];
    DIR *dir = opendir(path);

    if (!dir) return 0;

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        snprintf(fullpath, sizeof(fullpath), "%s/%s", path, entry->d_name);

        if (entry->d_type == DT_DIR) {
            total_size += get_dir_size(fullpath);
        } else {
            total_size += get_file_size(fullpath);
        }
    }

    closedir(dir);
    return total_size;
}

// تحويل الحجم إلى الوحدات المناسبة
void format_size(unsigned long long size, char *result) {
    int i = 0;
    double formatted_size = (double)size;

    // نستمر في القسمة حتى نجد الوحدة المناسبة
    while (formatted_size >= BIT && i < (sizeof(SIZES) / sizeof(SIZES[0])) - 1) {
        formatted_size /= BIT;
        i++;
    }

    sprintf(result, "%.2f \033[1;34m%s\033[0m", formatted_size, SIZES[i]);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <file_or_directory>\n", argv[0]);
        return 1;
    }

    char formatted_size[20];
    unsigned long long size = 0;

    // حساب الحجم حسب نوع المسار (ملف أو مجلد)
    if (access(argv[1], F_OK) != -1) {
        struct stat st;
        stat(argv[1], &st);
        if (S_ISDIR(st.st_mode)) {
            size = get_dir_size(argv[1]);
        } else {
            size = get_file_size(argv[1]);
        }

        // عرض الحجم بوحدة مناسبة
        format_size(size, formatted_size);
        printf("Size of\033[1;33m %s: \033[1;35m%s\n", argv[1], formatted_size);
    } else {
        printf("No such file or directory: '%s'\n", argv[1]);
    }

    return 0;
}
