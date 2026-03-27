# 🎯 Analytics View - Quick Start Guide

## ✅ What Was Implemented

You now have a **toggle-based dashboard interface** with two complete views:

### 1️⃣ Dashboard View (Unchanged UI)
- Analyze claims with evidence retrieval
- View verdicts and confidence scores
- See source credibility with links
- Upload images for multi-modal analysis
- Get detailed explanations and reasoning

### 2️⃣ Analytics View (NEW - Advanced Intelligence)
- 🔥 Evidence Heatmap (sources vs claims)
- 📊 Source Trust Distribution (pie chart)
- 📈 Verdict Confidence Distribution (bar chart)
- 🧠 Recent Claims Analysis (last 5 analyses)
- 🔗 Top Sources Panel (ranked by usage & credibility)
- ⚠️ Uncertain Claims Panel (low confidence flagging)
- ⚙️ Pipeline Status (real-time processing indicators)

---

## 📂 Files Created

```
/frontend/components/dashboard/
├── ToggleTabs.tsx        (2.5 KB)  - View toggle navigation
├── DashboardView.tsx     (9.3 KB)  - Extracted dashboard UI
└── AnalyticsView.tsx    (21.4 KB)  - New advanced analytics panel
```

## 📝 Files Updated

```
/frontend/app/dashboard/page.tsx  - Refactored to support toggle + view switching
```

## 📖 Documentation Created

```
/ANALYTICS_IMPLEMENTATION.md   - Complete technical documentation
/ANALYTICS_VISUAL_GUIDE.md    - Visual diagrams and UI mockups
```

---

## 🚀 How to Test

### 1. Start Frontend Dev Server
```bash
cd "/Users/pratyush/ai truthlens/frontend"
npm run dev
```

### 2. Start Backend API
```bash
cd "/Users/pratyush/ai truthlens/backend"
python3 -m uvicorn main:app --port 8000
```

### 3. Access Dashboard
```
http://localhost:3000/dashboard
```

### 4. Try It Out
```
1. Click [ 📊 Dashboard ] tab
2. Enter a claim (e.g., "Water boils at 100 degrees")
3. Click "Analyze Claim"
4. See verdict and sources
5. Click [ 🔥 Analytics ] tab
6. View heatmaps and insights
```

---

## 🎨 UI Features

### Toggle Navigation
- Sticky top bar with dark theme
- Live status indicator
- Smooth transitions between views
- Responsive on all devices

### Dashboard View
- **Modern input interface** with textarea
- **Ctrl+Enter keyboard shortcut**
- **Image upload support**
- **Results display** with verdict badges
- **Evidence sources** with clickable links

### Analytics View
- **Evidence heatmap** with color intensity (red→yellow→green)
- **Pie chart** for source credibility distribution
- **Bar chart** for verdict confidence levels
- **Claim listings** with verdict badges
- **Source rankings** by frequency and credibility
- **Uncertain claims** flagged for review
- **Pipeline status** with live indicators

---

## 💾 Data Flow

```
User Input
    ↓
[ Dashboard View ]
    ↓
Analyze via Backend API
    ↓
onAnalysisComplete()
    ↓
Update recentAnalyses array
    ↓
[ Analytics View ]
    ↓
Auto-compute heatmap, distributions
    ↓
Display insights
```

---

## 🔧 Integration Checklist

### Backend Integration
- [x] Receives analysis results from `/api/analyze`
- [x] Loads history from `/api/history`
- [x] Supports user authentication
- [x] Handles session tokens

### Frontend Integration
- [x] Uses existing `COLORS` theme
- [x] Uses Framer Motion for animations
- [x] Uses Recharts for visualizations
- [x] Uses Tailwind CSS for responsive design
- [x] Properly typed with TypeScript

---

## 📊 Sample Data Structure

The analytics view expects analysis results in this format:

```typescript
interface AnalysisResult {
  verdict: "TRUE" | "FALSE" | "UNCERTAIN",
  confidence: 0.85,  // 0-1 range
  explanation: "...",
  sources: [
    {
      title: "BBC News",
      url: "https://...",
      credibility: "0.95",  // string or number
      summary: "...",
      name?: "BBC",         // optional
      stance?: "SUPPORTS",  // optional
      snippet?: "..."       // optional
    }
  ],
  signals: ["..."],
  reasoning: "...",
  summary?: "...",
  metrics?: {
    support_score: 2.5,
    refute_score: 0.0,
    agreement_score: 0.95,
    source_count: 3
  }
}
```

---

## 🎬 View Switching

