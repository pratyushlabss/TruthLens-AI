# Supabase Cloud Migration Guide

This document provides instructions for setting up the Supabase cloud database and completing the migration from SQLite.

## Prerequisites

- Supabase account created at https://supabase.com
- Project URL: `https://qmcthtltsxyfdotakjkc.supabase.co`
- Anon Key: `sb_publishable_dvvCGR1fZA7vguvmUqrKXQ_DpWpru5U`

## Required Database Tables

You need to create the following tables in your Supabase project. Go to the SQL Editor in Supabase Dashboard and run these queries:

### 1. Profiles Table (for user information)

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for users to access their own profile
CREATE POLICY "Users can view their own profile" 
  ON profiles FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" 
  ON profiles FOR UPDATE 
  USING (auth.uid() = id);
```

### 2. Analysis History Table (for storing analysis results)

```sql
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

-- Create index for faster queries
CREATE INDEX analysis_history_user_id_idx ON analysis_history(user_id);
CREATE INDEX analysis_history_created_at_idx ON analysis_history(created_at);

-- Enable RLS
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

-- Create policies for users to access only their own analyses
CREATE POLICY "Users can view their own analysis history" 
  ON analysis_history FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analyses" 
  ON analysis_history FOR INSERT 
  WITH CHECK (auth.uid() = user_id);
```

## Frontend Implementation Status

✅ **Completed:**
- Supabase client initialization (`lib/supabase.ts`)
- Refactored authentication context to use Supabase Auth API
- Updated login/signup pages to use Supabase authentication
- Protected route wrapper component for authentication checks
- Analysis history component to display recent user analyses
- Modified analyze API endpoint to save results to Supabase

✅ **Features:**
- User registration with email and password
- Automatic profile creation on signup
- Login with email and password
- Session management via Supabase
- Analysis results automatically saved to cloud database
- Recent analysis history displayed in dashboard

## Backend Integration

The backend API endpoint `/api/analyze` now:
1. Receives form data (text, URL, or image)
2. Calls the backend AI model for analysis
3. Receives analysis result from backend
4. Saves the result to Supabase `analysis_history` table

No changes needed to the backend `/api/analyze` endpoint. The frontend handles saving to Supabase.

## Environment Variables

Frontend `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=https://qmcthtltsxyfdotakjkc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_dvvCGR1fZA7vguvmUqrKXQ_DpWpru5U
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create the Supabase tables (run SQL queries above in Supabase Dashboard)

3. Start the frontend:
```bash
npm run dev
```

## Testing Flows

### Sign Up Flow
1. Go to `/signup`
2. Enter email, password, username
3. Click "Sign Up"
4. User profile is automatically created in `profiles` table
5. Redirected to dashboard or email verification page

### Login Flow
1. Go to `/login`
2. Enter email and password
3. Click "Login"
4. Session is managed by Supabase automatically
5. Redirected to dashboard

### Analysis Flow
1. From dashboard, enter a claim to analyze
2. Click "Analyze Claim" to submit
3. Backend processes the claim and returns result
4. Result is automatically saved to `analysis_history` table
5. Recent analyses displayed in the history section

### Logout Flow
1. Click logout/profile menu
2. Session is cleared from Supabase
3. Redirected to login page

## Troubleshooting

### "Missing Supabase environment variables" error
- Ensure `.env.local` has correct `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Run `npm install` to ensure `@supabase/supabase-js` is installed

### "Failed to create profile" on signup
- Check that `profiles` table exists and has correct schema
- Verify RLS policies are created correctly
- Check Supabase logs for detailed errors

### Analysis not saving to database
- Verify `analysis_history` table exists
- Check that user is authenticated (token is being passed)
- Verify RLS policies allow inserts for the user
- Check browser console for detailed error messages

### "User not found" after login
- Ensure `profiles` table entry was created during signup
- For existing users migrating from SQLite, manually create profiles entries

## Next Steps

1. ✅ Supabase client created
2. ✅ Authentication refactored to use Supabase
3. ✅ Database schema defined (SQL queries provided)
4. ✅ Frontend components updated
5. Run SQL queries in Supabase Dashboard to create tables
6. Test complete signup → login → analysis → history flow
7. Consider backend migration to Supabase for complete cloud deployment

## Security Notes

- Anon key is for client-side use only (read-only by default)
- RLS (Row Level Security) ensures users can only access their own data
- Email/password is handled securely by Supabase Auth
- All sensitive operations are protected by RLS policies
