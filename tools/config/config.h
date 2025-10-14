/**
 * @file config.h
 * @brief Header file for the configuration management logic of 'configer'.
 */

#ifndef CONFIG_H
#define CONFIG_H

// --- Function Prototypes ---

/**
 * @brief Sets or updates a value in the JSON configuration file.
 * @param filepath The full path to sniper-config.json.
 * @param category The top-level key in the JSON.
 * @param key The specific key to set.
 * @param value The new value for the key.
 * @return 0 on success, 1 on failure.
 */
int set_value(const char *filepath, const char *category, const char *key, const char *value);

/**
 * @brief Deletes a key-value pair from the JSON configuration file.
 * @param filepath The full path to sniper-config.json.
 * @param category The top-level key in the JSON.
 * @param key The specific key to delete.
 * @return 0 on success, 1 on failure.
 */
int delete_value(const char *filepath, const char *category, const char *key);

/**
 * @brief Retrieves and prints a specific value from the JSON configuration file.
 * @param filepath The full path to sniper-config.json.
 * @param category The top-level key in the JSON.
 * @param key The specific key to retrieve.
 * @return 0 on success, 1 on failure.
 */
int get_value(const char *filepath, const char *category, const char *key);

#endif // CONFIG_H
