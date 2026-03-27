'use client';

import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { COLORS } from '@/lib/theme';

interface LayoutProps {
  children: ReactNode;
  showHeader?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ children, showHeader = true }) => {
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ backgroundColor: COLORS.bg.primary }}
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col ml-64">
        {/* Header */}
        {showHeader && <Header />}

        {/* Content Area */}
        <div
          className={`
            flex-1 overflow-y-auto
            ${showHeader ? 'mt-20' : 'mt-0'}
          `}
          style={{
            backgroundColor: COLORS.bg.primary,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
