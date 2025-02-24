# Windows PowerShell setup script
Write-Host "Setting up development environment..."

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

# Install/upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..."
pip install -r requirements.txt

Write-Host "Setup complete! Virtual environment is activated."
Write-Host "You can activate the environment manually with: .\.venv\Scripts\Activate.ps1"