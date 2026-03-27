'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

interface ExtractedClaim {
  id: string;
  text: string;
  verdict: 'TRUE' | 'FALSE' | 'UNKNOWN';
  confidence: number;
  reasoning: string;
}

interface ClaimBreakdownPanelProps {
  claims?: ExtractedClaim[];
}

const defaultClaims: ExtractedClaim[] = [
  {
    id: '1',
    text: 'Water boils at 100 degrees Celsius',
    verdict: 'TRUE',
    confidence: 99,
    reasoning: 'Universally accepted scientific fact, confirmed by multiple sources.',
  },
  {
    id: '2',
    text: 'This vaccine causes infertility',
    verdict: 'FALSE',
    confidence: 96,
    reasoning: 'No credible evidence found. Multiple studies contradict this claim.',
  },
  {
    id: '3',
    text: 'Economic impact is significant',
    verdict: 'UNKNOWN',
    confidence: 45,
    reasoning: 'Depends on specific context and timeframe. Requires more information.',
  },
];

const ClaimBreakdownPanel: React.FC<ClaimBreakdownPanelProps> = ({
  claims = defaultClaims,
}) => {
  const getVerdictColor = (verdict: ExtractedClaim['verdict']) => {
    switch (verdict) {
      case 'TRUE':
        return COLORS.verdict.real;
      case 'FALSE':
        return COLORS.verdict.fake;
      case 'UNKNOWN':
        return COLORS.verdict.rumor;
    }
  };

  const getVerdictBg = (verdict: ExtractedClaim['verdict']) => {
    switch (verdict) {
      case 'TRUE':
        return `${COLORS.verdict.real}15`;
      case 'FALSE':
        return `${COLORS.verdict.fake}15`;
      case 'UNKNOWN':
        return `${COLORS.verdict.rumor}15`;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.25 }}
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
        <span>🔗</span>
        Claim Breakdown
      </h3>

      {/* Claims List */}
      <div className="space-y-3">
        {claims.map((claim, index) => {
          const verdictColor = getVerdictColor(claim.verdict);
          const verdictBg = getVerdictBg(claim.verdict);

          return (
            <motion.div
              key={claim.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: 0.15 + index * 0.05 }}
              className="border rounded-lg p-4 transition-all hover:border-opacity-100"
              style={{
                borderColor: COLORS.border.light,
                backgroundColor: verdictBg,
                borderLeftColor: verdictColor,
                borderLeftWidth: '3px',
              }}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex-1">
                  <p
                    className="font-medium text-sm leading-relaxed"
                    style={{ color: COLORS.text.primary }}
                  >
                    &quot;{claim.text}&quot;
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <div className="text-right">
                    <span
                      className="text-sm font-bold px-2.5 py-1 rounded block mb-1"
                      style={{
                        backgroundColor: verdictColor,
                        color: COLORS.bg.primary,
                      }}
                    >
                      {claim.verdict}
                    </span>
                    <span
                      className="text-xs"
                      style={{ color: verdictColor }}
                    >
                      {claim.confidence}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Confidence Bar */}
              <div
                className="h-1.5 rounded-full overflow-hidden mb-3"
                style={{ backgroundColor: COLORS.border.light }}
              >
                <motion.div
                  className="h-full rounded-full"
                  style={{
                    background: verdictColor,
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${claim.confidence}%` }}
                  transition={{ duration: 1, delay: 0.3 + index * 0.05 }}
                />
              </div>

              {/* Reasoning */}
              <p
                className="text-xs leading-relaxed"
                style={{ color: COLORS.text.secondary }}
              >
                {claim.reasoning}
              </p>
            </motion.div>
          );
        })}
      </div>

      {/* Stats */}
      <div
        className="mt-6 p-4 rounded-lg border grid grid-cols-3 gap-4"
        style={{
          backgroundColor: COLORS.bg.tertiary,
          borderColor: COLORS.border.light,
        }}
      >
        <div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs mb-1 uppercase tracking-wide"
          >
            Total Claims
          </p>
          <p
            style={{ color: COLORS.text.primary }}
            className="text-2xl font-bold"
          >
            {claims.length}
          </p>
        </div>
        <div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs mb-1 uppercase tracking-wide"
          >
            True
          </p>
          <p
            style={{ color: COLORS.verdict.real }}
            className="text-2xl font-bold"
          >
            {claims.filter(c => c.verdict === 'TRUE').length}
          </p>
        </div>
        <div>
          <p
            style={{ color: COLORS.text.tertiary }}
            className="text-xs mb-1 uppercase tracking-wide"
          >
            False
          </p>
          <p
            style={{ color: COLORS.verdict.fake }}
            className="text-2xl font-bold"
          >
            {claims.filter(c => c.verdict === 'FALSE').length}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ClaimBreakdownPanel;
