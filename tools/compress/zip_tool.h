/**
 * @file zip_tool.h
 * @brief Header file for ZIP compression functionality.
 *
 * Declares the core functions and data structures used for creating ZIP archives,
 * including the main compression orchestrator and utility functions.
 */

#ifndef ZIP_TOOL_H
#define ZIP_TOOL_H

#include <zip.h>     // From libzip library
#include <time.h>    // For clock_t
#include <stdbool.h> // For bool type

/**
 * @brief The main function to handle the entire ZIP compression process for a folder.
 *
 * This function orchestrates the process by opening a ZIP archive, recursively
 * walking the source directory to add files, closing the archive, and optionally
 * testing its integrity.
 *
 * @param folder_path Path to the folder to compress.
 * @param output_file Path to the output ZIP file.
 * @param level Compression level (0-9, or -1 for default).
 * @param verbose If true, enables detailed logging for each file.
 * @param test_archive If true, tests the archive's integrity after creation.
 * @param num_threads (Not implemented) Reserved for future multi-threading.
 * @param exclude_ext File extension to exclude (e.g., ".log").
 * @param password (Not implemented) Reserved for password protection.
 * @param filter_ext File extension to include exclusively (e.g., ".txt").
 * @param skip_hidden If true, skips files and directories starting with a dot.
 * @return 0 on success, 1 on failure.
 */
int compress_folder(
    const char *folder_path, 
    const char *output_file, 
    int level, 
    bool verbose, 
    bool test_archive, 
    int num_threads, 
    const char *exclude_ext, 
    const char *password, 
    const char *filter_ext, 
    bool skip_hidden
);

/**
 * @brief Recursively iterates through a folder and adds its contents to a ZIP archive.
 *
 * This is the core worker function that traverses the directory tree.
 *
 * @param archive The active zip archive handle.
 * @param folder_path The current folder being processed.
 * @param base_path The relative path to use inside the ZIP archive.
 * @param verbose Flag for verbose output.
 * @param skip_hidden Flag to skip hidden files/directories.
 * @param exclude_ext File extension to exclude.
 * @param filter_ext File extension to include exclusively.
 */
void zip_folder(
    zip_t *archive, 
    const char *folder_path, 
    const char *base_path, 
    bool verbose, 
    bool skip_hidden, 
    const char *exclude_ext, 
    const char *filter_ext
);

/**
 * @brief Checks if a filename should be excluded based on its extension.
 * @param filename The name of the file.
 * @param exclude_ext The extension to exclude (e.g., ".log").
 * @return 1 if the file should be excluded, 0 otherwise.
 */
int exclude_file(const char *filename, const char *exclude_ext);

/**
 * @brief Checks if a filename should be included based on a filter extension.
 * @param filename The name of the file.
 * @param filter_ext The only extension to include (e.g., ".txt").
 * @return 1 if the file's extension matches the filter, 0 otherwise.
 */
int filter_file(const char *filename, const char *filter_ext);

#endif // ZIP_TOOL_H
