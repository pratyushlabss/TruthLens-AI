# TruthLens AI Dashboard - Visual Preview

## 🎨 Component Layout Map

### Dashboard Page Structure
```
┌─────────────────────────────────────────────────────────────────────┐
│  TL         │  🔍 Analyze a claim, URL, or image...    🔔  User     │
│ TruthLens   │                                                        │
│  AI         ├────────────────────────────────────────────────────────┤
│             │                                                         │
│ Dashboard   │    ╔════════════════════════════════════════════════╗ │
│ Analyze ✓   │    ║  TruthLens AI                                 ║ │
│ Sessions(3) │    ║  Advanced AI-powered fact-checking            ║ │
│ Analytics   │    ╚════════════════════════════════════════════════╝ │
│ Settings    │                                                         │
│             │    ┌──────────────────────────────────────────────────┐│
│ ─────────── │    │ AnalysisInput Component (Multi-tab Input)      ││
│ User Pf ✓   │    │ [Text] [URL] [Image]                          ││
│ Settings    │    │                                                 ││
│ Logout      │    │ [Large textarea for claim analysis]            ││
│             │    │                          [Analyze Button] ✨   ││
│             │    └──────────────────────────────────────────────────┘│
│             │                                                         │
│             │  ┌──────────────────────────┬──────────────────────┐  │
│             │  │ VerdictCard              │ ModelBreakdown       │  │
│             │  │ ❌ MISINFORMATION        │ 🔬 Model Breakdown   │  │
│             │  │                          │ 🧠 RoBERTa NLP: 92%  │  │
│             │  │      ◯  85%              │ 📈 Evidence: 85%     │  │
│             │  │    ╱    ╲                │ 🌊 Propagation: 78%  │  │
│             │  │  ╱        ╲              │                      │  │
│             │  │ │   85     │             │ Weighted: 86%       │  │
│             │  │  ╲        ╱              │                      │  │
│             │  │    ╲____╱               └──────────────────────┘  │
│             │  │                                                     │
│             │  │ High confidence          Models weighted by         │
│             │  │ in assessment            importance                │
│             │  └──────────────────────────┴──────────────────────┘  │
│             │                                                         │
│             │  ┌──────────────────────────┬──────────────────────┐  │
│             │  │ KeySignalsPanel          │ PropagationAnalysis │  │
│             │  │ 🚨 Key Signals           │ 📊 Propagation      │  │
│             │  │                          │                      │  │
│             │  │ [🔴 Conspiracy detected] │ 📈 Tweet Velocity:  │  │
│             │  │ [🔴 No credible sources] │    1,250/hour       │  │
│             │  │ [🟡 Emotional triggers]  │ 🌐 Cluster Size:    │  │
│             │  │ [🟡 High prop risk]      │    847 networks     │  │
│             │  │                          │ ↗️  Reshare Factor:  │  │
│             │  │ High Risk: 2             │    3.2x             │  │
│             │  │ Warnings: 2              │ 📊 Risk: MEDIUM      │  │
│             │  │ Avg Conf: 86%            │    [████░░] 67%      │  │
│             │  └──────────────────────────┴──────────────────────┘  │
│             │                                                         │
│             │  ┌────────────────────────────────────────────────┐   │
│             │  │ EvidenceSourcesPanel                           │   │
│             │  │ 📚 Evidence Sources                            │   │
│             │  │                                                │   │
│             │  │ Total: 3 | Supporting: +2 | Contradicting: -1│   │
│             │  │                                                │   │
│             │  │ ┌──────────────────────────────────────────┐  │   │
│             │  │ │ ✓ Reuters                  [HIGH] 98%   │  │   │
│             │  │ │   reuters.com/article-123                │  │   │
│             │  │ │   This fact has been independently...   │  │   │
│             │  │ │   🔗 View Original                       │  │   │
│             │  │ └──────────────────────────────────────────┘  │   │
│             │  │                                                │   │
│             │  │ ┌──────────────────────────────────────────┐  │   │
│             │  │ │ ✕ Medium Blog                [LOW] 62%   │  │   │
│             │  │ │   medium.com/user-article               │  │   │
│             │  │ │   Despite mainstream claims, this...    │  │   │
│             │  │ │   🔗 View Original                       │  │   │
│             │  │ └──────────────────────────────────────────┘  │   │
│             │  └────────────────────────────────────────────────┘   │
│             │                                                         │
│             │  ┌────────────────────────────────────────────────┐   │
│             │  │ ClaimBreakdownPanel                            │   │
│             │  │ 🔗 Claim Breakdown                             │   │
│             │  │                                                │   │
│             │  │ "Water boils at 100 degrees" → TRUE 99% ✓     │   │
│             │  │ [███████████████████████] Universal fact        │   │
│             │  │                                                │   │
│             │  │ "Vaccine causes infertility" → FALSE 96% ✗     │   │
│             │  │ [███████████████████████] No credible evidence  │   │
│             │  │                                                │   │
│             │  │ Total Claims: 3 | True: 2 | False: 1          │   │
│             │  └────────────────────────────────────────────────┘   │
│             │                                                         │
│             │  ┌────────────────────────────────────────────────┐   │
│             │  │ 💾 Save Analysis?   [Skip]   [Save Analysis]  │   │
│             │  └────────────────────────────────────────────────┘   │
│             │                                                         │
└─────────────┴─────────────────────────────────────────────────────────┘
```

