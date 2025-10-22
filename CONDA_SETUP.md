# Conda环境配置指南

## 问题

环境检查显示：`Conda not installed`

## 原因

Anaconda已安装，但PowerShell无法找到`conda`命令。这通常是因为：
1. Conda没有添加到系统PATH
2. PowerShell没有初始化Conda

## 解决方案

### 方法1：初始化Conda（推荐）

1. 打开 **Anaconda PowerShell Prompt**（从开始菜单搜索）

2. 在Anaconda PowerShell中运行：
```powershell
conda init powershell
```

3. 关闭并重新打开PowerShell

4. 再次运行环境检查：
```powershell
.\scripts\check-environment.ps1
```

### 方法2：使用Anaconda PowerShell Prompt

如果不想初始化系统PowerShell，可以直接使用Anaconda PowerShell Prompt：

1. 从开始菜单打开 **Anaconda PowerShell Prompt**

2. 切换到项目目录：
```powershell
cd C:\project\first-calc-toolkit
```

3. 运行所有脚本都使用这个终端

### 方法3：手动添加到PATH

1. 找到Anaconda安装目录（通常是 `C:\Users\<用户名>\anaconda3`）

2. 添加以下路径到系统PATH：
   - `C:\Users\<用户名>\anaconda3`
   - `C:\Users\<用户名>\anaconda3\Scripts`
   - `C:\Users\<用户名>\anaconda3\Library\bin`

3. 重启PowerShell

## 验证

运行以下命令验证Conda是否可用：

```powershell
conda --version
```

应该显示类似：`conda 23.x.x`

## 下一步

Conda配置完成后：

1. 运行环境检查：
```powershell
.\scripts\check-environment.ps1
```

2. 设置Python环境：
```powershell
.\scripts\setup-conda-env.ps1
```

3. 安装前端依赖：
```powershell
cd frontend
npm install
cd ..
```

4. 启动开发服务：
```powershell
.\scripts\dev-start-all.ps1
```

## 替代方案：不使用Conda

如果你不想使用Conda，也可以使用Python的venv：

### 1. 创建虚拟环境

```powershell
cd backend
python -m venv venv
```

### 2. 激活虚拟环境

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 修改启动脚本

编辑 `scripts/dev-start-backend.ps1` 和 `scripts/dev-start-celery.ps1`，将：
```powershell
conda activate hospital-backend
```

替换为：
```powershell
.\backend\venv\Scripts\Activate.ps1
```

## 常见问题

### Q: conda init后仍然无法使用conda命令

**A**: 尝试以下步骤：
1. 完全关闭所有PowerShell窗口
2. 重新打开PowerShell
3. 如果还不行，重启电脑

### Q: 提示"无法加载文件，因为在此系统上禁止运行脚本"

**A**: 需要修改PowerShell执行策略：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: 我想使用系统Python而不是Conda

**A**: 可以的！只需：
1. 确保Python 3.12已安装
2. 使用venv创建虚拟环境（见上面的替代方案）
3. 修改启动脚本中的环境激活命令

## 推荐配置

为了获得最佳开发体验，推荐：

1. **使用Anaconda PowerShell Prompt** - 最简单，无需配置
2. **或者初始化Conda** - 可以在任何PowerShell中使用
3. **配置VS Code** - 在VS Code中选择正确的Python解释器

### VS Code Python解释器配置

1. 按 `Ctrl+Shift+P`
2. 输入 "Python: Select Interpreter"
3. 选择 `hospital-backend` 环境（如果使用Conda）
4. 或选择 `.\backend\venv\Scripts\python.exe`（如果使用venv）

## 总结

- ✅ 最简单：使用 **Anaconda PowerShell Prompt**
- ✅ 最灵活：**初始化Conda** 到系统PowerShell
- ✅ 最轻量：使用 **Python venv**

选择适合你的方式即可！
