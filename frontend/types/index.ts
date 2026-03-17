export interface AnalysisSession {
  id: string;
  title: string;
  timestamp: Date;
  category: "Politics" | "Health" | "Tech" | "Other";
}

export interface AnalysisResult {
  verdict: "REAL" | "RUMOR" | "FAKE";
  confidenceScore: number;
  keywords: Array<{
    keyword: string;
    importance: number;
  }>;
  trustworthySources: Array<{
    title: string;
    url: string;
    credibility: number;
    excerpt: string;
  }>;
  contradictorySources: Array<{
    title: string;
    url: string;
    credibility: number;
    excerpt: string;
  }>;
  sentiment: {
    fear: number;
    anger: number;
    neutral: number;
  };
  bias: {
    leftBias: number;
    rightBias: number;
  };
  propagationData: Array<{
    cluster: string;
    size: number;
    engagement: number;
  }>;
  explainability: string;
}

export interface SourceItem {
  title: string;
  url: string;
  credibility_score: number;
}

export interface EnhancedAnalysisResponse {
  verdict: "REAL" | "RUMOR" | "FAKE";
  confidence: number;
  scores: {
    real: number;
    rumor: number;
    fake: number;
  };
  confidence_label: "LOW" | "MEDIUM" | "HIGH";
  key_signals: string[];
  highlighted_text: string[];
  reasoning: string;
  sources: SourceItem[];
  summary: string;
}

export interface HistoryItem {
  id: string;
  text: string;
  verdict: "REAL" | "RUMOR" | "FAKE";
  confidence: number;
  confidence_label: "LOW" | "MEDIUM" | "HIGH";
  timestamp: string;
}

export interface SystemStatus {
  apiHealth: "healthy" | "degraded" | "down";
  modelHealth: "healthy" | "degraded" | "down";
  responseTime: number;
  lastChecked: Date;
}

export interface UserProfile {
  name: string;
  email: string;
  avatar: string;
  organization?: string;
}
