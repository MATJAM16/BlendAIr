# Blend(AI)r

**AI-powered Blender add-on for prompt, gesture, and Supabase/MCP-driven 3D editing**

---

## 🚀 What is Blend(AI)r?

Blend(AI)r lets you control Blender with natural language prompts and hand gestures, backed by cloud storage and real-time job queues. It supports:
- **Prompt-driven editing:** Type what you want ("Rotate 15°, add rugged plastic texture…") and see it happen, powered by your choice of the world's best LLMs (OpenAI, Gemini, HuggingFace, DeepSeek, Grok, Replicate, Anthropic, Perplexity, BlendAIr Cloud, or local).
- **Voice input/output:** Speak prompts and hear results using free local or premium cloud voices (auto-selects best/lowest cost).
- **Gesture control:** Use your webcam and hand signals to trigger actions.
- **Supabase integration:** Sync models, renders, and jobs to the cloud.
- **Optional BlenderMCP:** Advanced context and multi-agent workflows via the Model Context Protocol.

---

## 🛠️ Features
- Import/export OBJ/STL models to/from Supabase Storage
- Prompt panel: send text to an LLM (auto-selects best model for code or general tasks), receive and safely execute Blender Python
- Supports DeepSeek, Grok, Replicate, Anthropic, Perplexity, HuggingFace (StarCoder2-15B for code, Llama-3/Mixtral for general), OpenAI, Gemini, BlendAIr Cloud, and local LLMs
- Voice input/output: local (Vosk, Piper) or cloud (OpenAI Whisper, ElevenLabs, etc.) auto-selected for quality/cost
- Gesture recognition (MediaPipe Hands + OpenCV)
- LuxCore render integration
- Job queue: async prompt/gesture jobs, real-time status
- Optional: connect to BlenderMCP for multi-agent context
- Fully tested, CI/CD, MIT license

---<img width="1536" height="1024" alt="blendair ai" src="https://github.com/user-attachments/assets/9a57dac2-4ddb-4ff0-a45d-cbff4f36107a" />


## 📦 Installation

### 1. Clone & Package
```bash
git clone https://github.com/Matjay007/BlendAIr.git
cd BlendAIr
zip -r blendair.zip blendair
```

### 2. Install Dependencies
Blender ≥ 3.6 ships with Python 3.10+. Install requirements:
```bash
<blender-exec> --python-expr "import subprocess,sys; subprocess.check_call([sys.executable,'-m','pip','install','-r','requirements.txt'])"
```

### 3. Install the Add-on
- Blender → Edit → Preferences → Add-ons → Install → select `blendair.zip`
- Enable “Blend(AI)r”

### 4. Configure Preferences
- **Supabase URL** and **Anon Key** (from your Supabase project)
- **LLM Provider:**
    - Choose from: BlendAIr Cloud (paid), OpenAI, Gemini, HuggingFace, DeepSeek, Grok, Replicate, Anthropic, Perplexity, or your own local LLM server (Ollama, LM Studio, etc.)
    - HuggingFace auto-selects the best model for code (StarCoder2-15B) or general (Llama-3/Mixtral)
    - Enter your API key for each provider as needed
- **Voice Input/Output:**
    - Local (free, private, fast) or cloud (ultra-natural, may incur cost)
    - Auto-selects best/lowest cost for BlendAIr Cloud users
- **BlenderMCP URL** (optional)
- **Gesture confidence threshold**

---![Uploading Untitled.png…]()


## 🖥️ Usage

### 🅿️ Floating Overlay Prompt Bar
- **Shortcut:** Press `Ctrl+Space` in the 3D Viewport to open the floating prompt bar overlay (always available, no sidebar required).
- **Voice:** Click the 🎤 button to speak your prompt (uses best/cheapest voice input automatically)
- **Provider:** Prompts are sent to the best LLM for the job (auto-selected for code/general)
- **Type your command:** e.g., "Rotate selected object 45 degrees around Z".
- **Press Enter:** The prompt is sent to the LLM and executed in Blender. Status and errors are shown in the overlay.
- **ESC:** Dismisses the overlay.
- **Why:** Fastest way to use Blend(AI)r—no UI hunting, always ready.

