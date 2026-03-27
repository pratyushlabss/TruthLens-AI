'use client';

import React, { useState } from 'react';
import { Bell, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { COLORS } from '@/lib/theme';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <div
      className={`
        fixed top-0 left-64 right-0 h-20 border-b backdrop-blur-md
        flex items-center justify-between px-6 z-40
        transition-all duration-300
      `}
      style={{
        backgroundColor: `${COLORS.bg.primary}E6`,
        borderColor: COLORS.border.light,
      }}
    >
      {/* User email display */}
      <div>
        <p style={{ color: COLORS.text.secondary }} className="text-sm">
          Welcome back, <span style={{ color: COLORS.text.primary }} className="font-semibold">{user?.username || 'User'}</span>
        </p>
      </div>

      {/* Right Section - Notifications & Profile */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2.5 rounded-lg transition-all hover:scale-110"
            style={{
              backgroundColor: COLORS.bg.secondary,
              color: COLORS.text.secondary,
            }}
          >
            <Bell size={20} />
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div
              className="absolute right-0 mt-2 w-72 rounded-lg border p-4 shadow-lg"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <h3 style={{ color: COLORS.text.primary }} className="font-semibold mb-3">
                Notifications
              </h3>
              <div className="space-y-2">
                <p style={{ color: COLORS.text.secondary }} className="text-sm">
                  Welcome back! You have 0 new notifications.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Logout Button */}
        <button
          onClick={logout}
          className="p-2.5 rounded-lg transition-all hover:scale-110"
          style={{
            backgroundColor: COLORS.bg.secondary,
            color: COLORS.text.secondary,
          }}
          title="Logout"
        >
          <LogOut size={20} />
        </button>
      </div>
    </div>
  );
};

export default Header;

