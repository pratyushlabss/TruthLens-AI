# TruthLens AI Dashboard - Quick Start Guide

## 🚀 Getting Started

### **1. View the Dashboard**
```bash
cd "/Users/pratyush/ai truthlens/frontend"
npm run dev
```
Open: `http://localhost:3000/dashboard`

### **2. File Structure**
```
frontend/
├── lib/theme.ts                    # Color & styling constants
├── components/
│   ├── layout/                     # Navigation & layout
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Layout.tsx
│   ├── analysis/                   # Analysis panels
│   │   ├── VerdictCard.tsx
│   │   ├── ModelBreakdown.tsx
│   │   ├── KeySignalsPanel.tsx
│   │   ├── EvidenceSourcesPanel.tsx
│   │   ├── ClaimBreakdownPanel.tsx
│   │   └── PropagationAnalysisPanel.tsx
│   └── input/
│       └── AnalysisInput.tsx
└── app/
    ├── dashboard/page.tsx          # Main dashboard
    ├── analytics/page.tsx          # Analytics page
    └── layout.tsx                  # App layout
```

---

## 🎨 Using the Theme System

### **Import Colors**
```tsx
import { COLORS, GLASS_EFFECT, SHADOWS } from '@/lib/theme';

// Use in components
<div style={{ 
  backgroundColor: COLORS.bg.primary,
  color: COLORS.text.primary,
  border: `1px solid ${COLORS.border.light}`
}}>
  Content
</div>
```

### **Available Color Groups**
```typescript
COLORS.bg          // Background colors
COLORS.verdict     // Verdict-specific colors (real/fake/rumor/neutral)
COLORS.data        // Data visualization colors
COLORS.text        // Text colors by emphasis
COLORS.border      // Border colors with opacity
COLORS.gradient    // Pre-made gradients
```

### **Effect Classes**
```tsx
// Glassmorphism
className={GLASS_EFFECT.light}    // Light blur
className={GLASS_EFFECT.medium}   // Medium blur
className={GLASS_EFFECT.dark}     // Strong blur

// Shadow/Glow
className={SHADOWS.glow}          // Default green glow
className={SHADOWS.glow_red}      // Red glow for fake
className={SHADOWS.glow_amber}    // Amber glow for rumor
```

---

## 📝 Component Usage Examples

### **VerdictCard**
```tsx
import VerdictCard from '@/components/analysis/VerdictCard';

export default function MyComponent() {
  return (
    <VerdictCard
      verdict="FAKE"           // "TRUE" | "FALSE" | "RUMOR" | "UNKNOWN"
      confidence={85}          // 0-100
      loading={false}          // Optional, default false
    />
  );
}
```

**Props:**
- `verdict`: The verdict string
- `confidence`: Confidence percentage (0-100)
- `loading`: Show loading state

---

### **ModelBreakdown**
```tsx
import ModelBreakdown from '@/components/analysis/ModelBreakdown';

export default function MyComponent() {
  const customModels = [
    {
      name: 'Custom Model',
      icon: <Icon />,
      score: 88,
      weight: 0.5,
      description: 'Model description',
    },
    // ... more models
  ];

  return <ModelBreakdown models={customModels} />;
}
```

**Default Models:**
- RoBERTa NLP (60% weight)
- Evidence Engine (25% weight)
- Propagation Risk (15% weight)

---

### **KeySignalsPanel**
```tsx
import KeySignalsPanel from '@/components/analysis/KeySignalsPanel';

const signals = [
  {
    id: '1',
    label: 'Conspiracy language detected',
    category: 'danger',  // 'danger' | 'warning' | 'info'
    explanation: 'Contains conspiracy patterns...',
    confidence: 95,
  },
  // ... more signals
];

export default function MyComponent() {
  return <KeySignalsPanel signals={signals} />;
}
```

---

### **EvidenceSourcesPanel**
```tsx
import EvidenceSourcesPanel from '@/components/analysis/EvidenceSourcesPanel';

const sources = [
  {
    id: '1',
    name: 'Reuters',
    url: 'https://reuters.com/article',
    credibility: 'High',  // 'High' | 'Medium' | 'Low'
    stance: 'supports',   // 'supports' | 'contradicts' | 'neutral'
    relevanceScore: 98,
    snippet: 'Quote from article...',
    date: '2 hours ago',
  },
  // ... more sources
];

export default function MyComponent() {
  return <EvidenceSourcesPanel sources={sources} />;
}
```

---

### **ClaimBreakdownPanel**
```tsx
import ClaimBreakdownPanel from '@/components/analysis/ClaimBreakdownPanel';

const claims = [
  {
    id: '1',
    text: 'Water boils at 100 degrees',
    verdict: 'TRUE',        // 'TRUE' | 'FALSE' | 'UNKNOWN'
    confidence: 99,
    reasoning: 'Universal scientific fact...',
  },
  // ... more claims
];

export default function MyComponent() {
  return <ClaimBreakdownPanel claims={claims} />;
}
```

---

### **PropagationAnalysisPanel**
```tsx
import PropagationAnalysisPanel from '@/components/analysis/PropagationAnalysisPanel';

const propagationData = {
  tweetVelocity: 1250,
  clusterSize: 847,
  reshareFactror: 3.2,
  estimatedReach: 2400000,
  riskLevel: 'MEDIUM',     // 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  viralScore: 67,
};

export default function MyComponent() {
  return <PropagationAnalysisPanel data={propagationData} />;
}
```

---

