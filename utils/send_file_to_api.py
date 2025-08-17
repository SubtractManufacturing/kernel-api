"""Send a file to the API running in WSL for conversion"""
import requests
import os
import sys

def convert_file(input_file, output_format='stl', api_url='http://localhost:8000'):
    """
    Send a file to the API for conversion
    
    Args:
        input_file: Path to the input file (STEP, IGES, STL, etc.)
        output_format: Desired output format (stl, obj, glb, gltf)
        api_url: API base URL
    """
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return False
    
    # Check API health
    print(f"Checking API at {api_url}...")
    try:
        health = requests.get(f"{api_url}/api/v1/health")
        if health.status_code == 200:
            print(f"✓ API is healthy: {health.json()}")
        else:
            print(f"✗ API health check failed: {health.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to API at {api_url}")
        print("Make sure the API is running in WSL with: python run.py")
        return False
    
    # Upload and convert file
    print(f"\nConverting {input_file} to {output_format}...")
    
    with open(input_file, 'rb') as f:
        files = {'file': (os.path.basename(input_file), f, 'application/octet-stream')}
        data = {
            'output_format': output_format,
            'deflection': 0.1,
            'angular_deflection': 0.5
        }
        
        response = requests.post(
            f"{api_url}/api/v1/convert",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Conversion successful!")
        print(f"  Job ID: {result.get('job_id')}")
        print(f"  Status: {result.get('status')}")
        
        # Download the converted file
        if result.get('job_id'):
            download_url = f"{api_url}/api/v1/download/{result['job_id']}"
            download_response = requests.get(download_url)
            
            if download_response.status_code == 200:
                # Save the converted file
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = f"{base_name}_converted.{output_format}"
                
                with open(output_file, 'wb') as f:
                    f.write(download_response.content)
                
                print(f"✓ Downloaded converted file: {output_file}")
                print(f"  File size: {len(download_response.content)} bytes")
                return True
            else:
                print(f"✗ Download failed: {download_response.status_code}")
                return False
    else:
        print(f"✗ Conversion failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def main():
    print("=" * 60)
    print("CAD File Converter - Send to WSL API")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python send_file_to_api.py <input_file> [output_format]")
        print("\nExamples:")
        print("  python send_file_to_api.py model.step stl")
        print("  python send_file_to_api.py part.stl obj")
        print("  python send_file_to_api.py design.step glb")
        print("\nSupported input formats: step, stp, iges, igs, stl")
        print("Supported output formats: stl, obj, glb, gltf")
        return
    
    input_file = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'stl'
    
    # Convert the file
    success = convert_file(input_file, output_format)
    
    if success:
        print("\n✓ Conversion complete!")
    else:
        print("\n✗ Conversion failed!")

if __name__ == "__main__":
    main()