'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import { COLORS } from '@/lib/theme';

interface KeySignalsPanelProps {
  signals?: string[];
}

const KeySignalsPanel: React.FC<KeySignalsPanelProps> = ({ signals = [] }) => {
  const displaySignals = signals.length > 0 ? signals : ['No key signals detected'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.15 }}
      className="p-6 rounded-2xl border"
      style={{
        backgroundColor: COLORS.bg.secondary,
        borderColor: COLORS.border.light,
      }}
    >
      <h3 style={{ color: COLORS.text.primary }} className="text-lg font-semibold mb-4 flex items-center gap-2">
        <AlertCircle size={20} />
        Key Signals
      </h3>

      <div className="space-y-3">
        {displaySignals.map((signal, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
            className="p-3 rounded-lg border-l-4"
            style={{
              backgroundColor: `${COLORS.verdict.fake}10`,
              borderLeftColor: COLORS.verdict.fake,
            }}
          >
            <p style={{ color: COLORS.text.secondary }} className="text-sm">
              • {signal}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default KeySignalsPanel;