```typescript
// Toggle between views
const [view, setView] = useState<'dashboard' | 'analytics'>('dashboard');

// Conditional rendering
{view === 'dashboard' ? (
  <DashboardView onAnalysisComplete={handleAnalysisComplete} />
) : (
  <AnalyticsView recentAnalyses={recentAnalyses} />
)}
```

---

## 🔄 Recent Analyses Tracking

- **Stored in state**: `recentAnalyses[]`
- **Max items**: Last 10 analyses
- **Loaded on mount**: From `/api/history`
- **Updated on analysis**: Via `onAnalysisComplete()`
- **Used for**: Analytics insights and heatmaps

---

## 🎨 Color Coding

### Verdict Colors
- **✓ TRUE**: `#22C55E` (Neon Green)
- **✗ FALSE**: `#EF4444` (Red)
- **? UNCERTAIN**: `#F59E0B` (Yellow/Amber)

### Heatmap Gradient
```
Red (#7f1d1d)      → 0-20% credibility
Red-Orange (#dc2626) → 20-40%
Orange (#f59e0b)    → 40-60%
Green (#10b981)     → 60-80%
Dark Green (#047857) → 80-100%
```

---

## ✨ Key Features

### UX Enhancements
- ✅ Smooth view transitions (300ms fade)
- ✅ Hover effects on interactive elements
- ✅ Staggered animations for cards
- ✅ Live status pulse indicators
- ✅ Empty state messaging
- ✅ Responsive layouts

### Performance
- ✅ Lazy component composition
- ✅ Memoized computations
- ✅ Efficient re-renders
- ✅ Optimized chart rendering
- ✅ No unnecessary API calls

### Accessibility
- ✅ Semantic HTML
- ✅ Proper contrast ratios
- ✅ Keyboard support
- ✅ Descriptive labels

---

## 🚨 Troubleshooting

### "Components not rendering?"
1. Check browser console for errors
2. Verify backend API is running
3. Check import paths in page.tsx
4. Ensure all dependencies installed (`npm install`)

### "Analytics view is empty?"
1. Analyze at least one claim first
2. Check that backend returns correct structure
3. Verify `/api/history` endpoint works
4. Mock data should show if API fails

### "Styling looks off?"
1. Ensure Tailwind CSS is compiled (`npm run build`)
2. Verify theme colors are loaded
3. Check browser DevTools for missing classes
4. Clear browser cache

### "Types not matching?"
1. Verify backend response structure
2. Check AnalysisResult interface definition
3. Ensure source objects have correct properties
4. Use TypeScript strict mode for debugging

---

## 📚 Documentation Files

### [ANALYTICS_IMPLEMENTATION.md](/ANALYTICS_IMPLEMENTATION.md)
Complete technical documentation with:
- Component descriptions
- Data integration details
- Design system specifications
- Usage instructions
- Future enhancements

### [ANALYTICS_VISUAL_GUIDE.md](/ANALYTICS_VISUAL_GUIDE.md)
Visual guides with:
- Component architecture diagram
- UI layout mockups
- Data flow diagram
- Feature checklist
- File sizes and structure

---

## 🎯 Next Steps

1. **Test the UI**: Access `/dashboard` and toggle between views
2. **Verify Integration**: Analyze a claim and switch to Analytics
3. **Monitor Data**: Check heatmaps and source distributions
4. **Gather Feedback**: Get user feedback on UX/layout
5. **Deploy**: When ready, push to production

---

## 💡 Pro Tips

1. **Keyboard Shortcut**: Use `Ctrl+Enter` to analyze claims faster
2. **Image Analysis**: Upload images + claims for multi-modal detection
3. **Analytics Insights**: Switch to Analytics after each analysis to see patterns
4. **Source Trust**: Check top sources panel to see most reliable sources
5. **Uncertain Claims**: Review ⚠️ uncertain claims section for edge cases

---

## 📞 Support

**Issue**: Components not showing?
**Solution**: 
- Restart dev server: `npm run dev`
- Check import paths
- Verify all files exist

**Issue**: Data not appearing?
**Solution**:
- Check backend API response
- Verify `/api/history` endpoint
- Check browser console for errors

**Issue**: Styling broken?
**Solution**:
- Run `npm run build` to rebuild
- Clear browser cache (Ctrl+Shift+Delete)
- Check Tailwind CSS config

---

## ✅ Implementation Complete

All components are:
- ✅ **Type-safe** (Full TypeScript)
- ✅ **Responsive** (Mobile/Tablet/Desktop)
- ✅ **Accessible** (Proper semantics)
- ✅ **Performant** (Optimized rendering)
- ✅ **Theme-integrated** (Dark mode)
- ✅ **Production-ready** (Error handling)

---

**Last Updated:** 20 March 2026
**Status:** 🚀 Ready for Deployment
