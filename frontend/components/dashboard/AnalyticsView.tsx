'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';
import { useAnalysis } from '@/lib/analysis-context';

interface Source {
  title: string;
  url: string;
  credibility: string | number;
  summary: string;
  supports?: string;
  name?: string;
  stance?: string;
  snippet?: string;
  relevance?: number;
}

interface AnalysisData {
  verdict: string;
  confidence: number;
  sources: Source[];
  explanation?: string;
  signals?: string[];
  reasoning?: string;
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

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

export default function AnalyticsView() {
  // Get unified data from centralized context
  const { analyticsData, latestAnalysis } = useAnalysis();

  // Memoize verdict distribution chart data
  const verdictChartData = React.useMemo(() => {
    if (!analyticsData) return [];
    return [
      {
        name: 'True',
        value: analyticsData.verdict_distribution.TRUE,
        color: COLORS.verdict.real,
      },
      {
        name: 'False',
        value: analyticsData.verdict_distribution.FALSE,
        color: COLORS.verdict.fake,
      },
      {
        name: 'Uncertain',
        value: analyticsData.verdict_distribution.UNCERTAIN,
        color: COLORS.verdict.rumor,
      },
    ];
  }, [analyticsData]);

  // Memoize confidence distribution data
  const confidenceChartData = React.useMemo(() => {
    if (!analyticsData) return [];
    return [
      {
        name: 'High (≥80%)',
        value: analyticsData.confidence_distribution.high,
        color: COLORS.verdict.real,
      },
      {
        name: 'Medium (50-79%)',
        value: analyticsData.confidence_distribution.medium,
        color: COLORS.verdict.rumor,
      },
      {
        name: 'Low (<50%)',
        value: analyticsData.confidence_distribution.low,
        color: COLORS.verdict.fake,
      },
    ];
  }, [analyticsData]);

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="p-8 pb-12 space-y-8"
      style={{ backgroundColor: COLORS.bg.primary }}
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="mb-8">
        <h1
          style={{ color: COLORS.text.primary }}
          className="text-4xl font-bold mb-2"
        >
          📊 Analytics
        </h1>
        <p style={{ color: COLORS.text.secondary }} className="text-lg">
          Unified view of all claim analyses and metrics
        </p>
      </motion.div>

      {/* Key Metrics */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {/* Total Claims */}
        <motion.div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <p style={{ color: COLORS.text.secondary }} className="text-sm mb-2">
            Total Claims
          </p>
          <p style={{ color: COLORS.text.primary }} className="text-3xl font-bold">
            {analyticsData?.total_claims || 0}
          </p>
        </motion.div>

        {/* Accuracy Rate */}
        <motion.div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <p style={{ color: COLORS.text.secondary }} className="text-sm mb-2">
            Accuracy Rate
          </p>
          <p style={{ color: COLORS.verdict.real }} className="text-3xl font-bold">
            {analyticsData?.accuracy_rate?.toFixed(1) || '0'}%
          </p>
        </motion.div>

        {/* Average Response Time */}
        <motion.div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <p style={{ color: COLORS.text.secondary }} className="text-sm mb-2">
            Avg Response Time
          </p>
          <p style={{ color: COLORS.text.primary }} className="text-3xl font-bold">
            {analyticsData?.avg_response_time?.toFixed(1) || '0'}s
          </p>
        </motion.div>

        {/* Average Confidence */}
        <motion.div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <p style={{ color: COLORS.text.secondary }} className="text-sm mb-2">
            Avg Confidence
          </p>
          <p style={{ color: COLORS.text.primary }} className="text-3xl font-bold">
            {((analyticsData?.avg_confidence || 0) * 100).toFixed(0)}%
          </p>
        </motion.div>
      </motion.div>

      {/* Charts Section */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Verdict Distribution */}
        <motion.div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
            Verdict Distribution
          </h2>
          {verdictChartData.length > 0 && verdictChartData.some((d) => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={verdictChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {verdictChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.bg.tertiary,
                    border: `1px solid ${COLORS.border.light}`,
                    borderRadius: '8px',
                    color: COLORS.text.primary,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: COLORS.text.tertiary }} className="text-center py-12">
              No data yet. Analyze claims to see distribution.
            </p>
          )}
        </motion.div>

        {/* Confidence Distribution */}
        <motion.div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
            Confidence Distribution
          </h2>
          {confidenceChartData.length > 0 && confidenceChartData.some((d) => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={confidenceChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border.light} />
                <XAxis
                  dataKey="name"
                  tick={{ fill: COLORS.text.secondary, fontSize: 12 }}
                  axisLine={{ stroke: COLORS.border.light }}
                />
                <YAxis
                  tick={{ fill: COLORS.text.secondary, fontSize: 12 }}
                  axisLine={{ stroke: COLORS.border.light }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.bg.tertiary,
                    border: `1px solid ${COLORS.border.light}`,
                    borderRadius: '8px',
                    color: COLORS.text.primary,
                  }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {confidenceChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: COLORS.text.tertiary }} className="text-center py-12">
              No data yet. Analyze claims to see distribution.
            </p>
          )}
        </motion.div>
      </motion.div>

      {/* Recent Analysis - PRIMARY COMPONENT */}
      <motion.div
        variants={itemVariants}
        className="p-6 rounded-2xl border"
        style={{
          backgroundColor: COLORS.bg.secondary,
          borderColor: COLORS.border.light,
        }}
      >
        <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
          📋 Recent Analyses
        </h2>
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {analyticsData?.recent_analyses && analyticsData.recent_analyses.length > 0 ? (
            analyticsData.recent_analyses.map((analysis, index) => (
              <motion.div
                key={`analysis-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-lg border"
                style={{
                  backgroundColor: COLORS.bg.tertiary,
                  borderColor: COLORS.border.medium,
                }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p style={{ color: COLORS.text.primary }} className="font-semibold mb-2">
                      {analysis.claim || 'Untitled Claim'}
                    </p>
                    <p style={{ color: COLORS.text.secondary }} className="text-sm mb-3 line-clamp-2">
                      {analysis.explanation || 'No explanation available'}
                    </p>
                    <div className="flex items-center gap-4 text-xs">
                      <span style={{ color: COLORS.text.tertiary }}>
                        📅 {new Date(analysis.timestamp || '').toLocaleDateString()} {new Date(analysis.timestamp || '').toLocaleTimeString()}
                      </span>
                      {analysis.response_time && (
                        <span style={{ color: COLORS.text.tertiary }}>
                          ⏱️ {analysis.response_time.toFixed(2)}s
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Verdict Badge */}
                  <div
                    className="px-4 py-3 rounded-lg flex flex-col items-center gap-1 whitespace-nowrap"
                    style={{
                      backgroundColor:
                        analysis.verdict === 'TRUE'
                          ? `${COLORS.verdict.real}20`
                          : analysis.verdict === 'FALSE'
                          ? `${COLORS.verdict.fake}20`
                          : `${COLORS.verdict.rumor}20`,
                    }}
                  >
                    <p
                      style={{
                        color:
                          analysis.verdict === 'TRUE'
                            ? COLORS.verdict.real
                            : analysis.verdict === 'FALSE'
                            ? COLORS.verdict.fake
                            : COLORS.verdict.rumor,
                      }}
                      className="font-bold text-sm"
                    >
                      {analysis.verdict || 'UNKNOWN'}
                    </p>
                    <p
                      style={{ color: COLORS.text.secondary }}
                      className="text-xs"
                    >
                      {((analysis.confidence || 0) * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <p style={{ color: COLORS.text.tertiary }} className="text-center py-12">
              No analyses yet. Try analyzing a claim!
            </p>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
