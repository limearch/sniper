// File: tools/secret-hound/src/hound_core/rule_parser.cpp
// Description: Implements the logic for parsing secret detection rules from JSON. (UPDATED with correct includes)

#include "rule_parser.hpp"
#include <fstream>
#include <sstream>
#include <stdexcept>

// Include the central SNIPER C utility library
// This block ensures C++ treats the header as a C header
extern "C" {
    #include "sniper_c_utils.h"
    #include "cJSON.h"
}

std::vector<DetectionRule> RuleParser::parse_rules_from_file(const std::string& filepath) {
    // Read the entire file into a string
    std::ifstream file_stream(filepath);
    if (!file_stream.is_open()) {
        throw std::runtime_error("Rule file not found or could not be opened: " + filepath);
    }
    std::stringstream buffer;
    buffer << file_stream.rdbuf();
    std::string file_content = buffer.str();

    // Parse the JSON content using cJSON
    cJSON* json = cJSON_Parse(file_content.c_str());
    if (json == NULL) {
        const char *error_ptr = cJSON_GetErrorPtr();
        std::string error_msg = "Failed to parse rule file. ";
        if (error_ptr != NULL) {
            error_msg += "Error before: " + std::string(error_ptr);
        }
        cJSON_Delete(json);
        throw std::runtime_error(error_msg);
    }

    if (!cJSON_IsArray(json)) {
        cJSON_Delete(json);
        throw std::runtime_error("Rule file must contain a JSON array at the root.");
    }

    std::vector<DetectionRule> rules;
    cJSON* rule_json = NULL;

    // Iterate over the JSON array
    cJSON_ArrayForEach(rule_json, json) {
        DetectionRule rule;

        cJSON* id = cJSON_GetObjectItemCaseSensitive(rule_json, "id");
        cJSON* description = cJSON_GetObjectItemCaseSensitive(rule_json, "description");
        cJSON* regex_str = cJSON_GetObjectItemCaseSensitive(rule_json, "regex");
        cJSON* min_entropy = cJSON_GetObjectItemCaseSensitive(rule_json, "min_entropy");

        if (cJSON_IsString(id) && (id->valuestring != NULL) &&
            cJSON_IsString(regex_str) && (regex_str->valuestring != NULL)) 
        {
            rule.id = id->valuestring;
            rule.regex_str = regex_str->valuestring;
            
            if (cJSON_IsString(description) && (description->valuestring != NULL)) {
                rule.description = description->valuestring;
            } else {
                rule.description = "No description provided.";
            }

            if (cJSON_IsNumber(min_entropy)) {
                rule.min_entropy = min_entropy->valuedouble;
            } else {
                rule.min_entropy = 0.0;
            }

            // Compile the regex for faster execution later
            try {
                rule.compiled_regex.assign(rule.regex_str, std::regex_constants::optimize);
            } catch (const std::regex_error& e) {
                // Skip invalid regex patterns but warn the user
                sniper_log(LOG_WARN, "secret-hound", "Skipping rule '%s' due to invalid regex: %s", rule.id.c_str(), e.what());
                continue;
            }
            rules.push_back(rule);
        } else {
             sniper_log(LOG_WARN, "secret-hound", "Skipping a rule due to missing 'id' or 'regex'.");
        }
    }

    cJSON_Delete(json);
    return rules;
}
