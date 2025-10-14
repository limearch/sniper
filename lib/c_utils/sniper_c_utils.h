/**
 * @file sniper_c_utils.h
 * @brief The public API for the SNIPER core C utility library.
 * @version 1.0
 * @date 2024-05-22
 *
 * This header provides a centralized set of high-level abstractions for
 * logging, option parsing, help rendering, and directory traversal, intended
 * to be used by all C-based tools within the SNIPER project to reduce code
 * duplication and ensure a consistent user experience.
 */

#ifndef SNIPER_C_UTILS_H
#define SNIPER_C_UTILS_H

// --- Standard Library Includes ---
// These are required for the type definitions in this header file.
#include <stddef.h>   // Required for size_t
#include <stdbool.h>  // Required for bool
#include <stdarg.h>   // Required for va_list
#include <sys/stat.h> // Required for struct stat
#include <dirent.h>   // Required for struct dirent (though not directly used in API)

// --- ANSI Color Definitions ---
#define C_RESET   "\033[0m"
#define C_BOLD    "\033[1m"
#define C_RED     "\033[91m"
#define C_GREEN   "\033[92m"
#define C_YELLOW  "\033[93m"
#define C_BLUE    "\033[94m"
#define C_MAGENTA "\033[0;35m"
#define C_CYAN    "\033[96m"
#define C_WHITE   "\033[97m"

// ==============================================================================
//                              Logging Subsystem
// ==============================================================================

/**
 * @enum LogLevel
 * @brief Defines the severity levels for log messages, mirroring sniper_env.py.
 */
typedef enum {
    LOG_DEBUG,
    LOG_INFO,
    LOG_SUCCESS,
    LOG_WARN,
    LOG_ERROR,
    LOG_UPDATE
} LogLevel;

/**
 * @brief Logs a formatted message to stderr with appropriate colors and prefixes.
 *
 * This function is the primary logging interface for all C tools, ensuring
 * a consistent output format across the entire SNIPER toolkit.
 *
 * @param level The log level (e.g., LOG_INFO, LOG_ERROR).
 * @param tool_name The name of the tool logging the message (e.g., "compress").
 * @param format A printf-style format string.
 * @param ... Variable arguments for the format string.
 */
void sniper_log(LogLevel level, const char* tool_name, const char* format, ...);

/**
 * @brief Logs a configuration change to the central sniper-config.log file.
 *
 * @param action The action taken (e.g., "SET", "DELETE").
 * @param category The top-level key in the JSON.
 * @param key The specific key being changed.
 * @param value The new value (can be NULL for DELETE).
 * @param source The name of the tool making the change.
 */
void sniper_log_config_update(const char* action, const char* category, const char* key, const char* value, const char* source);


// ==============================================================================
//                         Command-Line Option Parsing
// ==============================================================================

/**
 * @enum OptionType
 * @brief Defines the data type of a command-line option's argument.
 */
typedef enum {
    OPT_FLAG,   // A boolean flag, e.g., --verbose. No argument is expected.
    OPT_STRING, // An option that takes a string argument, e.g., --output <file>.
    OPT_INT     // An option that takes an integer argument, e.g., --level 9.
} OptionType;

/**
 * @struct SniperOption
 * @brief A declarative structure to define a single command-line option.
 */
typedef struct {
    char short_name;        ///< The short name of the option (e.g., 'v'). Use 0 if none.
    const char* long_name;  ///< The long name of the option (e.g., "verbose").
    OptionType type;        ///< The type of the option's value (FLAG, STRING, INT).
    void* value_ptr;        ///< A pointer to the variable where the parsed value will be stored.
    const char* help_text;  ///< A brief description of the option for the help screen (not yet used).
} SniperOption;

/**
 * @brief Parses command-line arguments based on a declarative array of options.
 *
 * This function abstracts away the complexity of getopt_long. It automatically
 * handles the -h/--help flags and populates the variables pointed to by value_ptr.
 *
 * @param argc The argument count from main().
 * @param argv The argument vector from main().
 * @param options An array of SniperOption structs. The array must be terminated
 *                by an entry where both short_name and long_name are 0/NULL.
 * @param tool_name The name of the tool, used for displaying the help screen.
 * @return The index of the first non-option argument in argv (similar to optind).
 */
int sniper_parse_options(int argc, char* argv[], SniperOption options[], const char* tool_name);


// ==============================================================================
//                        Directory Traversal Subsystem
// ==============================================================================

/**
 * @struct WalkInfo
 * @brief Contains detailed information about a single file system entry
 *        found during a directory walk.
 */
typedef struct {
    const char* root_path;     ///< The absolute path where the walk began.
    char* full_path;           ///< The absolute path of the current entry.
    char* relative_path;       ///< The path of the entry relative to root_path.
    const char* filename;      ///< The basename of the entry.
    struct stat stat_info;     ///< The result of lstat() on the entry.
    int depth;                 ///< The current recursion depth (0 at root).
} WalkInfo;

/**
 * @typedef WalkCallback
 * @brief A function pointer type for the callback used by sniper_directory_walk.
 * @param info A pointer to a WalkInfo struct with details about the current entry.
 * @param user_data A generic pointer to user-defined data passed through the walk.
 * @return 0 to continue the walk, or any non-zero value to stop immediately.
 */
typedef int (*WalkCallback)(const WalkInfo* info, void* user_data);

/**
 * @struct WalkOptions
 * @brief A structure to control the behavior of the directory walk.
 */
typedef struct {
    bool follow_symlinks; ///< If true, symbolic links to directories will be traversed.
    bool skip_hidden;     ///< If true, files and directories starting with '.' will be ignored.
    int max_depth;        ///< Maximum recursion depth. -1 for unlimited.
} WalkOptions;

/**
 * @brief Recursively walks a directory tree and calls a callback for each entry.
 *
 * This function provides a powerful and safe abstraction for directory traversal,
 * handling path construction and recursion automatically.
 *
 * @param root_path The directory to start walking from.
 * @param options A pointer to WalkOptions to customize the walk, or NULL for default behavior.
 * @param callback The function to call for each file/directory found.
 * @param user_data A generic pointer that will be passed to every call of the callback function.
 * @return 0 on successful completion, or the non-zero value returned by the callback if the walk was stopped.
 */
int sniper_directory_walk(const char* root_path, const WalkOptions* options, WalkCallback callback, void* user_data);


// ==============================================================================
//                              General Utilities
// ==============================================================================

/**
 * @brief Gets the absolute path of the 'sniper' project's root directory.
 * @param buffer A character buffer to store the resulting path.
 * @param buffer_size The size of the buffer.
 * @return 0 on success, 1 on failure.
 */
int sniper_get_root_path(char* buffer, size_t buffer_size);

/**
 * @brief Displays the rich help screen for a specific tool.
 *
 * This function calls the central Python help renderer, providing a consistent
 * and high-quality help experience for all C-based tools.
 *
 * @param tool_name The name of the tool (e.g., "compress", "configer").
 */
void sniper_show_tool_help(const char* tool_name);

/**
 * @brief Checks if a command-line tool exists in the system's PATH.
 * @param command_name The name of the command to check (e.g., "python3").
 * @return 1 if the command exists, 0 otherwise.
 */
int sniper_command_exists(const char* command_name);


#endif // SNIPER_C_UTILS_H
