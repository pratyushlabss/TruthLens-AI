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
  const [sourceDistribution, setSourceDistribution] = useState<any[]>([]);
  const [confidenceDistribution, setConfidenceDistribution] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [topSources, setTopSources] = useState<any[]>([]);
  const [uncertainClaims, setUncertainClaims] = useState<any[]>([]);
  
  // Get analytics data from context
  const { analyticsData, sessions } = useAnalysis();

  // Update visualizations when analytics data changes
  useEffect(() => {
    if (!analyticsData) {
      setSourceDistribution([]);
      setConfidenceDistribution([]);
      setHeatmapData([]);
      setTopSources([]);
      setUncertainClaims([]);
      return;
    }

    // Build source distribution from context data
    if (analyticsData.confidence_distribution) {
      setSourceDistribution([
        {
          name: 'High Credibility',
          value: analyticsData.confidence_distribution.high || 0,
          color: COLORS.verdict.real,
        },
        {
          name: 'Medium Credibility',
          value: analyticsData.confidence_distribution.medium || 0,
          color: COLORS.verdict.rumor,
        },
        {
          name: 'Low Credibility',
          value: analyticsData.confidence_distribution.low || 0,
          color: COLORS.verdict.fake,
        },
      ]);
    }

    // Build confidence distribution from verdict breakdown
    if (analyticsData.verdict_distribution) {
      setConfidenceDistribution([
        {
          name: 'True',
          value: analyticsData.verdict_distribution.TRUE || 0,
          color: COLORS.verdict.real,
        },
        {
          name: 'False',
          value: analyticsData.verdict_distribution.FALSE || 0,
          color: COLORS.verdict.fake,
        },
        {
          name: 'Uncertain',
          value: analyticsData.verdict_distribution.UNCERTAIN || 0,
          color: COLORS.verdict.rumor,
        },
      ]);
    }

    // Build top sources from context
    if (analyticsData.source_usage && Array.isArray(analyticsData.source_usage)) {
      const topSourcesList = analyticsData.source_usage
        .slice(0, 5)
        .map((source: any) => ({
          name: source.name,
          credibility: Math.round((source.avg_credibility || 0) * 100),
          frequency: source.frequency || 0,
        }));
      setTopSources(topSourcesList);
    }

    // Build heatmap from context
    if (analyticsData.heatmap_data && Array.isArray(analyticsData.heatmap_data)) {
      const heatmap = analyticsData.heatmap_data
        .slice(0, 8)
        .map((item: any) => ({
          source: item.source,
          bars: item.bars || [],
        }));
      setHeatmapData(heatmap);
    }

    // Build uncertain claims from context
    if (analyticsData.recent_analyses && Array.isArray(analyticsData.recent_analyses)) {
      const uncertain = analyticsData.recent_analyses
        .filter((analysis: any) => analysis.confidence < 0.6)
        .slice(0, 5)
        .map((analysis: any) => ({
          claim: analysis.input_text,
          confidence: analysis.confidence,
          verdict: analysis.verdict,
        }));
      setUncertainClaims(uncertain);
    }
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
          🧠 AI Intelligence Dashboard
        </h1>
        <p style={{ color: COLORS.text.secondary }} className="text-lg">
          Advanced analytics and evidence patterns across all analyses
        </p>
      </motion.div>

      {/* Pipeline Status */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        {[
          { label: 'Scraping', status: 'active', icon: '🌐' },
          { label: 'Evidence Extraction', status: 'active', icon: '📄' },
          { label: 'Verdict Engine', status: 'active', icon: '⚙️' },
        ].map((item, index) => (
          <motion.div
            key={index}
            whileHover={{ scale: 1.02 }}
            className="p-4 rounded-xl border"
            style={{
              backgroundColor: `${COLORS.bg.secondary}80`,
              borderColor: COLORS.border.light,
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{item.icon}</span>
                <div>
                  <p style={{ color: COLORS.text.secondary }} className="text-xs uppercase">
                    {item.label}
                  </p>
                  <p
                    style={{ color: COLORS.verdict.real }}
                    className="font-semibold text-sm"
                  >
                    ✓ Active
                  </p>
                </div>
              </div>
              <div
                className="w-3 h-3 rounded-full animate-pulse"
                style={{ backgroundColor: COLORS.verdict.real }}
              />
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Evidence Heatmap */}
        <motion.div
          variants={itemVariants}
          className="lg:col-span-2 p-6 rounded-2xl border"
          style={{
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
            🔥 Evidence Heatmap
          </h2>
          <div className="space-y-3">
            {heatmapData.length > 0 ? (
              heatmapData.slice(0, 8).map((row, idx) => (
                <div key={idx}>
                  <div
                    style={{ color: COLORS.text.secondary }}
                    className="text-xs font-semibold mb-1"
                  >
                    {row.source}
                  </div>
                  <div className="flex gap-1">
                    {row.bars.map((intensity: number, barIdx: number) => {
                      const colors = [
                        '#7f1d1d',
                        '#991b1b',
                        '#b91c1c',
                        '#dc2626',
                        '#ef4444',
                        '#fca5a5',
                        '#f59e0b',
                        '#10b981',
                        '#059669',
                        '#047857',
                      ];
                      const colorIndex = Math.floor((intensity / 100) * (colors.length - 1));
                      return (
                        <div
                          key={barIdx}
                          className="flex-1 h-8 rounded-sm border"
                          style={{
                            backgroundColor: colors[colorIndex],
                            borderColor: COLORS.border.light,
                            opacity: 0.8,
                          }}
                          title={`${intensity}%`}
                        />
                      );
                    })}
                  </div>
                </div>
              ))
            ) : (
              <p style={{ color: COLORS.text.tertiary }} className="text-center py-8">
                No data yet. Analyze claims to populate heatmap.
              </p>
            )}
          </div>
        </motion.div>

        {/* Source Trust Distribution */}
        <motion.div
          variants={itemVariants}
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-4">
            📊 Source Trust
          </h2>
          {sourceDistribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={sourceDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {sourceDistribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.bg.secondary,
                    border: `1px solid ${COLORS.border.light}`,
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: COLORS.text.primary }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : null}
          <div className="mt-4 space-y-2">
            {sourceDistribution.map((dist: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <span style={{ color: COLORS.text.secondary }}>{dist.name}</span>
                <span style={{ color: dist.color }} className="font-semibold">
                  {dist.value || 0}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </motion.div>

      {/* Confidence Distribution */}
      <motion.div
        variants={itemVariants}
        className="p-6 rounded-2xl border"
        style={{
          backgroundColor: `${COLORS.bg.secondary}80`,
          borderColor: COLORS.border.light,
        }}
      >
        <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
          📈 Verdict Confidence Distribution
        </h2>
        {confidenceDistribution.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={confidenceDistribution}>
              <CartesianGrid stroke={COLORS.border.light} />
              <XAxis stroke={COLORS.text.tertiary} dataKey="name" />
              <YAxis stroke={COLORS.text.tertiary} />
              <Tooltip
                contentStyle={{
                  backgroundColor: COLORS.bg.secondary,
                  border: `1px solid ${COLORS.border.light}`,
                  borderRadius: '8px',
                }}
                labelStyle={{ color: COLORS.text.primary }}
              />
              <Bar dataKey="value" fill={COLORS.verdict.neutral} />
            </BarChart>
          </ResponsiveContainer>
        ) : null}
      </motion.div>

      {/* Claim Intelligence Panel */}
      <motion.div
        variants={itemVariants}
        className="p-6 rounded-2xl border"
        style={{
          backgroundColor: `${COLORS.bg.secondary}80`,
          borderColor: COLORS.border.light,
        }}
      >
        <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
          🧠 Recent Claims Analysis
        </h2>
        <div className="space-y-3">
          {sessions && sessions.length > 0 ? (
            sessions.slice(0, 5).map((session, idx) => (
              <motion.div
                key={idx}
                whileHover={{ scale: 1.01 }}
                className="p-4 rounded-lg border flex items-start justify-between"
                style={{
                  backgroundColor: `${COLORS.bg.tertiary}40`,
                  borderColor: COLORS.border.light,
                }}
              >
                <div className="flex-1">
                  <p style={{ color: COLORS.text.primary }} className="text-sm font-semibold mb-1">
                    {session.input_text}
                  </p>
                  <div className="flex items-center gap-4 text-xs">
                    <span
                      style={{
                        color: session.verdict === 'TRUE' ? COLORS.verdict.real :
                               session.verdict === 'FALSE' ? COLORS.verdict.fake :
                               COLORS.verdict.rumor,
                        backgroundColor: session.verdict === 'TRUE' ? `${COLORS.verdict.real}20` :
                                        session.verdict === 'FALSE' ? `${COLORS.verdict.fake}20` :
                                        `${COLORS.verdict.rumor}20`,
                      }}
                      className="px-2 py-1 rounded-full font-semibold"
                    >
                      {session.verdict}
                    </span>
                    <span style={{ color: COLORS.text.tertiary }}>
                      Confidence: {(session.confidence * 100).toFixed(0)}%
                    </span>
                    <span style={{ color: COLORS.text.tertiary }}>
                      Sources: {session.source_count}
                    </span>
                  </div>
                </div>
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0 mt-1"
                  style={{
                    backgroundColor: session.verdict === 'TRUE' ? COLORS.verdict.real :
                                    session.verdict === 'FALSE' ? COLORS.verdict.fake :
                                    COLORS.verdict.rumor,
                  }}
                />
              </motion.div>
            ))
          ) : (
            <p style={{ color: COLORS.text.tertiary }} className="text-center py-8">
              No recent analyses. Start by analyzing claims in the Dashboard.
            </p>
          )}
        </div>
      </motion.div>

      {/* Top Sources Panel */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 lg:grid-cols-2 gap-8"
      >
        {/* Top Sources */}
        <motion.div
          variants={itemVariants}
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
            🔗 Top Sources
          </h2>
          <div className="space-y-3">
            {topSources.length > 0 ? (
              topSources.map((source, idx) => (
                <motion.div
                  key={idx}
                  whileHover={{ x: 4 }}
                  className="p-4 rounded-lg border flex items-between justify-between"
                  style={{
                    backgroundColor: `${COLORS.bg.tertiary}40`,
                    borderColor: COLORS.border.light,
                  }}
                >
                  <div>
                    <p style={{ color: COLORS.text.primary }} className="font-semibold">
                      #{idx + 1} {source.name}
                    </p>
                    <p style={{ color: COLORS.text.tertiary }} className="text-xs">
                      Used in {source.frequency} analyses
                    </p>
                  </div>
                  <div className="text-right">
                    <p
                      style={{ color: COLORS.verdict.real }}
                      className="text-lg font-bold"
                    >
                      {source.credibility}%
                    </p>
                    <p style={{ color: COLORS.text.tertiary }} className="text-xs">
                      Credibility
                    </p>
                  </div>
                </motion.div>
              ))
            ) : (
              <p style={{ color: COLORS.text.tertiary }} className="text-center py-8">
                No sources yet.
              </p>
            )}
          </div>
        </motion.div>

        {/* Uncertain Claims */}
        <motion.div
          variants={itemVariants}
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-xl font-bold mb-6">
            ⚠️ Uncertain Claims
          </h2>
          <div className="space-y-3">
            {uncertainClaims.length > 0 ? (
              uncertainClaims.map((claim, idx) => (
                <motion.div
                  key={idx}
                  whileHover={{ scale: 1.01 }}
                  className="p-4 rounded-lg border"
                  style={{
                    backgroundColor: `${COLORS.verdict.rumor}10`,
                    borderColor: COLORS.verdict.rumor + '40',
                  }}
                >
                  <p style={{ color: COLORS.text.primary }} className="text-sm font-semibold mb-2">
                    {claim.claim}
                  </p>
                  <div className="flex items-center justify-between">
                    <span style={{ color: COLORS.verdict.rumor }} className="text-xs font-semibold">
                      ⚠️ Low Confidence
                    </span>
                    <span style={{ color: COLORS.text.tertiary }} className="text-xs">
                      {(claim.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </motion.div>
              ))
            ) : (
              <p style={{ color: COLORS.text.tertiary }} className="text-center py-8">
                No uncertain claims detected. Great accuracy!
              </p>
            )}
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
