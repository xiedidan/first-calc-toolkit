# 🚀 START HERE - Quick Setup Guide

## ✅ All Scripts Fixed!

All PowerShell scripts have been updated and are ready to use.

**Latest Fix**: Scripts now use `conda run` to ensure commands execute in the correct Conda environment. See [CONDA_RUN_FIX.md](./CONDA_RUN_FIX.md) for details.

## 📋 Quick Start (3 Steps)

### Step 1: Check Environment

```powershell
.\scripts\check-environment.ps1
```

**Expected Output:**
- ✅ WSL2: OK
- ✅ Docker: OK
- ✅ Docker Compose: OK
- ⚠️ Conda: May show "FAILED" (see below)
- ✅ Node.js: OK
- ✅ npm: OK
- ✅ All ports available
- ✅ All project files OK

### Step 2: Setup Python Environment

**Option A: Using Anaconda PowerShell Prompt (Recommended)**

1. Open "Anaconda PowerShell Prompt" from Start Menu
2. Navigate to project:
   ```powershell
   cd C:\project\first-calc-toolkit
   ```
3. Run setup:
   ```powershell
   .\scripts\setup-conda-env.ps1
   ```

**Option B: Initialize Conda in Regular PowerShell**

1. Open "Anaconda PowerShell Prompt"
2. Run:
   ```powershell
   conda init powershell
   ```
3. Restart PowerShell
4. Run setup:
   ```powershell
   .\scripts\setup-conda-env.ps1
   ```

### Step 3: Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

## 🎯 Start Development

### One-Click Start (Recommended)

```powershell
.\scripts\dev-start-all.ps1
```

This will open 3 new windows:
- Window 1: Backend (FastAPI)
- Window 2: Celery Worker
- Window 3: Frontend (Vue.js)

### Manual Start (Alternative)

```powershell
# Terminal 1: Start Docker
docker-compose -f docker-compose.dev.yml up -d

# Terminal 2: Start Backend
.\scripts\dev-start-backend.ps1

# Terminal 3: Start Celery
.\scripts\dev-start-celery.ps1

# Terminal 4: Start Frontend
.\scripts\dev-start-frontend.ps1
```

## 🌐 Access Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc

## 🛑 Stop Services

```powershell
.\scripts\dev-stop-all.ps1
```

Or simply close the PowerShell windows.

## 📚 Documentation

- **SCRIPTS_FIXED.md** - Script fix details
- **CONDA_SETUP.md** - Conda configuration guide
- **CURRENT_STATUS.md** - Current project status
- **QUICKSTART.md** - Detailed quick start guide
- **DEPLOYMENT_READY.md** - Complete deployment guide

## ❓ Troubleshooting

### "Conda not installed" Error

**Solution**: Use Anaconda PowerShell Prompt or initialize conda:
```powershell
conda init powershell
```

See [CONDA_SETUP.md](./CONDA_SETUP.md) for details.

### Port Already in Use

**Solution**: Check which process is using the port:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Docker Not Running

**Solution**: Start Docker Desktop from Start Menu.

### Script Execution Policy Error

**Solution**: Allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🎉 You're Ready!

Follow the 3 steps above and you'll be up and running in minutes!

**Need help?** Check the documentation files listed above.
