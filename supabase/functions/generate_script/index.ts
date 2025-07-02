// Supabase Edge Function: generate_script
// Save as supabase/functions/generate_script/index.ts and deploy with:
// supabase functions deploy generate_script
// Converts a natural-language prompt into a Blender Python script via OpenAI.
// TODO: Adjust model + temperature as needed.

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import OpenAI from "https://deno.land/x/openai@v4.12.0/mod.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.4";

serve(async (req) => {
  const { prompt, project_id = null, model_id = null } = await req.json();

  if (!prompt) {
    return new Response("Missing prompt", { status: 400 });
  }

  const openaiKey = Deno.env.get("OPENAI_API_KEY");
  if (!openaiKey) {
    return new Response("Missing OPENAI_API_KEY", { status: 500 });
  }

  const openai = new OpenAI({ apiKey: openaiKey });

  const chat = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "You are a Blender Python assistant. Convert the user prompt into a safe Python script that manipulates the active scene. Do not import os, subprocess, or perform network calls.",
      },
      { role: "user", content: prompt },
    ],
    max_tokens: 300,
  });

  const script = chat.choices?.[0]?.message?.content ?? "";

  // Optionally enqueue into 'jobs' table so the Blender runner picks it up.
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE");
  if (supabaseUrl && supabaseKey && project_id && model_id) {
    const sb = createClient(supabaseUrl, supabaseKey);
    await sb.from("jobs").insert({
      project_id,
      model_id,
      type: "prompt",
      input: prompt,
      status: "queued",
      result_path: null,
      script,
    });
  }

  return new Response(JSON.stringify({ script }), {
    headers: { "Content-Type": "application/json" },
  });
});
