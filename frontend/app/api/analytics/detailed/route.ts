import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/**
 * GET /api/analytics/detailed - Get detailed analytics for current user
 * Proxies to backend: GET /api/analytics
 * Backend analytics endpoint returns detailed charts and visualization data
 */
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("Authorization");
    
    if (!authHeader) {
      return NextResponse.json(
        { error: "No authorization header provided" },
        { status: 401 }
      );
    }

    const response = await fetch(`${BACKEND_URL}/api/analytics`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authHeader,
      },
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      console.error(`Analytics error (${response.status}):`, data);
      return NextResponse.json(
        { error: data.detail || "Failed to fetch analytics" },
        { status: response.status }
      );
    }

    console.log("Analytics fetched successfully");
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Analytics fetch error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch analytics" },
      { status: 500 }
    );
  }
}
