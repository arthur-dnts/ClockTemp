#!/bin/bash

# install.sh - Installs ClockTemp on the system
# Copyright (c) 2025 Arthur Dantas
# Licensed under the GNU General Public License v3

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo ./install.sh"
    exit 1
fi

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed. Please install it (e.g., 'sudo apt install python3' on Debian/Ubuntu)."
    exit 1
fi

# Check for requests library and install if missing
if ! python3 -c "import requests" &> /dev/null; then
    echo "The 'requests' library is not installed. Installing it now..."
    if ! pip3 install requests; then
        echo "Failed to install 'requests'. Please install it manually with 'pip3 install requests'."
        exit 1
    fi
fi

# Define source and destination directories
SOURCE_DIR="$(dirname "$(realpath "$0")")"
DEST_DIR="/usr/local/share/clocktemp"

# Check if source files exist
for file in "$SOURCE_DIR/clocktemp.py" "$SOURCE_DIR/temperature.py" "$SOURCE_DIR/clock.py"; do
    if [ ! -f "$file" ]; then
        echo "Error: $file not found in $SOURCE_DIR"
        exit 1
    fi
done

# Create the destination directory if it doesn't exist
echo "Creating directory $DEST_DIR..."
mkdir -p "$DEST_DIR" || {
    echo "Error: Failed to create $DEST_DIR"
    exit 1
}
chmod 755 "$DEST_DIR"  # Ensure directory has appropriate permissions

# Copy the files to the destination directory
echo "Copying files to $DEST_DIR..."
cp "$SOURCE_DIR/clocktemp.py" "$DEST_DIR/" || {
    echo "Error: Failed to copy clocktemp.py"
    exit 1
}
cp "$SOURCE_DIR/cal.py" "$DEST_DIR/" || {
    echo "Error: Failed to copy cal.py"
    exit 1
}
cp "$SOURCE_DIR/temperature.py" "$DEST_DIR/" || {
    echo "Error: Failed to copy temperature.py"
    exit 1
}
cp "$SOURCE_DIR/clock.py" "$DEST_DIR/" || {
    echo "Error: Failed to copy clock.py"
    exit 1
}

# Make clocktemp.py executable
echo "Making clocktemp.py executable..."
chmod +x "$DEST_DIR/clocktemp.py" || {
    echo "Error: Failed to set executable permissions on $DEST_DIR/clocktemp.py"
    exit 1
}

# Create a symbolic link in /usr/local/bin
echo "Creating symbolic link in /usr/local/bin..."
ln -sf "$DEST_DIR/clocktemp.py" /usr/local/bin/clocktemp || {
    echo "Error: Failed to create symbolic link in /usr/local/bin/clocktemp"
    exit 1
}

# Confirmation message
echo "Installation completed! Try running 'clocktemp' in the terminal."