### **AnalysisInput**
```tsx
import AnalysisInput from '@/components/input/AnalysisInput';

export default function MyComponent() {
  const handleAnalyze = (text: string) => {
    console.log('Analyzing:', text);
    // Call your API endpoint
  };

  return (
    <AnalysisInput
      onAnalyze={handleAnalyze}
      loading={false}
    />
  );
}
```

---

### **Layout Wrapper**
```tsx
import Layout from '@/components/layout/Layout';

export default function MyPage() {
  return (
    <Layout showHeader={true}>
      <div className="p-8">
        {/* Your content here */}
      </div>
    </Layout>
  );
}
```

**Props:**
- `children`: Page content
- `showHeader`: Show/hide header `(default: true)`

---

## 🎬 Animation Examples

### **Add Entry Animation**
```tsx
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>
  Content
</motion.div>
```

### **Stagger Children**
```tsx
<motion.div>
  {items.map((item, index) => (
    <motion.div
      key={item.id}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      {item.name}
    </motion.div>
  ))}
</motion.div>
```

### **Scale on Hover**
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

---

## 🎨 Styling Custom Components

### **Using Theme Colors**
```tsx
<div
  style={{
    backgroundColor: COLORS.bg.secondary,
    borderColor: COLORS.border.light,
    color: COLORS.text.primary,
  }}
  className="p-4 rounded-lg border"
>
  Content
</div>
```

### **Creating Verdict-Colored Elements**
```tsx
const verdictColors = {
  REAL: COLORS.verdict.real,
  FAKE: COLORS.verdict.fake,
  RUMOR: COLORS.verdict.rumor,
};

<div
  style={{
    backgroundColor: `${verdictColors[verdict]}15`,  // With opacity
    borderColor: verdictColors[verdict],
    color: verdictColors[verdict],
  }}
>
  {verdict}
</div>
```

### **Glassmorphism Cards**
```tsx
<div
  className={`p-6 rounded-2xl border ${GLASS_EFFECT.dark}`}
  style={{
    backgroundColor: `${COLORS.bg.secondary}80`,
    borderColor: COLORS.border.light,
  }}
>
  Card content
</div>
```

---

## 🔧 API Integration

### **Mock Data (Currently Used)**
All components include default mock data. To integrate with real API:

1. **Remove `defaultData`** from component props
2. **Fetch data** from your backend
3. **Pass as props** to components

### **Example Integration**
```tsx
'use client';

import { useState, useEffect } from 'react';
import VerdictCard from '@/components/analysis/VerdictCard';

export default function Dashboard() {
  const [verdict, setVerdict] = useState('UNKNOWN');
  const [confidence, setConfidence] = useState(0);
  const [loading, setLoading] = useState(false);

  const analyzeClahm = async (text: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
      const data = await response.json();
      setVerdict(data.verdict);
      setConfidence(data.confidence);
    } finally {
      setLoading(false);
    }
  };

  return (
    <VerdictCard
      verdict={verdict}
      confidence={confidence}
      loading={loading}
    />
  );
}
```

---

## 📊 Response Format Mapping

Map your API response to component props:

```typescript
// API Response
{
  verdict: "FAKE",                    // → VerdictCard.verdict
  confidence: 85,                     // → VerdictCard.confidence
  models: [
    { name: "RoBERTa", score: 92, ... },  // → ModelBreakdown.models
  ],
  key_signals: [                      // → KeySignalsPanel.signals
    { id: "1", label: "...", ... }
  ],
  sources: [                          // → EvidenceSourcesPanel.sources
    { id: "1", name: "Reuters", ... }
  ],
  claims: [                           // → ClaimBreakdownPanel.claims
    { id: "1", text: "...", ... }
  ],
  propagation: {                      // → PropagationAnalysisPanel.data
    tweetVelocity: 1250,
    ...
  }
}
```

---

## 🐛 Troubleshooting

### **Components Not Rendering**
- Ensure all required props are passed
- Check console for TypeScript errors
- Verify mock data structure matches interfaces

### **Styling Issues**
- Confirm `lib/theme.ts` is imported correctly
- Check Tailwind CSS configuration
- Verify class names are spelled correctly

### **Animation Not Working**
- Import `motion` from `framer-motion`
- Ensure parent has proper layout context
- Check animation duration vs transition

### **Data Not Updating**
- Add `.json()` parsing after fetch
- Verify API endpoint returns expected structure
- Log response to check data shape

---

## 📚 Additional Resources

### **Component Props**
All components have TypeScript interfaces defined in source files

### **Responsive Breakpoints**
```
Mobile:  < 640px     (sm)
Tablet:  640-1024px  (md/lg)
Desktop: > 1024px    (lg/xl)
```

### **Color Accessibility**
All colors meet WCAG AA contrast ratios on dark backgrounds

---

## ✅ Deployment Checklist

- [ ] Replace mock data with real API calls
- [ ] Test all responsive breakpoints
- [ ] Verify keyboard navigation
- [ ] Test loading states
- [ ] Test error states
- [ ] Optimize images/assets
- [ ] Setup error logging
- [ ] Configure API endpoints
- [ ] Test on production domain

---

## 🎯 Next Steps

1. **Connect to Backend**: Integrate with `/api/analyze` endpoint
2. **Add Sessions Storage**: Save/load previous analyses
3. **Implement Sharing**: Export or share analysis results
4. **Add Settings**: User preferences, API keys, etc.
5. **Deploy**: To Vercel or your hosting platform

---

**Happy Building! 🚀**

For questions about specific components, check their source files in `frontend/components/`.
