# TruthLens - Start Here! 🚀

**Welcome!** You have a complete, production-ready AI Misinformation Dashboard.

---

## ⚡ Get Started in 60 Seconds

### 1. Install Dependencies
```bash
cd /Users/pratyush/ai\ truthlens/frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Open in Browser
Visit **http://localhost:3000** 🎉

You should see the TruthLens dashboard with a working UI!

---

## 📁 What's Included

✅ **Complete Frontend App** - Fully functional React/Next.js app  
✅ **Dark Theme** - Professional glassmorphism design  
✅ **Responsive Design** - Works on mobile, tablet, desktop  
✅ **7 Documentation Files** - Complete guides  
✅ **Docker Ready** - Deploy in one command  
✅ **TypeScript** - Type-safe code  

---

## 🎯 What to Do Next

### Option A: Explore the UI
1. Run `npm run dev`
2. Click "Analyze Now" button
3. Watch the processing state
4. See the results dashboard

### Option B: Customize
1. Edit `app/page.tsx` to modify UI
2. Update colors in `tailwind.config.ts`
3. Add components in `components/`

### Option C: Integrate Backend
1. Update `services/api.ts`
2. Set `NEXT_PUBLIC_API_URL` in `.env.local`
3. Connect to your Python backend

### Option D: Deploy
1. See `SETUP.md` for deployment options
2. Vercel: `npm install -g vercel && vercel deploy`
3. Docker: `docker-compose up -d`

---

## 📚 Documentation Guide

| File | Use This When... |
|------|-----------------|
| **README.md** | You want to get started |
| **QUICK_REFERENCE.md** | You need quick answers |
| **SETUP.md** | You want to deploy |
| **STYLE_GUIDE.md** | You're customizing styles |
| **PROJECT_INDEX.md** | You want all the details |
| **DELIVERY_SUMMARY.md** | You want an overview |

---

## 🛠️ Common Commands

```bash
# Development
npm run dev              # Start dev server

# Building
npm run build            # Create production build
npm start                # Run production server

# Quality
npm run lint             # Check code quality
npm run type-check       # Check TypeScript

# Docker
docker-compose up -d     # Start in Docker
docker-compose logs -f   # View logs
docker-compose down      # Stop Docker
```

---

## 🎨 Quick Customization

### Change Colors
Edit `tailwind.config.ts`:
```typescript
colors: {
  primary: { 500: "#6b88ff" },  // Change this
  secondary: { 500: "#a855f7" }  // Or this
}
```

### Change Theme
The app uses dark mode by default. To switch:
Edit `app/layout.tsx` - change `className="dark"`

### Add Your Logo
Replace "TruthLens" in `app/page.tsx` with your logo:
```tsx
<h1>Your Company Name</h1>
```

---

## 🔗 Backend Integration

### 1. Update API URL
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://your-backend:5000
```

### 2. Implement API Methods
Edit `services/api.ts` to call your backend:
```typescript
async analyzeText(text: string) {
  // Call your backend
}
```

### 3. Test Connection
Check browser console for API calls

---

## 📱 Responsive Breakpoints

The app automatically adapts:
- **Mobile**: < 768px (hamburger sidebar)
- **Tablet**: 768px (2-column layout)
- **Desktop**: 1024px (full layout)

---

## ⚠️ Common Issues

### Port Already in Use
```bash
npm run dev -- -p 3001  # Use different port
```

### Module Not Found
```bash
rm -rf node_modules package-lock.json
npm install
```

### Build Fails
```bash
npm run type-check  # Check for TypeScript errors
npm run lint        # Check for linting issues
```

---

## 🚀 Deployment Quick Links

### Vercel (Easiest)
```bash
npm i -g vercel && vercel deploy
```

### Docker
```bash
docker-compose up -d
```

### Node.js Server
```bash
npm run build && npm start
```

See `SETUP.md` for detailed instructions.

---

## 📊 Project Structure

```
frontend/
├── app/          ← Main application
├── components/   ← React components
├── services/     ← API client
├── types/        ← TypeScript interfaces
├── Docs/         ← 7 Documentation files
└── Config/       ← Setup files
```

---

## ✅ Next Steps

- [ ] Run `npm install`
- [ ] Run `npm run dev`
- [ ] Explore the UI
- [ ] Read `SETUP.md` for deployment
- [ ] Integrate with your backend
- [ ] Deploy to production

---

## 🎓 Learning Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org/)

---

## 💡 Pro Tips

1. **Hot Reload**: Changes auto-reload in dev mode
2. **TypeScript**: Use strict mode - it catches bugs!
3. **Tailwind**: Use existing classes - no custom CSS needed
4. **Components**: Keep components small and reusable

---

## 🎉 You're All Set!

```bash
npm install && npm run dev
```

**Open http://localhost:3000** and start exploring! 🚀

---

**Questions?** Check the relevant documentation file or reach out.

**Built with ❤️ for truth and transparency**
