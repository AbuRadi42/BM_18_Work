#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
INSTALL_DIR="/usr/local"
CONFIG_DIR="/etc/openalpr"
RUNTIME_DATA_DIR="${INSTALL_DIR}/share/openalpr/runtime_data"
OPENALPR_REPO="https://github.com/openalpr/openalpr.git"
# Define the repository root directory (adjust if needed)
OPENALPR_DIR="/workspace/BM_18_Work/1stProject/A. vehiclePresence/openalpr"
OPENALPR_SRC_DIR="${OPENALPR_DIR}/src"

# Update and install dependencies
echo "Updating package list and installing dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential cmake libopencv-dev libtesseract-dev liblog4cplus-dev

# Clone OpenALPR repository if not already cloned
if [ ! -d "$OPENALPR_DIR" ]; then
    echo "Cloning OpenALPR repository..."
    git clone "$OPENALPR_REPO" "$OPENALPR_DIR"
else
    echo "OpenALPR repository already cloned."
fi

# Clean previous build if exists
if [ -d "$OPENALPR_SRC_DIR/build" ]; then
    echo "Cleaning previous build..."
    rm -rf "$OPENALPR_SRC_DIR/build"
fi

# Build and install OpenALPR
echo "Building and installing OpenALPR..."
cd "$OPENALPR_SRC_DIR"
mkdir -p build
cd build
cmake ..
make
sudo make install

# Verify installation
if [ ! -f "${INSTALL_DIR}/lib/libopenalpr.so.2" ]; then
    echo "Error: OpenALPR library not found!"
    exit 1
else
    echo "OpenALPR library installed successfully."
fi

sudo ldconfig

# Set up configuration files
echo "Setting up configuration files..."
sudo mkdir -p "$CONFIG_DIR"
sudo cp "${OPENALPR_DIR}/config/openalpr.conf.user" "$CONFIG_DIR/openalpr.conf"
sudo cp "${OPENALPR_DIR}/config/alprd.conf.user" "$CONFIG_DIR/alprd.conf"

# Verify runtime data
if [ ! -d "$RUNTIME_DATA_DIR" ]; then
    echo "Error: Runtime data directory not found!"
    exit 1
else
    echo "Runtime data directory found."
fi

# Set library path
echo "Setting library path..."
export LD_LIBRARY_PATH=${INSTALL_DIR}/lib:$LD_LIBRARY_PATH
echo "export LD_LIBRARY_PATH=${INSTALL_DIR}/lib:\$LD_LIBRARY_PATH" >> ~/.bashrc

# Reinstall Python bindings
echo "Reinstalling OpenALPR Python bindings..."
pip uninstall -y openalpr
pip install openalpr

# Test OpenALPR installation
echo "Testing OpenALPR installation..."
if alpr -v; then
    echo "OpenALPR installed and configured successfully!"
else
    echo "Error: OpenALPR test failed!"
    exit 1
fi

echo "Setup completed successfully!"
