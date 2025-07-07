"""Helpers for communicating with the LLM service."""
import requests
from typing import Optional
from .addon_prefs import get_pref


def fetch_script(prompt: str) -> Optional[str]:
    prefs = get_pref()
    provider = getattr(prefs, 'llm_provider', 'blendair_cloud')
    headers = {}
    url = ''
    data = {}

    # Only use local_llm_endpoint for 'local' provider
    if provider == 'local':
        url = getattr(prefs, 'local_llm_endpoint', 'http://localhost:8000/generate')
        data = {"prompt": prompt}
    elif provider == 'blendair_cloud':
        url = 'https://api.your-blendair-cloud.com/generate'  # Replace with your real endpoint
        key = getattr(prefs, 'blendair_api_key', None)
        if not key:
            print("[BlendAIr] Missing BlendAIr Cloud API key.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        data = {"prompt": prompt}
    elif provider == 'openai':
        url = 'https://api.openai.com/v1/chat/completions'
        key = getattr(prefs, 'openai_api_key', None)
        if not key:
            print("[BlendAIr] Missing OpenAI API key.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        headers['Content-Type'] = 'application/json'
        data = {
            "model": "gpt-4o",  # Or allow user to configure
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7
        }
    elif provider == 'gemini':
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={getattr(prefs, "gemini_api_key", "")}'
        data = {"contents": [{"parts": [{"text": prompt}]}]}
    elif provider == 'huggingface':
        # Auto-select best HuggingFace model for code vs general prompt
        # StarCoder2-15B for code, Mixtral-8x7B or Llama-3 for general
        import re
        if re.search(r'(python|script|code|function|def |class )', prompt, re.I):
            model = 'bigcode/starcoder2-15b'
        else:
            # Prefer Llama-3 if available, else Mixtral
            model = 'meta-llama/Meta-Llama-3-8B-Instruct'  # fallback to Mixtral if needed
        url = f'https://api-inference.huggingface.co/models/{model}'
        key = getattr(prefs, 'huggingface_api_key', None)
        if not key:
            print("[BlendAIr] Missing HuggingFace API key.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        data = {"inputs": prompt}
    elif provider == 'anthropic':
        url = 'https://api.anthropic.com/v1/messages'
        key = getattr(prefs, 'anthropic_api_key', None)
        if not key:
            print("[BlendAIr] Missing Anthropic API key.")
            return None
        headers['x-api-key'] = key
        headers['anthropic-version'] = '2023-06-01'
        data = {
            "model": "claude-3-opus-20240229",  # Or allow user to configure
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}]
        }
    elif provider == 'pplx':
        url = 'https://api.perplexity.ai/chat/completions'
        key = getattr(prefs, 'pplx_api_key', None)
        if not key:
            print("[BlendAIr] Missing Perplexity API key.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        headers['Content-Type'] = 'application/json'
        data = {
            "model": "pplx-70b-chat",  # Or allow user to configure
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7
        }
    elif provider == 'replicate':
        url = 'https://api.replicate.com/v1/predictions'
        key = getattr(prefs, 'replicate_api_token', None)
        if not key:
            print("[BlendAIr] Missing Replicate API token.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        data = {"input": {"prompt": prompt}}
    elif provider == 'grok':
        url = 'https://api.grok.x.ai/v1/chat/completions'
        key = getattr(prefs, 'grok_api_key', None)
        if not key:
            print("[BlendAIr] Missing Grok API key.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        headers['Content-Type'] = 'application/json'
        data = {
            "model": "grok-1",  # Or allow user to configure
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7
        }
    elif provider == 'deepseek':
        url = 'https://api.deepseek.com/v1/chat/completions'
        key = getattr(prefs, 'deepseek_api_key', None)
        if not key:
            print("[BlendAIr] Missing DeepSeek API key.")
            return None
        headers['Authorization'] = f'Bearer {key}'
        headers['Content-Type'] = 'application/json'
        data = {
            "model": "deepseek-coder",  # Or allow user to configure
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7
        }
    else:
        print(f"[BlendAIr] Unknown LLM provider: {provider}")
        return None

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        resp.raise_for_status()
        # Parse response for script depending on provider
        if provider == 'openai':
            return resp.json()['choices'][0]['message']['content']
        elif provider == 'gemini':
            return resp.json()['candidates'][0]['content']['parts'][0]['text']
        elif provider == 'huggingface':
            return resp.json()[0]['generated_text'] if isinstance(resp.json(), list) else resp.json().get('generated_text')
        elif provider == 'anthropic':
            return resp.json()['content'][0]['text']
        elif provider == 'pplx':
            return resp.json()['choices'][0]['message']['content']
        elif provider == 'replicate':
            return resp.json()['output']
        elif provider == 'grok':
            return resp.json()['choices'][0]['message']['content']
        elif provider == 'deepseek':
            return resp.json()['choices'][0]['message']['content']
        else:
            # BlendAIr Cloud, local, fallback
            return resp.json().get('script')
    except Exception as e:
        print(f"[BlendAIr] Failed to fetch script: {e}")
        return None


# -----------------------------------------------------------------------------
# Public helper used by operators and tests
# -----------------------------------------------------------------------------

def send_prompt(prompt: str):
    """Thin wrapper around fetch_script for external callers."""
    return fetch_script(prompt)

