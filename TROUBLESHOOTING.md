# Troubleshooting Guide

## ⚠️ Known Issue: Routes Not Loading

If you see 404 errors when trying to use AI features, the backend server may have cached old code.

### ✅ Quick Fix (Windows)

**Double-click this file:**
```
RESTART_BACKEND.bat
```

This will:
1. Stop any running Python processes
2. Clear all Python cache
3. Start fresh backend server

### ✅ Manual Fix

```cmd
# 1. Stop current backend (Ctrl+C or close terminal)

# 2. Open NEW Command Prompt and run:
cd C:\Users\gideo\slv-housing-market\backend

# 3. Clear cache
for /d /r %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

# 4. Activate venv
venv\Scripts\activate

# 5. Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ✅ Verify It Works

Open a new terminal and test:

```cmd
curl http://localhost:8000/api/property-ai/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Property AI Analysis",
  "phase": "1 (Property Summaries)"
}
```

---

## Common Issues

### Issue: "Module not found" errors

**Fix:**
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Fix:**
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with the number from above)
taskkill /F /PID <PID>
```

### Issue: Frontend can't connect to backend

**Checklist:**
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] No firewall blocking connections
- [ ] CORS configured correctly in `backend/app/config.py`

### Issue: "Google API key required" error

**Fix:**
```cmd
cd backend
echo GOOGLE_API_KEY=your_key_here >> .env
```

---

## Testing Checklist

Run these tests to verify everything works:

### Backend Tests

```cmd
# Health check
curl http://localhost:8000/health

# AI health check
curl http://localhost:8000/api/property-ai/health

# Get properties
curl http://localhost:8000/api/properties/

# Test AI summary (requires properties in database)
curl -X POST http://localhost:8000/api/property-ai/summarize \
  -H "Content-Type: application/json" \
  -d "{\"filters\":{},\"max_properties\":10}"
```

### Frontend Tests

1. Open http://localhost:5173
2. Check if homepage loads
3. Upload a CSV file with property data
4. Click "✨ Summarize Current Results with AI"
5. Click "🎯 Get Personalized Property Recommendations"
6. Fill out criteria and get recommendations

---

## Getting Help

If issues persist:

1. **Check server logs** for error messages
2. **Verify Python version:** `python --version` (should be 3.11+)
3. **Verify Node version:** `node --version` (should be 18+)
4. **Check `.env` file** has all required variables

---

## Clean Reset

If all else fails, do a complete reset:

```cmd
# Backend
cd backend
rmdir /s /q venv
rmdir /s /q __pycache__
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
rmdir /s /q node_modules
npm install

# Restart both servers
```

---

*Last updated: January 24, 2026*