---

## 🌈 Color Scheme in Action

### **Verdict Indicators**
```
┌─────────────────────────────────────────────┐
│ ✓ REAL/TRUE        → 🟢 Neon Green #22C55E  │
│ ✕ FAKE/FALSE       → 🔴 Red       #EF4444  │
│ ? RUMOR/UNKNOWN    → 🟡 Amber     #F59E0B  │
│ — NEUTRAL/INFO     → 🟣 Purple    #8B5CF6  │
└─────────────────────────────────────────────┘
```

### **Component Styling**
```
┌─────────────────────────────────────────────┐
│ Background:    Deep Navy  #0B0F1A           │
│ Cards:         Dark Gray  #111827           │
│ Borders:       White/10   rgba(255,255...)  │
│ Hovers:        WhiteF/5   rgba(255,255...)  │
│ Text Primary:  Near White #F9FAFB           │
│ Text Tertiary: Med Gray   #9CA3AF           │
└─────────────────────────────────────────────┘
```

---

## 📱 Responsive Breakpoints

### **Desktop Layout (lg: 1024px+)**
- Fixed 264px sidebar
- Multi-column grid layouts
- Full chart displays
- 3-column panels: Verdict + Models side-by-side

### **Tablet Layout (md: 768px)**
- Sidebar toggleable
- 2-column panels
- Simplified charts

### **Mobile Layout (sm: 640px)**
- Sidebar collapses
- Single-column stacked
- Touch-optimized buttons
- Vertical charts

---

## ⚡ Animation Sequences

### **Page Load Sequence**
```
1. Hero section fades in (0ms)
2. Input component slides in (100ms delay)
3. Result panels stagger in (200ms+ delay per panel)
   - VerdictCard: 200ms
   - ModelBreakdown: 300ms
   - KeySignalsPanel: 400ms
   - Etc.
```

### **Verdict Card Animation**
```
1. Card background fades in
2. Circular progress ring animates (1.5s)
3. Confidence number counts up (1.5s)
4. Glow effect pulses continuously
```

### **Signal Expansion**
```
1. Card animates to hover state
2. Content expands smoothly (0.3s)
3. Text fades in simultaneously
```

---

## 🎯 Interactive Elements

### **Hover States**
```
Buttons:     Scale 1.05, shadow increase
Cards:       Border color change, background lighten
Links:       Color change, translate right
Icons:       Rotate on expand (180°)
```

### **Focus States**
```
Input:       Border glow, shadow expansion
Buttons:     Ring effect, scale change
Navigation:  Highlight with active color
```

### **Active States** 
```
Sidebar Nav: Green left border, highlighted background
Tabs:        Color change with bottom border
```

---

## 📊 Data Display Patterns

### **VerdictCard**
Shows confident verdict with animated circular progress indicator

### **ModelBreakdown**
3-model horizontal bars with weighted composite calculation

### **KeySignalsPanel**
Expandable chips organized by risk level (Danger/Warning/Info)

### **EvidenceSourcesPanel**
Card-based source list with sentiment indicators (✓/✕)

### **PropagationAnalysisPanel**
Metric cards with formatted numbers + risk gauge

### **ClaimBreakdownPanel**
Table-like layout with per-claim verdicts and reasoning

---

## 🎨 Typography

### **Heading Sizes**
```
h1: 3.75rem (60px)  - Page titles
h2: 2.25rem (36px)  - Section titles
h3: 1.875rem (30px) - Component headers
h4: 1.125rem (18px) - Card titles
p:  1rem (16px)     - Body text
p:  0.875rem (14px) - Secondary text
p:  0.75rem (12px)  - Tertiary text
```

