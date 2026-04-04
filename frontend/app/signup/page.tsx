'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

export default function SignupPage() {
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

        {/* Message */}
        <div
          className="p-8 rounded-2xl border"
          style={{
            ...GLASS_EFFECT,
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-2xl font-bold mb-6">
            Use Test Credentials
          </h2>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-4 rounded-lg mb-6"
            style={{
              backgroundColor: `${COLORS.verdict.real}20`,
              borderColor: COLORS.verdict.real,
              border: '1px solid',
            }}
          >
            <p style={{ color: COLORS.verdict.real }} className="text-sm font-medium mb-3">
              ℹ️ Signup is disabled. Use test credentials to log in:
            </p>
            <div style={{ color: COLORS.text.secondary }} className="text-sm space-y-2">
              <p><strong>Email:</strong> test@truthlens.local</p>
              <p><strong>Password:</strong> password123</p>
              <p className="text-xs mt-3">Or use any credentials from our test users list.</p>
            </div>
          </motion.div>

          <Link
            href="/login"
            className="w-full py-3 rounded-lg font-semibold transition-all text-center block"
            style={{
              background: COLORS.gradient.neon,
              color: COLORS.bg.primary,
            }}
          >
            Back to Login
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
