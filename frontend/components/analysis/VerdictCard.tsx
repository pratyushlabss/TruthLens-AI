'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { COLORS, GLASS_EFFECT, SHADOWS } from '@/lib/theme';

interface VerdictCardProps {
  verdict: 'TRUE' | 'FALSE' | 'REAL' | 'FAKE' | 'RUMOR' | 'UNKNOWN';
  confidence: number;
  loading?: boolean;
}

const VerdictCard: React.FC<VerdictCardProps> = ({ 
  verdict, 
  confidence, 
  loading = false 
}) => {
  const [displayConfidence, setDisplayConfidence] = useState(0);

  // Animate confidence number
  useEffect(() => {
    if (!loading) {
      const duration = 1500; // 1.5 seconds
      const steps = 60;
      const increment = confidence / steps;
      let current = 0;
      const interval = setInterval(() => {
        current += increment;
        if (current >= confidence) {
          setDisplayConfidence(confidence);
          clearInterval(interval);
        } else {
          setDisplayConfidence(Math.round(current));
        }
      }, duration / steps);
      return () => clearInterval(interval);
    }
  }, [confidence, loading]);

  const verdictConfig: Record<string, any> = {
    TRUE: {
      label: 'LEGITIMATE',
      color: COLORS.verdict.real,
      bg: 'rgba(34, 197, 94, 0.1)',
      glow: SHADOWS.glow,
      icon: '✓',
    },
    FALSE: {
      label: 'MISINFORMATION',
      color: COLORS.verdict.fake,
      bg: 'rgba(239, 68, 68, 0.1)',
      glow: SHADOWS.glow_red,
      icon: '✕',
    },
    REAL: {
      label: 'LEGITIMATE',
      color: COLORS.verdict.real,
      bg: 'rgba(34, 197, 94, 0.1)',
      glow: SHADOWS.glow,
      icon: '✓',
    },
    FAKE: {
      label: 'MISINFORMATION',
      color: COLORS.verdict.fake,
      bg: 'rgba(239, 68, 68, 0.1)',
      glow: SHADOWS.glow_red,
      icon: '✕',
    },
    RUMOR: {
      label: 'UNVERIFIED',
      color: COLORS.verdict.rumor,
      bg: 'rgba(245, 158, 11, 0.1)',
      glow: SHADOWS.glow_amber,
      icon: '?',
    },
    UNKNOWN: {
      label: 'INCONCLUSIVE',
      color: COLORS.verdict.neutral,
      bg: 'rgba(139, 92, 246, 0.1)',
      glow: '',
      icon: '—',
    },
  };

  const config = verdictConfig[verdict as string] || verdictConfig.UNKNOWN;
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (displayConfidence / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`
        relative p-8 rounded-2xl border overflow-hidden
        transition-all duration-300
        ${GLASS_EFFECT.dark}
      `}
      style={{
        backgroundColor: config.bg,
        borderColor: config.color,
      }}
    >
      {/* Animated Border Glow */}
      <div
        className="absolute inset-0 rounded-2xl blur-xl opacity-50"
        style={{
          background: config.color,
          pointerEvents: 'none',
          filter: 'blur(20px)',
        }}
      />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <p
              style={{ color: COLORS.text.tertiary }}
              className="text-sm uppercase tracking-wider mb-2"
            >
              Analysis Result
            </p>
            <h2
              className="text-4xl font-bold"
              style={{ color: config.color }}
            >
              {config.label}
            </h2>
          </div>

          {/* Large Icon Badge */}
          <motion.div
            className="w-24 h-24 rounded-full flex items-center justify-center text-5xl font-bold"
            style={{
              backgroundColor: config.bg,
              color: config.color,
              border: `3px solid ${config.color}`,
            }}
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {config.icon}
          </motion.div>
        </div>

        {/* Confidence Circle & Percentage */}
        <div className="flex items-center justify-center mt-12 mb-8">
          <div className="relative w-40 h-40">
            {/* Background circle */}
            <svg
              className="w-full h-full transform -rotate-90"
              viewBox="0 0 100 100"
            >
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={COLORS.border.medium}
                strokeWidth="3"
              />
              {/* Progress circle */}
              <motion.circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={config.color}
                strokeWidth="4"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                transition={{ duration: 1.5 }}
              />
            </svg>

            {/* Center text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <motion.div
                key={displayConfidence}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3 }}
                className="text-center"
              >
                <p
                  className="text-5xl font-bold"
                  style={{ color: config.color }}
                >
                  {displayConfidence}
                </p>
                <p
                  style={{ color: COLORS.text.secondary }}
                  className="text-sm mt-1"
                >
                  Confidence
                </p>
              </motion.div>
            </div>
          </div>
        </div>

        {/* Confidence Description */}
        <p
          className="text-center text-sm px-4"
          style={{ color: COLORS.text.secondary }}
        >
          {loading ? (
            <span className="animate-pulse">Analyzing...</span>
          ) : confidence >= 80 ? (
            'High confidence: strong, consistent evidence supports this verdict.'
          ) : confidence >= 60 ? (
            'Moderate confidence: evidence leans this way, but additional review is recommended.'
          ) : confidence >= 40 ? (
            'Low confidence: limited or mixed evidence; treat this verdict as inconclusive and consult more sources.'
          ) : (
            'Very low confidence: system could not find enough reliable or consistent evidence. This claim remains unresolved.'
          )}
        </p>

        {/* Confidence Gradient Bar */}
        <div
          className="mt-6 h-2 rounded-full overflow-hidden"
          style={{ backgroundColor: COLORS.border.medium }}
        >
          <motion.div
            className="h-full rounded-full"
            style={{
              background: COLORS.gradient.neon,
            }}
            initial={{ width: 0 }}
            animate={{ width: `${displayConfidence}%` }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default VerdictCard;
