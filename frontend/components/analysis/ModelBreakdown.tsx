'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Brain, TrendingUp, Network } from 'lucide-react';
import { COLORS, GLASS_EFFECT, SHADOWS } from '@/lib/theme';

interface ModelScore {
  name: string;
  icon: React.ReactNode;
  score: number;
  weight: number;
  description: string;
}

interface ModelBreakdownProps {
  models?: ModelScore[];
}

const defaultModels: ModelScore[] = [
  {
    name: 'RoBERTa NLP',
    icon: <Brain size={20} />,
    score: 92,
    weight: 0.6,
    description: 'Language pattern analysis',
  },
  {
    name: 'Evidence Engine',
    icon: <TrendingUp size={20} />,
    score: 85,
    weight: 0.25,
    description: 'Source credibility verification',
  },
  {
    name: 'Propagation Risk',
    icon: <Network size={20} />,
    score: 78,
    weight: 0.15,
    description: 'Viral spread analysis',
  },
];

const ModelBreakdown: React.FC<ModelBreakdownProps> = ({ models = defaultModels }) => {
  const totalWeightedScore = models.reduce((sum, model) => sum + model.score * model.weight, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.1 }}
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
        <span>🔬</span>
        Model Breakdown
      </h3>

      {/* Models Grid */}
      <div className="space-y-4 mb-6">
        {models.map((model, index) => (
          <motion.div
            key={model.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 + index * 0.1 }}
            className="space-y-2"
          >
            {/* Model Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="p-2 rounded-lg"
                  style={{
                    backgroundColor: COLORS.bg.tertiary,
                    color: COLORS.verdict.real,
                  }}
                >
                  {model.icon}
                </div>
                <div>
                  <h4
                    style={{ color: COLORS.text.primary }}
                    className="text-sm font-semibold"
                  >
                    {model.name}
                  </h4>
                  <p
                    style={{ color: COLORS.text.tertiary }}
                    className="text-xs"
                  >
                    {model.description}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p
                  style={{ color: COLORS.verdict.real }}
                  className="text-xl font-bold"
                >
                  {model.score}%
                </p>
                <p
                  style={{ color: COLORS.text.tertiary }}
                  className="text-xs"
                >
                  Weight: {(model.weight * 100).toFixed(0)}%
                </p>
              </div>
            </div>

            {/* Score Bar */}
            <div
              className="h-2 rounded-full overflow-hidden"
              style={{ backgroundColor: COLORS.border.medium }}
            >
              <motion.div
                className="h-full rounded-full"
                style={{
                  background: COLORS.gradient.neon,
                }}
                initial={{ width: 0 }}
                animate={{ width: `${model.score}%` }}
                transition={{ duration: 1, delay: 0.2 + index * 0.1 }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Divider */}
      <div
        className="my-6 h-px"
        style={{ backgroundColor: COLORS.border.light }}
      />

      {/* Weighted Score Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="p-4 rounded-lg border"
        style={{
          backgroundColor: `${COLORS.verdict.real}15`,
          borderColor: COLORS.verdict.real,
        }}
      >
        <div className="flex items-center justify-between">
          <div>
            <p
              style={{ color: COLORS.text.tertiary }}
              className="text-sm"
            >
              Weighted Composite Score
            </p>
            <p
              style={{ color: COLORS.verdict.real }}
              className="text-2xl font-bold mt-1"
            >
              {Math.round(totalWeightedScore)}%
            </p>
          </div>
          <div
            className="text-4xl font-bold"
            style={{ color: `${COLORS.verdict.real}40` }}
          >
            ⚖️
          </div>
        </div>
      </motion.div>

      {/* Model Legend */}
      <p
        style={{ color: COLORS.text.tertiary }}
        className="text-xs mt-4 px-2"
      >
        Models are weighted by importance. Higher scores indicate stronger confidence in the verdict.
      </p>
    </motion.div>
  );
};

export default ModelBreakdown;
