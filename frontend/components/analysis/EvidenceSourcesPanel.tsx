'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink } from 'lucide-react';
import { COLORS } from '@/lib/theme';

interface Source {
  title: string;
  url: string;
  credibility: string;
  summary: string;
  supports?: string;
}

interface EvidenceSourcesPanelProps {
  sources?: Source[];
}

const EvidenceSourcesPanel: React.FC<EvidenceSourcesPanelProps> = ({ sources = [] }) => {
  const displaySources = sources.length > 0 ? sources : [];

  const getCredibilityColor = (credibility: string) => {
    switch (credibility?.toLowerCase()) {
      case 'high':
        return COLORS.verdict.real;
      case 'medium':
        return COLORS.verdict.rumor;
      case 'low':
        return COLORS.verdict.fake;
      default:
        return COLORS.text.secondary;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="p-6 rounded-2xl border"
      style={{
        backgroundColor: COLORS.bg.secondary,
        borderColor: COLORS.border.light,
      }}
    >
      <h3 style={{ color: COLORS.text.primary }} className="text-lg font-semibold mb-4">
        Evidence Sources ({displaySources.length})
      </h3>

      {displaySources.length === 0 ? (
        <p style={{ color: COLORS.text.secondary }} className="text-sm">
          No credible sources found
        </p>
      ) : (
        <div className="space-y-4">
          {displaySources.map((source, idx) => (
            <motion.a
              key={idx}
              href={source.url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              className="p-4 rounded-lg border block hover:opacity-80 transition-all"
              style={{
                backgroundColor: COLORS.bg.tertiary,
                borderColor: COLORS.border.medium,
              }}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 style={{ color: COLORS.text.primary }} className="font-semibold text-sm line-clamp-2">
                  {source.title}
                </h4>
                {source.url && <ExternalLink size={16} style={{ color: COLORS.text.tertiary }} className="flex-shrink-0 ml-2" />}
              </div>

              <p style={{ color: COLORS.text.secondary }} className="text-xs mb-2 line-clamp-2">
                {source.summary}
              </p>

              <div className="flex items-center justify-between">
                <span
                  className="text-xs font-semibold px-2 py-1 rounded"
                  style={{
                    backgroundColor: `${getCredibilityColor(source.credibility)}20`,
                    color: getCredibilityColor(source.credibility),
                  }}
                >
                  {source.credibility} Credibility
                </span>

                {source.supports && (
                  <span
                    className="text-xs font-semibold px-2 py-1 rounded"
                    style={{
                      backgroundColor: `${
                        source.supports === 'TRUE' ? COLORS.verdict.real : COLORS.verdict.fake
                      }20`,
                      color: source.supports === 'TRUE' ? COLORS.verdict.real : COLORS.verdict.fake,
                    }}
                  >
                    {source.supports === 'TRUE' ? '✓ Supports' : '✗ Contradicts'}
                  </span>
                )}
              </div>
            </motion.a>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default EvidenceSourcesPanel;
