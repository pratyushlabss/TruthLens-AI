import { NextRequest, NextResponse } from "next/server";

// PRODUCTION API KEYS - Load from environment variables
const HF_TOKEN = process.env.HF_TOKEN;
const PINECONE_KEY = process.env.PINECONE_KEY;
const SCRAPER_KEY = process.env.SCRAPER_KEY;

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const textInput = formData.get("text") as string || "";
    const urlInput = formData.get("url") as string || "";
    const imageFile = formData.get("image") as File | null;

    let processedText = textInput;
    let imageDescription = "";

    // 1. AUTOPILOT SCRAPING (WebScraping.ai)
    if (urlInput) {
      try {
        const scrapeRes = await fetch(`https://api.webscraping.ai/html?url=${encodeURIComponent(urlInput)}&api_key=${SCRAPER_KEY}`);
        if (scrapeRes.ok) {
          const html = await scrapeRes.text();
          // Clean HTML tags and limit length for model efficiency
          processedText = html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').substring(0, 2000);
        }
      } catch (err) {
        console.error("Scraping failed, falling back to textInput");
      }
    }

    // 2. IMAGE ANALYSIS (Hugging Face BLIP)
    if (imageFile) {
      const imageBuffer = await imageFile.arrayBuffer();
      const blipRes = await fetch("https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base", {
        headers: { Authorization: `Bearer ${HF_TOKEN}` },
        method: "POST",
        body: imageBuffer,
      });
      const blipData = await blipRes.json();
      imageDescription = blipData[0]?.generated_text || "";
    }

    // 3. NLP CLASSIFICATION (Hugging Face RoBERTa)
    // Combine scraped text, user text, and image context for a full picture
    const finalContent = `${processedText} ${imageDescription}`.trim();
    
    if (!finalContent) {
       return NextResponse.json({ error: "No content provided for analysis" }, { status: 400 });
    }

    const nlpRes = await fetch("https://api-inference.huggingface.co/models/roberta-base-openai-detector", {
      headers: { Authorization: `Bearer ${HF_TOKEN}` },
      method: "POST",
      body: JSON.stringify({ inputs: finalContent }),
    });
    
    const nlpData = await nlpRes.json();
    // Safety check for model warming up or API errors
    const fakeScore = nlpData[0]?.find((item: any) => item.label === "Fake")?.score || 0.5;

    // 4. FUSION CALCULATION (Weighted Logic)
    const confidence = Math.round((1 - fakeScore) * 100);
    const verdict = confidence > 70 ? "REAL" : confidence > 40 ? "RUMOR" : "FAKE";

    return NextResponse.json({
      verdict,
      confidence,
      details: {
        text_analyzed: processedText.substring(0, 150) + "...",
        image_context: imageDescription,
        nlp_score: Number((1 - fakeScore).toFixed(4))
      }
    });

  } catch (error: any) {
    console.error("Analysis Error:", error);
    return NextResponse.json({ error: "Analysis failed", details: error.message }, { status: 500 });
  }
}