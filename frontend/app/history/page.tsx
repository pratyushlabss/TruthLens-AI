"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { HistoryItem } from "@/types";

const verdictColor: Record<HistoryItem["verdict"], string> = {
  REAL: "text-green-400 bg-green-500/10 border-green-500/30",
  FAKE: "text-red-400 bg-red-500/10 border-red-500/30",
  RUMOR: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
};

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        const response = await fetch("/api/history", { cache: "no-store" });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Failed to load history");
        }
        setHistory(Array.isArray(data.history) ? data.history : []);
      } catch (err: any) {
        setError(err.message || "History unavailable");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, []);

  return (
    <div className="min-h-screen bg-background text-white p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Analysis History</h1>
          <Link href="/" className="px-4 py-2 rounded-lg border border-white/20 hover:bg-white/5">
            Back to Analyzer
          </Link>
        </div>

        {loading && <p className="text-gray-400">Loading history...</p>}
        {error && <p className="text-red-300">{error}</p>}

        {!loading && !error && (
          <div className="space-y-3">
            {history.map((item) => (
              <div key={item.id} className="rounded-xl border border-white/10 bg-gray-900/60 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-gray-100">{item.text}</p>
                    <p className="text-xs text-gray-400 mt-1">{new Date(item.timestamp).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex px-2 py-1 rounded-md text-xs border ${verdictColor[item.verdict]}`}>
                      {item.verdict}
                    </span>
                    <p className="text-sm text-gray-300 mt-2">{item.confidence.toFixed(2)}% ({item.confidence_label})</p>
                  </div>
                </div>
              </div>
            ))}
            {!history.length && <p className="text-gray-400">No analysis history found yet.</p>}
          </div>
        )}
      </div>
    </div>
  );
}
