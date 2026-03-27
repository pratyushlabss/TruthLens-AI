# Supabase Cloud Migration - QUICK START

## 🚀 Get Running in 5 Minutes

### Step 1: Create Database Tables (2 minutes)

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project: `qmcthtltsxyfdotakjkc`
3. Click **SQL Editor** (left sidebar)
4. Click **New query**
5. Copy and paste this SQL:

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

6. Click **Run** (or Ctrl+Enter)
7. ✅ Tables created!

### Step 2: Install Dependencies (1 minute)

```bash
cd frontend
npm install
```

### Step 3: Verify Environment (30 seconds)

Check `frontend/.env.local` has these lines:

```
NEXT_PUBLIC_SUPABASE_URL=https://qmcthtltsxyfdotakjkc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_dvvCGR1fZA7vguvmUqrKXQ_DpWpru5U
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Start Frontend (30 seconds)

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Step 5: Test the Flow (1 minute)

1. **Sign Up**
   - Go to `/signup`
   - Enter: email, password, username
   - Should redirect to dashboard

2. **Analyze a Claim**
   - Enter: "Water boils at 100 degrees"
   - Click: "Analyze Claim"
   - Watch result appear

3. **Check Database**
   - Supabase Dashboard → **Table Editor**
   - Click `analysis_history`
   - ✅ See your analysis saved!

## ✅ Verification Checklist

- [ ] Tables created in Supabase (check Table Editor)
- [ ] `npm install` completed without errors
- [ ] `.env.local` has Supabase credentials
- [ ] Frontend runs on `:3000` without errors
- [ ] Can signup and create account
- [ ] Can login with created account
- [ ] Can perform analysis
- [ ] Analysis appears in `analysis_history` table
- [ ] No `OperationalError` messages

## 🆘 Quick Troubleshooting

### "Missing Supabase environment variables"
→ Check `.env.local` has both `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### "Tables don't exist" (errors during signup)
→ Go back to Step 1, run SQL queries again

### "Analysis not saving"
→ Check browser DevTools Console (F12) for errors

### "Can't signup/login"
→ Check Supabase Dashboard → **Auth** → **Users** (Is user created?)

## 📊 What's Changed

| Aspect | Before | After |
|--------|--------|-------|
| Auth | Custom JWT on backend | Supabase Auth API |
| Database | SQLite local | Supabase PostgreSQL cloud |
| Session Storage | localStorage token | Supabase managed |
| Analysis History | Not tracked | Automatically saved |
| User Data | Only on backend | Accessible from frontend |

## 🎯 What Works Now

✅ Sign up with email/password
✅ Login with email/password  
✅ Automatic profile creation
✅ Persistent sessions
✅ Analysis saved to cloud automatically
✅ View your analysis history
✅ Different users see only their data
✅ Zero "OperationalError" on login

## 📚 Full Documentation

See these files for more details:
- **`SUPABASE_MIGRATION_GUIDE.md`** - Complete setup & SQL
- **`CLOUD_MIGRATION_SUMMARY.md`** - Technical overview
- **`frontend/.env.local`** - Configuration

## 🔑 Key Credentials (Already Set)

- **Supabase URL:** `https://qmcthtltsxyfdotakjkc.supabase.co`
- **Anon Key:** `sb_publishable_dvvCGR1fZA7vguvmUqrKXQ_DpWpru5U`
- **Backend:** `http://localhost:8000`

## 🎉 Done!

Your TruthLens AI app is now running with cloud authentication and database storage. No more local SQLite issues!

### Next (Optional)
- Migrate backend to Supabase Python client
- Set up custom domain
- Configure email verification
- Enable multi-factor authentication
