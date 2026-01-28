# Quick Start Guide - Phase 1 Testing

## 🚀 Getting Started (3 Steps)

Your AI property analysis feature is **completely implemented** and ready to use. You just need to restart the backend server to load the new routes.

---

## Step 1: Restart Backend Server

The backend is running but needs a fresh start to load the AI routes.

### Windows (Easiest):

1. **Stop current backend:**
   - Find the terminal/command prompt running uvicorn
   - Press `Ctrl+C` to stop it
   - OR close that terminal window entirely

2. **Start fresh backend:**
   - Open a **new** Command Prompt or PowerShell
   - Run these commands:
     ```cmd
     cd C:\Users\gideo\slv-housing-market\backend
     venv\Scripts\activate
     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
     ```

3. **Verify it worked:**
   - You should see: `INFO: Application startup complete.`
   - Open a new terminal and run:
     ```cmd
     curl http://localhost:8000/api/property-ai/health
     ```
   - You should see:
     ```json
     {
       "status": "healthy",
       "service": "Property AI Analysis",
       "phase": "1 (Property Summaries)"
     }
     ```

---

## Step 2: Frontend Should Already Be Running

Check if frontend is running by visiting: http://localhost:5173

**If it's NOT running:**
```cmd
cd C:\Users\gideo\slv-housing-market\frontend
npm run dev
```

You should see: `Local: http://localhost:5173/`

---

## Step 3: Test the AI Feature! 🎉

1. **Open browser** to http://localhost:5173

2. **Upload test data** (if no properties shown):
   - Click "Upload CSV" button in header
   - Upload any CSV with columns: address, city, price, beds, baths, sqft

3. **Click the AI button:**
   - Look for **"✨ Summarize Current Results with AI"** button
   - It appears above the property grid when properties are loaded

4. **Watch the magic happen:**
   - Loading animation (3-5 seconds)
   - AI summary panel appears with:
     - 📊 Market overview
     - 💡 Key insights
     - 📈 Statistics dashboard
     - 🎯 Buyer recommendations

---

## 🔍 Troubleshooting

### Problem: Backend won't start

**Error:** "Address already in use"

**Fix:**
```cmd
# Find and kill the process using port 8000
netstat -ano | findstr :8000
# Note the PID (last column), then:
taskkill /PID <the_pid_number> /F

# Then try starting backend again
```

### Problem: "✨ Summarize" button doesn't appear

**Cause:** No properties loaded

**Fix:**
1. Check if properties are displayed on the page
2. If not, click "Upload CSV" and upload property data
3. Or adjust filters to show properties

### Problem: AI returns an error

**Most likely cause:** Backend needs restart (Step 1 above)

**Other causes:**
- Check Google API key is set in `backend/.env`
- Check backend logs for errors
- Verify `GOOGLE_API_KEY` in `.env` file

### Problem: Frontend won't load

**Fix:**
```cmd
cd C:\Users\gideo\slv-housing-market\frontend
npm install
npm run dev
```

---

## 📊 What to Expect

### Sample AI Response

When you click "Summarize", you'll see something like:

```
🎯 AI Market Summary

Confidence: High | 42 Properties Analyzed

Overview:
The market shows 42 properties in Sandy with strong value
opportunities. Average price is $425,000 with monthly costs
around $2,150. Properties are moving quickly with only 12
days average on market.

💡 Key Insights:
• Best value: 123 Main St at $240/sqft, well below market average
• Low inventory indicates seller's market with competitive pricing
• Properties in Sandy Bench offer 15% better value than city average

📈 Market Statistics:
┌─────────────────┬──────────┐
│ Avg Price       │ $425,000 │
│ Median Price    │ $410,000 │
│ Avg Monthly     │ $2,150   │
│ Avg $/sqft      │ $245.50  │
└─────────────────┴──────────┘

🎯 Recommendations:

💙 First-Time Buyers
Focus on properties under $400k with HOA under $100.
Consider 456 Oak Ave for best starter value.

💚 Families
Prioritize 4+ bedroom homes near schools. Properties in
Area 3 offer best family amenities.

💜 Investors
Look for properties with price/sqft under $230 and high
rental demand areas.
```

---

## ✅ Verification Checklist

Use this to verify everything works:

- [ ] Backend starts without errors
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] AI health check works: `curl http://localhost:8000/api/property-ai/health`
- [ ] Frontend loads at http://localhost:5173
- [ ] Can see property filters on home page
- [ ] Properties display (or can upload CSV)
- [ ] "✨ Summarize" button appears
- [ ] Clicking summarize shows loading state
- [ ] AI summary panel appears with content
- [ ] Confidence badge displays
- [ ] Statistics show correctly
- [ ] Refresh button works

---

## 🎓 Next Steps After Testing

Once you've verified Phase 1 works:

### Option 1: Continue to Phase 2
Phase 2 adds **Property Recommendations**:
- Personalized property suggestions
- Match scores with explanations
- Pros/cons for each recommendation

### Option 2: Review the Implementation
- Read `PHASE1_COMPLETE.md` for full documentation
- Explore the code in `backend/app/services/`
- Check out the React component in `frontend/src/components/`

### Option 3: Customize
- Adjust the AI prompts in `property_analysis_service.py`
- Modify the UI in `PropertySummaryPanel.tsx`
- Add custom statistics or insights

---

## 📞 Need Help?

If you encounter any issues:

1. **Check the logs:**
   - Backend: Look at the terminal running uvicorn
   - Frontend: Check browser console (F12)

2. **Verify environment:**
   - Python virtual environment is activated
   - Google API key is set in `.env`
   - Node modules are installed

3. **Common fixes:**
   - Restart backend server (Step 1)
   - Clear browser cache
   - Check API key is valid

---

## 🎉 You're All Set!

The implementation is complete and ready to use. Just follow the 3 steps above and you'll have a working AI-powered property analysis feature!

**Have fun testing!** 🚀

---

*Last updated: January 24, 2026*
