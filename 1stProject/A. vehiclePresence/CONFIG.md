# OpenALPR Setup Guide for European License Plate Detection

This guide provides step-by-step instructions for setting up OpenALPR to detect European license plates. It covers installation, configuration, and troubleshooting tips.

## Prerequisites

- Basic knowledge of Linux command line.
- Python 3.x installed on your system.
- Access to a terminal or command prompt.

---
 - Before you begin: You could simply run the command `./setup_openalpr.sh` and it'll do it all for you
---

## Step 1: Install OpenALPR

OpenALPR is not always available in the default package repositories. You may need to build it from source or find a precompiled binary.

### Option 1: Install from Package Manager (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y openalpr openalpr-daemon openalpr-utils
```

**Note**: If the packages are not found, proceed with building from source.

### Option 2: Build from Source

1. **Install Dependencies**:

   ```bash
   sudo apt-get install -y build-essential cmake libopencv-dev libtesseract-dev liblog4cplus-dev
   ```

2. **Clone the OpenALPR Repository**:

   ```bash
   git clone https://github.com/openalpr/openalpr.git
   cd openalpr/src
   ```

3. **Build and Install**:

   ```bash
   mkdir build
   cd build
   cmake ..
   make
   sudo make install
   ```

## Step 2: Verify Installation

1. **Check Library Path**:

   Ensure the OpenALPR shared library (`libopenalpr.so.2`) is available. It is typically located in `/usr/lib/` or `/usr/local/lib/`.

   ```bash
   ls /usr/lib/ | grep libopenalpr
   ```

2. **Set Library Path**:

   If the library is in a non-standard directory, set the `LD_LIBRARY_PATH`:

   ```bash
   export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
   ```

3. **Verify OpenALPR Command-Line Tool**:

   ```bash
   alpr -v
   ```

   This command should display the version of OpenALPR if it's correctly installed.

## Step 3: Configure OpenALPR

1. **Locate Configuration File**:

   The configuration file is usually located at `/etc/openalpr/openalpr.conf`. You may need to create or edit a user-specific configuration file, such as `openalpr.conf.user`.

2. **Edit Configuration File**:

   Open the configuration file in a text editor and set the following parameters:

   ```ini
   country = eu
   runtime_data = /usr/share/openalpr/runtime_data/
   ```

   Adjust the `country` parameter to `eu` for general European plates or specify a particular country code (e.g., `fr` for France).

3. **Runtime Data Directory**:

   Ensure the `runtime_data` directory contains the necessary OCR templates and plate patterns for the specified country. The directory structure might look like this:

   ```
   runtime_data/
   ├── ocr/
   │   └── ocr_plate_eu.txt
   ├── config/
   │   └── eu.conf
   ├── regex/
   │   └── eu.regex
   └── ...
   ```

## Step 4: Install OpenALPR Python Bindings

1. **Install via pip**:

   ```bash
   pip install openalpr
   ```

2. **Test Python Bindings**:

   Create a simple Python script to test the bindings:

   ```python
   from openalpr import Alpr

   alpr = Alpr("eu", "/path/to/openalpr.conf", "/path/to/runtime_data")
   if not alpr.is_loaded():
       print("Error loading OpenALPR")
   else:
       print("OpenALPR loaded successfully")
   ```

## Step 5: Integrate with Flask Application

1. **Update Flask Application**:

   Ensure your Flask application is configured to use OpenALPR for license plate detection. Update the paths to the configuration file and runtime data in your script.

2. **Run Flask Application**:

   ```bash
   python script.py
   ```

## Troubleshooting

- **Library Not Found**: Ensure the OpenALPR library is in the library path. You may need to set `LD_LIBRARY_PATH`.
- **Permission Issues**: Ensure your user has the necessary permissions to access the OpenALPR library and its dependencies.
- **Dependencies**: Verify that all dependencies, such as Tesseract OCR and OpenCV, are installed and correctly configured.

## Additional Resources

- [OpenALPR Documentation](https://doc.openalpr.com/)
- [OpenALPR GitHub Repository](https://github.com/openalpr/openalpr)

By following these steps, you should be able to set up OpenALPR for detecting European license plates. If you encounter any issues, refer to the documentation or seek help from the community.