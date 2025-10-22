# Conda Activation Fix

## ✅ Problem Solved

The issue was that `conda activate` in PowerShell scripts doesn't actually activate the environment for subsequent commands because each command runs in its own context.

## 🔧 Solution

Updated scripts to use `conda run -n <env_name>` instead of `conda activate`.

### Before (Not Working)
```powershell
conda activate hospital-backend
uvicorn app.main:app --reload
```

### After (Working)
```powershell
conda run -n hospital-backend --no-capture-output uvicorn app.main:app --reload
```

## 📝 Updated Scripts

- ✅ `dev-start-backend.ps1` - Now uses `conda run`
- ✅ `dev-start-celery.ps1` - Now uses `conda run`

## 🚀 How It Works

`conda run` executes a command in a specified Conda environment:

```powershell
conda run -n <environment_name> <command>
```

The `--no-capture-output` flag ensures that output is displayed in real-time.

## ✨ Ready to Use

Now you can start the services:

### Start Backend
```powershell
.\scripts\dev-start-backend.ps1
```

### Start Celery
```powershell
.\scripts\dev-start-celery.ps1
```

### Start All Services
```powershell
.\scripts\dev-start-all.ps1
```

## 📚 Reference

- `conda run` documentation: https://docs.conda.io/projects/conda/en/latest/commands/run.html
- This approach works in any PowerShell (not just Anaconda PowerShell Prompt)

## 🎯 Benefits

1. ✅ Works in regular PowerShell
2. ✅ Works in Anaconda PowerShell Prompt
3. ✅ No need to manually activate environment
4. ✅ Ensures correct environment is always used
5. ✅ More reliable for automation

## 💡 Alternative: Manual Activation

If you prefer to manually activate the environment:

```powershell
# In Anaconda PowerShell Prompt
conda activate hospital-backend

# Then run commands directly
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

But using `conda run` in scripts is more reliable!
