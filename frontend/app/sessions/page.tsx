'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Layout from '@/components/layout/Layout';
import { useAnalysis } from '@/lib/analysis-context';
import { supabase } from '@/lib/supabase';
import { COLORS } from '@/lib/theme';
import Link from 'next/link';

export default function SessionsPage() {
  const { sessions, refreshAnalytics } = useAnalysis();
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  // Get session token and fetch analytics
  useEffect(() => {
    const getTokenAndFetch = async () => {
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession();
        if (session?.access_token) {
          setSessionToken(session.access_token);
          await refreshAnalytics(session.access_token);
        }
      } catch (error) {
        console.error('Error getting session:', error);
      }
    };
    getTokenAndFetch();
  }, [refreshAnalytics]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'TRUE':
        return COLORS.verdict.real;
      case 'FALSE':
        return COLORS.verdict.fake;
      case 'UNCERTAIN':
        return COLORS.verdict.rumor;
      default:
        return COLORS.text.secondary;
    }
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
          <h1 style={{ color: COLORS.text.primary }} className="text-4xl font-bold mb-3">
            📜 Analysis History
          </h1>
          <p style={{ color: COLORS.text.secondary }} className="mb-8">
            All claims you've analyzed in real-time mode
          </p>

          {!sessions || sessions.length === 0 ? (
            <div
              className="text-center py-12 rounded-2xl border"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <p style={{ color: COLORS.text.secondary }} className="mb-4">
                No analyses yet. Start by analyzing a claim!
              </p>
              <Link href="/dashboard">
                <button
                  className="px-6 py-2.5 rounded-lg font-semibold"
                  style={{
                    background: COLORS.gradient.neon,
                    color: COLORS.bg.primary,
                  }}
                >
                  Go to Dashboard
                </button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4 max-w-4xl">
              {sessions.map((session, idx) => (
                <motion.div
                  key={`${session.query_id}-${idx}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: idx * 0.05 }}
                  className="p-6 rounded-2xl border hover:border-opacity-100 transition-all"
                  style={{
                    backgroundColor: COLORS.bg.secondary,
                    borderColor: COLORS.border.light,
                  }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 style={{ color: COLORS.text.primary }} className="text-lg font-semibold mb-2">
                        {session.input_text}
                      </h3>
                      <div className="flex items-center gap-4 flex-wrap">
                        {/* Verdict Badge */}
                        <span
                          className="px-3 py-1 rounded-lg text-sm font-semibold"
                          style={{
                            backgroundColor: `${getVerdictColor(session.verdict)}20`,
                            color: getVerdictColor(session.verdict),
                          }}
                        >
                          {session.verdict}
                        </span>

                        {/* Confidence */}
                        <span style={{ color: COLORS.text.tertiary }} className="text-sm">
                          Confidence: <span style={{ color: COLORS.text.primary }} className="font-semibold">
                            {(session.confidence * 100).toFixed(0)}%
                          </span>
                        </span>

                        {/* Sources */}
                        <span style={{ color: COLORS.text.tertiary }} className="text-sm">
                          Sources: <span style={{ color: COLORS.text.primary }} className="font-semibold">
                            {session.source_count}
                          </span>
                        </span>

                        {/* Date */}
                        <span style={{ color: COLORS.text.tertiary }} className="text-sm">
                          {formatDate(session.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </Layout>
  );
}

