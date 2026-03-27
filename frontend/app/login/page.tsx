'use client';

import React, { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuth } from '@/lib/auth';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!email || !password) {
        setError('Email and password are required');
        setLoading(false);
        return;
      }
      
      await login(email, password);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ backgroundColor: COLORS.bg.primary }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        {/* Brand */}
        <div className="text-center mb-8">
          <div
            className="flex items-center justify-center gap-2 mb-4"
            style={{ justifyContent: 'center' }}
          >
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center font-bold text-xl"
              style={{
                background: COLORS.gradient.neon,
                color: COLORS.bg.primary,
              }}
            >
              TL
            </div>
            <h1 style={{ color: COLORS.text.primary }} className="text-3xl font-bold">
              TruthLens
            </h1>
          </div>
          <p style={{ color: COLORS.text.secondary }} className="text-sm">
            AI-powered fact-checking platform
          </p>
        </div>

        {/* Login Form */}
        <div
          className="p-8 rounded-2xl border"
          style={{
            ...GLASS_EFFECT,
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-2xl font-bold mb-6">
            Login
          </h2>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-3 rounded-lg mb-4"
              style={{
                backgroundColor: `${COLORS.verdict.fake}20`,
                borderColor: COLORS.verdict.fake,
                border: '1px solid',
              }}
            >
              <p style={{ color: COLORS.verdict.fake }} className="text-sm font-medium">
                {error}
              </p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label
                style={{ color: COLORS.text.secondary }}
                className="block text-sm font-medium mb-2"
              >
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-2.5 rounded-lg border outline-none transition-all"
                style={{
                  backgroundColor: COLORS.bg.tertiary,
                  borderColor: COLORS.border.medium,
                  color: COLORS.text.primary,
                }}
                required
              />
            </div>

            {/* Password */}
            <div>
              <label
                style={{ color: COLORS.text.secondary }}
                className="block text-sm font-medium mb-2"
              >
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-lg border outline-none transition-all"
                style={{
                  backgroundColor: COLORS.bg.tertiary,
                  borderColor: COLORS.border.medium,
                  color: COLORS.text.primary,
                }}
                required
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg font-semibold transition-all"
              style={{
                background: COLORS.gradient.neon,
                color: COLORS.bg.primary,
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          {/* Signup Link */}
          <p style={{ color: COLORS.text.secondary }} className="text-center mt-6 text-sm">
            Don&apos;t have an account?{' '}
            <Link
              href="/signup"
              style={{ color: COLORS.verdict.real }}
              className="font-semibold hover:underline"
            >
              Sign up
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
