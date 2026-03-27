# 🚀 TruthLens Cloud Migration - Step-by-Step Checklist

## 5-MINUTE SETUP GUIDE

### STEP 1️⃣: Create Database Tables (2 minutes)

**Location:** Supabase Dashboard → SQL Editor

**What to do:**
- [ ] Open https://app.supabase.com
- [ ] Click your project: `qmcthtltsxyfdotakjkc`
- [ ] Click "SQL Editor" in left sidebar
- [ ] Click "New query"
- [ ] Copy entire SQL block from below
- [ ] Paste into editor
- [ ] Click "Run" (or Ctrl+Enter)
- [ ] ✅ See "queries executed successfully"

**SQL to Copy & Paste:**
```sql
-- Create profiles table
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile" 
  ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" 
  ON profiles FOR UPDATE USING (auth.uid() = id);

-- Create analysis_history table
CREATE TABLE analysis_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  text_input TEXT,
  url_input TEXT,
  image_input TEXT,
  verdict TEXT NOT NULL,
  confidence_score FLOAT NOT NULL,
  detailed_analysis JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX analysis_history_user_id_idx ON analysis_history(user_id);
CREATE INDEX analysis_history_created_at_idx ON analysis_history(created_at);

ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own analysis history" 
  ON analysis_history FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own analyses" 
  ON analysis_history FOR INSERT WITH CHECK (auth.uid() = user_id);
```

**Verify Success:**
- [ ] Message says "queries executed successfully"
- [ ] Go to "Table Editor" → See `profiles` table
- [ ] Go to "Table Editor" → See `analysis_history` table
- ✅ **TABLES CREATED**

---

### STEP 2️⃣: Install Dependencies (1 minute)

**Location:** Your Terminal

**What to do:**
```bash
cd frontend
npm install
```

**What to expect:**
- Terminal shows "added X packages"
- No error messages (warnings are OK)
- Completes without errors

**Verify Success:**
- [ ] No red error messages
- [ ] `node_modules` folder created
- ✅ **DEPENDENCIES INSTALLED**

---

### STEP 3️⃣: Start Frontend (30 seconds)

**Location:** Terminal in `frontend/` directory

**What to do:**
```bash
npm run dev
```

**What to expect:**
- Terminal says: `▲ Next.js 14.x.x`
- Terminal says: `- Local: http://localhost:3000`
- No error messages

**Browser:**
- [ ] Open http://localhost:3000
- [ ] Page loads successfully
- ✅ **SERVER RUNNING**

---

### STEP 4️⃣: Sign Up (2 minutes)

**Location:** http://localhost:3000

**What to do:**
1. [ ] Click "Sign Up" or go to `/signup`
2. [ ] Enter email: `test@example.com`
3. [ ] Enter password: `TestPassword123!`
4. [ ] Enter username: `testuser`
5. [ ] Click "Sign Up" button
6. [ ] Wait for redirect to dashboard

**What to expect:**
- [ ] Form submits
- [ ] Page redirects to `/dashboard`
- [ ] Dashboard appears with claim analyzer box

**Check Supabase (verify data saved):**
- [ ] Go to Supabase Dashboard → Auth
- [ ] Click "Users" tab
- [ ] See user with email `test@example.com`
- [ ] Go to Supabase Dashboard → Table Editor
- [ ] Click `profiles` table
- [ ] See row with your username and email
- ✅ **USER ACCOUNT CREATED**

---

### STEP 5️⃣: Analyze a Claim (2 minutes)

