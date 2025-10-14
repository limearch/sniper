/**
 * @file tar_compress.h
 * @brief Header for TAR compression functionality.
 */

#ifndef TAR_COMPRESS_H
#define TAR_COMPRESS_H

#include <stdbool.h> // Include for bool type

/**
 * @brief Compresses a folder into a TAR archive using the system's `tar` command.
 *
 * @param folder_path The source directory to compress.
 * @param output_file The destination archive file (e.g., archive.tar.gz).
 * @param compression_type The compression algorithm to use ("gzip", "bzip2", "xz", or NULL for none).
 * @param verbose If true, enables verbose logging.
 * @return 0 on success, 1 on failure.
 */
int tar_compress_folder(const char *folder_path, const char *output_file, const char *compression_type, bool verbose);

#endif // TAR_COMPRESS_H
