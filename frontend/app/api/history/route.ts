import { NextResponse } from "next/server";

const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_API_URL}/api/history`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || "Failed to fetch history" },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "History fetch failed" },
      { status: 500 }
    );
  }
}
