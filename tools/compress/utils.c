/**
 * @file utils.c
 * @brief Utility functions specific to the 'compress' tool for filtering files.
 */

#include "zip_tool.h"
#include <string.h>

/**
 * @brief Checks if a filename should be excluded based on its extension.
 */
int exclude_file(const char *filename, const char *exclude_ext) {
    if (!exclude_ext || !filename) return 0;
    
    // Find the last occurrence of '.' to get the extension
    const char *ext = strrchr(filename, '.');
    
    // Check if an extension exists and if it matches the exclude_ext
    if (ext && strcmp(ext, exclude_ext) == 0) {
        return 1; // Should be excluded
    }
    return 0;
}

/**
 * @brief Checks if a filename should be included based on a filter extension.
 *        If a filter is provided, ONLY files with that extension are included.
 */
int filter_file(const char *filename, const char *filter_ext) {
    if (!filter_ext || !filename) {
        // If no filter is specified, every file passes the filter check.
        return 1;
    }

    const char *ext = strrchr(filename, '.');

    // If an extension exists and it matches the filter, it passes.
    if (ext && strcmp(ext, filter_ext) == 0) {
        return 1; // Include this file
    }
    
    // Otherwise, it does not pass the filter.
    return 0;
}
