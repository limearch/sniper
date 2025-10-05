// File: tools/compress/zip_folder.c | Language: C

#include <stdio.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <zip.h>
#include "zip_tool.h"

/**
 * @brief Recursively iterates through a folder and adds its contents to a ZIP archive.
 *
 * @param archive The zip archive handle.
 * @param folder_path The current folder being processed.
 * @param base_path The relative path inside the ZIP archive.
 * @param verbose Flag for verbose output.
 * @param skip_hidden Flag to skip hidden files/directories.
 * @param exclude_ext File extension to exclude.
 * @param filter_ext File extension to include exclusively.
 */
void zip_folder(zip_t *archive, const char *folder_path, const char *base_path, int verbose, int skip_hidden, const char *exclude_ext, const char *filter_ext) {
    DIR *dir = opendir(folder_path);
    if (!dir) {
        perror("opendir");
        return;
    }

    struct dirent *entry;
    char full_path[1024];
    char relative_path[1024];

    while ((entry = readdir(dir)) != NULL) {
        // Skip '.' and '..' directories
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        // Skip hidden files if the flag is set
        if (skip_hidden && entry->d_name[0] == '.') {
            continue;
        }

        snprintf(full_path, sizeof(full_path), "%s/%s", folder_path, entry->d_name);
        // Create the relative path for the file inside the zip
        if (strlen(base_path) > 0) {
            snprintf(relative_path, sizeof(relative_path), "%s/%s", base_path, entry->d_name);
        } else {
            strcpy(relative_path, entry->d_name);
        }

        struct stat statbuf;
        if (stat(full_path, &statbuf) == 0) {
            if (S_ISDIR(statbuf.st_mode)) {
                // If it's a directory, add an entry for it and recurse
                zip_dir_add(archive, relative_path, ZIP_FL_ENC_UTF_8);
                // *** THIS IS THE CORRECTED RECURSIVE CALL ***
                zip_folder(archive, full_path, relative_path, verbose, skip_hidden, exclude_ext, filter_ext);
            } else {
                // It's a file, check against filters
                if (exclude_ext && exclude_file(entry->d_name, exclude_ext)) {
                    if (verbose) printf("Excluding: %s\n", relative_path);
                    continue;
                }
                if (filter_ext && !filter_file(entry->d_name, filter_ext)) {
                    if (verbose) printf("Skipping (filter): %s\n", relative_path);
                    continue;
                }

                // Add file to the archive
                zip_source_t *source = zip_source_file(archive, full_path, 0, 0);
                if (source == NULL || zip_file_add(archive, relative_path, source, ZIP_FL_OVERWRITE | ZIP_FL_ENC_UTF_8) < 0) {
                    zip_source_free(source);
                    fprintf(stderr, "Error adding file '%s': %s\n", full_path, zip_strerror(archive));
                } else {
                    if (verbose) {
                        printf("Added: %s\n", relative_path);
                    }
                }
            }
        }
    }

    closedir(dir);
}