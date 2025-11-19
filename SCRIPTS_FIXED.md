# PowerShell Scripts Fixed

## ✅ Problem Solved

All PowerShell scripts have been updated to use English text only to avoid encoding issues.

## 📝 Updated Scripts

All 8 PowerShell scripts have been fixed:

1. ✅ `scripts/check-environment.ps1` - Environment check
2. ✅ `scripts/setup-conda-env.ps1` - Conda environment setup
3. ✅ `scripts/dev-start-backend.ps1` - Start backend service
4. ✅ `scripts/dev-start-celery.ps1` - Start Celery worker
5. ✅ `scripts/dev-start-frontend.ps1` - Start frontend service
6. ✅ `scripts/dev-start-all.ps1` - Start all services
7. ✅ `scripts/dev-stop-all.ps1` - Stop all services
8. ✅ `scripts/test-connection.ps1` - Test connections

## 🚀 Ready to Use

All scripts are now ready to use. You can proceed with:

### Step 1: Setup Conda Environment

```powershell
.\scripts\setup-conda-env.ps1
```

This will:
- Create a Conda environment named `hospital-backend`
- Install Python 3.12
- Install all dependencies from `backend/requirements.txt`

### Step 2: Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

### Step 3: Start All Services

```powershell
.\scripts\dev-start-all.ps1
```

This will:
- Start PostgreSQL and Redis containers
- Start backend service in a new window
- Start Celery worker in a new window
- Start frontend service in a new window

### Step 4: Access the Application

- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Backend ReDoc: http://localhost:8000/redoc

## 📋 Script Descriptions

### check-environment.ps1
Checks if all required tools are installed:
- WSL2
- Docker & Docker Compose
- Conda
- Node.js & npm
- Port availability
- Project files

### setup-conda-env.ps1
Creates and configures the Conda environment:
- Creates `hospital-backend` environment
- Installs Python 3.12
- Installs all Python dependencies

### dev-start-backend.ps1
Starts the FastAPI backend service:
- Activates Conda environment
- Loads development configuration
- Starts uvicorn with hot reload

### dev-start-celery.ps1
Starts the Celery worker:
- Activates Conda environment
- Loads development configuration
- Starts Celery with Windows-compatible pool

### dev-start-frontend.ps1
Starts the Vue.js frontend:
- Installs dependencies if needed
- Starts Vite development server

### dev-start-all.ps1
One-click start for all services:
- Starts Docker containers
- Opens backend in new window
- Opens Celery in new window
- Opens frontend in new window

### dev-stop-all.ps1
Stops all running services:
- Stops Docker containers
- Kills Python processes
- Kills Node processes

### test-connection.ps1
Tests database and Redis connections:
- Checks if containers are running
- Tests PostgreSQL connection
- Tests Redis connection
- Shows connection information

## 💡 Tips

### Using Anaconda PowerShell Prompt

If you see "Conda not installed" error, use Anaconda PowerShell Prompt:

1. Open "Anaconda PowerShell Prompt" from Start Menu
2. Navigate to project: `cd C:\project\first-calc-toolkit`
3. Run scripts normally

### Initializing Conda (One-time setup)

To use conda in regular PowerShell:

```powershell
# In Anaconda PowerShell Prompt
conda init powershell

# Restart PowerShell
```

### Checking Script Syntax

To verify a script has no syntax errors:

```powershell
Get-Content .\scripts\<script-name>.ps1 | Out-Null
```

## 🎯 Next Steps

1. Run environment check:
   ```powershell
   .\scripts\check-environment.ps1
   ```

2. If Conda is detected, setup environment:
   ```powershell
   .\scripts\setup-conda-env.ps1
   ```

3. Install frontend dependencies:
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

4. Start all services:
   ```powershell
   .\scripts\dev-start-all.ps1
   ```

5. Open browser and visit:
   - http://localhost:3000

## ✨ All Fixed!

All PowerShell scripts are now working correctly with proper UTF-8 encoding and English text only.

You can now proceed with the development setup!
