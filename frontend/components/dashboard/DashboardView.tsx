'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { COLORS } from '@/lib/theme';
import { useAnalysis } from '@/lib/analysis-context';
import { useAuth } from '@/lib/auth';
import { supabase } from '@/lib/supabase';
import VerdictCard from '@/components/analysis/VerdictCard';
import KeySignalsPanel from '@/components/analysis/KeySignalsPanel';
import EvidenceSourcesPanel from '@/components/analysis/EvidenceSourcesPanel';

interface Source {
  title: string;
  url: string;
  credibility: string;
  summary: string;
  supports?: string;
}

interface AnalysisResult {
  verdict: string;
  confidence: number;
  explanation: string;
  sources: Source[];
  signals: string[];
  reasoning: string;
}

interface DashboardViewProps {
  onAnalysisComplete?: (result: AnalysisResult) => void;
}

export default function DashboardView({ onAnalysisComplete }: DashboardViewProps) {
  const [claimText, setClaimText] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Global analysis context
  const { addAnalysis, refreshAnalytics } = useAnalysis();
  const { user } = useAuth();

  // Get session token
  React.useEffect(() => {
    const getSessionToken = async () => {
      try {
        // Skip if Supabase not configured
        if (!supabase) {
          console.warn('Supabase not configured - proceeding without session token');
          return;
        }

        const {
          data: { session },
        } = await supabase.auth.getSession();
        if (session?.access_token) {
          setSessionToken(session.access_token);
        }
      } catch (error) {
        console.error('Error getting session:', error);
      }
    };
    getSessionToken();
  }, []);

  const handleAnalyze = async () => {
    if (!claimText.trim()) return;

    setLoading(true);
    const startTime = Date.now();
    try {
      const formData = new FormData();
      formData.append('text', claimText);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
        headers: sessionToken ? { 'Authorization': `Bearer ${sessionToken}` } : {},
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      const responseTime = (Date.now() - startTime) / 1000; // Convert to seconds
      
      // Enrich data with additional fields
      const enrichedAnalysis = {
        ...data,
        claim: claimText,
        timestamp: new Date().toISOString(),
        response_time: responseTime,
        uncertainty_flag: data.verdict === 'UNCERTAIN',
      };
      
      setResult(enrichedAnalysis);
      
      // Add to global analysis context - THIS WILL TRIGGER ANALYTICS REAL-TIME UPDATE
      addAnalysis(enrichedAnalysis);
      
      // Call callback
      onAnalysisComplete?.(enrichedAnalysis);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze claim. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !claimText.trim()) {
      alert('Please enter a claim and select an image');
      return;
    }

    setLoading(true);
    const startTime = Date.now();
    try {
      const formData = new FormData();
      formData.append('text', claimText);
      formData.append('image', file);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
        headers: sessionToken ? { 'Authorization': `Bearer ${sessionToken}` } : {},
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      const responseTime = (Date.now() - startTime) / 1000; // Convert to seconds
      
      // Enrich data with additional fields
      const enrichedAnalysis = {
        ...data,
        claim: claimText,
        timestamp: new Date().toISOString(),
        response_time: responseTime,
        uncertainty_flag: data.verdict === 'UNCERTAIN',
      };
      
      setResult(enrichedAnalysis);
      
      // Add to global analysis context - THIS WILL TRIGGER ANALYTICS REAL-TIME UPDATE
      addAnalysis(enrichedAnalysis);
      
      // Call callback
      onAnalysisComplete?.(enrichedAnalysis);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze image and claim');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 pb-12" style={{ backgroundColor: COLORS.bg.primary }}>
      {/* Hero Section */}
      {!result && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12 text-center"
        >
          <h1 style={{ color: COLORS.text.primary }} className="text-5xl font-bold mb-4">
            TruthLens AI
          </h1>
          <p style={{ color: COLORS.text.secondary }} className="text-lg max-w-2xl mx-auto">
            Advanced AI-powered fact-checking with real evidence retrieval and explainable verdicts.
          </p>
        </motion.div>
      )}

      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className={`mb-8 max-w-4xl mx-auto ${result ? 'mt-0' : ''}`}
      >
        <div
          className="p-6 rounded-2xl border"
          style={{
            backgroundColor: COLORS.bg.secondary,
            borderColor: COLORS.border.light,
          }}
        >
          <h2 style={{ color: COLORS.text.primary }} className="text-lg font-semibold mb-4">
            Enter Claim to Analyze
          </h2>

          {/* Text Input */}
          <textarea
            value={claimText}
            onChange={(e) => setClaimText(e.target.value)}
            placeholder="Enter a claim, news headline, or statement to fact-check..."
            className="w-full p-4 rounded-lg border outline-none transition-all resize-none mb-4"
            style={{
              backgroundColor: COLORS.bg.tertiary,
              borderColor: COLORS.border.medium,
              color: COLORS.text.primary,
              minHeight: '100px',
            }}
            onKeyDown={(e) => {
              if (e.ctrlKey && e.key === 'Enter') {
                handleAnalyze();
              }
            }}
          />

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={handleAnalyze}
              disabled={loading || !claimText.trim()}
              className="flex-1 py-2.5 rounded-lg font-semibold transition-all disabled:opacity-50"
              style={{
                background: COLORS.gradient.neon,
                color: COLORS.bg.primary,
              }}
            >
              {loading ? 'Analyzing...' : 'Analyze Claim'}
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="px-6 py-2.5 rounded-lg font-semibold border transition-all"
              style={{
                borderColor: COLORS.border.medium,
                color: COLORS.text.secondary,
              }}
            >
              + Image
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </div>

          {/* Keyboard hint */}
          {!loading && (
            <p style={{ color: COLORS.text.tertiary }} className="text-xs mt-3">
              Tip: Press Ctrl+Enter to analyze
            </p>
          )}
        </div>
      </motion.div>

      {/* Results Section */}
      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          className="space-y-8"
        >
          {/* Verdict Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <VerdictCard
                verdict={result.verdict as 'TRUE' | 'FALSE'}
                confidence={result.confidence}
                loading={false}
              />
            </div>

            {/* Explanation Box */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="p-6 rounded-2xl border"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <h3 style={{ color: COLORS.text.primary }} className="text-lg font-semibold mb-3">
                Explanation
              </h3>
              <p style={{ color: COLORS.text.secondary }} className="text-sm leading-relaxed">
                {result.explanation}
              </p>
            </motion.div>
          </div>

          {/* Key Signals */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <KeySignalsPanel signals={result.signals} />

            {/* Reasoning */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="p-6 rounded-2xl border"
              style={{
                backgroundColor: COLORS.bg.secondary,
                borderColor: COLORS.border.light,
              }}
            >
              <h3 style={{ color: COLORS.text.primary }} className="text-lg font-semibold mb-3">
                Analysis Details
              </h3>
              <p style={{ color: COLORS.text.secondary }} className="text-sm leading-relaxed">
                {result.reasoning}
              </p>
            </motion.div>
          </div>

          {/* Evidence Sources */}
          <EvidenceSourcesPanel sources={result.sources} />

          {/* New Analysis Button */}
          <div className="text-center">
            <button
              onClick={() => {
                setResult(null);
                setClaimText('');
              }}
              className="px-6 py-2.5 rounded-lg font-semibold transition-all"
              style={{
                backgroundColor: COLORS.bg.secondary,
                color: COLORS.text.primary,
                border: `1px solid ${COLORS.border.light}`,
              }}
            >
              Analyze Another Claim
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
