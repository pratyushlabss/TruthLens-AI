import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Initialize Supabase client for server-side operations
const supabase = SUPABASE_URL && SUPABASE_ANON_KEY 
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : null;

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const authHeader = request.headers.get("Authorization");

    // Convert formData to URLSearchParams for proper form encoding
    const backendFormData = new FormData();
    for (const [key, value] of formData.entries()) {
      backendFormData.append(key, value);
    }

    // Call backend AI analysis endpoint
    const response = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: "POST",
      body: backendFormData,
      headers: {
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    });

    const analysisResult = await response.json();

    if (!response.ok) {
      return NextResponse.json(analysisResult, { status: response.status });
    }

    // Extract user ID from auth header if available
    let userId: string | null = null;
    if (authHeader && supabase) {
      try {
        const token = authHeader.replace("Bearer ", "");
        const {
          data: { user },
        } = await supabase.auth.getUser(token);
        userId = user?.id || null;
      } catch (error) {
        console.error("Failed to extract user ID from token:", error);
      }
    }

    // Save analysis result to Supabase if user is authenticated
    if (userId && supabase) {
      try {
        const { error: insertError } = await supabase
          .from("analysis_history")
          .insert([
            {
              user_id: userId,
              text_input: formData.get("text") || null,
              url_input: formData.get("url") || null,
              image_input: formData.get("image") ? "image_uploaded" : null,
              verdict: analysisResult.verdict || "unknown",
              confidence_score: analysisResult.confidence || 0,
              detailed_analysis: analysisResult,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ]);

        if (insertError) {
          console.error("Failed to save analysis to Supabase:", insertError);
          // Don't fail the entire request if saving to DB fails
        }
      } catch (error) {
        console.error("Error saving analysis to Supabase:", error);
        // Continue anyway - the analysis was successful
      }
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