![Overlay Screenshot Placeholder](docs/overlay_bar.png)

### Classic Panel Workflow
1. **Open the Blend(AI)r Panel**
   - In 3D Viewport, press N → “Blend(AI)r” tab
2. **Project/Model Selector:** Pick or enter your project name
3. **Upload Model:** Export current scene as OBJ and upload to Supabase
4. **Prompt Panel:** Type a natural-language command and click “Run Prompt”
5. **Download Model:** Import the latest processed OBJ from Supabase
6. **Render:** Trigger a LuxCore render and save PNG
7. **MCP Integration:** Toggle “Use BlenderMCP” and fetch context if desired
8. **Gesture Mode:** Toggle webcam, use gestures (see cheat sheet)

---

## ✋ Gesture Cheat Sheet
- **Open palm:** (Demo) triggers last prompt
- **Fist:** (Extend in `gestures.py`)
- **Two fingers:** (Extend in `gestures.py`)

---

## ☁️ Supabase Setup
- Create a Supabase project
- Run the schema in `db/bootstrap.sql` to create tables and buckets
- Deploy the Edge Function in `supabase/functions/generate_script`
- Set your Supabase URL and anon key in the add-on preferences

---

## 🤖 LLM/Edge Function
- For local dev, run:
  ```bash
  uvicorn local_llm_server.app:app --reload
  ```
- For production, deploy `generate_script` to Supabase Functions
- Set the endpoint in add-on preferences

---

## 🧩 BlenderMCP (Optional)
- [BlenderMCP GitHub](https://github.com/ahujasid/blender-mcp)
- To use socket-based MCP, run their server and set the MCP URL in preferences
- Our add-on supports REST MCP by default; socket support can be added

---

## 🛠️ Development & Testing
```bash
pip install -r requirements.txt -e .
pytest
```
- Tests run with a stubbed `bpy` for CI compatibility

---

## 🐳 CI/CD
- GitHub Actions: installs deps, runs tests, packages add-on ZIP on every push

---

## 🆘 Troubleshooting

If you encounter issues:
- Ensure all dependencies are installed in Blender's Python (see Installation)
- For prompt errors: check your API key, endpoint, and internet connectivity
- For 'Use Prompt' errors: make sure you have selected a valid LLM provider and entered the correct API key. If using HuggingFace, the add-on will auto-select the best model (StarCoder2-15B for code, Llama-3/Mixtral for general). For BlendAIr Cloud, ensure your pay-as-you-go API key is active.
- For gesture errors: check your webcam and MediaPipe install
- For Supabase: verify your project URL and anon key
- For voice: if local voice does not work, try switching to a cloud provider or check your microphone permissions
- Check the [issues](https://github.com/Matjay007/BlendAIr/issues) or [discussions](https://github.com/Matjay007/BlendAIr/discussions) for help

---

## 🤝 Contributing
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- PRs, issues, and suggestions welcome!

---

## 📄 License
MIT – see [LICENSE](LICENSE)

---

## 🏆 Credits

- [Supabase](https://supabase.com/)
- [OpenAI](https://openai.com/)
- [HuggingFace](https://huggingface.co/)
- [DeepSeek](https://platform.deepseek.com/)
- [Grok](https://grok.x.ai/)
- [Replicate](https://replicate.com/)
- [Anthropic](https://www.anthropic.com/)
- [Perplexity](https://www.perplexity.ai/)
- [MediaPipe](https://mediapipe.dev/)
- [BlendLuxCore](https://luxcorerender.org/)
- [BlenderMCP](https://github.com/ahujasid/blender-mcp)
