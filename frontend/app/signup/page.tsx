'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuth } from '@/lib/auth';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

export default function SignupPage() {
  const { signup } = useAuth();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Client-side validation
    if (!email || !username || !password || !confirmPassword) {
      setError('All fields are required');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await signup(email, password, username);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Signup failed. Please try again.';
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
            Join thousands fact-checking claims
          </p>
        </div>

        {/* Signup Form */}
        <div
          className="p-8 rounded-2xl border"
          style={{
            ...GLASS_EFFECT,
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-2xl font-bold mb-6">
            Create Account
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
            {/* Username */}
            <div>
              <label
                style={{ color: COLORS.text.secondary }}
                className="block text-sm font-medium mb-2"
              >
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="your_username"
                className="w-full px-4 py-2.5 rounded-lg border outline-none transition-all"
                style={{
                  backgroundColor: COLORS.bg.tertiary,
                  borderColor: COLORS.border.medium,
                  color: COLORS.text.primary,
                }}
                required
              />
            </div>

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

            {/* Confirm Password */}
            <div>
              <label
                style={{ color: COLORS.text.secondary }}
                className="block text-sm font-medium mb-2"
              >
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
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
              {loading ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          {/* Login Link */}
          <p style={{ color: COLORS.text.secondary }} className="text-center mt-6 text-sm">
            Already have an account?{' '}
            <Link
              href="/login"
              style={{ color: COLORS.verdict.real }}
              className="font-semibold hover:underline"
            >
              Login
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