### **Font Weights**
```
Regular:  400  - Body text
Medium:   500  - Secondary headings
Semibold: 600  - Component titles
Bold:     700  - Primary headings
```

---

## 🔄 Loading States

### **Skeleton Screens**
Components show loading state with:
- Animated pulse effects
- Placeholder gradients
- Spinner animations

### **Button States**
```
Normal:    Green gradient background
Hover:     Scale 1.05
Loading:   ⚙️ Analyzing... with spinner
Disabled:  Opacity 0.5, cursor not-allowed
```

---

## ✨ Visual Effects

### **Glassmorphism**
`.backdrop-blur-md` + `from-white/10 to-white/5`  
Creates frosted glass effect over dark background

### **Glow Effects**
- Real verdict: Emerald 500/20 shadow
- Fake verdict: Red 500/20 shadow
- Rumor verdict: Amber 500/20 shadow

### **Gradient Backgrounds**
- Neon: Green to emerald
- Danger: Red to dark red
- Warning: Amber to dark amber
- Calm: Purple to indigo

---

## 🎬 Example Component Rendering

### **VerdictCard Showing FALSE**
```
┌─────────────────────────────────┐
│ Analysis Result                 │
│ 🔴 MISINFORMATION               │
│                    [✕ Icon]    │
│                                 │
│         ◯─────────────           │
│       ╱               ╲          │
│      │  70 Confidence  │         │
│      │                 │         │
│       ╲               ╱          │
│         ◯─────────────           │
│                                 │
│  High confidence in assessment  │
│  [████████████████░░░░] 70%     │
└─────────────────────────────────┘
```

### **KeySignalsPanel Expanded**
```
┌──────────────────────────────────────────┐
│ 🚨 Key Signals                           │
├──────────────────────────────────────────┤
│ ┌────────────────────────────────────┐   │
│ │ 🔴 Conspiracy language detected 95%│   │
│ │ Contains conspiracy theory patterns │   │
│ │ Detection confidence: 95%          │   │
│ └────────────────────────────────────┘   │
│ ┌────────────────────────────────────┐   │
│ │ 🔴 No credible sources 88%         │   │
│ │ No mainstream outlets verify claim │   │
│ │ Detection confidence: 88%          │   │
│ └────────────────────────────────────┘   │
│                                           │
│ High Risk: 2 | Warnings: 2 | Avg: 86%   │
└──────────────────────────────────────────┘
```

---

## 🌐 Navigation Visual

### **Sidebar Navigation**
```
┌──────────────────┐
│ TL               │  ← Logo badge with gradient
│ TruthLens        │
│ AI Fact Check    │
├──────────────────┤
│ 🏠 Dashboard     │  ← Normal
│ 🔍 Analyze    ✓  │  ← Active (highlighted)
│ 📋 Sessions  [3] │  ← Badge
│ 📈 Analytics     │
│ ⚙️ Settings      │
├──────────────────┤
│ 🔐 User          │  ← Profile card
│ Settings         │
│ Logout           │
└──────────────────┘
```

---

## 📈 Charts Preview (Analytics Page)

### **Trend Line Chart**
```
100 │         ┏━┓
 80 │    ┏━━━┛ └━┓
 60 │ ┏━┛         └━━━┓
 40 │┏┛                └━┓
 20 │
  0 └─────────────────────
    Mon Tue Wed Thu Fri Sat Sun

Legend: ─ Real  ─ Fake  ─ Rumor
```

### **Pie Chart Distribution**
```
      Real 45%
        ▭▭▭
    ▭▭▭▭▭▭▭▭
  ▭▭▭▭▭▭▭▭▭▭▭▭
 ▭ Fake 28%  Rumor ▭
 ▭ Unknown 6% 21% ▭
  ▭▭▭▭▭▭▭▭▭▭▭▭
    ▭▭▭▭▭▭▭▭
        ▭▭▭
```

---

## 🎯 Key Performance Features

✅ **Smooth Animations**: 60fps transitions  
✅ **Responsive Design**: Mobile to desktop  
✅ **Accessible**: Keyboard navigation  
✅ **Fast Loading**: Optimized components  
✅ **Dark Theme**: Easy on the eyes  
✅ **High Contrast**: WCAG compliant colors  

---

**Dashboard Version:** 1.0.0  
**Last Updated:** 17 March 2026  
**Status:** ✨ Production Ready
