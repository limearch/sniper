// File: tools/secret-hound/src/hound_core/rule_parser.cpp
// Description: Implements the logic for parsing secret detection rules from JSON. (UPDATED)

#include "rule_parser.hpp"
#include <fstream>
#include <sstream>
#include <stdexcept>

extern "C" {
    #include "sniper_c_utils.h"
    #include "cJSON.h"
}

std::vector<DetectionRule> RuleParser::parse_rules_from_file(const std::string& filepath) {
    std::ifstream file_stream(filepath);
    if (!file_stream.is_open()) {
        throw std::runtime_error("Rule file not found or could not be opened: " + filepath);
    }
    std::stringstream buffer;
    buffer << file_stream.rdbuf();
    std::string file_content = buffer.str();

    cJSON* json = cJSON_Parse(file_content.c_str());
    if (json == NULL) {
        const char *error_ptr = cJSON_GetErrorPtr();
        std::string error_msg = "Failed to parse rule file. ";
        if (error_ptr != NULL) error_msg += "Error before: " + std::string(error_ptr);
        cJSON_Delete(json);
        throw std::runtime_error(error_msg);
    }

    if (!cJSON_IsArray(json)) {
        cJSON_Delete(json);
        throw std::runtime_error("Rule file must contain a JSON array at the root.");
    }

    std::vector<DetectionRule> rules;
    cJSON* rule_json = NULL;

    cJSON_ArrayForEach(rule_json, json) {
        DetectionRule rule;
        cJSON* id = cJSON_GetObjectItemCaseSensitive(rule_json, "id");
        cJSON* regex_str = cJSON_GetObjectItemCaseSensitive(rule_json, "regex");

        if (cJSON_IsString(id) && (id->valuestring != NULL) &&
            cJSON_IsString(regex_str) && (regex_str->valuestring != NULL)) 
        {
            rule.id = id->valuestring;
            rule.regex_str = regex_str->valuestring;
            
            cJSON* description = cJSON_GetObjectItemCaseSensitive(rule_json, "description");
            if (cJSON_IsString(description) && (description->valuestring != NULL)) {
                rule.description = description->valuestring;
            }

            cJSON* min_entropy = cJSON_GetObjectItemCaseSensitive(rule_json, "min_entropy");
            if (cJSON_IsNumber(min_entropy)) {
                rule.min_entropy = min_entropy->valuedouble;
            }

            // --- NEW: Parse confidence level ---
            cJSON* confidence = cJSON_GetObjectItemCaseSensitive(rule_json, "confidence");
            if (cJSON_IsString(confidence) && (confidence->valuestring != NULL)) {
                rule.confidence = confidence->valuestring;
                // Convert string confidence to a numeric level for easy comparison.
                if (rule.confidence == "high") rule.confidence_level = 2;
                else if (rule.confidence == "medium") rule.confidence_level = 1;
                else rule.confidence_level = 0; // low
            }

            try {
                rule.compiled_regex.assign(rule.regex_str, std::regex_constants::optimize);
            } catch (const std::regex_error& e) {
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
