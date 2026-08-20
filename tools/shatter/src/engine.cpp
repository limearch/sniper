// src/engine.cpp
#include "engine.hpp"

#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <openssl/evp.h>
#include <cstring>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <chrono>

// --- Global State for Monitoring ---
// Atomic variables allow threads to update stats without full locking.
static std::atomic<uint64_t> g_attempts(0);
static std::atomic<bool> g_found(false);

// We store the "current word" here for the UI to sample. 
// It doesn't need to be perfectly thread-safe (visual artifact only), 
// but we use a mutex to prevent tearing if strict safety is desired.
static char g_current_word[256] = {0}; 
static std::mutex g_monitor_mutex;

// --- Helper Functions ---

// Convert Hex string to Byte Vector
static bool hex_to_bytes(const char* hex, std::vector<unsigned char>& out) {
    if (!hex) return false;
    size_t len = std::strlen(hex);
    if (len == 0 || len % 2 != 0) return false;
    
    out.clear();
    out.reserve(len / 2);
    
    for (size_t i = 0; i < len; i += 2) {
        char hi = hex[i];
        char lo = hex[i+1];
        
        auto h2n = [](char c) -> int {
            if (c >= '0' && c <= '9') return c - '0';
            if (c >= 'a' && c <= 'f') return 10 + (c - 'a');
            if (c >= 'A' && c <= 'F') return 10 + (c - 'A');
            return -1;
        };
        
        int hn = h2n(hi);
        int ln = h2n(lo);
        if (hn < 0 || ln < 0) return false;
        
        out.push_back(static_cast<unsigned char>((hn << 4) | ln));
    }
    return true;
}

// Perform PBKDF2 Check (WinZip AES Standard)
static bool verify_single_candidate(
    const unsigned char* password,
    size_t pwd_len,
    const unsigned char* salt, int salt_len,
    const unsigned char* expected_verifier, int expected_verifier_len,
    int key_len
) {
    // WinZip AES defines derived key length as 2*key_len + 2 bytes
    const int dk_len = (2 * key_len) + 2;
    unsigned char dk[128]; // Max needed is usually 66 bytes for AES-256
    
    // 1000 Iterations is standard for WinZip AES
    if (!PKCS5_PBKDF2_HMAC(
            reinterpret_cast<const char*>(password), static_cast<int>(pwd_len),
            salt, salt_len,
            1000,
            EVP_sha1(),
            dk_len,
            dk)) {
        return false;
    }

    // The verifier is the last 2 bytes of the derived key
    const unsigned char* calc_verifier = dk + (2 * key_len);
    return (std::memcmp(calc_verifier, expected_verifier, expected_verifier_len) == 0);
}

// Data structure passed to each worker thread
struct ThreadControl {
    const char* base;           // Mapped memory base pointer
    size_t offset_start;        // Start byte index
    size_t offset_end;          // End byte index
    const unsigned char* salt;
    int salt_len;
    const unsigned char* verifier;
    int verifier_len;
    int key_len;
    char* out_password;         // Pointer to write found password
    size_t out_size;            // Size of output buffer
};

// Find the next newline character
static size_t find_next_eol(const char* base, size_t from, size_t end) {
    for (size_t i = from; i < end; ++i) {
        if (base[i] == '\n') return i;
    }
    return end;
}

// --- Worker Logic ---

