#!/bin/bash

# Setup a directory with a symlink loop
rm -rf test_dir_symlink
mkdir -p test_dir_symlink/a/b
touch test_dir_symlink/a/file_a.txt
ln -s ../a test_dir_symlink/a/b/loop

EXECUTABLE=./bin/fastfind
echo "--- Running Symlink Loop Detection Test ---"

# This command should finish quickly and not enter an infinite loop.
# We test this by timing it. If it takes more than 2 seconds, it likely failed.
timeout 2s $EXECUTABLE -p '.*' -d test_dir_symlink --follow-symlinks > /dev/null
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✅ PASS: Program finished without getting stuck in a symlink loop."
elif [ "$EXIT_CODE" -eq 124 ]; then
    echo "❌ FAIL: Program timed out, possibly stuck in a symlink loop."
else
    echo "❌ FAIL: Program exited with an unexpected error code $EXIT_CODE."
fi

# Cleanup
rm -rf test_dir_symlink