# Family CFO - Quick Start Guide

## 🚀 Current Status

**System:** ✅ Fully operational  
**Version:** v1.0.0  
**Next:** V1.1 AI Activation

---

## 📍 Access Points

- **Mobile App:** http://localhost:6503
- **Admin Dashboard:** http://localhost:6502
- **API Docs:** http://localhost:6501/docs
- **Database:** localhost:6500

**Login:** admin / password123

---

## ⚡ Quick Actions

### Activate AI Service (V1.1)

**Option 1: Use Batch Script**
```bash
cd f:\Augment-coder\familyltdcfo\backend
.\restart_with_ai.bat
```

**Option 2: Manual Restart**
1. Stop backend (Ctrl+C in backend terminal)
2. Run:
```bash
cd f:\Augment-coder\familyltdcfo\backend
$env:DATABASE_URL="postgresql://admin:password123@localhost:6500/family_cfo"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 6501
```

**Verify:** Look for `✅ AI Service enabled - Provider: openrouter`

### Test AI Categorization
```powershell
$body = @{merchant="PetroCan"; amount=75.50} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:6501/api/ai/categorize-transaction" -Method Post -ContentType "application/json" -Body $body
```

---

## 📊 System Overview

**Services Running:**
- PostgreSQL (6500) - Database
- FastAPI (6501) - Backend API
- React (6502) - Admin Dashboard
- React (6503) - Mobile App

**Data:**
- Net Worth: $1,562,700
- Transactions: 5+
- Accounts: 3 (TFSA/RRSP/RESP)
- Assets: 4

---

## 📚 Documentation

- `final_summary.md` - Complete project summary
- `walkthrough.md` - V1.1 activation guide
- `api_integration_plan.md` - API details
- `task.md` - Task checklist

---

## 🎯 Next Steps

1. **Activate AI** (5 min) - Restart backend
2. **Test Features** (10 min) - Verify auto-categorization
3. **Docker Deploy** (2-3 hrs) - V1.2 milestone

---

**Status:** 🟢 Ready for AI activation!
