@echo off
echo 添加收费项目测试数据...
cd backend
call C:\software\anaconda3\Scripts\activate.bat hospital-backend
python scripts/seed_charge_items.py
pause
