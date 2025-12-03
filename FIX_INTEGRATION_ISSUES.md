# Quick Fix Guide for Integration Issues

**Found 2 issues - here's how to fix them:**

---

## ✅ **Issue 1: LLM Service - Anthropic Version Error**

**Error:**
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

**Cause:** Anthropic package version 0.7.1 is outdated and incompatible with newer httpx

**Fix:**

```bash
cd llm-service

# Make sure venv is activated
source venv/bin/activate

# Uninstall old version
pip uninstall anthropic -y

# Install newer compatible version
pip install anthropic==0.40.0 httpx==0.27.0

# Verify installation
pip show anthropic
# Should show: Version: 0.40.0

# Now try running again
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## ✅ **Issue 2: Go Backend - Missing go.sum Entries**

**Error:**
```
missing go.sum entry for module providing package github.com/gin-gonic/gin
```

**Cause:** go.sum file doesn't exist or is incomplete

**Fix:**

```bash
cd backend

# Method 1: Generate go.sum (Recommended)
go mod tidy

# This will:
# - Download all dependencies
# - Create/update go.sum file
# - Verify dependencies

# Method 2: If that doesn't work
rm go.sum  # Remove old file
go mod download
go mod verify

# Now try running
go run cmd/server/main.go
```

**Expected Output:**
```
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.
[GIN-debug] GET    /health                   --> main.main.func1 (3 handlers)
[GIN-debug] POST   /api/interview/start      --> ...
Server starting on port 8080
[GIN] 2024/12/04 - 17:00:00 | 200 | 123.456µs | 127.0.0.1 | GET      "/health"
```

---

## 🚀 **Quick Commands (Copy-Paste)**

### **Fix LLM Service:**
```bash
cd llm-service
source venv/bin/activate
pip uninstall anthropic -y
pip install anthropic==0.40.0 httpx==0.27.0
python main.py
```

### **Fix Go Backend:**
```bash
cd ../backend
go mod tidy
go run cmd/server/main.go
```

### **Test Both:**
```bash
# In new terminal:
curl http://localhost:8000/health  # Should return {"status":"healthy"}
curl http://localhost:8080/health  # Should return {"status":"healthy"}
```

---

## ⚠️ **Important: Add Claude API Key**

Before running LLM service, you MUST add your API key:

```bash
cd llm-service

# Edit .env file
nano .env  # or use any text editor

# Add your key:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx

# Save and exit
```

**Get API Key:**
1. Visit: https://console.anthropic.com/
2. Sign up (free $5 credits)
3. Go to "API Keys"
4. Click "Create Key"
5. Copy and paste into `.env`

---

## ✅ **Verification Steps**

### **After Fixing:**

**1. Check LLM Service:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

curl -X POST http://localhost:8000/api/question/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"DSA","difficulty":"Junior","position":0}'
# Should return a question JSON
```

**2. Check Backend:**
```bash
curl http://localhost:8080/health
# Should return: {"status":"healthy"}
```

**3. Check Frontend:**
```bash
# Should already be running from before
# Open: http://localhost:3000
```

---

## 📊 **Expected Results**

### **All 3 Terminals Running:**

**Terminal 1 (LLM Service):**
```
✓ Uvicorn running on http://0.0.0.0:8000
✓ No errors
```

**Terminal 2 (Backend):**
```
✓ Server starting on port 8080
✓ No errors
```

**Terminal 3 (Frontend):**
```
✓ Local: http://localhost:3000
✓ Ready in 3s
```

---

## 🎯 **Next Steps After Fixing**

1. **Verify all 3 services healthy:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8080/health
   ```

2. **Test integration:**
   ```bash
   curl -X POST http://localhost:8080/api/interview/start \
     -H "Content-Type: application/json" \
     -d '{"candidateName":"Test","topic":"DSA","difficulty":"Junior","duration":30}'
   ```

3. **Test in browser:**
   - Open http://localhost:3000
   - Fill form
   - Click "Start Interview"
   - Should work! 🎉

---

## 🐛 **If Still Not Working**

### **LLM Service Issues:**
```bash
# Check Python version (need 3.9+)
python --version

# Check venv activated
which python  # Should show path with 'venv'

# Reinstall everything
pip install -r requirements.txt --force-reinstall

# Check for API key
echo $ANTHROPIC_API_KEY  # Should not be empty
```

### **Backend Issues:**
```bash
# Check Go version (need 1.21+)
go version

# Clean and rebuild
go clean -modcache
go mod download
go mod tidy

# Check for errors
go run cmd/server/main.go 2>&1 | grep -i error
```

---

## 📞 **Need More Help?**

**Error still happening? Share:**
1. Which service is failing?
2. Full error message
3. Terminal output
4. What command you ran

**I'll help debug!** 🔧