**Location:** Dashboard (http://localhost:3000/dashboard)

**What to do:**
1. [ ] In text box, type: `Water boils at 100 degrees Celsius`
2. [ ] Click "Analyze Claim" button
3. [ ] Wait 5-10 seconds for backend processing
4. [ ] See result appear (TRUE/FALSE verdict)

**What to expect:**
- [ ] Spinning indicator while processing
- [ ] Result shows verdict (TRUE or FALSE)
- [ ] Result shows confidence percentage
- [ ] No error messages in browser
- [ ] No "OperationalError" anywhere

**Check Supabase (verify analysis saved):**
- [ ] Go to Supabase Dashboard → Table Editor
- [ ] Click `analysis_history` table
- [ ] See new row with:
  - your username in `user_id`
  - your claim text in `text_input`
  - verdict in `verdict` column (TRUE/FALSE)
  - confidence score in `confidence_score` column
- ✅ **ANALYSIS SAVED TO CLOUD**

---

### STEP 6️⃣: Check Browser Console (30 seconds)

**Location:** Analytics + Debugging

**What to do:**
1. [ ] Press F12 (or right-click → Inspect)
2. [ ] Click "Console" tab
3. [ ] Look at all messages

**What to expect:**
- [ ] NO red error messages
- [ ] NO "OperationalError" messages
- [ ] NO 500 errors
- [ ] Messages about successful requests are fine
- [ ] You should see something like:
  - `Analysis saved successfully`
  - Or just no errors

**If you see errors:**
- [ ] Take a screenshot
- [ ] Check troubleshooting section below
- [ ] Refer to SUPABASE_MIGRATION_GUIDE.md

- ✅ **NO ERRORS DETECTED**

---

### STEP 7️⃣: Test Login/Logout (2 minutes)

**Location:** Dashboard

**What to do:**
1. [ ] Click "Logout" or logout button
2. [ ] You redirect to login page
3. [ ] Click "Log In" or already on login
4. [ ] Enter email: `test@example.com`
5. [ ] Enter password: `TestPassword123!`
6. [ ] Click "Log In"
7. [ ] Dashboard loads

**What to expect:**
- [ ] Logout works instantly
- [ ] Login form accepts credentials
- [ ] Login works and redirects to dashboard
- [ ] NO "OperationalError" messages
- [ ] Session persists (stay logged in if you refresh)

- ✅ **AUTHENTICATION WORKING**

---

## ✅ SUCCESS CHECKLIST

**If all these are checked, you're done:**

- [ ] Tables created in Supabase (verified in Table Editor)
- [ ] Dependencies installed (npm install succeeded)
- [ ] Frontend running on localhost:3000
- [ ] Can sign up and create account
- [ ] Profile appears in Supabase `profiles` table
- [ ] Can analyze a claim
- [ ] Analysis appears in Supabase `analysis_history` table
- [ ] Browser console has no red errors
- [ ] NO "OperationalError" messages anywhere
- [ ] Can login/logout without errors
- [ ] Dashboard loads after login

**If all checked:** 🎉 **MIGRATION COMPLETE!**

---

## 🆘 TROUBLESHOOTING

### ❌ "Tables don't exist" error during signup
**Fix:** Go back to STEP 1, copy-paste SQL again, run in SQL Editor

### ❌ "Missing Supabase environment variables"
**Fix:** Check `frontend/.env.local` has these lines:
```
NEXT_PUBLIC_SUPABASE_URL=https://qmcthtltsxyfdotakjkc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_dvvCGR1fZA7vguvmUqrKXQ_DpWpru5U
```

### ❌ "npm install" fails
**Fix:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### ❌ Frontend won't start / port 3000 in use
**Fix:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Then try again
npm run dev
```

### ❌ Can't signup / error on signup form
**Check:**
- Supabase tables were created (STEP 1)
- Email is unique (try different email)
- Password is strong (uppercase, lowercase, number, special char)

### ❌ Analysis doesn't appear in database
**Check:**
- Browser console (F12) for errors
- Signal that analysis "completed" on frontend
- `analysis_history` table exists in Supabase

### ❌ Can signup but can't login
**Check:**
- Email matches exactly what you signed up with
- Password matches exactly what you signed up with
- Supabase Dashboard → Auth → Users (user should be listed)

---

## 📞 NEED MORE HELP?

See these files:
- **Quick Reference:** `START_SUPABASE_MIGRATION.md`
- **Complete Setup:** `SUPABASE_MIGRATION_GUIDE.md`
- **Technical Details:** `CLOUD_MIGRATION_SUMMARY.md`
- **Status Report:** `MIGRATION_STATUS.md`

---

## 🎯 WHAT'S HAPPENING

**Step 1:** Creating database tables in cloud (Supabase PostgreSQL)
**Step 2:** Installing connection library (@supabase/supabase-js)
**Step 3:** Starting Next.js development server
**Step 4:** Creating user account using Supabase Auth
**Step 5:** Analyzing claim and automatically saving to cloud
**Step 6:** Confirming no database errors in console
**Step 7:** Testing logout/login flow

**Result:** Complete cloud-based authentication and data storage with zero local database errors!

---

## ⏱️ TOTAL TIME: ~10-15 minutes

Don't panic if something takes longer than expected. The SQL setup is the slowest part but still ~1-2 minutes.

---

**Good luck! 🚀**
