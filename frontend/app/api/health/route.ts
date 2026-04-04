import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/**
 * Health check endpoint
 * Tests backend connectivity and returns status
 * Helps debugging connection issues
 */
export async function GET(request: NextRequest) {
  try {
    const startTime = Date.now();
    
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      // Set timeout for health check
      signal: AbortSignal.timeout(5000),
    });

    const data = await response.json();
    const responseTime = Date.now() - startTime;

    if (!response.ok) {
      console.error(`Health check failed with status ${response.status}:`, data);
      return NextResponse.json(
        { 
          status: "unhealthy", 
          backend_status: response.status,
          message: "Backend health check failed",
          details: data,
          response_time_ms: responseTime,
        },
        { status: 503 }
      );
    }

    console.log(`Backend health check passed in ${responseTime}ms`);
    return NextResponse.json(
      {
        status: "healthy",
        backend: data,
        response_time_ms: responseTime,
        frontend_timestamp: new Date().toISOString(),
      },
      { status: 200 }
    );
  } catch (error: any) {
    const errorMsg = error?.message || "Unknown error";
    console.error("Health check error:", errorMsg);
    
    // Check if it's a timeout
    if (error.name === "AbortError") {
      return NextResponse.json(
        { 
          status: "unhealthy",
          error: "Backend timeout",
          message: "Backend did not respond within 5 seconds",
          details: errorMsg,
        },
        { status: 503 }
      );
    }
    
    // Check if it's a connection error
    if (errorMsg.includes("ECONNREFUSED") || errorMsg.includes("fetch failed")) {
      return NextResponse.json(
        { 
          status: "unhealthy",
          error: "Connection failed",
          message: `Cannot connect to backend at ${BACKEND_URL}`,
          details: errorMsg,
          backend_url: BACKEND_URL,
        },
        { status: 503 }
      );
    }
    
    return NextResponse.json(
      { 
        status: "unhealthy", 
        error: "Internal error",
        details: errorMsg,
      },
      { status: 500 }
    );
  }
}
