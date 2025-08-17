# Setting up STEP Conversion with WSL2

## Prerequisites
1. Windows 10 version 2004 or higher (Build 19041 or higher)
2. WSL2 installed

## Step 1: Install WSL2

```powershell
# Run in PowerShell as Administrator
wsl --install

# Restart your computer after installation
```

## Step 2: Install Ubuntu in WSL2

```powershell
# Install Ubuntu 22.04
wsl --install -d Ubuntu-22.04

# Set WSL2 as default
wsl --set-default-version 2
```

## Step 3: Setup the Project in WSL2

```bash
# Open WSL2 Ubuntu terminal
wsl

# Update packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip -y

# Install development tools
sudo apt install build-essential libgl1-mesa-glx -y

# Navigate to your project (Windows drives are mounted under /mnt)
cd /mnt/c/Users/jkkic/PycharmProjects/kernel-api

# Create virtual environment with Python 3.12
python3.12 -m venv venv_wsl

# Activate it
source venv_wsl/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Install OCP (should work without issues in Linux)
pip install cadquery-ocp

# Run the API
python run.py
```

## Step 4: Access from Windows

The API running in WSL2 will be accessible from Windows at:
- http://localhost:8000

## Benefits
- Full STEP/IGES support works perfectly
- No segmentation faults
- Better performance for CAD operations
- Can still edit files in Windows

## VSCode Integration

Install "WSL" extension in VSCode, then:
```bash
# In WSL terminal
code .
```

This opens VSCode connected to WSL with full IntelliSense support.