/**
 * @file config.c
 * @brief Implements the core logic for the configer tool (get, set, delete)
 *        using the cJSON library.
 */

#include "config.h"
#include "sniper_c_utils.h" // For logging
#include "cJSON.h"          // For JSON manipulation

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * @brief Reads the entire content of a file into a dynamically allocated string.
 * @param filename The path to the file.
 * @return A heap-allocated string with the file content, or NULL on failure. Caller must free.
 */
static char* read_file(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (!file) return NULL;
    
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    char *content = malloc(length + 1);
    if (!content) {
        fclose(file);
        return NULL;
    }
    
    if (fread(content, 1, length, file) != (size_t)length) {
        free(content);
        fclose(file);
        return NULL;
    }

    content[length] = '\0';
    fclose(file);
    return content;
}

/**
 * @brief Writes data to a file, overwriting its content.
 * @param filename The path to the file.
 * @param data The string data to write.
 * @return 0 on success, 1 on failure.
 */
static int write_file(const char *filename, const char *data) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        sniper_log(LOG_ERROR, "configer", "Could not write to file %s.", filename);
        return 1;
    }
    fputs(data, file);
    fclose(file);
    return 0;
}

int set_value(const char *filepath, const char *category, const char *key, const char *value) {
    char *data = read_file(filepath);
    // If file doesn't exist, create an empty JSON object. Otherwise, parse it.
    cJSON *json = data ? cJSON_Parse(data) : cJSON_CreateObject();
    if (data) free(data);

    if (!json) {
        sniper_log(LOG_ERROR, "configer", "Failed to parse JSON. Check file format at: %s", filepath);
        return 1;
    }

    cJSON *cat = cJSON_GetObjectItemCaseSensitive(json, category);
    if (!cJSON_IsObject(cat)) { // If category doesn't exist or is not an object, create it.
        cat = cJSON_AddObjectToObject(json, category);
    }
    
    // Check if the key already exists to replace it, otherwise add a new one.
    cJSON* existing_item = cJSON_GetObjectItemCaseSensitive(cat, key);
    if (existing_item) {
        cJSON_ReplaceItemInObject(cat, key, cJSON_CreateString(value));
    } else {
        cJSON_AddItemToObject(cat, key, cJSON_CreateString(value));
    }
    
    char *out = cJSON_Print(json); // Get formatted JSON string
    cJSON_Delete(json);

    if (!out) {
        sniper_log(LOG_ERROR, "configer", "Failed to generate JSON string for writing.");
        return 1;
    }

    int result = write_file(filepath, out);
    if (result == 0) {
        // Log the change using the central library function
        sniper_log_config_update("SET", category, key, value, "configer");
    }
    
    free(out);
    return result;
}

int get_value(const char *filepath, const char *category, const char *key) {
    char *data = read_file(filepath);
    if (!data) {
        sniper_log(LOG_ERROR, "configer", "Config file not found at: %s", filepath);
        return 1;
    }

    cJSON *json = cJSON_Parse(data);
    free(data);
    if (!json) {
        sniper_log(LOG_ERROR, "configer", "Failed to parse JSON. Check file format.");
        return 1;
    }

    cJSON *cat = cJSON_GetObjectItemCaseSensitive(json, category);
    if (!cat) {
        sniper_log(LOG_WARN, "configer", "Category '%s' not found.", category);
    } else {
        cJSON *item = cJSON_GetObjectItemCaseSensitive(cat, key);
        if (item && cJSON_IsString(item)) {
            printf("%s\n", item->valuestring); // Print raw value to stdout
        } else if (item && cJSON_IsNumber(item)) {
            printf("%g\n", item->valuedouble);
        } else if (item && cJSON_IsBool(item)) {
            printf("%s\n", cJSON_IsTrue(item) ? "true" : "false");
        } else {
            sniper_log(LOG_WARN, "configer", "Key '%s' not found in category '%s'.", key, category);
        }
    }

    cJSON_Delete(json);
    return 0;
}

int delete_value(const char *filepath, const char *category, const char *key) {
    char *data = read_file(filepath);
    if (!data) {
        sniper_log(LOG_WARN, "configer", "Config file not found. Nothing to delete.");
        return 0; // Not a fatal error
    }

    cJSON *json = cJSON_Parse(data);
    free(data);
    if (!json) {
        sniper_log(LOG_ERROR, "configer", "Failed to parse JSON.");
        return 1;
    }

    cJSON *cat = cJSON_GetObjectItemCaseSensitive(json, category);
    if (cat && cJSON_HasObjectItem(cat, key)) {
        cJSON_DeleteItemFromObject(cat, key);
    } else {
        sniper_log(LOG_WARN, "configer", "Key or category not found. Nothing to delete.");
        cJSON_Delete(json);
        return 0;
    }

    char *out = cJSON_Print(json);
    cJSON_Delete(json);
    if (!out) {
        sniper_log(LOG_ERROR, "configer", "Failed to generate JSON string for writing.");
        return 1;
    }

    int result = write_file(filepath, out);
    if (result == 0) {
        sniper_log_config_update("DELETE", category, key, NULL, "configer");
    }

    free(out);
    return result;
}
