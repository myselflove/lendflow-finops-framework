# LendFlow FinOps Platform — Troubleshooting Guide

## 1. Backend Service Issues

### Issue: Backend fails to start with `ModuleNotFoundError`
- **Root Cause**: Virtual environment not active or dependencies missing.
- **Fix**:
  ```powershell
  .\app\backend\.venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

### Issue: Port 8000 already in use
- **Root Cause**: An existing uvicorn or backend process is holding port 8000.
- **Fix**:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  ```

---

## 2. Frontend Development Server Issues

### Issue: Vite fails to start or build errors out
- **Root Cause**: `node_modules` not installed or stale lockfile.
- **Fix**:
  ```powershell
  cd app/frontend
  npm install
  npm run build
  ```

---

## 3. Deliverables Generation Issues

### Issue: `openpyxl` or `python-pptx` missing during script execution
- **Fix**:
  ```powershell
  .\app\backend\.venv\Scripts\python.exe -m pip install openpyxl python-pptx
  .\app\backend\.venv\Scripts\python.exe scripts/generate_deliverables.py
  ```

---

## 4. Test Suite Execution Issues

### Issue: Pytest cannot import `app.backend.main`
- **Fix**: Ensure `PYTHONPATH` includes workspace root. The `pytest.ini` file in root already configures `pythonpath = .`. Run tests using:
  ```powershell
  .\app\backend\.venv\Scripts\python.exe -m pytest -v
  ```
