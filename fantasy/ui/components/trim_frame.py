import gradio
import fantasy.globals
from fantasy import wording
from fantasy.vision import count_video_frame_total
from fantasy.ui import core as ui
from fantasy.utilities import is_video

TRIM_FRAME_START_SLIDER = None
TRIM_FRAME_END_SLIDER = None


def render():
	global TRIM_FRAME_START_SLIDER
	global TRIM_FRAME_END_SLIDER

	trim_frame_start_slider_args = {
		'label': wording.get('trim_frame_start_slider_label'),
		'step': 1,
		'visible': False
	}
	trim_frame_end_slider_args = {
		'label': wording.get('trim_frame_end_slider_label'),
		'step': 1,
		'visible': False
	}

	if is_video(fantasy.globals.target_path):
		video_frame_total = count_video_frame_total(fantasy.globals.target_path)

		trim_frame_start_slider_args['value'] = fantasy.globals.trim_frame_start or 0
		trim_frame_start_slider_args['maximum'] = video_frame_total
		trim_frame_start_slider_args['visible'] = True

		trim_frame_end_slider_args['value'] = fantasy.globals.trim_frame_end or video_frame_total
		trim_frame_end_slider_args['maximum'] = video_frame_total
		trim_frame_end_slider_args['visible'] = True

	TRIM_FRAME_START_SLIDER = gradio.Slider(**trim_frame_start_slider_args)
	TRIM_FRAME_END_SLIDER = gradio.Slider(**trim_frame_end_slider_args)


def listen():
	TRIM_FRAME_START_SLIDER.change(update_trim_frame_start, inputs=TRIM_FRAME_START_SLIDER, outputs=TRIM_FRAME_START_SLIDER)
	TRIM_FRAME_END_SLIDER.change(update_trim_frame_end, inputs=TRIM_FRAME_END_SLIDER, outputs=TRIM_FRAME_END_SLIDER)

	target_video = ui.get_component('target_video')

	if target_video:
		for method in ['upload', 'change', 'clear']:
			getattr(target_video, method)(remote_update, outputs=[TRIM_FRAME_START_SLIDER, TRIM_FRAME_END_SLIDER])


def remote_update():
	if is_video(fantasy.globals.target_path):
		video_frame_total = count_video_frame_total(fantasy.globals.target_path)

		fantasy.globals.trim_frame_start = None
		fantasy.globals.trim_frame_end = None

		return gradio.update(value=0, maximum=video_frame_total, visible=True), gradio.update(value=video_frame_total, maximum=video_frame_total, visible=True)

	return gradio.update(value=None, maximum=None, visible=False), gradio.update(value=None, maximum=None, visible=False)


def update_trim_frame_start(trim_frame_start):
	fantasy.globals.trim_frame_start = trim_frame_start if trim_frame_start > 0 else None

	return gradio.update(value = trim_frame_start)


def update_trim_frame_end(trim_frame_end):
	video_frame_total = count_video_frame_total(fantasy.globals.target_path)

	fantasy.globals.trim_frame_end = trim_frame_end if trim_frame_end < video_frame_total else None

	return gradio.update(value = trim_frame_end)
