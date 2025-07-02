# Blend(AI)r

**AI-powered Blender add-on for prompt, gesture, and Supabase/MCP-driven 3D editing**

---

## 🚀 What is Blend(AI)r?

Blend(AI)r lets you control Blender with natural language prompts and hand gestures, backed by cloud storage and real-time job queues. It supports:
- **Prompt-driven editing:** Type what you want (“Rotate 15°, add rugged plastic texture…”) and see it happen.
- **Gesture control:** Use your webcam and hand signals to trigger actions.
- **Supabase integration:** Sync models, renders, and jobs to the cloud.
- **Optional BlenderMCP:** Advanced context and multi-agent workflows via the Model Context Protocol.

---

## 🛠️ Features
- Import/export OBJ/STL models to/from Supabase Storage
- Prompt panel: send text to an LLM, receive and safely execute Blender Python
- Gesture recognition (MediaPipe Hands + OpenCV)
- LuxCore render integration
- Job queue: async prompt/gesture jobs, real-time status
- Optional: connect to BlenderMCP for multi-agent context
- Fully tested, CI/CD, MIT license

---

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
- **LLM endpoint:**
    - For local dev: `http://localhost:8000/generate` (run `uvicorn local_llm_server.app:app --reload`)
    - For production: use your deployed Supabase Edge Function URL
- **BlenderMCP URL** (optional)
- **Gesture confidence threshold**

---

## 🖥️ Usage

### 🆕 Floating Overlay Prompt Bar
- **Shortcut:** Press `Ctrl+Space` in the 3D Viewport to open the floating prompt bar overlay (always available, no sidebar required).
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
- **No response to prompt:** Check LLM endpoint in preferences, ensure server is running
- **Supabase errors:** Double-check URL/key and that tables/buckets exist
- **Gesture not detected:** Ensure webcam is enabled, MediaPipe and OpenCV installed
- **LuxCore not rendering:** Enable BlendLuxCore in Blender’s add-ons
- **MCP not connecting:** Check server URL and that it’s running

---

## 🤝 Contributing
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- PRs, issues, and suggestions welcome!

---

## 📄 License
MIT – see [LICENSE](LICENSE)

---

## Credits
- [Supabase](https://supabase.com/)
- [Blender](https://blender.org/)
- [MediaPipe](https://mediapipe.dev/)
- [BlendLuxCore](https://luxcorerender.org/)
- [BlenderMCP](https://github.com/ahujasid/blender-mcp)
