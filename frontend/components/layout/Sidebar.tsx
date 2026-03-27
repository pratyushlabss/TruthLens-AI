'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  BarChart3, 
  History, 
  Settings, 
  Home,
  TrendingUp
} from 'lucide-react';
import { COLORS } from '@/lib/theme';

interface NavItem {
  label: string;
  icon: React.ReactNode;
  href: string;
  badge?: number;
}

const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems: NavItem[] = [
    { label: 'Dashboard', icon: <Home size={20} />, href: '/dashboard' },
    { label: 'Sessions', icon: <History size={20} />, href: '/sessions', badge: 0 },
    { label: 'Analytics', icon: <TrendingUp size={20} />, href: '/analytics' },
    { label: 'Settings', icon: <Settings size={20} />, href: '/settings' },
  ];

  const isActive = (href: string) => pathname === href || pathname.startsWith(href);

  return (
    <div
      className={`fixed left-0 top-0 h-screen w-64 border-r transition-all duration-300 flex flex-col`}
      style={{
        backgroundColor: COLORS.bg.primary,
        borderColor: COLORS.border.light,
      }}
    >
      {/* Logo Section */}
      <div className="p-6 border-b" style={{ borderColor: COLORS.border.light }}>
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg"
            style={{
              background: COLORS.gradient.neon,
              color: COLORS.bg.primary,
            }}
          >
            TL
          </div>
          <div>
            <h2 style={{ color: COLORS.text.primary }} className="font-bold text-lg">
              TruthLens
            </h2>
            <p style={{ color: COLORS.text.tertiary }} className="text-xs">
              AI Fact Check
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            <div
              className={`
                relative flex items-center gap-3 px-4 py-3 rounded-lg
                transition-all duration-200 cursor-pointer group
                ${isActive(item.href) ? 'border' : ''}
              `}
              style={{
                backgroundColor: isActive(item.href) ? COLORS.bg.tertiary : 'transparent',
                color: isActive(item.href) ? COLORS.verdict.real : COLORS.text.secondary,
                borderColor: isActive(item.href) ? COLORS.verdict.real : 'transparent',
              }}
            >
              {/* Glow effect for active item */}
              {isActive(item.href) && (
                <div
                  className="absolute inset-0 rounded-lg blur opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{ background: `${COLORS.verdict.real}40` }}
                />
              )}
              
              <span className="relative z-10">{item.icon}</span>
              <span className="relative z-10 font-medium">{item.label}</span>
              
              {item.badge !== undefined && item.badge > 0 && (
                <span
                  className="ml-auto text-xs font-bold px-2 py-1 rounded"
                  style={{
                    backgroundColor: COLORS.verdict.real,
                    color: COLORS.bg.primary,
                  }}
                >
                  {item.badge}
                </span>
              )}
            </div>
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t" style={{ borderColor: COLORS.border.light }}>
        <p style={{ color: COLORS.text.tertiary }} className="text-xs text-center">
          v1.0.0
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
