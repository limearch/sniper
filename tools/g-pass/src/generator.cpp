#include "generator.hpp"
#include <algorithm>
#include <vector>
#include <cmath> // For pow

PasswordGenerator::PasswordGenerator() {
    std::random_device rd;
    rng.seed(rd());
}

std::string PasswordGenerator::generate(const PasswordConfig& config) {
    std::string charset;
    std::vector<char> required_chars;

    if (config.use_lower) {
        charset += CHARSET_LOWER;
        if (config.length > 0) required_chars.push_back(CHARSET_LOWER[std::uniform_int_distribution<int>(0, CHARSET_LOWER.length() - 1)(rng)]);
    }
    if (config.use_upper) {
        charset += CHARSET_UPPER;
        if (config.length > 0) required_chars.push_back(CHARSET_UPPER[std::uniform_int_distribution<int>(0, CHARSET_UPPER.length() - 1)(rng)]);
    }
    if (config.use_numbers) {
        charset += CHARSET_NUMBERS;
        if (config.length > 0) required_chars.push_back(CHARSET_NUMBERS[std::uniform_int_distribution<int>(0, CHARSET_NUMBERS.length() - 1)(rng)]);
    }
    if (config.use_symbols) {
        charset += CHARSET_SYMBOLS;
        if (config.length > 0) required_chars.push_back(CHARSET_SYMBOLS[std::uniform_int_distribution<int>(0, CHARSET_SYMBOLS.length() - 1)(rng)]);
    }
    if (config.use_unicode) {
        charset += CHARSET_UNICODE;
        if (config.length > 0) required_chars.push_back(CHARSET_UNICODE[std::uniform_int_distribution<int>(0, CHARSET_UNICODE.length() - 1)(rng)]);
    }

    if (charset.empty()) {
        return "Error: No character sets selected.";
    }

    std::string final_charset;
    std::copy_if(charset.begin(), charset.end(), std::back_inserter(final_charset),
                 [&](char c) { return config.exclude_chars.find(c) == std::string::npos; });

    if (final_charset.empty()) {
        return "Error: All characters excluded.";
    }

    std::string password;
    password.reserve(config.length);

    std::uniform_int_distribution<int> dist(0, final_charset.length() - 1);
    for (int i = 0; i < config.length; ++i) {
        password += final_charset[dist(rng)];
    }

    if (!required_chars.empty() && required_chars.size() <= (size_t)config.length) {
        for(size_t i = 0; i < required_chars.size(); ++i) {
            password[i] = required_chars[i];
        }
    }
    
    std::shuffle(password.begin(), password.end(), rng);

    return password;
}

// --- Crunch Mode Implementation ---

unsigned long long PasswordGenerator::calculate_crunch_total(int min_len, int max_len, const std::string& charset) {
    unsigned long long total = 0;
    for (int len = min_len; len <= max_len; ++len) {
        total += static_cast<unsigned long long>(std::pow(charset.length(), len));
    }
    return total;
}

void PasswordGenerator::crunch_recursive(int max_len, const std::string& charset, std::string current, OutputCallback& callback) {
    if (current.length() == (size_t)max_len) {
        return;
    }
    for (char c : charset) {
        std::string next = current + c;
        callback(next);
        crunch_recursive(max_len, charset, next, callback);
    }
}

void PasswordGenerator::generate_crunch(int min_len, int max_len, const std::string& charset, OutputCallback callback) {
    for (int len = min_len; len <= max_len; ++len) {
        crunch_recursive(len, charset, "", callback);
    }
}

void PasswordGenerator::pattern_recursive(const std::string& pattern, size_t index, std::string current, OutputCallback& callback) {
    if (index == pattern.length()) {
        callback(current);
        return;
    }

    std::string charset_for_pos;
    char p = pattern[index];
    switch(p) {
        case '@': charset_for_pos = CHARSET_LOWER; break;
        case ',': charset_for_pos = CHARSET_UPPER; break;
        case '%': charset_for_pos = CHARSET_NUMBERS; break;
        case '^': charset_for_pos = CHARSET_SYMBOLS; break;
        default: charset_for_pos = std::string(1, p); break;
    }

    for (char c : charset_for_pos) {
        pattern_recursive(pattern, index + 1, current + c, callback);
    }
}

void PasswordGenerator::generate_crunch_pattern(const std::string& pattern, OutputCallback callback) {
    pattern_recursive(pattern, 0, "", callback);
}
