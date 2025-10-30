/**
 * @file main.go
 * @brief A Go program to analyze Git history for secrets.
 *
 * This tool iterates through a Git repository's history up to a specified depth.
 * For each modified or added file in each commit, it extracts the file's content
 * (blob) and invokes the C++ core scanner (`secret-hound --scan-file`) on it.
 *
 * It then enriches the raw JSON output from the C++ scanner with Git-specific
 * metadata (commit hash, original file path) and prints the final combined
 * JSON object to stdout, ready to be consumed by the Python reporter.
 */

package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"
)

/**
 * @struct fileBlob
 * @brief Represents a single version of a file (a blob) from a specific commit.
 */
type fileBlob struct {
	hash    string // The Git blob hash of the file content
	path    string // The original path of the file in the repository
	commit  string // The hash of the commit this version belongs to
}

/**
 * @brief Main entry point for the Git analyzer.
 */
func main() {
	if len(os.Args) < 3 {
		fmt.Fprintln(os.Stderr, "Usage: git_analyzer <path_to_hound_core> <depth>")
		os.Exit(1)
	}
	houndCorePath := os.Args[1]
	depthStr := os.Args[2]
	depth, err := strconv.Atoi(depthStr)
	if err != nil {
		depth = 100 // Default to a safe depth if parsing fails
	}

	// 1. Get a list of all file blobs from the git history.
	blobs, err := getGitBlobs(depth)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error getting git blobs: %v\n", err)
		os.Exit(1)
	}
	
	// Use a map to track scanned content hashes, preventing redundant scans of identical files.
	scannedHashes := make(map[string]bool)
	
	// 2. Set up a concurrent pipeline using a work queue (buffered channel) and worker goroutines.
	var wg sync.WaitGroup
	blobChan := make(chan fileBlob, len(blobs))

	numWorkers := 4 // A reasonable number of concurrent file scanners
	wg.Add(numWorkers)

	for i := 0; i < numWorkers; i++ {
		go func() {
			defer wg.Done()
			for blob := range blobChan {
				if _, exists := scannedHashes[blob.hash]; exists {
					continue // Skip if this exact content has already been scanned
				}
				scannedHashes[blob.hash] = true
				
				scanBlobContent(houndCorePath, blob)
			}
		}()
	}

	// 3. Feed the work queue with all the collected blobs.
	for _, blob := range blobs {
		blobChan <- blob
	}
	close(blobChan) // Signal to workers that no more jobs will be added.

	wg.Wait() // Wait for all worker goroutines to complete.
}

/**
 * @brief Retrieves a list of all unique file blobs within the specified commit depth.
 * It parses the output of `git log` to find added/modified files and then uses
 * `git ls-tree` to get their corresponding blob hashes.
 * @param depth The maximum number of commits to look back.
 * @return A slice of fileBlob structs and an error if one occurred.
 */
func getGitBlobs(depth int) ([]fileBlob, error) {
	cmd := exec.Command("git", "log", fmt.Sprintf("--max-count=%d", depth), "--name-status", "--pretty=format:COMMIT %H", "--no-renames")
	
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	if err := cmd.Start(); err != nil {
		return nil, err
	}

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
		
		// We only care about Added ('A') or Modified ('M') files.
		if len(parts) > 1 && (parts[0] == "A" || parts[0] == "M") {
			filePath := parts[1]
			// Get the blob hash for the file within its specific commit.
			blobHashCmd := exec.Command("git", "ls-tree", currentCommit, filePath)
			output, err := blobHashCmd.Output()
			if err == nil {
				treeParts := strings.Fields(string(output))
				if len(treeParts) > 2 {
					blobs = append(blobs, fileBlob{
						hash:   treeParts[2],
						path:   filePath,
						commit: currentCommit,
					})
				}
			}
		}
	}
	
	if err := cmd.Wait(); err != nil {
		// Suppress exit code 1, which can happen in empty repos.
        if exitErr, ok := err.(*exec.ExitError); ok && exitErr.ExitCode() == 1 {
            // This is not a fatal error.
        } else {
		    return nil, err
        }
	}
	
	return blobs, nil
}

/**
 * @brief Scans the content of a single Git blob for secrets.
 * It writes the blob's content to a temporary file and then executes the
 * C++ core scanner on that file.
 * @param houndCorePath The path to the C++ core scanner executable.
 * @param blob The fileBlob to scan.
 */
func scanBlobContent(houndCorePath string, blob fileBlob) {
	// Create a temporary file to hold the blob's content.
	tmpfile, err := ioutil.TempFile("", "secret-hound-git-*.tmp")
	if err != nil {
		return
	}
	defer os.Remove(tmpfile.Name())

	// Get the content of the blob from git using 'cat-file'.
	contentCmd := exec.Command("git", "cat-file", "-p", blob.hash)
	content, err := contentCmd.Output()
	if err != nil {
		return
	}
	tmpfile.Write(content)
	tmpfile.Close()

	// Execute the C++ core scanner in its internal, single-file mode.
	scanCmd := exec.Command(houndCorePath, "--scan-file", tmpfile.Name())
	
	output, err := scanCmd.Output()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Go analyzer: core scanner failed on blob %s: %v\n", blob.hash, err)
		return
	}
	
	// Process each line of JSON output from the core scanner.
	scanner := bufio.NewScanner(strings.NewReader(string(output)))
	for scanner.Scan() {
		// Enrich the raw JSON finding with Git context and print it.
		// The result is a new, more detailed JSON object.
		fmt.Printf("{\"commit\": \"%s\", \"original_path\": \"%s\", %s\n",
			blob.commit,
			blob.path,
			scanner.Text()[1:], // Efficiently skip the opening '{' of the inner JSON.
		)
	}
}
