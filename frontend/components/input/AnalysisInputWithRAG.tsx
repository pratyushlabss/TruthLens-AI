'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Link as LinkIcon, FileText, Loader } from 'lucide-react';
import { COLORS, GLASS_EFFECT } from '@/lib/theme';
import { analyzeClaimWithRAG, convertRAGResponseToAnalysisResult, checkRAGHealth } from '@/lib/rag-service';
import { useAnalysis } from '@/lib/analysis-context';

interface AnalysisInputProps {
  onAnalyze?: (text: string) => void;
  loading?: boolean;
  onResultsReady?: (results: any) => void;
}

const ragApiBase = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://127.0.0.1:8000';

const AnalysisInputWithRAG: React.FC<AnalysisInputProps> = ({ 
  onAnalyze, 
  loading = false,
  onResultsReady 
}) => {
  const [inputValue, setInputValue] = useState('');
  const [inputType, setInputType] = useState<'text' | 'url' | 'image'>('text');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ragHealthy, setRagHealthy] = useState<boolean | null>(null);
  const { addAnalysis } = useAnalysis();

  // Check RAG API health on mount
  useEffect(() => {
    let mounted = true;
    let intervalId: ReturnType<typeof setInterval> | null = null;

    const checkHealth = async () => {
      const healthy = await checkRAGHealth();
      if (mounted) {
        setRagHealthy(healthy);
        if (!healthy) {
          console.warn('RAG API is not available');
        }
      }
    };

    checkHealth();
    intervalId = setInterval(checkHealth, 10000);

    const handleFocus = () => {
      checkHealth();
    };
    window.addEventListener('focus', handleFocus);

    return () => {
      mounted = false;
      if (intervalId) {
        clearInterval(intervalId);
      }
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const handleAnalyze = async () => {
    if (!inputValue.trim()) {
      setError('Please enter a claim to analyze');
      return;
    }

    setError(null);
    setIsAnalyzing(true);

    try {
      // Call RAG API
      const ragResponse = await analyzeClaimWithRAG(inputValue, 5);

      if (!ragResponse.success) {
        throw new Error(ragResponse.metadata.error || 'Analysis failed');
      }

      // Convert RAG response to frontend format
      const analysisResult = convertRAGResponseToAnalysisResult(ragResponse);

      // Save to context with metadata
      const startTime = Date.now();
      if (addAnalysis) {
        addAnalysis({
          claim: inputValue,
          ...analysisResult,
          timestamp: new Date().toISOString(),
          response_time: (Date.now() - startTime) / 1000,
          uncertainty_flag: analysisResult.verdict === 'UNCERTAIN',
        });
      }

      // Call callback if provided
      if (onResultsReady) {
        onResultsReady(analysisResult);
      }

      // Clear input
      setInputValue('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(`Error: ${errorMessage}`);
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey && !isAnalyzing) {
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
      {/* API Status */}
      {ragHealthy === false && (
        <div className="mb-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <p style={{ color: COLORS.verdict.rumor }} className="text-sm">
            ⚠️ RAG API not responding. Check if server is running on port 8000.
          </p>
        </div>
      )}
      <div className="mb-4 flex flex-wrap items-center gap-2 text-xs">
        <span style={{ color: COLORS.text.tertiary }}>RAG API:</span>
        <span
          className="font-semibold"
          style={{
            color: ragHealthy === null
              ? COLORS.text.tertiary
              : ragHealthy
                ? COLORS.verdict.real
                : COLORS.verdict.rumor,
          }}
        >
          {ragHealthy === null
            ? 'Checking...'
            : ragHealthy
              ? 'Online'
              : 'Offline'}
        </span>
        <span style={{ color: COLORS.text.tertiary }} className="truncate">
          {ragApiBase}
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b" style={{ borderColor: COLORS.border.light }}>
        {tabItems.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setInputType(tab.id as 'text' | 'url' | 'image')}
            disabled={isAnalyzing}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium
              border-b-2 transition-all
              ${inputType === tab.id
                ? 'border-opacity-100'
                : 'border-opacity-0 text-opacity-60'
              }
              ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}
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
            disabled={isAnalyzing}
            placeholder="Enter a claim to fact-check (e.g., 'Paris is the capital of France')"
            className="w-full h-32 p-4 rounded-lg bg-black/30 border text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2"
            style={{
              borderColor: COLORS.border.light,
            }}
          />
        )}

        {inputType === 'url' && (
          <div className="flex gap-2">
            <input
              type="url"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isAnalyzing}
              placeholder="Enter URL (e.g., https://example.com/article)"
              className="flex-1 p-4 rounded-lg bg-black/30 border text-white placeholder-gray-500 focus:outline-none focus:ring-2"
              style={{
                borderColor: COLORS.border.light,
              }}
            />
          </div>
        )}

        {inputType === 'image' && (
          <div
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-black/10 transition-colors"
            style={{ borderColor: COLORS.verdict.real }}
          >
            <Upload size={32} style={{ color: COLORS.verdict.real }} className="mx-auto mb-2" />
            <p style={{ color: COLORS.text.secondary }} className="text-sm">
              Click to upload image or drag and drop
            </p>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <p style={{ color: COLORS.verdict.fake }} className="text-sm">
            {error}
          </p>
        </div>
      )}

      {/* Analyze Button */}
      <div className="flex gap-3">
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || ragHealthy === false}
          className={`
            flex-1 px-6 py-3 rounded-lg font-semibold
            transition-all flex items-center justify-center gap-2
            ${isAnalyzing || ragHealthy === false
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:scale-105'
            }
          `}
          style={{
            backgroundColor: COLORS.verdict.real,
            color: COLORS.bg.primary,
          }}
        >
          {isAnalyzing ? (
            <>
              <Loader size={18} className="animate-spin" />
              Analyzing...
            </>
          ) : (
            'Fact Check with RAG'
          )}
        </button>

        <button
          onClick={() => {
            setInputValue('');
            setError(null);
          }}
          disabled={isAnalyzing || !inputValue.trim()}
          className="px-6 py-3 rounded-lg font-semibold transition-all"
          style={{
            backgroundColor: COLORS.bg.tertiary,
            color: COLORS.text.secondary,
            opacity: isAnalyzing || !inputValue.trim() ? 0.5 : 1,
          }}
        >
          Clear
        </button>
      </div>

      {/* Info */}
      <p style={{ color: COLORS.text.tertiary }} className="text-xs mt-4">
        💡 Tip: Press Ctrl+Enter to analyze. RAG retrieves evidence from Wikipedia and scores using semantic similarity.
      </p>
    </motion.div>
  );
};

export default AnalysisInputWithRAG;
