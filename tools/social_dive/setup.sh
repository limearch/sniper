#!/bin/bash

# A simple setup script for the social-dive tool.

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="social-dive"
SOURCE_SCRIPT="bin/social-dive"

echo "Starting setup for Social-Dive..."

# Check if the script is run as root.
if [ "$(id -u)" -ne 0 ]; then
  echo "This script requires root privileges to install to $INSTALL_DIR."
  echo "Please run with sudo: sudo ./setup.sh"
  exit 1
fi

# Check if the source script exists.
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "Error: Source script '$SOURCE_SCRIPT' not found."
    echo "Please run this script from the project's root directory."
    exit 1
fi

echo "Making the script executable..."
chmod +x "$SOURCE_SCRIPT"

echo "Copying script to $INSTALL_DIR/$SCRIPT_NAME..."
cp "$SOURCE_SCRIPT" "$INSTALL_DIR/$SCRIPT_NAME"

# Verify installation.
if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo "-----------------------------------------------------"
    echo -e "\033[32m✅ Installation complete!\033[0m"
    echo "You can now run the tool from anywhere by typing: $SCRIPT_NAME"
    echo "Example: social-dive johndoe -o results.txt"
    echo "-----------------------------------------------------"
else
    echo "-----------------------------------------------------"
    echo -e "\033[31m❌ Installation failed.\033[0m"
    echo "Could not copy the script to $INSTALL_DIR."
    echo "Please check your permissions and path."
    echo "-----------------------------------------------------"
    exit 1
fi
