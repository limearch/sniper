/**
 * @file main.go
 * @brief A Go program to analyze Git history for secrets (REFACTORED).
 *
 * This version now pipes blob content directly to the C++ core scanner's stdin
 * via the new `--scan-stdin` flag, which is more efficient and reliable than
 * using temporary files.
 */

package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"
)
// ... (struct fileBlob and getGitBlobs function remain the same)
type fileBlob struct {
	hash    string
	path    string
	commit  string
}

func main() {
    // ... (argument parsing remains the same)
	if len(os.Args) < 3 {
		fmt.Fprintln(os.Stderr, "Usage: git_analyzer <path_to_hound_core> <depth>")
		os.Exit(1)
	}
	houndCorePath := os.Args[1]
	depth, _ := strconv.Atoi(os.Args[2])
	if depth <= 0 { depth = 100 }

	blobs, err := getGitBlobs(depth)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error getting git blobs: %v\n", err)
		os.Exit(1)
	}

	scannedHashes := make(map[string]bool)
	var wg sync.WaitGroup
	blobChan := make(chan fileBlob, len(blobs))
	numWorkers := 4
	wg.Add(numWorkers)

	for i := 0; i < numWorkers; i++ {
		go func() {
			defer wg.Done()
			for blob := range blobChan {
				if _, exists := scannedHashes[blob.hash]; !exists {
					scannedHashes[blob.hash] = true
					scanBlobContent(houndCorePath, blob)
				}
			}
		}()
	}

	for _, blob := range blobs {
		blobChan <- blob
	}
	close(blobChan)
	wg.Wait()
}


func scanBlobContent(houndCorePath string, blob fileBlob) {
	// Get the blob content from git.
	contentCmd := exec.Command("git", "cat-file", "-p", blob.hash)
	content, err := contentCmd.Output()
	if err != nil {
		return
	}

	// --- REFACTORED: Use stdin pipe instead of temp files ---
	scanCmd := exec.Command(houndCorePath, "--scan-stdin")
	
	stdin, err := scanCmd.StdinPipe()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to create stdin pipe for hound-core: %v\n", err)
		return
	}

	// Concurrently write the content to the C++ process's stdin.
	go func() {
		defer stdin.Close()
		io.WriteString(stdin, string(content))
	}()

	// Execute the command and capture its output.
	output, err := scanCmd.CombinedOutput()
	if err != nil {
		// Log errors from the core scanner to stderr for debugging.
		fmt.Fprintf(os.Stderr, "hound-core error on blob %s: %v\nOutput:\n%s\n", blob.hash, err, string(output))
		return
	}
	
	// Process each line of JSON from the core scanner.
	scanner := bufio.NewScanner(strings.NewReader(string(output)))
	for scanner.Scan() {
		// Enrich the finding with Git context and print the combined JSON.
		fmt.Printf("{\"commit\": \"%s\", \"original_path\": \"%s\", %s\n",
			blob.commit,
			blob.path,
			scanner.Text()[1:], // Skip the opening '{' of the inner JSON.
		)
	}
}

// ... (getGitBlobs function remains the same as provided previously)
func getGitBlobs(depth int) ([]fileBlob, error) {
	cmd := exec.Command("git", "log", fmt.Sprintf("--max-count=%d", depth), "--name-status", "--pretty=format:COMMIT %H", "--no-renames")
	stdout, err := cmd.StdoutPipe()
	if err != nil { return nil, err }
	if err := cmd.Start(); err != nil { return nil, err }

	var blobs []fileBlob
	var currentCommit string
	scanner := bufio.NewScanner(stdout)

	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Fields(line)
		
		if len(parts) > 1 && parts[0] == "COMMIT" {
			currentCommit = parts[1]
			continue
		}
		
		if len(parts) > 1 && (parts[0] == "A" || parts[0] == "M") {
			filePath := parts[1]
			blobHashCmd := exec.Command("git", "ls-tree", currentCommit, filePath)
			output, err := blobHashCmd.Output()
			if err == nil {
				treeParts := strings.Fields(string(output))
				if len(treeParts) > 2 {
					blobs = append(blobs, fileBlob{hash: treeParts[2], path: filePath, commit: currentCommit})
				}
			}
		}
	}
	
	cmd.Wait() // Ignore error from git log on empty repos
	return blobs, nil
}
