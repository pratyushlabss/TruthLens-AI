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
