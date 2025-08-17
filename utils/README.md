# Utility Scripts

This folder contains utility scripts for interacting with the Kernel API.

## Files

- **send_file_to_api.py** - Python script to send files to the API for conversion
  ```bash
  python send_file_to_api.py <input_file> [output_format]
  ```

- **web_upload.html** - Web interface for uploading and converting files
  - Open in browser for a GUI interface
  - Drag & drop file upload
  - Automatic download of converted files

- **test_wsl_api.bat** - Windows batch script to test the API running in WSL
  ```bash
  test_wsl_api.bat
  ```

## Usage Examples

### Convert a STEP file to STL
```bash
python send_file_to_api.py model.step stl
```

### Convert using web interface
1. Open `web_upload.html` in your browser
2. Drag and drop your file
3. Select output format
4. Click Convert