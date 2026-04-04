import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    // Convert formData to URLSearchParams for proper form encoding
    const backendFormData = new FormData();
    for (const [key, value] of formData.entries()) {
      backendFormData.append(key, value);
    }

    // Call backend AI analysis endpoint
    const response = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: "POST",
      body: backendFormData,
    });

    const analysisResult = await response.json();

    if (!response.ok) {
      return NextResponse.json(analysisResult, { status: response.status });
    }

    return NextResponse.json(analysisResult);
  } catch (error) {
    console.error("Analyze error:", error);
    return NextResponse.json(
      { error: "Analysis failed", detail: String(error) },
      { status: 500 }
    );
  }
}

