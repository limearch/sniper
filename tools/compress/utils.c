#include <string.h>
#include "zip_tool.h"

// Function to check if the file extension matches the exclusion list
int exclude_file(const char *filename, const char *exclude_ext) {
    if (!exclude_ext) return 0;
    const char *ext = strrchr(filename, '.');
    if (ext && strcmp(ext, exclude_ext) == 0) {
        return 1;
    }
    return 0;
}

// Function to filter files based on file extension
int filter_file(const char *filename, const char *filter_ext) {
    const char *ext = strrchr(filename, '.');
    if (ext && strcmp(ext, filter_ext) == 0) {
        return 1;
    }
    return 0;
}
