'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Link as LinkIcon, FileText } from 'lucide-react';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';

interface AnalysisInputProps {
  onAnalyze?: (text: string) => void;
  loading?: boolean;
}

const AnalysisInput: React.FC<AnalysisInputProps> = ({ onAnalyze, loading = false }) => {
  const [inputValue, setInputValue] = useState('');
  const [inputType, setInputType] = useState<'text' | 'url' | 'image'>('text');

  const handleAnalyze = () => {
    if (inputValue.trim() && onAnalyze) {
      onAnalyze(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAnalyze();
    }
  };

  const tabItems = [
    { id: 'text', label: 'Text', icon: <FileText size={18} /> },
    { id: 'url', label: 'URL', icon: <LinkIcon size={18} /> },
    { id: 'image', label: 'Image', icon: <Upload size={18} /> },
  ] as const;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`
        p-6 rounded-2xl border
        ${GLASS_EFFECT.dark}
      `}
      style={{
        backgroundColor: `${COLORS.bg.secondary}80`,
        borderColor: COLORS.border.light,
      }}
    >
      {/* Tabs */}
      <div className="flex gap-2 mb-6 mb-6 border-b" style={{ borderColor: COLORS.border.light }}>
        {tabItems.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setInputType(tab.id as 'text' | 'url' | 'image')}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium
              border-b-2 transition-all
              ${inputType === tab.id
                ? 'border-opacity-100'
                : 'border-opacity-0 text-opacity-60'
              }
            `}
            style={{
              color: inputType === tab.id ? COLORS.verdict.real : COLORS.text.secondary,
              borderColor: COLORS.verdict.real,
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="mb-4">
        {inputType === 'text' && (
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter a claim, statement, or news article to analyze..."
            className={`
              w-full p-4 rounded-lg border resize-none outline-none
              transition-all focus:border-2
              ${GLASS_EFFECT.light}
            `}
            style={{
              backgroundColor: COLORS.bg.primary,
              borderColor: COLORS.border.light,
              color: COLORS.text.primary,
              minHeight: '120px',
            }}
          />
        )}

        {inputType === 'url' && (
          <input
            type="url"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Paste a URL to analyze (https://...)"
            className={`
              w-full p-4 rounded-lg border outline-none
              transition-all focus:border-2
              ${GLASS_EFFECT.light}
            `}
            style={{
              backgroundColor: COLORS.bg.primary,
              borderColor: COLORS.border.light,
              color: COLORS.text.primary,
            }}
          />
        )}

        {inputType === 'image' && (
          <div
            className="w-full p-8 rounded-lg border-2 border-dashed text-center cursor-pointer transition-all hover:opacity-80"
            style={{
              borderColor: COLORS.verdict.real,
              backgroundColor: `${COLORS.verdict.real}10`,
            }}
          >
            <Upload
              size={32}
              style={{ color: COLORS.verdict.real }}
              className="mx-auto mb-2"
            />
            <p style={{ color: COLORS.text.primary }} className="font-medium mb-1">
              Drop image here or click to browse
            </p>
            <p style={{ color: COLORS.text.tertiary }} className="text-sm">
              Supports JPG, PNG, GIF - up to 10MB
            </p>
          </div>
        )}
      </div>

      {/* Button & Info */}
      <div className="flex items-center justify-between">
        <p style={{ color: COLORS.text.tertiary }} className="text-sm">
          {/* eslint-disable-next-line react/no-unescaped-entities */}
          Ctrl + Enter to analyze
        </p>

        <button
          onClick={handleAnalyze}
          disabled={!inputValue.trim() || loading}
          className={`
            px-8 py-3 rounded-lg font-semibold
            transition-all transform hover:scale-105 active:scale-95
            disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
            relative overflow-hidden
          `}
          style={{
            background: COLORS.gradient.neon,
            color: COLORS.bg.primary,
          }}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin">⚙️</span>
              Analyzing...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              🔍 Analyze Claim
            </span>
          )}
        </button>
      </div>

      {/* Help Text */}
      <p
        style={{ color: COLORS.text.tertiary }}
        className="text-xs mt-4 text-center"
      >
        TruthLens AI uses advanced NLP, credibility scoring, and propagation analysis to detect misinformation.
      </p>
    </motion.div>
  );
};

export default AnalysisInput;
