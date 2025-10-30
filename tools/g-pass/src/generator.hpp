#ifndef GENERATOR_HPP
#define GENERATOR_HPP

#include <string>
#include <random>
#include <functional> // For std::function

// Character sets
const std::string CHARSET_LOWER = "abcdefghijklmnopqrstuvwxyz";
const std::string CHARSET_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const std::string CHARSET_NUMBERS = "0123456789";
const std::string CHARSET_SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?";
const std::string CHARSET_UNICODE = "αβγδεζηθικλμνξοπρστυφχψω"; // Example set

struct PasswordConfig {
    int length = 16;
    bool use_lower = true;
    bool use_upper = true;
    bool use_numbers = true;
    bool use_symbols = true;
    bool use_unicode = false;
    std::string exclude_chars;
};

class PasswordGenerator {
public:
    using OutputCallback = std::function<void(const std::string&)>;

    PasswordGenerator();
    
    // Fast random generation
    std::string generate(const PasswordConfig& config);
    
    // Crunch mode generation
    void generate_crunch(int min_len, int max_len, const std::string& charset, OutputCallback callback);
    void generate_crunch_pattern(const std::string& pattern, OutputCallback callback);
    
    // Helper for crunch mode
    unsigned long long calculate_crunch_total(int min_len, int max_len, const std::string& charset);

private:
    std::mt19937 rng;
    void crunch_recursive(int max_len, const std::string& charset, std::string current, OutputCallback& callback);
    void pattern_recursive(const std::string& pattern, size_t index, std::string current, OutputCallback& callback);
};

#endif // GENERATOR_HPP
