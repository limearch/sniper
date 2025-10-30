/**
 * @file scanner.cpp
 * @brief Implements the core file scanning logic, including multi-threading,
 *        regex matching, and entropy analysis. (UPDATED for output flushing).
 */

#include "scanner.hpp"
#include <iostream>
#include <fstream>
#include <cmath>
#include <map>
#include <vector>
#include <time.h> // Required for nanosleep

// Include the central SNIPER C utility library
extern "C" {
    #include "sniper_c_utils.h"
}

// Data structure passed to the directory walk callback.
struct WalkData {
    Scanner* scanner_instance;
};

/**
 * @brief Callback function for sniper_directory_walk.
 * This function is called for every file and directory found by the walker.
 */
int directory_walk_callback(const WalkInfo* info, void* user_data) {
    // We are only interested in regular files for scanning.
    if (!S_ISREG(info->stat_info.st_mode)) {
        return 0; // Continue walking
    }

    WalkData* data = (WalkData*)user_data;
    
    // Create the task arguments on the heap because the task runs asynchronously.
    ScanTaskArgs* task_args = new ScanTaskArgs{
        data->scanner_instance,
        std::string(info->full_path)
    };

    // Use the public method to add the file to the thread pool's queue.
    data->scanner_instance->add_scan_task(task_args);
    
    return 0; // Continue walking
}

Scanner::Scanner(std::vector<DetectionRule> rules, int num_threads) 
    : rules(std::move(rules)), active_tasks(0) {
    pool = threadpool_create(num_threads, 4096);
    if (!pool) {
        throw std::runtime_error("Failed to create thread pool.");
    }
}

Scanner::~Scanner() {
    if (pool) {
        threadpool_destroy(pool);
    }
}

void Scanner::scan_directory(const std::string& directory_path) {
    WalkData walk_data = {this};
    WalkOptions options = {.follow_symlinks = false, .skip_hidden = true, .max_depth = -1};
    sniper_directory_walk(directory_path.c_str(), &options, directory_walk_callback, &walk_data);
}

void Scanner::wait_for_completion() {
    while (true) {
        pthread_mutex_lock(&pool->lock);
        // The condition for completion is that the queue is empty AND no tasks are currently running.
        bool done = (pool->count == 0 && active_tasks == 0);
        pthread_mutex_unlock(&pool->lock);
        if (done) {
            break;
        }

        // Use the POSIX-standard nanosleep for a non-busy wait.
        struct timespec sleep_time;
        sleep_time.tv_sec = 0;
        sleep_time.tv_nsec = 100000000; // 100 milliseconds
        nanosleep(&sleep_time, NULL);
    }
}

void Scanner::add_scan_task(ScanTaskArgs* task_args) {
    // Increment the counter BEFORE adding the task.
    active_tasks++;
    if (threadpool_add(pool, &Scanner::scan_file_task_wrapper, task_args) != 0) {
        // If adding fails, decrement the counter to maintain consistency.
        active_tasks--;
        delete task_args;
    }
}

const std::vector<DetectionRule>& Scanner::get_rules() const {
    return rules;
}

double Scanner::calculate_shannon_entropy(const std::string& data) {
    if (data.empty()) {
        return 0.0;
    }
    std::map<char, int> freqs;
    for (char c : data) {
        freqs[c]++;
    }
    double entropy = 0.0;
    double len = static_cast<double>(data.length());
    for (auto const& [key, val] : freqs) {
        double p_x = static_cast<double>(val) / len;
        if (p_x > 0) {
            entropy -= p_x * log2(p_x);
        }
    }
    return entropy;
}

void Scanner::scan_file_task_wrapper(void* args) {
    ScanTaskArgs* task_args = static_cast<ScanTaskArgs*>(args);
    task_args->scanner_instance->scan_file(task_args->file_path);
    delete task_args; 
}

void Scanner::scan_file(const std::string& file_path) {
    std::ifstream file_stream(file_path);
    if (!file_stream.is_open()) {
        active_tasks--;
        return;
    }

    std::string line;
    int line_num = 1;
    while (std::getline(file_stream, line)) {
        for (const auto& rule : rules) {
            std::smatch match;
            std::string::const_iterator search_start(line.cbegin());
            
            while (std::regex_search(search_start, line.cend(), match, rule.compiled_regex)) {
                std::string matched_str = match[0].str();
                
                bool entropy_ok = true;
                double entropy = 0.0;

                if (rule.min_entropy > 0.0) {
                    entropy = calculate_shannon_entropy(matched_str);
                    if (entropy < rule.min_entropy) {
                        entropy_ok = false;
                    }
                }

                if (entropy_ok) {
                    std::lock_guard<std::mutex> lock(output_mutex);
                    
                    // --- START OF CRITICAL FIX ---
                    // Use std::endl to ensure the output buffer is flushed immediately to the pipe.
                    // This guarantees the Python reporter receives the data in real-time and prevents deadlocks.
                    std::cout << "{\"file\": \"" << file_path
                              << "\", \"line\": " << line_num
                              << ", \"rule_id\": \"" << rule.id
                              << "\", \"description\": \"" << rule.description
                              << "\", \"match\": \"" << matched_str
                              << "\", \"entropy\": " << entropy
                              << "}" << std::endl; // <-- std::endl flushes the stream.
                    // --- END OF CRITICAL FIX ---
                }
                search_start = match.suffix().first;
            }
        }
        line_num++;
    }

    // Decrement the counter to signal that this task is complete.
    active_tasks--;
}
