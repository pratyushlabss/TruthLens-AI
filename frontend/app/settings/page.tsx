'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Layout from '@/components/layout/Layout';
import { useAuth } from '@/lib/auth';
import { COLORS } from '@/lib/theme';

export default function SettingsPage() {
  const { user } = useAuth();
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      setMessage('Password must be at least 6 characters');
      return;
    }

    // TODO: Call API endpoint for password change
    setMessage('Password changed successfully');
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  return (
    <Layout>
      <div className="p-8 pb-12" style={{ backgroundColor: COLORS.bg.primary }}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          {/* Title */}
          <h1 style={{ color: COLORS.text.primary }} className="text-4xl font-bold mb-8">
            Settings
          </h1>

          {/* Account Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-2xl"
          >
            {/* Profile Info */}
            <div
              className="p-6 rounded-2xl border mb-6"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <h2 style={{ color: COLORS.text.primary }} className="text-xl font-semibold mb-4">
                Profile Information
              </h2>
              <div className="space-y-4">
                <div>
                  <label style={{ color: COLORS.text.secondary }} className="block text-sm mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={user?.username || ''}
                    disabled
                    className="w-full px-4 py-2 rounded-lg border"
                    style={{
                      backgroundColor: COLORS.bg.tertiary,
                      borderColor: COLORS.border.medium,
                      color: COLORS.text.tertiary,
                    }}
                  />
                </div>
                <div>
                  <label style={{ color: COLORS.text.secondary }} className="block text-sm mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full px-4 py-2 rounded-lg border"
                    style={{
                      backgroundColor: COLORS.bg.tertiary,
                      borderColor: COLORS.border.medium,
                      color: COLORS.text.tertiary,
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Change Password */}
            <div
              className="p-6 rounded-2xl border mb-6"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <h2 style={{ color: COLORS.text.primary }} className="text-xl font-semibold mb-4">
                Change Password
              </h2>
              <div className="space-y-4">
                <div>
                  <label style={{ color: COLORS.text.secondary }} className="block text-sm mb-2">
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-2 rounded-lg border outline-none"
                    style={{
                      backgroundColor: COLORS.bg.tertiary,
                      borderColor: COLORS.border.medium,
                      color: COLORS.text.primary,
                    }}
                  />
                </div>
                <div>
                  <label style={{ color: COLORS.text.secondary }} className="block text-sm mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-2 rounded-lg border outline-none"
                    style={{
                      backgroundColor: COLORS.bg.tertiary,
                      borderColor: COLORS.border.medium,
                      color: COLORS.text.primary,
                    }}
                  />
                </div>
                <div>
                  <label style={{ color: COLORS.text.secondary }} className="block text-sm mb-2">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-2 rounded-lg border outline-none"
                    style={{
                      backgroundColor: COLORS.bg.tertiary,
                      borderColor: COLORS.border.medium,
                      color: COLORS.text.primary,
                    }}
                  />
                </div>
                <button
                  onClick={handlePasswordChange}
                  className="w-full py-2.5 rounded-lg font-semibold transition-all"
                  style={{
                    background: COLORS.gradient.neon,
                    color: COLORS.bg.primary,
                  }}
                >
                  Update Password
                </button>
                {message && (
                  <p style={{ color: COLORS.verdict.real }} className="text-sm text-center">
                    {message}
                  </p>
                )}
              </div>
            </div>

            {/* Preferences */}
            <div
              className="p-6 rounded-2xl border"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <h2 style={{ color: COLORS.text.primary }} className="text-xl font-semibold mb-4">
                Preferences
              </h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label style={{ color: COLORS.text.secondary }}>Dark Mode</label>
                  <button
                    onClick={() => setDarkMode(!darkMode)}
                    className={`relative w-12 h-6 rounded-full transition-all ${darkMode ? 'bg-green-600' : 'bg-gray-400'}`}
                  >
                    <div
                      className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-transform ${
                        darkMode ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <div className="flex items-center justify-between border-t" style={{ borderColor: COLORS.border.medium }}>
                  <label style={{ color: COLORS.text.secondary }} className="pt-4">
                    Email Notifications
                  </label>
                  <button
                    onClick={() => setNotifications(!notifications)}
                    className={`relative w-12 h-6 rounded-full transition-all ${notifications ? 'bg-green-600' : 'bg-gray-400'}`}
                  >
                    <div
                      className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-transform ${
                        notifications ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </Layout>
  );
}
