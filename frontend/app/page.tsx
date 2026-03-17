"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { EnhancedAnalysisResponse, HistoryItem } from "@/types";
import { Menu, X, Upload, Loader, AlertCircle, ExternalLink } from "lucide-react";

type AppState = "input" | "processing" | "results";
type InputTab = "text" | "url" | "image";

const verdictStyle: Record<EnhancedAnalysisResponse["verdict"], string> = {
  REAL: "text-green-400 border-green-500/40 bg-green-500/10",
  FAKE: "text-red-400 border-red-500/40 bg-red-500/10",
  RUMOR: "text-yellow-400 border-yellow-500/40 bg-yellow-500/10",
};

const confidenceBarStyle: Record<"LOW" | "MEDIUM" | "HIGH", string> = {
  LOW: "bg-red-500",
  MEDIUM: "bg-yellow-500",
  HIGH: "bg-green-500",
};

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [appState, setAppState] = useState<AppState>("input");
  const [activeTab, setActiveTab] = useState<InputTab>("text");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [textInput, setTextInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState("");

  const [analysisResult, setAnalysisResult] = useState<EnhancedAnalysisResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const highlightedPreview = useMemo(() => {
    if (!analysisResult || !analysisResult.highlighted_text?.length) {
      return textInput;
    }

    let rendered = textInput;
    for (const token of analysisResult.highlighted_text) {
      if (!token || token.length < 3) continue;
      const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      rendered = rendered.replace(new RegExp(`(${escaped})`, "ig"), "<mark class='bg-primary-500/40 px-1 rounded'>$1</mark>");
    }
    return rendered;
  }, [analysisResult, textInput]);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetch("/api/history", { cache: "no-store" });
        if (!response.ok) return;
        const data = await response.json();
        setHistory(Array.isArray(data.history) ? data.history : []);
      } catch {
        // Keep UI functional when history endpoint is unavailable.
      }
    };

    loadHistory();
  }, [appState]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(String(reader.result || ""));
    reader.readAsDataURL(file);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setAppState("processing");

    try {
      const formData = new FormData();
      if (activeTab === "text" && textInput.trim()) {
        formData.append("text", textInput.trim());
      } else if (activeTab === "url" && urlInput.trim()) {
        formData.append("url", urlInput.trim());
      } else if (activeTab === "image" && selectedImage) {
        formData.append("image", selectedImage);
      } else {
        throw new Error("Please provide valid input before analyzing.");
      }

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Analysis failed");
      }

      setAnalysisResult(payload as EnhancedAnalysisResponse);
      setAppState("results");
    } catch (err: any) {
      setError(err.message || "Unexpected error");
      setAppState("input");
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setTextInput("");
    setUrlInput("");
    setSelectedImage(null);
    setImagePreview("");
    setAnalysisResult(null);
    setError("");
    setAppState("input");
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <aside
        className={`fixed left-0 top-0 h-screen w-72 bg-gradient-to-b from-gray-900 to-gray-950 border-r border-white/10 z-40 overflow-y-auto transition-transform ${
          sidebarOpen ? "" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="p-6 border-b border-white/10">
          <h1 className="text-2xl font-bold gradient-text">TruthLens</h1>
          <p className="text-xs text-gray-400 mt-1">Explainable Fact-Checking AI</p>
        </div>

        <div className="p-6 border-b border-white/10 space-y-3">
          <button
            onClick={resetAll}
            className="w-full px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors font-medium"
          >
            New Analysis
          </button>
          <Link
            href="/history"
            className="block w-full text-center px-4 py-2.5 rounded-lg border border-white/15 text-gray-200 hover:bg-white/5 transition-colors"
          >
            Open History Dashboard
          </Link>
        </div>

        <div className="p-6">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase">Latest Claims</h2>
          <div className="space-y-2">
            {history.slice(0, 6).map((item) => (
              <div key={item.id} className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="text-sm text-gray-200 line-clamp-2">{item.text}</p>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className={`font-semibold ${verdictStyle[item.verdict].split(" ")[0]}`}>{item.verdict}</span>
                  <span className="text-gray-400">{new Date(item.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ))}
            {!history.length && <p className="text-sm text-gray-500">No history yet.</p>}
          </div>
        </div>
      </aside>

      <main className="flex-1 lg:ml-72 flex flex-col">
        <div className="h-16 border-b border-white/10 bg-gray-900/50 backdrop-blur-sm flex items-center px-6 gap-4">
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="lg:hidden text-gray-400 hover:text-white transition-colors"
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <div className="text-sm text-gray-300">Backend: http://localhost:8000</div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {appState === "input" && (
            <div className="max-w-4xl mx-auto p-8">
              <h1 className="text-4xl font-bold text-white mb-2">Analyze Content</h1>
              <p className="text-gray-400 mb-8">Get verdict, confidence calibration, explainability, and trusted sources.</p>

              <form onSubmit={handleSubmit} className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl border border-white/10 p-8">
                <div className="flex gap-3 mb-6 border-b border-white/10 pb-4">
                  {(["text", "url", "image"] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 rounded-lg capitalize transition-colors ${
                        activeTab === tab ? "bg-primary-500 text-white" : "text-gray-400 hover:text-gray-200"
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                {activeTab === "text" && (
                  <textarea
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    placeholder="Enter claim text..."
                    className="w-full h-44 px-4 py-3 bg-gray-950 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 resize-none"
                  />
                )}

                {activeTab === "url" && (
                  <input
                    type="url"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="https://example.com/article"
                    className="w-full px-4 py-3 bg-gray-950 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                  />
                )}

                {activeTab === "image" && (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500/60 transition-colors"
                  >
                    {imagePreview ? (
                      <img src={imagePreview} alt="Preview" className="h-48 mx-auto rounded-lg object-cover" />
                    ) : (
                      <div className="flex flex-col items-center gap-3 text-gray-300">
                        <Upload size={30} className="text-gray-500" />
                        <p>Click to upload image</p>
                      </div>
                    )}
                    <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                  </div>
                )}

                {error && (
                  <div className="mt-4 p-4 bg-red-500/10 border border-red-500/40 rounded-lg flex items-start gap-2">
                    <AlertCircle size={18} className="text-red-400 mt-0.5" />
                    <p className="text-red-300 text-sm">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="mt-6 w-full py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-700 rounded-lg text-white font-medium flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader size={18} className="animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Analyze"
                  )}
                </button>
              </form>
            </div>
          )}

          {appState === "processing" && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-primary-500/20 border-t-primary-500 animate-spin" />
                <p className="text-white text-lg font-semibold">Running explainable analysis...</p>
              </div>
            </div>
          )}

          {appState === "results" && analysisResult && (
            <div className="max-w-5xl mx-auto p-8 space-y-6">
              <button onClick={resetAll} className="text-primary-300 hover:text-primary-200 text-sm">← New analysis</button>

              <div className={`rounded-2xl border p-6 ${verdictStyle[analysisResult.verdict]}`}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm uppercase opacity-80">Verdict</p>
                    <h2 className="text-4xl font-bold">{analysisResult.verdict}</h2>
                  </div>
                  <div className="text-right">
                    <p className="text-sm opacity-90">Confidence</p>
                    <p className="text-2xl font-bold">{analysisResult.confidence.toFixed(2)}%</p>
                    <p className="text-sm">{analysisResult.confidence_label}</p>
                  </div>
                </div>

                <div className="mt-5">
                  <div className="h-3 bg-gray-800/70 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${confidenceBarStyle[analysisResult.confidence_label]}`}
                      style={{ width: `${Math.max(0, Math.min(100, analysisResult.confidence))}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <section className="bg-gray-800/50 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-3">Reasoning</h3>
                  <p className="text-gray-300">{analysisResult.reasoning || analysisResult.summary}</p>
                </section>

                <section className="bg-gray-800/50 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-3">Key Signals</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.key_signals.map((signal) => (
                      <span key={signal} className="px-2.5 py-1 text-xs rounded-full bg-primary-500/20 text-primary-200 border border-primary-500/30">
                        {signal}
                      </span>
                    ))}
                    {!analysisResult.key_signals.length && <span className="text-gray-400">No strong signals extracted.</span>}
                  </div>
                </section>
              </div>

              <section className="bg-gray-800/50 border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-3">Highlighted Terms</h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  {analysisResult.highlighted_text.map((w) => (
                    <span key={w} className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-200 border border-yellow-500/30 text-xs">
                      {w}
                    </span>
                  ))}
                </div>
                {textInput && (
                  <p
                    className="text-gray-300 text-sm leading-6"
                    dangerouslySetInnerHTML={{ __html: highlightedPreview }}
                  />
                )}
              </section>

              <section className="bg-gray-800/50 border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Top Sources</h3>
                <div className="space-y-3">
                  {analysisResult.sources?.map((source) => (
                    <a
                      key={`${source.url}-${source.title}`}
                      href={source.url || "#"}
                      target="_blank"
                      rel="noreferrer"
                      className="block p-4 bg-gray-900/70 rounded-xl border border-white/10 hover:border-primary-500/40 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-white font-medium">{source.title}</p>
                          <p className="text-sm text-gray-400 break-all">{source.url}</p>
                        </div>
                        <div className="text-right">
                          <div className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-primary-500/20 text-primary-200 border border-primary-500/30">
                            {source.credibility_score.toFixed(1)} credibility
                          </div>
                          <div className="mt-2 text-gray-400 flex justify-end">
                            <ExternalLink size={14} />
                          </div>
                        </div>
                      </div>
                    </a>
                  ))}
                  {!analysisResult.sources?.length && <p className="text-gray-400">No sources found.</p>}
                </div>
              </section>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
