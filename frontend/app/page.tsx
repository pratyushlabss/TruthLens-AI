"use client";

import React, { useState, useRef, FormEvent, ChangeEvent } from "react";
import { AnalysisSession, SystemStatus, UserProfile } from "@/types";
import {
  Plus,
  Menu,
  X,
  Settings,
  CheckCircle,
  AlertCircle,
  Upload,
  Loader,
} from "lucide-react";

type AppState = "input" | "processing" | "results";
type InputTab = "text" | "url" | "image";

interface AnalysisResponse {
  verdict: "REAL" | "FAKE" | "RUMOR";
  confidence: number;
  scores: {
    real: number;
    fake: number;
    rumor: number;
  };
  scoreBreakdown: {
    nlp: number;
    evidence: number;
    imageContent: number;
  };
  summary: string;
  signals: string[];
  propagationRisk: "LOW" | "MEDIUM" | "HIGH";
  evidenceSources: Array<{
    name: string;
    url: string;
    relevance: number;
    supports: "CONFIRMS" | "CONTRADICTS" | "NEUTRAL";
  }>;
}

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [appState, setAppState] = useState<AppState>("input");
  const [activeTab, setActiveTab] = useState<InputTab>("text");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Input states
  const [textInput, setTextInput] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>("");

  // Results state
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(
    null
  );

  const fileInputRef = useRef<HTMLInputElement>(null);

  const recentSessions: AnalysisSession[] = [
    {
      id: "1",
      title: "COVID-19 Vaccine Claims",
      timestamp: new Date(),
      category: "Health",
    },
    {
      id: "2",
      title: "Election Fraud Allegations",
      timestamp: new Date(),
      category: "Politics",
    },
    {
      id: "3",
      title: "AI Takeover Rumors",
      timestamp: new Date(),
      category: "Tech",
    },
  ];

  const systemStatus: SystemStatus = {
    apiHealth: "healthy",
    modelHealth: "healthy",
    responseTime: 245,
    lastChecked: new Date(),
  };

  const userProfile: UserProfile = {
    name: "Dr. Sarah Chen",
    email: "sarah.chen@truthlens.ai",
    avatar: "SC",
  };

  // Handle image selection
  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setError("");
    }
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setAppState("processing");

    try {
      const formData = new FormData();

      if (activeTab === "text" && textInput.trim()) {
        formData.append("text", textInput);
      } else if (activeTab === "url" && urlInput.trim()) {
        formData.append("url", urlInput);
      } else if (activeTab === "image" && selectedImage) {
        formData.append("image", selectedImage);
      } else {
        throw new Error("Please provide input for the selected tab");
      }

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = (await response.json()) as { error?: string };
        throw new Error(data.error || "Analysis failed");
      }

      const result = (await response.json()) as AnalysisResponse;
      setAnalysisResult(result);
      setAppState("results");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An error occurred";
      setError(message);
      setAppState("input");
    } finally {
      setLoading(false);
    }
  };

  // Reset for new analysis
  const handleNewAnalysis = () => {
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
      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-screen w-64 bg-gradient-to-b from-gray-900 to-gray-950 border-r border-white border-opacity-10 z-40 overflow-y-auto ${
          sidebarOpen ? "" : "-translate-x-full lg:translate-x-0"
        } transition-transform`}
      >
        <div className="p-6 border-b border-white border-opacity-10">
          <h1 className="text-2xl font-bold gradient-text">TruthLens</h1>
          <p className="text-xs text-gray-400 mt-1">AI Analysis Platform</p>
        </div>

        <div className="p-6 border-b border-white border-opacity-10">
          <button
            onClick={handleNewAnalysis}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors font-medium"
          >
            <Plus size={20} />
            New Analysis
          </button>
        </div>

        <div className="p-6 border-b border-white border-opacity-10">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase">
            Recent History
          </h2>
          <div className="space-y-2">
            {recentSessions.map((session) => (
              <div
                key={session.id}
                className="p-3 rounded-lg bg-white bg-opacity-5 hover:bg-opacity-10 transition-colors cursor-pointer"
              >
                <p className="text-sm font-medium text-gray-200">
                  {session.title}
                </p>
                <p className="text-xs text-gray-400 mt-1">{session.category}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 border-b border-white border-opacity-10">
          <h2 className="text-sm font-semibold text-gray-300 mb-4 uppercase">
            System Status
          </h2>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle
                size={16}
                className={
                  systemStatus.apiHealth === "healthy"
                    ? "text-green-500"
                    : "text-red-500"
                }
              />
              <span className="text-gray-300">API: Healthy</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle
                size={16}
                className={
                  systemStatus.modelHealth === "healthy"
                    ? "text-green-500"
                    : "text-red-500"
                }
              />
              <span className="text-gray-300">Models: Ready</span>
            </div>
            <div className="text-xs text-gray-400 mt-2">
              Avg Response: {systemStatus.responseTime}ms
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center gap-3 p-4 rounded-lg bg-white bg-opacity-5 border border-white border-opacity-10">
            <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center font-semibold text-white">
              {userProfile.avatar}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-200">
                {userProfile.name}
              </p>
              <p className="text-xs text-gray-400">{userProfile.email}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 lg:ml-64 flex flex-col">
        {/* Top Bar */}
        <div className="h-16 border-b border-white border-opacity-10 bg-gray-900 bg-opacity-50 backdrop-blur-sm flex items-center px-6 gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden text-gray-400 hover:text-white transition-colors"
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <div className="flex-1" />
          <Settings
            size={20}
            className="text-gray-400 cursor-pointer hover:text-white transition-colors"
          />
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          {appState === "input" && (
            <div className="max-w-4xl mx-auto p-8">
              <div className="mb-8">
                <h1 className="text-4xl font-bold text-white mb-2">
                  Analyze Content
                </h1>
                <p className="text-gray-400">
                  Verify the truthfulness of text, URLs, or images with AI
                </p>
              </div>

              <form
                onSubmit={handleSubmit}
                className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl border border-white border-opacity-10 backdrop-blur-md p-8"
              >
                {/* Tabs */}
                <div className="flex gap-4 mb-8 border-b border-white border-opacity-10 pb-4">
                  {(["text", "url", "image"] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => {
                        setActiveTab(tab);
                        setError("");
                      }}
                      className={`px-4 py-2 font-medium capitalize rounded-lg transition-colors ${
                        activeTab === tab
                          ? "bg-primary-500 text-white"
                          : "text-gray-400 hover:text-gray-300"
                      }`}
                    >
                      {tab === "url" ? "URL" : tab}
                    </button>
                  ))}
                </div>

                {/* Text Input */}
                {activeTab === "text" && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Paste your text here
                    </label>
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder="Enter the text or claim you want to analyze..."
                      className="w-full h-48 px-4 py-3 bg-gray-950 border border-white border-opacity-10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 resize-none"
                    />
                  </div>
                )}

                {/* URL Input */}
                {activeTab === "url" && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Enter article URL
                    </label>
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      placeholder="https://example.com/article"
                      className="w-full px-4 py-3 bg-gray-950 border border-white border-opacity-10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                    />
                    <p className="text-xs text-gray-400 mt-2">
                      We'll automatically scrape and analyze the article content
                    </p>
                  </div>
                )}

                {/* Image Upload */}
                {activeTab === "image" && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Upload image
                    </label>
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-white border-opacity-20 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 hover:border-opacity-50 transition-colors"
                    >
                      {imagePreview ? (
                        <div className="flex flex-col items-center gap-4">
                          <img
                            src={imagePreview}
                            alt="Preview"
                            className="h-48 object-cover rounded-lg"
                          />
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedImage(null);
                              setImagePreview("");
                            }}
                            className="text-sm text-gray-400 hover:text-red-400"
                          >
                            Remove image
                          </button>
                        </div>
                      ) : (
                        <div className="flex flex-col items-center gap-3">
                          <Upload size={32} className="text-gray-500" />
                          <div>
                            <p className="text-white font-medium">
                              Click to upload or drag and drop
                            </p>
                            <p className="text-gray-400 text-sm">
                              PNG, JPG up to 10MB
                            </p>
                          </div>
                        </div>
                      )}
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-2">
                      Images will be converted to text using AI and analyzed
                    </p>
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className="mb-6 p-4 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-50 rounded-lg flex items-start gap-3">
                    <AlertCircle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-red-300 text-sm">{error}</p>
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-6 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader size={20} className="animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Analyze Content"
                  )}
                </button>
              </form>
            </div>
          )}

          {appState === "processing" && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-primary-500 border-opacity-20 border-t-primary-500 animate-spin" />
                <h2 className="text-2xl font-bold text-white mb-2">
                  Analyzing...
                </h2>
                <p className="text-gray-400">
                  Running through AI models and evidence retrieval
                </p>
              </div>
            </div>
          )}

          {appState === "results" && analysisResult && (
            <div className="max-w-4xl mx-auto p-8">
              <div className="mb-8">
                <button
                  onClick={handleNewAnalysis}
                  className="text-primary-400 hover:text-primary-300 text-sm font-medium mb-4"
                >
                  ← Start New Analysis
                </button>
                <h1 className="text-4xl font-bold text-white">
                  Analysis Results
                </h1>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                {/* Verdict Card */}
                <div
                  className={`rounded-2xl border backdrop-blur-md p-8 ${
                    analysisResult.verdict === "REAL"
                      ? "bg-green-500 bg-opacity-10 border-green-500 border-opacity-30"
                      : analysisResult.verdict === "FAKE"
                        ? "bg-red-500 bg-opacity-10 border-red-500 border-opacity-30"
                        : "bg-yellow-500 bg-opacity-10 border-yellow-500 border-opacity-30"
                  }`}
                >
                  <div className="text-center">
                    <p className="text-gray-400 text-sm uppercase mb-2">
                      Verdict
                    </p>
                    <p
                      className={`text-4xl font-bold mb-2 ${
                        analysisResult.verdict === "REAL"
                          ? "text-green-400"
                          : analysisResult.verdict === "FAKE"
                            ? "text-red-400"
                            : "text-yellow-400"
                      }`}
                    >
                      {analysisResult.verdict}
                    </p>
                    <p className="text-gray-300">
                      Confidence:{" "}
                      <span className="font-bold">
                        {Math.round(analysisResult.confidence)}%
                      </span>
                    </p>
                  </div>
                </div>

                {/* Score Breakdown */}
                <div className="bg-gray-800 bg-opacity-50 border border-white border-opacity-10 rounded-2xl backdrop-blur-md p-8">
                  <p className="text-gray-400 text-sm uppercase mb-4">
                    Score Breakdown
                  </p>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-300">Real</span>
                        <span className="font-bold text-white">
                          {analysisResult.scores.real}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{ width: `${analysisResult.scores.real}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-300">Fake</span>
                        <span className="font-bold text-white">
                          {analysisResult.scores.fake}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-red-500"
                          style={{ width: `${analysisResult.scores.fake}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-300">Rumor</span>
                        <span className="font-bold text-white">
                          {analysisResult.scores.rumor}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-yellow-500"
                          style={{ width: `${analysisResult.scores.rumor}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Summary & Signals */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div className="bg-gray-800 bg-opacity-50 border border-white border-opacity-10 rounded-2xl backdrop-blur-md p-8">
                  <h3 className="text-lg font-bold text-white mb-4">Summary</h3>
                  <p className="text-gray-300">{analysisResult.summary}</p>
                </div>

                <div className="bg-gray-800 bg-opacity-50 border border-white border-opacity-10 rounded-2xl backdrop-blur-md p-8">
                  <h3 className="text-lg font-bold text-white mb-4">Key Signals</h3>
                  <ul className="space-y-2">
                    {analysisResult.signals.map((signal, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle
                          size={16}
                          className="text-primary-400 flex-shrink-0 mt-1"
                        />
                        <span className="text-gray-300">{signal}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Evidence Sources */}
              <div className="bg-gray-800 bg-opacity-50 border border-white border-opacity-10 rounded-2xl backdrop-blur-md p-8">
                <h3 className="text-lg font-bold text-white mb-4">
                  Evidence Sources
                </h3>
                <div className="space-y-3">
                  {analysisResult.evidenceSources.map((source, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-gray-900 rounded-lg border border-white border-opacity-5"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-white">
                            {source.name}
                          </p>
                          <p className="text-sm text-gray-400">
                            {source.url}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-primary-400">
                            {source.relevance}% relevant
                          </p>
                          <p className="text-xs text-gray-400 capitalize">
                            {source.supports}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
