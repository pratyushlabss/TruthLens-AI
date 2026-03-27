'use client';

import React from 'react';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

interface ToggleTabsProps {
  activeView: 'dashboard' | 'analytics';
  onViewChange: (view: 'dashboard' | 'analytics') => void;
}

export default function ToggleTabs({ activeView, onViewChange }: ToggleTabsProps) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'analytics', label: 'Analytics', icon: '🔥' },
  ] as const;

  return (
    <div
      className="sticky top-0 z-40 backdrop-blur-xl border-b transition-all duration-300"
      style={{
        backgroundColor: `${COLORS.bg.primary}E6`,
        borderColor: COLORS.border.light,
      }}
    >
      <div className="px-8 py-4 flex items-center gap-2">
        <div className="flex gap-2 bg-gradient-to-r from-transparent to-transparent rounded-xl p-1"
          style={{
            backgroundColor: `${COLORS.bg.secondary}40`,
            border: `1px solid ${COLORS.border.light}`,
          }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onViewChange(tab.id)}
              className={`
                px-6 py-2 rounded-lg font-semibold
                transition-all duration-300
                flex items-center gap-2
                whitespace-nowrap
              `}
              style={{
                backgroundColor: activeView === tab.id
                  ? `${COLORS.verdict.neutral}20`
                  : 'transparent',
                color: activeView === tab.id
                  ? COLORS.verdict.neutral
                  : COLORS.text.secondary,
                border: activeView === tab.id
                  ? `1px solid ${COLORS.verdict.neutral}40`
                  : `1px solid transparent`,
              }}
            >
              <span className="text-lg">{tab.icon}</span>
              <span className="text-sm md:text-base">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Divider */}
        <div
          className="ml-4 h-6 w-px"
          style={{ backgroundColor: COLORS.border.light }}
        />

        {/* Status Indicator */}
        <div className="ml-4 flex items-center gap-2">
          <div
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ backgroundColor: COLORS.verdict.real }}
          />
          <span
            style={{ color: COLORS.text.tertiary }}
            className="text-xs"
          >
            Live
          </span>
        </div>
      </div>
    </div>
  );
}
