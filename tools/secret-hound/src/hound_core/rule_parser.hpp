// File: tools/secret-hound/src/hound_core/rule_parser.hpp
// Description: Defines the structures for holding parsed secret-detection rules
// and the interface for parsing them from a JSON file.

#ifndef RULE_PARSER_HPP
#define RULE_PARSER_HPP

#include <string>
#include <vector>
#include <regex>

// Represents a single rule for detecting a secret.
struct DetectionRule {
    std::string id;              // Unique identifier, e.g., "AWS_KEY"
    std::string description;     // Human-readable description
    std::string regex_str;       // The regular expression pattern
    std::regex compiled_regex;   // The compiled regex object for performance
    double min_entropy;          // Minimum Shannon entropy required to match (0 if not used)
};

// The main class responsible for loading and managing rules.
class RuleParser {
public:
    /**
     * @brief Parses a JSON file containing an array of detection rules.
     * @param filepath The path to the JSON rule file.
     * @return A vector of DetectionRule structs.
     * @throws std::runtime_error if the file cannot be read or parsed.
     */
    static std::vector<DetectionRule> parse_rules_from_file(const std::string& filepath);
};

#endif // RULE_PARSER_HPP
