/**
 * @file scanner.cpp
 * @brief Implements the core file scanning logic for secret-hound.
 * @version 2.2 (Corrected JSON Output & Smart Scan Logic)
 * 
 * - Implements `escape_json_string` to ensure all output is valid JSON.
 * - Implements "smart" scanning logic for high-risk files by lowering entropy
 *   thresholds and performing generic entropy checks.
 */

#include "scanner.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <map>
#include <vector>
#include <time.h>

extern "C" {
    #include "sniper_c_utils.h"
}

/**
 * @brief Escapes characters in a string to make it a valid JSON string value.
 * This is crucial for preventing malformed JSON when secrets contain quotes or backslashes.
 * @param s The input string.
 * @return The escaped string.
 */
std::string escape_json_string(const std::string& s) {
    std::stringstream escaped;
    for (char c : s) {
        switch (c) {
            case '"':  escaped << "\\\""; break;
            case '\\': escaped << "\\\\"; break;
            case '\b': escaped << "\\b";  break;
            case '\f': escaped << "\\f";  break;
            case '\n': escaped << "\\n";  break;
            case '\r': escaped << "\\r";  break;
            case '\t': escaped << "\\t";  break;
            default:
                // Non-printable characters are ignored for simplicity.
                if ('\x00' <= c && c <= '\x1f') {
                    // Ignored
                } else {
                    escaped << c;
                }
        }
    }
    return escaped.str();
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

void Scanner::scan_content(const std::string& content, const std::string& source_name) {
    std::istringstream content_stream(content);
    std::string line;
    int line_num = 1;
    while (std::getline(content_stream, line)) {
        process_line(line, line_num, source_name, false); // is_high_risk is false for generic content
        line_num++;
    }
}

void Scanner::wait_for_completion() {
    while (true) {
        pthread_mutex_lock(&pool->lock);
        bool done = (pool->count == 0 && active_tasks == 0);
        pthread_mutex_unlock(&pool->lock);
        if (done) {
            break;
        }
        struct timespec sleep_time = {0, 100000000}; // 100ms
        nanosleep(&sleep_time, NULL);
    }
}

void Scanner::add_scan_task(ScanTaskArgs* task_args) {
    active_tasks++;
    if (threadpool_add(pool, &Scanner::scan_file_task_wrapper, task_args) != 0) {
        active_tasks--;
        delete task_args;
    }
}

const std::vector<DetectionRule>& Scanner::get_rules() const {
    return rules;
}

double Scanner::calculate_shannon_entropy(const std::string& data) {
    if (data.empty()) return 0.0;
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
    // --- "Smart" Logic: Check if the file is high-risk based on its name/path ---
    bool is_high_risk_file = false;
    const char* high_risk_patterns[] = {
        ".env", ".pem", ".key", "id_rsa", "credentials", ".npmrc", 
        ".history", ".bash_history", ".zsh_history", "htpasswd", ".properties",
        NULL // Sentinel value
    };
    for (int i = 0; high_risk_patterns[i] != NULL; ++i) {
        if (file_path.find(high_risk_patterns[i]) != std::string::npos) {
            is_high_risk_file = true;
            break;
        }
    }

    std::ifstream file_stream(file_path);
    if (!file_stream.is_open()) {
        active_tasks--;
        return;
    }
    std::string line;
    int line_num = 1;
    while (std::getline(file_stream, line)) {
        process_line(line, line_num, file_path, is_high_risk_file);
        line_num++;
    }
    active_tasks--;
}

void Scanner::process_line(const std::string& line, int line_num, const std::string& source_name, bool is_high_risk) {
    // 1. Scan using predefined regex rules
    for (const auto& rule : rules) {
        std::smatch match;
        std::string::const_iterator search_start(line.cbegin());
        
        while (std::regex_search(search_start, line.cend(), match, rule.compiled_regex)) {
            std::string matched_str = match[0].str();
            
            double entropy = 0.0;
            double required_entropy = rule.min_entropy;

            // Smart Logic: For high-risk files, lower the entropy requirement.
            if (is_high_risk && required_entropy > 3.0) {
                required_entropy = 3.0;
            }

            if (required_entropy > 0.0) {
                entropy = calculate_shannon_entropy(matched_str);
                if (entropy < required_entropy) {
                    search_start = match.suffix().first;
                    continue; // Skip if entropy is too low
                }
            }

            // If we reach here, the secret is valid.
            std::lock_guard<std::mutex> lock(output_mutex);
            std::cout << "{\"file\": \"" << escape_json_string(source_name)
                      << "\", \"line\": " << line_num
                      << ", \"rule_id\": \"" << escape_json_string(rule.id)
                      << "\", \"description\": \"" << escape_json_string(rule.description)
                      << "\", \"match\": \"" << escape_json_string(matched_str)
                      << "\", \"entropy\": " << entropy
                      << "}" << std::endl;
            
            search_start = match.suffix().first;
        }
    }
    
    // 2. "Smart" Logic: Perform a generic high-entropy scan on high-risk files.
    if (is_high_risk) {
        std::stringstream ss(line);
        std::string word;
        // Split line by common delimiters to find potential secret values.
        while (std::getline(ss, word, ' ')) {
             std::getline(ss, word, '=');
             std::getline(ss, word, '"');
             std::getline(ss, word, '\'');

            if (word.length() >= 20 && word.length() <= 128) {
                double entropy = calculate_shannon_entropy(word);
                // Use a high threshold for generic strings to reduce false positives.
                if (entropy > 4.2) { 
                     std::lock_guard<std::mutex> lock(output_mutex);
                     std::cout << "{\"file\": \"" << escape_json_string(source_name)
                               << "\", \"line\": " << line_num
                               << ", \"rule_id\": \"" << "GenericHighEntropy"
                               << "\", \"description\": \"" << "High entropy string in sensitive file"
                               << "\", \"match\": \"" << escape_json_string(word)
                               << "\", \"entropy\": " << entropy
                               << "}" << std::endl;
                }
            }
        }
    }
}
