# Blend(AI)r – Blender add-on for AI-powered editing

Blend(AI)r lets you drive Blender scenes with natural-language **prompts** or **hand gestures**
and sync your assets through **Supabase**.

* Load any OBJ / STL
* Type a prompt such as `"Rotate 15° around Z and add a red metallic material"` – the
  add-on calls an LLM endpoint that returns a Python snippet which is executed safely.
* Toggle **Gesture Mode** to control basic actions with your webcam.
* One-click upload / download models via Supabase Storage.

---

## Installation

1. **Clone & zip**
   ```bash
   git clone https://github.com/yourorg/blendair.git
   cd blendair
   zip -r blendair.zip blendair
   ```
2. **Install dependencies** (Blender ≥ 3.6 ships with its own Python):
   ```bash
   <blender-exec> --python-expr "import subprocess,sys; subprocess.check_call([sys.executable,'-m','pip','install','-r','requirements.txt'])"
   ```
3. In Blender **Edit ▸ Preferences ▸ Add-ons ▸ Install**, select `blendair.zip`, enable it.
4. In **Preferences ▸ Add-ons ▸ Blend(AI)r** set:
   * Supabase URL and key
   * LLM endpoint (e.g. `http://localhost:8000/generate`)
   * Gesture confidence threshold

---

## Usage

Open the **Blend(AI)r** tab in the 3D View sidebar.

* **Upload Current Model** – exports the scene to OBJ and pushes to Supabase.
* **Run Prompt** – opens a text field; on *Enter* the prompt is sent to the LLM and the
  returned code is queued and executed.
* **Gesture Mode** – start your webcam; an open palm triggers a demo print-statement (extend
  `gestures.py` to map more gestures ⇄ operators).

---

## Development & Tests

```bash
pip install -r requirements.txt -e .
pytest
```

### GitHub Actions CI
Every push installs headless Blender, dependencies, runs tests, and bundles `blendair.zip` as an artifact.

---

## License
MIT – see `LICENSE`.
