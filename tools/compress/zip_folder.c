/**
 * @file zip_folder.c
 * @brief Implements the recursive directory traversal for ZIP compression.
 */

#include "zip_tool.h"
#include "sniper_c_utils.h" // For logging

#include <stdio.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <zip.h>
#include <limits.h> // For PATH_MAX

void zip_folder(
    zip_t *archive, 
    const char *folder_path, 
    const char *base_path, 
    bool verbose, 
    bool skip_hidden, 
    const char *exclude_ext, 
    const char *filter_ext
) {
    DIR *dir = opendir(folder_path);
    if (!dir) {
        sniper_log(LOG_WARN, "compress:zip", "Could not open directory: %s", folder_path);
        return;
    }

    struct dirent *entry;
    char full_path[PATH_MAX];
    char relative_path[PATH_MAX];

    while ((entry = readdir(dir)) != NULL) {
        // Skip '.' and '..' pseudo-directories
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        // Skip hidden files if the flag is set
        if (skip_hidden && entry->d_name[0] == '.') {
            continue;
        }

        snprintf(full_path, sizeof(full_path), "%s/%s", folder_path, entry->d_name);
        
        // Create the relative path for the entry inside the zip archive.
        // This ensures the archive doesn't contain the absolute path.
        if (strlen(base_path) > 0) {
            snprintf(relative_path, sizeof(relative_path), "%s/%s", base_path, entry->d_name);
        } else {
            // For the root level, the relative path is just the filename.
            strncpy(relative_path, entry->d_name, sizeof(relative_path) -1);
            relative_path[sizeof(relative_path)-1] = '\0';
        }

        struct stat statbuf;
        if (stat(full_path, &statbuf) == 0) {
            if (S_ISDIR(statbuf.st_mode)) {
                // If it's a directory, add an entry for it in the archive and then recurse into it.
                zip_dir_add(archive, relative_path, ZIP_FL_ENC_UTF_8);
                zip_folder(archive, full_path, relative_path, verbose, skip_hidden, exclude_ext, filter_ext);
            } else {
                // It's a file, so check it against the filters.
                if (exclude_ext && exclude_file(entry->d_name, exclude_ext)) {
                    if (verbose) sniper_log(LOG_DEBUG, "compress:zip", "Excluding (by ext): %s", relative_path);
                    continue;
                }
                if (filter_ext && !filter_file(entry->d_name, filter_ext)) {
                    if (verbose) sniper_log(LOG_DEBUG, "compress:zip", "Skipping (filter mismatch): %s", relative_path);
                    continue;
                }

                // Create a zip_source from the file on disk.
                zip_source_t *source = zip_source_file(archive, full_path, 0, 0);
                if (source == NULL) {
                    sniper_log(LOG_ERROR, "compress:zip", "Error creating source for '%s': %s", full_path, zip_strerror(archive));
                    continue;
                }
                
                // Add the file to the archive using the source.
                if (zip_file_add(archive, relative_path, source, ZIP_FL_OVERWRITE | ZIP_FL_ENC_UTF_8) < 0) {
                    zip_source_free(source); // Must free the source even on failure
                    sniper_log(LOG_ERROR, "compress:zip", "Error adding file '%s': %s", full_path, zip_strerror(archive));
                } else {
                    if (verbose) {
                        sniper_log(LOG_DEBUG, "compress:zip", "Added: %s", relative_path);
                    }
                }
            }
        }
    }

    closedir(dir);
}
