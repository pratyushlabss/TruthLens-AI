# 🔐 TruthLens Auth - Quick Reference

## 🚀 Start Here

### 1. Ensure Backend is Running
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
# ✅ Should see: "Uvicorn running on http://0.0.0.0:8000"
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
# ✅ Should see: "▲ Next.js ... ready on http://localhost:3000"
```

### 3. Test Signup/Login
- Open http://localhost:3000
- Should redirect to /login
- Try signup or login

---

## 📚 API Reference

### Signup
```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "username": "user_username"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "abc-123",
    "email": "user@example.com",
    "username": "user_username",
    "created_at": "2026-03-17T..."
  }
}
```

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

### Get Current User
```bash
curl http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "user_id": "abc-123",
  "email": "user@example.com",
  "username": "user_username",
  "created_at": "2026-03-17T..."
}
```

### Logout
```bash
curl -X POST http://localhost:3000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔄 Frontend Usage

### In a Component
```typescript
import { useAuth } from '@/lib/auth';

export default function MyComponent() {
  const { user, token, loading, logout } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Not logged in</div>;
  
  return (
    <div>
      <p>Hello, {user.username}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Login Function
```typescript
const { login } = useAuth();

await login('user@example.com', 'password123');
// ✅ Automatically redirects to /dashboard
```

### Signup Function
```typescript
const { signup } = useAuth();

await signup('user@example.com', 'password123', 'username');
// ✅ Automatically redirects to /dashboard
```

---

## 🔧 Key Files & Their Purpose

| File | Purpose |
|------|---------|
| `backend/utils/security.py` | Password hashing, JWT creation/validation |
| `backend/api/auth.py` | Signup/login/me endpoints |
| `backend/database/models.py` | User database model |
| `frontend/lib/auth.tsx` | Auth state management & persistence |
| `frontend/app/login/page.tsx` | Login UI |
| `frontend/app/signup/page.tsx` | Signup UI |
| `frontend/app/api/auth/*` | API proxies |

---

## 🐛 Debugging

### Check Backend Logs
```bash
tail -50 /tmp/backend.log
```

### Check Frontend Logs
```bash
tail -50 /tmp/frontend_dev.log
```

### Test Backend Directly
```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123","username":"testuser"}'

# Should return: access_token, token_type, user
```

### Test Token Validation
```bash
# Get a token from signup above, then:
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN_HERE"
# Should return user info (200)
# Or error (401)
```

---

## ⚡ Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| 401 Invalid credentials | Check email exists, password correct |
| 400 Email already registered | Use different email or reset DB |
| 500 Internal Server Error | Check backend logs: `tail -50 /tmp/backend.log` |
| Token not working | Ensure format: `Bearer <token>` with space |
| Frontend not connecting | Check NEXT_PUBLIC_API_URL in .env |
| Password not hashing | Backend must be running with new code |

---

## 🧪 Run Tests
```bash
python3 test_auth.py
```

Expected output:
```
✓ ALL TESTS PASSED!
  ✓ Signup with password hashing
  ✓ JWT token generation
  ✓ Login with verification
  ✓ Bearer token extraction from header
  ✓ User info retrieval with token
  ✓ Invalid token rejection
```

---

## 📝 Environment Requirements

```bash
# .env file must contain:
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
NEXT_PUBLIC_API_URL=http://localhost:8000
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## ✨ Security Checklist

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with expiration
- ✅ Bearer token in Authorization header
- ✅ CORS enabled only for frontend
- ✅ Generic error messages (no email enumeration)
- ✅ SQL injection prevented (SQLAlchemy ORM)
- ✅ XSS protection (React built-in)
- ✅ HTTPS ready (use in production!)

---

## 🚀 Production Deployment

1. **Update secrets:**
   ```bash
   SECRET_KEY=$(openssl rand -hex 32)
   JWT_SECRET=$(openssl rand -hex 32)
   ```

2. **Set environment:** `ENV=production`

3. **Use PostgreSQL:** Cloud DB (Supabase, Neon, AWS RDS)

4. **Enable HTTPS:** Use reverse proxy (Nginx, Cloudflare)

5. **Set correct CORS:** `CORS_ORIGINS=your-domain.com`

---

## 📞 Support

For issues:
1. Check logs: `tail -50 /tmp/backend.log`
2. Run tests: `python3 test_auth.py`
3. Check database: Verify PostgreSQL is running
4. Verify environment: Confirm `.env` is loaded

---

✅ **System is ready for use!**