static void thread_worker_mapped(const ThreadControl& ctl) {
    const char* buf = ctl.base;
    size_t start = ctl.offset_start;
    size_t end = ctl.offset_end;

    // Adjust start: If we are not at the beginning of the file, 
    // advance to the next newline to ensure we don't start in the middle of a word.
    // The previous chunk's thread handles the word crossing the boundary.
    if (start != 0) {
        if (buf[start-1] != '\n') {
            size_t nxt = find_next_eol(buf, start, end);
            if (nxt == end) return; // Reached end of chunk
            start = nxt + 1;
        }
    }

    size_t pos = start;
    uint64_t local_attempts = 0;

    // Main scanning loop
    while (pos < end && !g_found.load(std::memory_order_relaxed)) {
        size_t line_end = find_next_eol(buf, pos, end);
        size_t raw_len = line_end - pos;
        
        // CRITICAL FIX: Handle Windows Line Endings (\r\n)
        // If the line ends in \r, we must exclude it from the password.
        // Otherwise, "password\r" != "password", causing failure.
        size_t effective_len = raw_len;
        if (effective_len > 0 && buf[pos + effective_len - 1] == '\r') {
            effective_len--;
        }

        if (effective_len > 0) {
            const unsigned char* cand_ptr = reinterpret_cast<const unsigned char*>(buf + pos);
            
            // UI Visualization Update
            // Only update the global "current word" every ~2048 tries to avoid locking overhead.
            if ((local_attempts & 0x7FF) == 0) {
                size_t copy_len = std::min(effective_len, (size_t)254);
                // Simple memcpy, race condition is benign for visualization purposes
                std::memcpy(g_current_word, buf + pos, copy_len);
                g_current_word[copy_len] = '\0';
            }

            // Verify Password
            if (verify_single_candidate(cand_ptr, effective_len, ctl.salt, ctl.salt_len, ctl.verifier, ctl.verifier_len, ctl.key_len)) {
                
                // Atomically claim success
                bool expected = false;
                if (g_found.compare_exchange_strong(expected, true)) {
                    // This thread found the password. Write it to output.
                    std::lock_guard<std::mutex> lk(g_monitor_mutex);
                    size_t to_copy = std::min(effective_len, ctl.out_size - 1);
                    std::memcpy(ctl.out_password, buf + pos, to_copy);
                    ctl.out_password[to_copy] = '\0';
                }
                return;
            }
        }

        // Update local stats
        local_attempts++;
        
        // Update global stats periodically to reduce bus contention
        if (local_attempts >= 1000) {
            g_attempts.fetch_add(local_attempts, std::memory_order_relaxed);
            local_attempts = 0;
        }

        // Move to next line (skip the \n)
        pos = line_end + 1;
    }

    // Flush remaining stats
    if (local_attempts > 0) {
        g_attempts.fetch_add(local_attempts, std::memory_order_relaxed);
    }
}

// --- Monitor Thread ---
// Runs in background to trigger the Python callback
void monitor_worker(ProgressCallback cb) {
    while (!g_found.load(std::memory_order_relaxed)) {
        // Sleep for 100ms
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        if (cb) {
             // Create a safe copy of the current word
             char temp_buf[256];
             std::memcpy(temp_buf, g_current_word, 256);
             temp_buf[255] = '\0';
             
             // Invoke Python callback
             cb(g_attempts.load(std::memory_order_relaxed), temp_buf);
        }
    }
}

// --- Main Interface ---

int crack_wordlist(
    const char* wordlist_path,
    const char* salt_hex,
    const char* verifier_hex,
    int key_len,
    int thread_count,
    char* out_password,
    size_t out_size,
    ProgressCallback progress_cb
) {
    // 1. Reset Global State
    g_attempts.store(0);
    g_found.store(false);
    std::memset(g_current_word, 0, sizeof(g_current_word));

    // 2. Parse Crypto Params
    std::vector<unsigned char> salt, verifier;
    if (!hex_to_bytes(salt_hex, salt) || !hex_to_bytes(verifier_hex, verifier)) {
        return -1; // Parse error
    }

    // 3. Open File
    int fd = open(wordlist_path, O_RDONLY);
    if (fd < 0) return -1;

    struct stat st;
    if (fstat(fd, &st) != 0) { close(fd); return -1; }
    size_t file_size = st.st_size;
    if (file_size == 0) { close(fd); return 0; }

    // 4. Memory Map File
    void* map_ptr = mmap(nullptr, file_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map_ptr == MAP_FAILED) { close(fd); return -1; }

    // 5. Setup Threads
    if (thread_count <= 0) {
        thread_count = std::thread::hardware_concurrency();
    }
    if (thread_count < 1) thread_count = 1;

    std::vector<std::thread> workers;
    size_t chunk = file_size / thread_count;
    const char* base = (const char*)map_ptr;

    // 6. Launch Monitor Thread (for UI)
    std::thread monitor;
    if (progress_cb) {
        monitor = std::thread(monitor_worker, progress_cb);
    }

    // 7. Launch Worker Threads
    for (int i = 0; i < thread_count; ++i) {
        size_t start = i * chunk;
        size_t end = (i == thread_count - 1) ? file_size : (start + chunk);
        
        ThreadControl ctl;
        ctl.base = base;
        ctl.offset_start = start;
        ctl.offset_end = end;
        ctl.salt = salt.data();
        ctl.salt_len = salt.size();
        ctl.verifier = verifier.data();
        ctl.verifier_len = verifier.size();
        ctl.key_len = key_len;
        ctl.out_password = out_password;
        ctl.out_size = out_size;
        
        workers.emplace_back(thread_worker_mapped, ctl);
    }

    // 8. Join Worker Threads
    for (auto& t : workers) {
        if (t.joinable()) t.join();
    }

    // 9. Cleanup Monitor
    if (monitor.joinable()) {
        monitor.detach(); // Allow it to exit naturally as g_found is checked
    }

    // 10. Cleanup Memory
    munmap(map_ptr, file_size);
    close(fd);

    return g_found.load() ? 1 : 0;
}
