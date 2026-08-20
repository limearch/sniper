// File: tools/secret-hound/src/hound_core/rule_parser.hpp
// Description: Defines structures for rules and the interface for parsing them. (UPDATED)

#ifndef RULE_PARSER_HPP
#define RULE_PARSER_HPP

#include <string>
#include <vector>
#include <regex>

// Represents a single rule for detecting a secret.
struct DetectionRule {
    std::string id;
    std::string description;
    std::string regex_str;
    std::regex compiled_regex;
    double min_entropy = 0.0;
    std::string confidence = "low"; // Confidence as a string (low, medium, high)
    int confidence_level = 0;      // Numeric confidence (0=low, 1=medium, 2=high)
};

// The main class responsible for loading and managing rules.
class RuleParser {
public:
    static std::vector<DetectionRule> parse_rules_from_file(const std::string& filepath);
};

#endif // RULE_PARSER_HPP
