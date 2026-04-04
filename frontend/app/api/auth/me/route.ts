import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("Authorization");
    
    if (!authHeader) {
      return NextResponse.json(
        { error: "No authorization header" },
        { status: 401 }
      );
    }

    const response = await fetch(`${BACKEND_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: authHeader,
      },
    });

    const data = await response.json();
    
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Auth me error:", error);
    return NextResponse.json(
      { error: "Internal Server Error", detail: String(error) },
      { status: 500 }
    );
  }
}
