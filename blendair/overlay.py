"""
Advanced floating overlay for Blend(AI)r:
- Draggable, resizable, animated overlay
- Autocomplete from history/macros
- Up/down arrow navigation
- Voice input (Vosk integration placeholder)
- Macro system (JSON import/export)
- Script review popup (syntax highlighting placeholder)
- Preview hooks (ghosted effect placeholder)
- Theming, accessibility, localization ready
"""
import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
import json
import os

# Overlay state
overlay_state = {
    'visible': False,
    'text': '',
    'caret': 0,
    'status': '',
    'dragging': False,
    'drag_offset': (0, 0),
    'pos': (40, 60),  # (x, y) lower-left
    'size': (540, 50),
    'autocomplete': [],
    'history': [],
    'history_idx': -1,
    'macros': {},
    'show_macros': False,
    'show_script_review': False,
    'review_script': '',
    'review_error': '',
    'preview_obj': None,
    'theme': 'dark',
    'font_size': 18,
}

MACRO_PATH = os.path.expanduser('~/.blendair_macros.json')

# --- Macro System ---
def load_macros():
    if os.path.exists(MACRO_PATH):
        with open(MACRO_PATH, 'r') as f:
            overlay_state['macros'] = json.load(f)
    else:
        overlay_state['macros'] = {
            "Rotate 90°": "Rotate selected object 90 degrees around Z",
            "Apply Red Material": "Set active object's material to red metallic",
        }

def save_macros():
    with open(MACRO_PATH, 'w') as f:
        json.dump(overlay_state['macros'], f, indent=2)

# --- Overlay Drawing ---
def draw_overlay(self, context):
    if not overlay_state['visible']:
        return
    x, y = overlay_state['pos']
    w, h = overlay_state['size']
    # Background
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    shader.bind()
    color = (0.08, 0.08, 0.1, 0.88) if overlay_state['theme'] == 'dark' else (0.98, 0.98, 0.98, 0.88)
    shader.uniform_float("color", color)
    coords = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": coords})
    batch.draw(shader)
    # Border
    shader.uniform_float("color", (0.2, 0.6, 1, 0.7))
    coords = [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)]
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": coords})
    batch.draw(shader)
    # Prompt text
    blf.position(0, x+18, y+h-28, 0)
    blf.size(0, overlay_state['font_size'], 72)
    blf.color(0, 1, 1, 1, 1)
    blf.draw(0, overlay_state['text'])
    # Caret
    caret_x = x+18 + blf.dimensions(0, overlay_state['text'][:overlay_state['caret']])[0]
    blf.position(0, caret_x, y+h-28, 0)
    blf.draw(0, '|')
    # Status
    blf.position(0, x+18, y+h-45, 0)
    blf.size(0, 12, 72)
    blf.color(0, 0.7, 0.7, 0.7, 1)
    blf.draw(0, overlay_state['status'])
    # Voice and gesture icons (right side)
    icon_y = y+h-32
    mic_x = x+w-60
    hand_x = x+w-32
    blf.position(0, mic_x, icon_y, 0)
    blf.size(0, 22, 72)
    blf.color(0, 0.85, 0.85, 0.2, 1)
    blf.draw(0, '\U0001F3A4')  # 🎤 microphone
    blf.position(0, hand_x, icon_y, 0)
    blf.size(0, 22, 72)
    blf.color(0, 0.4, 0.85, 1, 1)
    blf.draw(0, '\U0001F590')  # 🖐️ hand
    # Optionally, draw gesture status
    gesture_status = overlay_state.get('gesture_status', 'off')
    blf.position(0, hand_x-32, icon_y, 0)
    blf.size(0, 12, 72)
    blf.color(0, 0.7, 0.7, 0.7, 1)
    blf.draw(0, f"{'ON' if gesture_status=='on' else 'OFF'}")
    # Autocomplete
    if overlay_state['autocomplete']:
        for i, opt in enumerate(overlay_state['autocomplete'][:5]):
            blf.position(0, x+28, y+h-54-22*i, 0)
            blf.size(0, 15, 72)
            blf.color(0, 0.95, 0.7, 0.9, 1)
            blf.draw(0, opt)
    # Macro list
    if overlay_state['show_macros']:
        for i, (name, prompt) in enumerate(overlay_state['macros'].items()):
            blf.position(0, x+w+16, y+h-28-22*i, 0)
            blf.size(0, 15, 72)
            blf.color(0, 0.8, 1, 1, 1)
            blf.draw(0, f"{name}: {prompt}")
    # Script review popup (placeholder)
    if overlay_state['show_script_review']:
        blf.position(0, x+28, y+h+24, 0)
        blf.size(0, 15, 72)
        blf.color(0, 1, 0.8, 1, 1)
        blf.draw(0, "Review script before execution:")
        blf.position(0, x+28, y+h+8, 0)
        blf.size(0, 13, 72)
        blf.color(0, 0.95, 1, 1, 1)
        blf.draw(0, overlay_state['review_script'][:120])
        if overlay_state['review_error']:
            blf.position(0, x+28, y+h-10, 0)
            blf.color(0, 1, 0.3, 0.3, 1)
            blf.draw(0, overlay_state['review_error'])

