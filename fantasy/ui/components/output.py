import gradio
import tempfile
import fantasy.globals
from fantasy import wording
from fantasy.core import limit_resources, conditional_process
from fantasy.utilities import is_image, is_video, normalize_output_path, clear_temp

OUTPUT_IMAGE = None
OUTPUT_VIDEO = None
OUTPUT_PATH_TEXTBOX  = None
OUTPUT_START_BUTTON = None
OUTPUT_CLEAR_BUTTON = None


def render():
	global OUTPUT_IMAGE
	global OUTPUT_VIDEO
	global OUTPUT_PATH_TEXTBOX
	global OUTPUT_START_BUTTON
	global OUTPUT_CLEAR_BUTTON

	OUTPUT_IMAGE = gradio.Image(
		label = wording.get('output_image_or_video_label'),
		visible = False
	)
	OUTPUT_VIDEO = gradio.Video(
		label = wording.get('output_image_or_video_label')
	)
	OUTPUT_PATH_TEXTBOX = gradio.Textbox(
		label = wording.get('output_path_textbox_label'),
		value = fantasy.globals.output_path or tempfile.gettempdir(),
		max_lines = 1
	)
	OUTPUT_START_BUTTON = gradio.Button(
		value = wording.get('start_button_label'),
		variant = 'primary'
	)
	OUTPUT_CLEAR_BUTTON = gradio.Button(
		value = wording.get('clear_button_label')
	)


def listen():
	OUTPUT_PATH_TEXTBOX.change(update_output_path, inputs=OUTPUT_PATH_TEXTBOX, outputs=OUTPUT_PATH_TEXTBOX)
	OUTPUT_START_BUTTON.click(start, inputs=OUTPUT_PATH_TEXTBOX, outputs=[OUTPUT_IMAGE, OUTPUT_VIDEO])
	OUTPUT_CLEAR_BUTTON.click(clear, outputs=[OUTPUT_IMAGE, OUTPUT_VIDEO])


def start(output_path):
	fantasy.globals.output_path = normalize_output_path(fantasy.globals.source_path, fantasy.globals.target_path, output_path)

	limit_resources()
	conditional_process()

	if is_image(fantasy.globals.output_path):
		return gradio.update(value=fantasy.globals.output_path, visible=True), gradio.update(value=None, visible=False)

	if is_video(fantasy.globals.output_path):
		return gradio.update(value=None, visible=False), gradio.update(value=fantasy.globals.output_path, visible=True)

	return gradio.update(), gradio.update()


def update_output_path(output_path):
	fantasy.globals.output_path = output_path

	return gradio.update(value = output_path)


def clear():
	if fantasy.globals.target_path:
		clear_temp(fantasy.globals.target_path)

	return gradio.update(value=None), gradio.update(value=None)
