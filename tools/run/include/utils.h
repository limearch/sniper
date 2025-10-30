/**
 * @file utils.h
 * @brief Utility function declarations specific to the 'run' tool.
 *
 * This header contains prototypes for functions that are unique to the 'run'
 * tool's logic, such as creating temporary executable names and checking
 * for command existence. General-purpose functions have been moved to
 * the central sniper_c_utils library.
 */

#ifndef RUN_UTILS_H
#define RUN_UTILS_H

#include <stdbool.h>
#include <time.h>

// --- Global Options ---
// This flag is controlled by the --no-color option.
extern bool g_use_color;
// This global pointer holds the path of the temporary file to be cleaned up on exit.
extern const char* g_temp_executable_to_cleanup;

// --- Function Prototypes ---

/**
 * @brief Checks if a command-line tool exists in the system's PATH.
 * @param name The command name to check.
 * @return True if the command exists, false otherwise.
 */
bool check_command(const char *name);

/**
 * @brief Creates a unique temporary filename for a compiled executable.
 *
 * It registers the created file path for automatic cleanup upon program exit.
 *
 * @param input_path The path of the source file, used to generate a base name.
 * @return A dynamically allocated string with the path to the temporary file, or NULL on failure.
 */
char *make_output_name(const char *input_path);

/**
 * @brief Calculates the time difference in seconds between two timespec structs.
 * @param start The starting time.
 * @param end The ending time.
 * @return The difference in seconds as a double.
 */
double get_time_diff(struct timespec *start, struct timespec *end);

/**
 * @brief Gets the last modification time of a file.
 * @param filepath The path to the file.
 * @return The modification time as time_t, or (time_t)-1 on error.
 */
time_t get_file_mtime(const char* filepath);

/**
 * @brief The atexit handler function that deletes the temporary executable.
 */
void cleanup_temp_file(void);

#endif // RUN_UTILS_H
