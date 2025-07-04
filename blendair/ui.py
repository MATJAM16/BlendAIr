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

prompt_bar_state = {
    'visible': False,
    'text': '',
    'caret': 0,
    'status': '',
    'pos': [100, 100],  # [x, y] position of top-left corner
    'dragging': False,
    'drag_offset': [0, 0],
}


# Handler registration
prompt_bar_handle = None

def toggle_prompt_bar(context):
    """Toggle the floating prompt bar overlay in the 3D Viewport."""
    global prompt_bar_handle
    prompt_bar_state['visible'] = not prompt_bar_state['visible']
    if prompt_bar_state['visible']:
        if prompt_bar_handle is None:
            prompt_bar_handle = bpy.types.SpaceView3D.draw_handler_add(draw_prompt_bar, (None, None), 'WINDOW', 'POST_PIXEL')
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
        x, y = event.mouse_region_x, event.mouse_region_y
        region = context.region
        width, height = region.width, region.height
        x0, y0 = prompt_bar_state['pos']
        bar_w, bar_h = 600, 60
        icon_gap = 38
        icon_size = 24
        # --- Mouse hover tooltips ---
        hover_tip = None
        right_x = x0+bar_w-8
        icons = [
            ('settings', '\u2699', "Settings", right_x - icon_gap*0),
            ('send', '\u2191', "Send (Enter)", right_x - icon_gap*1),
            ('delete', '\U0001F5D1', "Delete", right_x - icon_gap*2),
            ('copy', '\U0001F4CB', "Copy", right_x - icon_gap*3),
            ('favorite', '★' if prompt_bar_state.get('favorite', False) else '☆', "Favorite", right_x - icon_gap*4),
            ('undo', '\u21BA', "Undo/Go Back", right_x - icon_gap*5),
            ('gesture', '\U0001F590', "Toggle Gesture", right_x - icon_gap*6),
            ('voice', '\U0001F3A4', "Toggle Voice", right_x - icon_gap*7),
        ]
        for name, _, tip, ix in icons:
            if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                hover_tip = tip
                break
        # Info/help icon (left)
        info_x = x0+12
        scene = context.scene
        if not getattr(scene, 'blendair_onboarding_complete', False):
            if info_x <= x <= info_x+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                hover_tip = "Onboarding & Help"
        if hover_tip:
            update_status(hover_tip)
        elif not event.type.startswith('MOUSE'):
            update_status('')
        # --- Mouse click handling ---
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # Settings
                name, _, _, ix = icons[0]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    bpy.ops.wm.show_preferences('INVOKE_DEFAULT')
                    return {'RUNNING_MODAL'}
                # Send
                name, _, _, ix = icons[1]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    from . import prompts
                    prompt = prompt_bar_state['text']
                    update_status('Sending prompt...')
                    script = prompts.fetch_script(prompt)
                    try:
                        from . import history
                        history.log_prompt(
                            user_id='local',
                            project_id=getattr(context.scene, 'blendair_project', 'demo'),
                            prompt=prompt,
                            response=script,
                            provider='',
                            model='',
                            token_usage=None,
                            cost_usd=None,
                            latency_ms=None,
                            previous_id=None
                        )
                    except Exception as e:
                        update_status(f'History log failed: {e}')
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
                # Delete
                name, _, _, ix = icons[2]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    prompt_bar_state['text'] = ''
                    prompt_bar_state['caret'] = 0
                    update_status('Prompt cleared.')
                    return {'RUNNING_MODAL'}
                # Copy
                name, _, _, ix = icons[3]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    bpy.context.window_manager.clipboard = prompt_bar_state['text']
                    update_status('Copied to clipboard.')
                    return {'RUNNING_MODAL'}
                # Favorite
                name, _, _, ix = icons[4]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    prompt_bar_state['favorite'] = not prompt_bar_state.get('favorite', False)
                    update_status('Favorited.' if prompt_bar_state['favorite'] else 'Unfavorited.')
                    return {'RUNNING_MODAL'}
                # Undo/Go Back
                name, _, _, ix = icons[5]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    try:
                        from . import history
                        history.go_back()
                        update_status('Undo/go back.')
                    except Exception as e:
                        update_status(f'Undo error: {e}')
                    return {'RUNNING_MODAL'}
                # Gesture
                name, _, _, ix = icons[6]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    try:
                        from . import gestures
                        gestures.toggle_gesture_listener()
                        prompt_bar_state['gesture_active'] = getattr(gestures, 'is_gesture_active', False)
                        update_status('Gesture: ON' if prompt_bar_state['gesture_active'] else 'Gesture: OFF')
                    except Exception as e:
                        update_status(f'Gesture error: {e}')
                    return {'RUNNING_MODAL'}
                # Voice
                name, _, _, ix = icons[7]
                if ix <= x <= ix+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                    prompt_bar_state['voice_active'] = not prompt_bar_state.get('voice_active', False)
                    update_status('Voice: ON (not yet implemented)' if prompt_bar_state['voice_active'] else 'Voice: OFF')
                    return {'RUNNING_MODAL'}
                # Info/help icon (left)
                if not getattr(scene, 'blendair_onboarding_complete', False):
                    if info_x <= x <= info_x+icon_size and y0+bar_h-40 <= y <= y0+bar_h-16:
                        bpy.ops.blendair.onboarding('INVOKE_DEFAULT')
                        return {'RUNNING_MODAL'}
                # Drag background (not on icons)
                icon_right = right_x - icon_gap*8
                if x0 <= x <= icon_right and y0 <= y <= y0+bar_h:
                    prompt_bar_state['dragging'] = True
                    prompt_bar_state['drag_offset'] = [x - x0, y - y0]
                    return {'RUNNING_MODAL'}
            elif event.value == 'RELEASE':
                prompt_bar_state['dragging'] = False
                return {'RUNNING_MODAL'}
        # Drag move
        if event.type == 'MOUSEMOVE' and prompt_bar_state.get('dragging', False):
            dx = x - prompt_bar_state['drag_offset'][0]
            dy = y - prompt_bar_state['drag_offset'][1]
            prompt_bar_state['pos'] = [dx, dy]
            return {'RUNNING_MODAL'}
        # --- Keyboard ---
        if event.type == 'ESC':
            prompt_bar_state['visible'] = False
            update_status('')
            return {'FINISHED'}
        if event.type == 'RET' and event.value == 'PRESS':
            # Same as Send
            from . import prompts
            prompt = prompt_bar_state['text']
            update_status('Sending prompt...')
            script = prompts.fetch_script(prompt)
            try:
                from . import history
                history.log_prompt(
                    user_id='local',
                    project_id=getattr(context.scene, 'blendair_project', 'demo'),
                    prompt=prompt,
                    response=script,
                    provider='',
                    model='',
                    token_usage=None,
                    cost_usd=None,
                    latency_ms=None,
                    previous_id=None
                )
            except Exception as e:
                update_status(f'History log failed: {e}')
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
        if (event.ctrl and event.type == 'Z' and event.value == 'PRESS'):
            try:
                from . import history
                history.go_back()
                update_status('Undo/go back.')
            except Exception as e:
                update_status(f'Undo error: {e}')
            return {'RUNNING_MODAL'}
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
            prompt_bar_state['text'] = (
                prompt_bar_state['text'][:prompt_bar_state['caret']] +
                event.ascii +
                prompt_bar_state['text'][prompt_bar_state['caret']:]
            )
            prompt_bar_state['caret'] += 1
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

