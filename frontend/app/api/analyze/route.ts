import { NextRequest, NextResponse } from "next/server";

// Backend API URL (load from environment or default)
const BACKEND_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export async function POST(req: NextRequest) {
  try {
    // Forward the request to the backend API
    // Backend is responsible for all API key management and external API calls
    const formData = await req.formData();

    // Forward form data to backend
    const response = await fetch(`${BACKEND_API_URL}/api/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.error || "Backend analysis failed" },
        { status: response.status }
      );
    }

    const analysisResult = await response.json();

    return NextResponse.json(analysisResult);

  } catch (error: any) {
    console.error("Frontend API Error:", error);
    return NextResponse.json(
      {
        error: "Analysis failed",
        details: error.message,
        hint: `Make sure backend is running at ${BACKEND_API_URL}`,
      },
      { status: 500 }
    );
  }
}