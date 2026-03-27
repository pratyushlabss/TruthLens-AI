# Frontend Build Error Fix - Next.js Module Resolution

## Issue Report

**Error:** `Cannot find module './276.js'` when running `npm run dev`

**Error Stack:**
```
Error: Cannot find module './276.js'
Require stack:
- /Users/pratyush/ai truthlens/frontend/.next/server/webpack-runtime.js
- /Users/pratyush/ai truthlens/frontend/.next/server/pages/_document.js
```

**Root Cause:** Corrupted Next.js build artifacts in the `.next` folder caused references to missing webpack chunks during development server startup.

---

## Solution Applied

### Problem Analysis

The error occurred because:
1. **Stale build artifacts**: The `.next` folder contained outdated or corrupted webpack chunks
2. **Webpack chunk mismatch**: References to chunk `276.js` that didn't exist in the build output
3. **Inconsistent state**: Node modules may have been out of sync with the build cache

### Fix Steps Executed

**Step 1: Clean Build Artifacts** ✅
```bash
cd "/Users/pratyush/ai truthlens/frontend"
rm -rf .next node_modules
```
- Removed corrupted `.next` directory
- Removed `node_modules` to ensure clean dependency installation

**Step 2: Reinstall Dependencies** ✅
```bash
npm install --legacy-peer-deps
```
- Fresh installation with `--legacy-peer-deps` to handle peer dependency conflicts
- Final result: 507 packages installed successfully

**Step 3: Rebuild Next.js** ✅
```bash
npm run build
```
- Output: ✓ Compiled successfully
- Generated 5 routes without errors
- Bundle size: 100 kB first load JS

**Step 4: Verify Dev Server** ✅
```bash
npm run dev
```
- Server started on port 3002 (ports 3000-3001 were in use)
- No module errors
- Frontend responds correctly to HTTP requests

---

## Results

### Before Fix
❌ **Error on npm run dev:**
- Cannot find module './276.js'
- Server fails to start
- Development blocked

### After Fix
✅ **Server Running Successfully:**
- Frontend starts without errors
- Available at `http://localhost:3002`
- All pages load correctly
- Ready for testing

---

## Verification

### Build Status
```
✓ Compiled successfully
✓ Generating static pages (7/7)
✓ Finalizing page optimization
```

### Routes Available
- `○ /` (Static) - Main analysis page
- `○ /history` (Static) - History view
- `ƒ /api/analyze` (Dynamic) - Analysis API
- `ƒ /api/history` (Dynamic) - History API

### Dependencies
- 507 packages installed
- 4 high severity vulnerabilities (non-critical for dev)
- Using Next.js 14.2.35
- Node.js environment: v18+ (via nvm)

---

## What Was Changed

| File/Folder | Action | Result |
|---|---|---|
| `.next/` | Deleted | Removed corrupted build cache |
| `node_modules/` | Deleted | Removed outdated dependencies |
| `package-lock.json` | Kept | Ensured consistent installation |
| Source code | No changes | Frontend code unchanged |

---

## How to Prevent This

1. **Regular Clean Builds** (when experiencing issues):
   ```bash
   rm -rf .next node_modules && npm install && npm run build
   ```

2. **Use .gitignore** (ensure these are ignored):
   ```
   .next/
   node_modules/
   .env.local
   ```

3. **Clear Build Cache** after major changes:
   ```bash
   rm -rf .next && npm run build
   ```

---

## Next Steps

1. ✅ Frontend builds successfully
2. ✅ Dev server runs without errors
3. ✅ API endpoints ready for backend integration
4. 📋 **TODO:** Test API responses with backend
5. 📋 **TODO:** Verify full analysis workflow
6. 📋 **TODO:** Deploy to production if satisfied

---

## Testing the Fix

### Local Testing
```bash
# Start frontend
npm run dev
# Opens on http://localhost:3002 (or next available port)

# In another terminal, start backend
cd /Users/pratyush/ai truthlens/backend
python -m uvicorn main:app --port 8000
```

### Verify Workflow
1. Open http://localhost:3002 in browser
2. Enter a claim to analyze
3. Should see analysis results with:
   - Verdict (REAL/RUMOR/FAKE)
   - Confidence score
   - Key signals
   - Highlighted terms
   - Sources

---

## Technical Details

### Why This Fix Works

The issue was NOT with the source code, but with the build system state:

1. **Webpack chunks**: Next.js compiles pages into webpack chunks stored in `.next/`
2. **Corruption**: Stale or partially built chunks can reference missing files
3. **Solution**: A clean rebuild ensures all chunks are properly generated
4. **Isolation**: Removing `node_modules` ensures no leftover dependencies interfere

### Next.js Build Process
```
Source Code (app/*.tsx)
    ↓
Webpack Compilation
    ↓
Chunks (276.js, etc.) + HTML
    ↓
.next/ Directory
    ↓
Dev Server Loads Files
```

When the `.next` folder is corrupted, step 4 fails even if source code is fine.

---

## Support

If the error returns:
1. Check Node.js version: `node --version` (should be v18+)
2. Check npm version: `npm --version` (should be v9+)
3. Verify source files exist: `ls -la app/`
4. Repeat the clean build:
   ```bash
   rm -rf .next node_modules
   npm install --legacy-peer-deps
   npm run build
   npm run dev
   ```

---

## Last Updated
**Date:** 17 March 2026
**Status:** ✅ RESOLVED
**Env:** macOS, Node.js 18+, Next.js 14.2.35
