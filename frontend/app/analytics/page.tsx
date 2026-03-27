'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
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
} from 'recharts';
import Layout from '@/components/layout/Layout';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

// Mock data
const trendData = [
  { date: 'Mon', misinformation: 45, real: 62, rumor: 28 },
  { date: 'Tue', misinformation: 52, real: 58, rumor: 35 },
  { date: 'Wed', misinformation: 38, real: 71, rumor: 22 },
  { date: 'Thu', misinformation: 65, real: 54, rumor: 41 },
  { date: 'Fri', misinformation: 55, real: 68, rumor: 31 },
  { date: 'Sat', misinformation: 72, real: 49, rumor: 44 },
  { date: 'Sun', misinformation: 48, real: 73, rumor: 26 },
];

const verdictDistribution = [
  { name: 'Real', value: 45, color: COLORS.verdict.real },
  { name: 'Fake', value: 28, color: COLORS.verdict.fake },
  { name: 'Rumor', value: 21, color: COLORS.verdict.rumor },
  { name: 'Unknown', value: 6, color: COLORS.verdict.neutral },
];

const recentAnalyzes = [
  {
    id: '1',
    claim: 'Water boils at 100 degrees Celsius',
    verdict: 'REAL',
    confidence: 99,
    date: '2 hours ago',
  },
  {
    id: '2',
    claim: 'This vaccine causes infertility',
    verdict: 'FAKE',
    confidence: 96,
    date: '4 hours ago',
  },
  {
    id: '3',
    claim: 'Economic impact is significant',
    verdict: 'RUMOR',
    confidence: 72,
    date: '6 hours ago',
  },
  {
    id: '4',
    claim: 'New technology discovered',
    verdict: 'UNKNOWN',
    confidence: 45,
    date: '1 day ago',
  },
];

