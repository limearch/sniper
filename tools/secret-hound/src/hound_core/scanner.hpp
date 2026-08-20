/**
 * @file scanner.hpp
 * @brief Defines the core Scanner class for secret detection.
 * @version 2.1 (Corrected Declaration)
 * 
 * This header defines the main Scanner class, which orchestrates multi-threaded
 * file and content scanning based on a provided set of detection rules.
 */

#ifndef SCANNER_HPP
#define SCANNER_HPP

#include "rule_parser.hpp"
#include "threadpool.hpp"
#include <string>
#include <vector>
#include <atomic>
#include <mutex>

// Forward declaration of the Scanner class to be used in ScanTaskArgs.
class Scanner;

/**
 * @struct ScanTaskArgs
 * @brief Structure passed as an argument to each file scanning task in the thread pool.
 */
struct ScanTaskArgs {
    Scanner* scanner_instance; // Pointer back to the main scanner instance for context.
    std::string file_path;     // The absolute path of the file to scan.
};

/**
 * @class Scanner
 * @brief The main scanner class that manages the thread pool and scanning logic.
 */
class Scanner {
public:
    /**
     * @brief Constructs a Scanner instance.
     * @param rules A vector of detection rules to use for scanning.
     * @param num_threads The number of worker threads for the thread pool.
     */
    Scanner(std::vector<DetectionRule> rules, int num_threads);

    /**
     * @brief Destroys the Scanner instance, ensuring the thread pool is shut down.
     */
    ~Scanner();

    /**
     * @brief Scans a single file for secrets. This is the core worker logic executed by threads.
     * @param file_path The path of the file to scan.
     */
    void scan_file(const std::string& file_path);

    /**
     * @brief Scans content provided as a string (e.g., from stdin).
     * @param content The string content to be scanned.
     * @param source_name A name for the source (e.g., "stdin") for reporting purposes.
     */
    void scan_content(const std::string& content, const std::string& source_name);

    /**
     * @brief Blocks until all pending scan tasks in the thread pool have completed.
     */
    void wait_for_completion();

    /**
     * @brief Public method to add a new file scanning task to the thread pool's queue.
     * @param task_args A pointer to the arguments for the task, allocated on the heap.
     */
    void add_scan_task(ScanTaskArgs* task_args);

    /**
     * @brief A static wrapper function to be used as a task by the C-style thread pool.
     * @param args A void pointer to a ScanTaskArgs struct.
     */
    static void scan_file_task_wrapper(void* args);

    /**
     * @brief Gets the rules currently loaded in the scanner.
     * @return A constant reference to the vector of detection rules.
     */
    const std::vector<DetectionRule>& get_rules() const;

    /**
     * @brief A public pointer to the thread pool, required by the C-style callback.
     */
    threadpool_t* pool;

private:
    std::vector<DetectionRule> rules;      // The set of rules to scan for.
    std::atomic<int> active_tasks;         // Counter for tasks currently being processed.
    std::mutex output_mutex;               // Mutex to protect std::cout for thread-safe JSON output.

    /**
     * @brief Calculates the Shannon entropy of a given string.
     * @param data The string to analyze.
     * @return The calculated entropy value.
     */
    static double calculate_shannon_entropy(const std::string& data);
    
    /**
     * @brief Processes a single line of text against all loaded rules.
     * @param line The line of text to process.
     * @param line_num The line number within its source.
     * @param source_name The name of the source file or stream.
     * @param is_high_risk A flag indicating if smart, more aggressive scanning should be used.
     */
    void process_line(const std::string& line, int line_num, const std::string& source_name, bool is_high_risk);
};

#endif // SCANNER_HPP
