"""
Floating overlay prompt bar for Blend(AI)r.
- Ctrl+Space toggles overlay in 3D Viewport
- Type prompt, press Enter to send to LLM
- ESC to dismiss
- Robust handler/modal registration for product use
"""
import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty, BoolProperty

# Addon-wide state (could be moved to WindowManager props)
prompt_bar_state = {
    'visible': False,
    'text': '',
    'caret': 0,
    'status': '',
}

def draw_prompt_bar(self, context):
    if not prompt_bar_state['visible']:
        return
    region = context.region
    width, height = region.width, region.height
    # Draw semi-transparent background
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float("color", (0, 0, 0, 0.55))
    coords = [(20, height-50), (width-20, height-50), (width-20, height-20), (20, height-20)]
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": coords})
    batch.draw(shader)
    # Draw LLM provider dropdown (simulate as text for now)
    try:
        from .addon_prefs import get_pref
        provider = getattr(get_pref(), 'llm_provider', 'blendair_cloud')
    except Exception:
        provider = 'blendair_cloud'
    provider_label = {
        'blendair_cloud': 'BlendAIr Cloud',
        'openai': 'OpenAI',
        'gemini': 'Gemini',
        'huggingface': 'HuggingFace',
        'grok': 'Grok',
        'deepseek': 'DeepSeek',
        'local': 'Local',
    }.get(provider, provider)
    blf.position(0, width-250, height-38, 0)
    blf.size(0, 16, 72)
    blf.color(0, 0.7, 1, 1, 1)
    blf.draw(0, f"LLM: {provider_label}")
    # Draw gear/settings icon
    blf.position(0, width-50, height-38, 0)
    blf.size(0, 20, 72)
    blf.color(0, 0.8, 0.8, 0.8, 1)
    blf.draw(0, '\u2699')  # ⚙️
    # Draw prompt text
    blf.position(0, 35, height-38, 0)
    blf.size(0, 18, 72)
    blf.color(0, 1, 1, 1, 1)
    blf.draw(0, prompt_bar_state['text'])
    # Draw caret
    caret_x = 35 + blf.dimensions(0, prompt_bar_state['text'][:prompt_bar_state['caret']])[0]
    blf.position(0, caret_x, height-38, 0)
    blf.draw(0, '|')
    # Draw status
    blf.position(0, 35, height-60, 0)
    blf.size(0, 12, 72)
    blf.color(0, 0.7, 0.7, 0.7, 1)
    blf.draw(0, prompt_bar_state['status'])

# Handler registration
prompt_bar_handle = None

def toggle_prompt_bar(context):
    """Toggle the floating prompt bar overlay in the 3D Viewport."""
    global prompt_bar_handle
    prompt_bar_state['visible'] = not prompt_bar_state['visible']
    if prompt_bar_state['visible']:
        if prompt_bar_handle is None:
            prompt_bar_handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_prompt_bar, (None, None), 'WINDOW', 'POST_PIXEL')
        # Only add modal if not already running
        if not any(isinstance(wm, PromptBarModalOperator) for wm in bpy.context.window_manager.operators):
            context.window_manager.modal_handler_add(PromptBarModalOperator())
    else:
        if prompt_bar_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(prompt_bar_handle, 'WINDOW')
            prompt_bar_handle = None

def update_status(msg):
    prompt_bar_state['status'] = msg

class PromptBarModalOperator(bpy.types.Operator):
    """Modal operator for floating overlay prompt bar."""
    bl_idname = "wm.blendair_prompt_modal"
    bl_label = "BlendAIr Prompt Modal"

    def modal(self, context, event):
        if not prompt_bar_state['visible']:
            return {'FINISHED'}
        if event.type == 'TIMER':
            return {'PASS_THROUGH'}
        if event.type == 'ESC':
            prompt_bar_state['visible'] = False
            update_status('')
            return {'FINISHED'}
        if event.type == 'RET' and event.value == 'PRESS':
            from . import prompts
            prompt = prompt_bar_state['text']
            update_status('Sending prompt...')
            script = prompts.fetch_script(prompt)
            if script:
                try:
                    exec(script, {'bpy': bpy})
                    update_status('Success!')
                except Exception as e:
                    update_status(f'Exec error: {e}')
            else:
                update_status('Failed to fetch script.')
            prompt_bar_state['visible'] = False
            return {'FINISHED'}
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if prompt_bar_state['caret'] > 0:
                prompt_bar_state['text'] = (prompt_bar_state['text'][:prompt_bar_state['caret']-1] +
                                             prompt_bar_state['text'][prompt_bar_state['caret']:])
                prompt_bar_state['caret'] -= 1
            return {'RUNNING_MODAL'}
        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            prompt_bar_state['caret'] = max(0, prompt_bar_state['caret']-1)
            return {'RUNNING_MODAL'}
        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            prompt_bar_state['caret'] = min(len(prompt_bar_state['text']), prompt_bar_state['caret']+1)
            return {'RUNNING_MODAL'}
        if event.ascii and event.value == 'PRESS' and len(event.ascii) == 1:
            prompt_bar_state['text'] = (prompt_bar_state['text'][:prompt_bar_state['caret']] +
                                         event.ascii +
                                         prompt_bar_state['text'][prompt_bar_state['caret']:])
            prompt_bar_state['caret'] += 1
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        """Start modal input for the floating overlay bar."""
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def register():
    """Register floating overlay modal and hotkey."""
    bpy.utils.register_class(PromptBarModalOperator)
    # Register hotkey (Ctrl+Space)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new(PromptBarModalOperator.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=False)
        kmi.active = True

def unregister():
    """Unregister floating overlay modal and hotkey."""
    bpy.utils.unregister_class(PromptBarModalOperator)
    # Remove hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.get("3D View")
        if km:
            for kmi in km.keymap_items:
                if kmi.idname == PromptBarModalOperator.bl_idname:
                    km.keymap_items.remove(kmi)
                    break
