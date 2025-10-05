// File: tools/compress/tar_compress.h | Language: C/C++ Header

#ifndef TAR_COMPRESS_H
#define TAR_COMPRESS_H

// Function declaration for compressing a folder into a TAR archive.
int tar_compress_folder(const char *folder_path, const char *output_file, const char *compression_type);

#endif // TAR_COMPRESS_H