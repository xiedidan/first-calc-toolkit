@echo off
cd backend
python -m alembic upgrade head
pause