# --- Modal Operator for Overlay ---
class BLENDAIR_OT_OverlayModal(bpy.types.Operator):
    bl_idname = "wm.blendair_overlay_modal"
    bl_label = "BlendAIr Advanced Overlay"

    def modal(self, context, event):
        # TODO: implement drag, resize, autocomplete, history, macros, script review, preview, voice
        # Placeholder: ESC closes, typing edits text, Enter prints
        if not overlay_state['visible']:
            return {'FINISHED'}
        if event.type == 'ESC':
            overlay_state['visible'] = False
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Drag start if in title bar
            mx, my = event.mouse_region_x, event.mouse_region_y
            x, y = overlay_state['pos']
            w, h = overlay_state['size']
            if x <= mx <= x+w and y+h-22 <= my <= y+h:
                overlay_state['dragging'] = True
                overlay_state['drag_offset'] = (mx-x, my-(y+h-22))
        if event.type == 'MOUSEMOVE' and overlay_state['dragging']:
            mx, my = event.mouse_region_x, event.mouse_region_y
            dx, dy = overlay_state['drag_offset']
            overlay_state['pos'] = (mx-dx, my-(overlay_state['size'][1]-22)-dy)
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            overlay_state['dragging'] = False
        if event.type == 'RET' and event.value == 'PRESS':
            # TODO: fetch script, show review popup
            overlay_state['status'] = 'Prompt submitted (demo)'
            overlay_state['show_script_review'] = True
            overlay_state['review_script'] = f"# Demo script for: {overlay_state['text']}"
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if overlay_state['caret'] > 0:
                overlay_state['text'] = (overlay_state['text'][:overlay_state['caret']-1] +
                                         overlay_state['text'][overlay_state['caret']:])
                overlay_state['caret'] -= 1
        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            overlay_state['caret'] = max(0, overlay_state['caret']-1)
        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            overlay_state['caret'] = min(len(overlay_state['text']), overlay_state['caret']+1)
        if event.type == 'UP_ARROW' and event.value == 'PRESS':
            # History up
            if overlay_state['history']:
                overlay_state['history_idx'] = (overlay_state['history_idx']-1) % len(overlay_state['history'])
                overlay_state['text'] = overlay_state['history'][overlay_state['history_idx']]
                overlay_state['caret'] = len(overlay_state['text'])
        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            # History down
            if overlay_state['history']:
                overlay_state['history_idx'] = (overlay_state['history_idx']+1) % len(overlay_state['history'])
                overlay_state['text'] = overlay_state['history'][overlay_state['history_idx']]
                overlay_state['caret'] = len(overlay_state['text'])
        if event.ascii and event.value == 'PRESS' and len(event.ascii) == 1:
            overlay_state['text'] = (overlay_state['text'][:overlay_state['caret']] +
                                     event.ascii +
                                     overlay_state['text'][overlay_state['caret']:])
            overlay_state['caret'] += 1
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# --- Registration ---
overlay_handle = None

def show_overlay(context):
    global overlay_handle
    overlay_state['visible'] = True
    load_macros()
    if overlay_handle is None:
        overlay_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_overlay, (None, None), 'WINDOW', 'POST_PIXEL')
    context.window_manager.modal_handler_add(BLENDAIR_OT_OverlayModal())

def hide_overlay():
    global overlay_handle
    overlay_state['visible'] = False
    if overlay_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(overlay_handle, 'WINDOW')
        overlay_handle = None

def register():
    bpy.utils.register_class(BLENDAIR_OT_OverlayModal)
    # TODO: Register hotkey (Ctrl+Space or user-configurable)

def unregister():
    bpy.utils.unregister_class(BLENDAIR_OT_OverlayModal)
    hide_overlay()
