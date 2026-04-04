'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import Layout from '@/components/layout/Layout';
import { COLORS } from '@/lib/theme';
import { useAuth } from '@/lib/auth';
import DashboardView from '@/components/dashboard/DashboardView';
import AnalyticsView from '@/components/dashboard/AnalyticsView';
import ToggleTabs from '@/components/dashboard/ToggleTabs';

interface Source {
  title: string;
  url: string;
  credibility: string;
  summary: string;
  supports?: string;
}

interface AnalysisResult {
  verdict: string;
  confidence: number;
  explanation: string;
  sources: Source[];
  signals: string[];
  reasoning: string;
  summary?: string;
  evidence_trace?: Array<{
    source: string;
    impact: string;
    reason: string;
    credibility: number;
  }>;
  metrics?: {
    support_score: number;
    refute_score: number;
    agreement_score: number;
    source_count: number;
  };
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [view, setView] = useState<'dashboard' | 'analytics'>('dashboard');
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisResult[]>([]);

  // Load analysis history
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetch('/api/history', {
          headers: user?.id ? { 'X-User-ID': user.id } : {},
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          console.warn('Failed to load history:', response.status, data);
          // Don't throw - allow dashboard to work without history
          return;
        }
        
        // Take the last 10 analyses
        const historyArray = Array.isArray(data) ? data : (data.history || []);
        setRecentAnalyses(historyArray.slice(-10).reverse());
        console.log('History loaded successfully:', historyArray.length, 'items');
      } catch (error: any) {
        console.error('Failed to load history:', error.message || error);
        // Don't throw - allow dashboard to work without history
      }
    };

    if (user?.id) {
      loadHistory();
    }
  }, [user?.id]);

  const handleAnalysisComplete = (result: AnalysisResult) => {
    // Add to recent analyses
    setRecentAnalyses((prev) => [result, ...prev].slice(0, 10));
  };

  return (
    <Layout>
      {/* Toggle Navigation */}
      <ToggleTabs activeView={view} onViewChange={setView} />

      {/* View Switcher */}
      <motion.div
        key={view}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {view === 'dashboard' ? (
          <DashboardView onAnalysisComplete={handleAnalysisComplete} />
        ) : (
          <AnalyticsView />
        )}
      </motion.div>
    </Layout>
  );
}
