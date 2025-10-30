// File: tools/secret-hound/src/hound_core/scanner.hpp
// Description: Defines the core Scanner class (UPDATED to fix access control errors).

#ifndef SCANNER_HPP
#define SCANNER_HPP

#include "rule_parser.hpp"
#include "threadpool.hpp"
#include <string>
#include <vector>
#include <atomic>
#include <mutex>

// Forward declaration of the Scanner class
class Scanner;

// Structure passed as an argument to each file scanning task in the thread pool.
struct ScanTaskArgs {
    Scanner* scanner_instance; // Pointer back to the main scanner instance
    std::string file_path;           // The path of the file to scan
};

// Main scanner class.
class Scanner {
public:
    /**
     * @brief Constructs a Scanner instance.
     * @param rules A vector of detection rules to use for scanning.
     * @param num_threads The number of worker threads to use.
     */
    Scanner(std::vector<DetectionRule> rules, int num_threads);
    ~Scanner();

    /**
     * @brief Recursively scans a directory for files and adds them to the scan queue.
     * @param directory_path The path to the directory to start scanning from.
     */
    void scan_directory(const std::string& directory_path);
    
    /**
     * @brief Scans a single file for secrets. This is the core worker logic.
     * @param file_path The path of the file to scan.
     */
    void scan_file(const std::string& file_path);
    
    /**
     * @brief Waits for all pending scan tasks in the thread pool to complete.
     */
    void wait_for_completion();

    /**
     * @brief A public method to add a file scanning task to the thread pool.
     * This encapsulates the threadpool_add logic.
     * @param task_args The arguments for the task.
     */
    void add_scan_task(ScanTaskArgs* task_args);

    /**
     * @brief A static wrapper function to be used as a task by the thread pool.
     * It must be public to be accessible as a function pointer.
     * @param args A pointer to a ScanTaskArgs struct.
     */
    static void scan_file_task_wrapper(void* args);

    // Make the rules vector public for access by static task functions.
    const std::vector<DetectionRule>& get_rules() const;

private:
    std::vector<DetectionRule> rules;
    threadpool_t* pool;
    std::atomic<int> active_tasks;
    std::mutex output_mutex; // Mutex to protect cout for thread-safe JSON output

    /**
     * @brief Calculates the Shannon entropy of a given string.
     * @param data The string to analyze.
     * @return The calculated entropy value.
     */
    static double calculate_shannon_entropy(const std::string& data);
};

#endif // SCANNER_HPP
