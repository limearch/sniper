#!/bin/bash

rm -rf test_dir_content
mkdir -p test_dir_content
echo -e "This is a test file.\nIt contains the magic_word for searching." > test_dir_content/file1.txt
echo "This file does not have the special keyword." > test_dir_content/file2.txt
echo "MAGIC_WORD in uppercase here." > test_dir_content/file3.txt
# Create a large file to test buffered reading
head -c 10M </dev/urandom | tr -dc 'a-zA-Z0-9' > test_dir_content/large_file.txt
echo "Another_Magic_Word" >> test_dir_content/large_file.txt

EXECUTABLE=./bin/fastfind

assert_content_count() {
    local description="$1"
    local command="$2"
    local expected_count="$3"
    
    local result_count=$($command | wc -l)
    
    if [ "$result_count" -eq "$expected_count" ]; then
        echo "✅ PASS: $description"
    else
        echo "❌ FAIL: $description (Expected $expected_count, got $result_count)"
        $command
    fi
}

echo "--- Running Content Search Tests ---"

# Test 1: Find file with specific content
assert_content_count "Find by content 'magic_word'" "$EXECUTABLE -p '.*' -d test_dir_content --content 'magic_word'" 1

# Test 2: Find by content, case-insensitive
assert_content_count "Find by content 'magic_word' (case-insensitive)" "$EXECUTABLE -p '.*' -d test_dir_content --content 'magic_word' -i" 2

# Test 3: No match
assert_content_count "No match for non-existent content" "$EXECUTABLE -p '.*' -d test_dir_content --content 'nonexistent'" 0

# Test 4: Content search in a large file
assert_content_count "Find content in a large file" "$EXECUTABLE -p 'large' -d test_dir_content --content 'Another_Magic_Word'" 1

# Cleanup
rm -rf test_dir_content