export default function AnalyticsPage() {
  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'REAL':
        return COLORS.verdict.real;
      case 'FAKE':
        return COLORS.verdict.fake;
      case 'RUMOR':
        return COLORS.verdict.rumor;
      case 'UNKNOWN':
        return COLORS.verdict.neutral;
      default:
        return COLORS.text.secondary;
    }
  };

  return (
    <Layout>
      <div
        className="p-8 pb-12"
        style={{ backgroundColor: COLORS.bg.primary }}
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1
            style={{ color: COLORS.text.primary }}
            className="text-4xl font-bold mb-2"
          >
            Analytics & Insights
          </h1>
          <p
            style={{ color: COLORS.text.secondary }}
            className="text-lg"
          >
            Weekly misinformation trends and detection statistics
          </p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Analyzed', value: '2,847', trend: '+18%' },
            { label: 'Misinformation Found', value: '342', trend: '+12%' },
            { label: 'Accuracy Rate', value: '96.8%', trend: '+2.1%' },
            { label: 'Avg Response Time', value: '1.2s', trend: '-0.3s' },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`
                p-4 rounded-lg border
                ${GLASS_EFFECT.dark}
              `}
              style={{
                backgroundColor: `${COLORS.bg.secondary}80`,
                borderColor: COLORS.border.light,
              }}
            >
              <p
                style={{ color: COLORS.text.tertiary }}
                className="text-xs uppercase tracking-wide mb-2"
              >
                {stat.label}
              </p>
              <div className="flex items-end justify-between">
                <p
                  style={{ color: COLORS.text.primary }}
                  className="text-2xl font-bold"
                >
                  {stat.value}
                </p>
                <p
                  style={{ color: COLORS.verdict.real }}
                  className="text-sm font-semibold"
                >
                  {stat.trend}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Trend Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className={`
              lg:col-span-2 p-6 rounded-2xl border
              ${GLASS_EFFECT.dark}
            `}
            style={{
              backgroundColor: `${COLORS.bg.secondary}80`,
              borderColor: COLORS.border.light,
            }}
          >
            <h3
              style={{ color: COLORS.text.primary }}
              className="text-lg font-bold mb-6"
            >
              📈 Weekly Verdict Distribution
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={COLORS.border.light}
                />
                <XAxis stroke={COLORS.text.tertiary} />
                <YAxis stroke={COLORS.text.tertiary} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.bg.secondary,
                    border: `1px solid ${COLORS.border.light}`,
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: COLORS.text.primary }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="real"
                  stroke={COLORS.verdict.real}
                  name="Real"
                  strokeWidth={2}
                  dot={{ fill: COLORS.verdict.real }}
                />
                <Line
                  type="monotone"
                  dataKey="misinformation"
                  stroke={COLORS.verdict.fake}
                  name="Misinformation"
                  strokeWidth={2}
                  dot={{ fill: COLORS.verdict.fake }}
                />
                <Line
                  type="monotone"
                  dataKey="rumor"
                  stroke={COLORS.verdict.rumor}
                  name="Rumor"
                  strokeWidth={2}
                  dot={{ fill: COLORS.verdict.rumor }}
                />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Pie Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className={`
              p-6 rounded-2xl border
              ${GLASS_EFFECT.dark}
            `}
            style={{
              backgroundColor: `${COLORS.bg.secondary}80`,
              borderColor: COLORS.border.light,
            }}
          >
            <h3
              style={{ color: COLORS.text.primary }}
              className="text-lg font-bold mb-6"
            >
              🎯 Verdict Distribution
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={verdictDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {verdictDistribution.map((entry, index) => (
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
          </motion.div>
        </div>

        {/* Recent Analyses Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className={`
            p-6 rounded-2xl border
            ${GLASS_EFFECT.dark}
          `}
          style={{
            backgroundColor: `${COLORS.bg.secondary}80`,
            borderColor: COLORS.border.light,
          }}
        >
          <h3
            style={{ color: COLORS.text.primary }}
            className="text-lg font-bold mb-6"
          >
            📋 Recent Analyses
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr
                  style={{ borderBottomColor: COLORS.border.light }}
                  className="border-b"
                >
                  <th
                    style={{ color: COLORS.text.tertiary }}
                    className="text-left py-3 px-4 font-semibold text-sm uppercase tracking-wide"
                  >
                    Claim
                  </th>
                  <th
                    style={{ color: COLORS.text.tertiary }}
                    className="text-left py-3 px-4 font-semibold text-sm uppercase tracking-wide"
                  >
                    Verdict
                  </th>
                  <th
                    style={{ color: COLORS.text.tertiary }}
                    className="text-left py-3 px-4 font-semibold text-sm uppercase tracking-wide"
                  >
                    Confidence
                  </th>
                  <th
                    style={{ color: COLORS.text.tertiary }}
                    className="text-left py-3 px-4 font-semibold text-sm uppercase tracking-wide"
                  >
                    Date
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyzes.map((analysis, index) => (
                  <tr
                    key={analysis.id}
                    style={{
                      borderBottomColor: COLORS.border.light,
                      backgroundColor:
                        index % 2 === 0 ? `${COLORS.bg.primary}80` : 'transparent',
                    }}
                    className="border-b hover:opacity-80 transition-opacity"
                  >
                    <td
                      style={{ color: COLORS.text.primary }}
                      className="py-3 px-4 text-sm"
                    >
                      {analysis.claim}
                    </td>
                    <td className="py-3 px-4 text-sm">
                      <span
                        className="inline-block px-3 py-1 rounded font-bold text-xs"
                        style={{
                          backgroundColor: getVerdictColor(analysis.verdict),
                          color: COLORS.bg.primary,
                        }}
                      >
                        {analysis.verdict}
                      </span>
                    </td>
                    <td
                      style={{ color: COLORS.verdict.real }}
                      className="py-3 px-4 text-sm font-semibold"
                    >
                      {analysis.confidence}%
                    </td>
                    <td
                      style={{ color: COLORS.text.tertiary }}
                      className="py-3 px-4 text-sm"
                    >
                      {analysis.date}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
}
