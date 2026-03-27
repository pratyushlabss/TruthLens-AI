'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Activity } from 'lucide-react';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

interface PropagationData {
  tweetVelocity: number;
  clusterSize: number;
  reshareFactror: number;
  estimatedReach: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  viralScore: number;
}

interface PropagationAnalysisPanelProps {
  data?: PropagationData;
}

const defaultData: PropagationData = {
  tweetVelocity: 1250, // tweets per hour
  clusterSize: 847, // unique clusters spreading
  reshareFactror: 3.2, // reshare ratio
  estimatedReach: 2400000, // estimated people
  riskLevel: 'MEDIUM',
  viralScore: 67,
};

const PropagationAnalysisPanel: React.FC<PropagationAnalysisPanelProps> = ({
  data = defaultData,
}) => {
  const getRiskColor = (risk: PropagationData['riskLevel']) => {
    switch (risk) {
      case 'CRITICAL':
        return COLORS.verdict.fake;
      case 'HIGH':
        return COLORS.verdict.fake;
      case 'MEDIUM':
        return COLORS.verdict.rumor;
      case 'LOW':
        return COLORS.verdict.real;
    }
  };

  const getRiskBg = (risk: PropagationData['riskLevel']) => {
    switch (risk) {
      case 'CRITICAL':
        return `${COLORS.verdict.fake}15`;
      case 'HIGH':
        return `${COLORS.verdict.fake}15`;
      case 'MEDIUM':
        return `${COLORS.verdict.rumor}15`;
      case 'LOW':
        return `${COLORS.verdict.real}15`;
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className={`
        p-6 rounded-2xl border
        ${GLASS_EFFECT.dark}
      `}
      style={{
        backgroundColor: `${COLORS.bg.secondary}80`,
        borderColor: COLORS.border.light,
      }}
    >
      {/* Header */}
      <h3
        className="text-lg font-bold mb-6 flex items-center gap-2"
        style={{ color: COLORS.text.primary }}
      >
        <span>📊</span>
        Propagation Analysis
      </h3>

      {/* Risk Level Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="p-4 rounded-lg border mb-6"
        style={{
          backgroundColor: getRiskBg(data.riskLevel),
          borderColor: getRiskColor(data.riskLevel),
          borderWidth: '2px',
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <p
            style={{ color: COLORS.text.secondary }}
            className="text-xs uppercase tracking-wider font-semibold"
          >
            Viral Risk Level
          </p>
          <div
            className="text-lg font-bold px-3 py-1.5 rounded"
            style={{
              backgroundColor: getRiskColor(data.riskLevel),
              color: COLORS.bg.primary,
            }}
          >
            {data.riskLevel}
          </div>
        </div>

        {/* Viral Score Gauge */}
        <div className="space-y-2">
          <div
            className="h-3 rounded-full overflow-hidden"
            style={{ backgroundColor: COLORS.border.medium }}
          >
            <motion.div
              className="h-full rounded-full"
              style={{
                background: getRiskColor(data.riskLevel),
              }}
              initial={{ width: 0 }}
              animate={{ width: `${data.viralScore}%` }}
              transition={{ duration: 1.5 }}
            />
          </div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs"
          >
            Viral Score: <span style={{ color: getRiskColor(data.riskLevel) }} className="font-bold">{data.viralScore}%</span>
          </p>
        </div>
      </motion.div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Tweet Velocity */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: COLORS.bg.tertiary,
            borderColor: COLORS.border.light,
          }}
        >
          <div className="flex items-start justify-between mb-3">
            <div>
              <p
                style={{ color: COLORS.text.tertiary }}
                className="text-xs uppercase tracking-wide mb-1"
              >
                Tweet Velocity
              </p>
              <p
                style={{ color: COLORS.data.secondary }}
                className="text-2xl font-bold"
              >
                {formatNumber(data.tweetVelocity)}
              </p>
            </div>
            <TrendingUp
              size={20}
              style={{ color: COLORS.data.secondary }}
            />
          </div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs"
          >
            tweets/hour
          </p>
        </motion.div>

        {/* Cluster Size */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.45 }}
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: COLORS.bg.tertiary,
            borderColor: COLORS.border.light,
          }}
        >
          <div className="flex items-start justify-between mb-3">
            <div>
              <p
                style={{ color: COLORS.text.tertiary }}
                className="text-xs uppercase tracking-wide mb-1"
              >
                Cluster Size
              </p>
              <p
                style={{ color: COLORS.data.secondary }}
                className="text-2xl font-bold"
              >
                {formatNumber(data.clusterSize)}
              </p>
            </div>
            <Activity
              size={20}
              style={{ color: COLORS.data.secondary }}
            />
          </div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs"
          >
            unique clusters
          </p>
        </motion.div>

        {/* Reshare Factor */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: COLORS.bg.tertiary,
            borderColor: COLORS.border.light,
          }}
        >
          <div>
            <p
              style={{ color: COLORS.text.tertiary }}
              className="text-xs uppercase tracking-wide mb-1"
            >
              Reshare Factor
            </p>
            <p
              style={{ color: COLORS.data.secondary }}
              className="text-2xl font-bold"
            >
              {data.reshareFactror.toFixed(1)}x
            </p>
          </div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs mt-2"
          >
            multiplier effect
          </p>
        </motion.div>

        {/* Estimated Reach */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.55 }}
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: COLORS.bg.tertiary,
            borderColor: COLORS.border.light,
          }}
        >
          <div>
            <p
              style={{ color: COLORS.text.tertiary }}
              className="text-xs uppercase tracking-wide mb-1"
            >
              Estimated Reach
            </p>
            <p
              style={{ color: COLORS.data.secondary }}
              className="text-2xl font-bold"
            >
              {formatNumber(data.estimatedReach)}
            </p>
          </div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs mt-2"
          >
            potential people
          </p>
        </motion.div>
      </div>

      {/* Risk Factors */}
      <div
        className="p-4 rounded-lg border"
        style={{
          backgroundColor: COLORS.bg.tertiary,
          borderColor: COLORS.border.light,
        }}
      >
        <p
          style={{ color: COLORS.text.primary }}
          className="text-sm font-semibold mb-3"
        >
          🚨 High-Risk Factors
        </p>
        <ul
          style={{ color: COLORS.text.secondary }}
          className="text-xs space-y-2"
        >
          <li>• Emotional language triggers strong reactions</li>
          <li>• Similar false claims went viral {data.reshareFactror}x faster</li>
          <li>• Spreading across {Math.round(data.clusterSize / 100)} major networks</li>
        </ul>
      </div>
    </motion.div>
  );
};

export default PropagationAnalysisPanel;
