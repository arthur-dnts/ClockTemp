#!/bin/bash

# Check if the script is running with superuser privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo: sudo ./install.sh"
  exit 1
fi

# Define the destination directory
DEST_DIR="/usr/local/share/clocktemp"

# Create the destination directory if it doesn't exist
echo "Creating directory $DEST_DIR..."
mkdir -p "$DEST_DIR"

# Move the files to the destination directory
echo "Moving files to $DEST_DIR..."
mv ./clocktemp.py "$DEST_DIR/"
mv ./temperature.py "$DEST_DIR/"
mv ./clock.py "$DEST_DIR/"

# Make clocktemp.py executable
echo "Making clocktemp.py executable..."
chmod +x "$DEST_DIR/clocktemp.py"

# Create a symbolic link in /usr/local/bin
echo "Creating symbolic link in /usr/local/bin..."
ln -sf "$DEST_DIR/clocktemp.py" /usr/local/bin/clocktemp

# Confirmation message
echo "Installation completed! Try running 'clocktemp' in the terminal."
