import gradio
import vitswap.choices
import vitswap.globals
from vitswap import wording
from vitswap.ui import core as ui
from vitswap.utilities import is_video

TEMP_FRAME_FORMAT_DROPDOWN = None
TEMP_FRAME_QUALITY_SLIDER = None


def render():
	global TEMP_FRAME_FORMAT_DROPDOWN
	global TEMP_FRAME_QUALITY_SLIDER

	TEMP_FRAME_FORMAT_DROPDOWN = gradio.Dropdown(
		label=wording.get('temp_frame_format_dropdown_label'),
		choices=vitswap.choices.temp_frame_format,
		value=vitswap.globals.temp_frame_format,
		visible=is_video(vitswap.globals.target_path)
	)
	TEMP_FRAME_QUALITY_SLIDER = gradio.Slider(
		label=wording.get('temp_frame_quality_slider_label'),
		value=vitswap.globals.temp_frame_quality,
		step=1,
		visible=is_video(vitswap.globals.target_path)
	)


def listen():
	TEMP_FRAME_FORMAT_DROPDOWN.select(update_temp_frame_format, inputs=TEMP_FRAME_FORMAT_DROPDOWN, outputs=TEMP_FRAME_FORMAT_DROPDOWN)
	TEMP_FRAME_QUALITY_SLIDER.change(update_temp_frame_quality, inputs=TEMP_FRAME_QUALITY_SLIDER, outputs=TEMP_FRAME_QUALITY_SLIDER)

	target_video = ui.get_component('target_video')

	if target_video:
		for method in ['upload', 'change', 'clear']:
			getattr(target_video, method)(remote_update, outputs=[TEMP_FRAME_FORMAT_DROPDOWN, TEMP_FRAME_QUALITY_SLIDER])


def remote_update():
	if is_video(vitswap.globals.target_path):
		return gradio.update(visible=True), gradio.update(visible=True)

	return gradio.update(visible=False), gradio.update(visible=False)


def update_temp_frame_format(temp_frame_format):
	vitswap.globals.temp_frame_format = temp_frame_format

	return gradio.update(value=temp_frame_format)


def update_temp_frame_quality(temp_frame_quality):
	vitswap.globals.temp_frame_quality = temp_frame_quality

	return gradio.update(value=temp_frame_quality)
