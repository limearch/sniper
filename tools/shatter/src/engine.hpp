// src/engine.hpp
#ifndef SHATTER_ENGINE_HPP
#define SHATTER_ENGINE_HPP

#include <cstddef>
#include <cstdint>

#ifdef __cplusplus
extern "C" {
#endif

// Type definition for the Python callback function.
// Parameters:
//  1. attempts_count: Total number of hashes tried so far.
//  2. current_word: The specific word currently being tested (for UI visualization).
typedef void (*ProgressCallback)(uint64_t, const char*);

/**
 * crack_wordlist
 *
 * Main entry point for the cracking engine.
 *
 * Parameters:
 *  - wordlist_path: Path to the wordlist file.
 *  - salt_hex: The target salt string in Hex format.
 *  - verifier_hex: The target verifier string in Hex format.
 *  - key_len: AES key length (16 for 128-bit, 24 for 192-bit, 32 for 256-bit).
 *  - thread_count: Number of worker threads (0 = auto-detect).
 *  - out_password: Buffer to write the found password into.
 *  - out_size: Size of the output buffer.
 *  - progress_cb: Pointer to the callback function for UI updates (New).
 *
 * Returns:
 *  - 1 if password found.
 *  - 0 if not found.
 *  - -1 on error.
 */
int crack_wordlist(
    const char* wordlist_path,
    const char* salt_hex,
    const char* verifier_hex,
    int key_len,
    int thread_count,
    char* out_password,
    size_t out_size,
    ProgressCallback progress_cb
);

#ifdef __cplusplus
}
#endif

#endif // SHATTER_ENGINE_HPP
