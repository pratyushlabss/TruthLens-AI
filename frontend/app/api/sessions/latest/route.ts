import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/**
 * GET /api/sessions/latest - Get latest queries for current user
 * Proxies to backend: GET /api/sessions/latest
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

    const response = await fetch(`${BACKEND_URL}/api/sessions/latest`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authHeader,
      },
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      console.error(`Sessions/latest error (${response.status}):`, data);
      return NextResponse.json(
        { error: data.detail || "Failed to fetch latest sessions" },
        { status: response.status }
      );
    }

    console.log("Sessions/latest fetched successfully");
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Sessions/latest fetch error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch sessions" },
      { status: 500 }
    );
  }
}
