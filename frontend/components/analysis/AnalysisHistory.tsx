'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/lib/auth';
import { COLORS } from '@/lib/theme';

interface AnalysisHistory {
  id: string;
  user_id: string;
  text_input: string | null;
  url_input?: string | null;
  image_input?: string | null;
  verdict: string;
  confidence_score: number;
  detailed_analysis: Record<string, any>;
  created_at: string;
}

export default function AnalysisHistory() {
  const { user } = useAuth();
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!user?.id) return;

      try {
        // History is loaded from context in real-time
        // No need to fetch from backend
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch analysis history:', err);
        setError('Failed to load history');
        setLoading(false);
      }
    };

    fetchHistory();
  }, [user?.id]);

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2" 
             style={{ borderColor: COLORS.verdict.real }}></div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-8">
        <p style={{ color: COLORS.text.secondary }}>No analysis history yet. Start by analyzing a claim!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 style={{ color: COLORS.text.primary }} className="text-xl font-semibold mb-4">
        Recent Analyses
      </h2>

      {history.map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.05 }}
          className="p-4 rounded-xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p style={{ color: COLORS.text.primary }} className="font-medium text-sm truncate">
                {item.text_input || item.url_input || 'Image Analysis'}
              </p>
              <div className="flex items-center gap-3 mt-2">
                <span
                  className="px-2 py-1 rounded text-xs font-semibold"
                  style={{
                    backgroundColor:
                      item.verdict === 'TRUE'
                        ? `${COLORS.verdict.real}20`
                        : item.verdict === 'FALSE'
                        ? `${COLORS.verdict.fake}20`
                        : `${COLORS.verdict.rumor}20`,
                    color:
                      item.verdict === 'TRUE'
                        ? COLORS.verdict.real
                        : item.verdict === 'FALSE'
                        ? COLORS.verdict.fake
                        : COLORS.verdict.rumor,
                  }}
                >
                  {item.verdict}
                </span>
                <span style={{ color: COLORS.text.secondary }} className="text-xs">
                  {Math.round(item.confidence_score * 100)}% confidence
                </span>
              </div>
            </div>
            <span style={{ color: COLORS.text.tertiary }} className="text-xs ml-4 whitespace-nowrap">
              {new Date(item.created_at).toLocaleDateString()}
            </span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
