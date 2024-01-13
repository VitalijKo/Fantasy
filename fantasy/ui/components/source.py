import gradio
import fantasy.globals
from fantasy import wording
from fantasy.ui import core as ui
from fantasy.utilities import is_image

SOURCE_FILE = None
SOURCE_IMAGE = None


def render():
	global SOURCE_FILE
	global SOURCE_IMAGE

	is_source_image = is_image(fantasy.globals.source_path)

	SOURCE_FILE = gradio.File(
		file_count='single',
		file_types=[
			'.png',
			'.jpg',
			'.webp'
		],
		label=wording.get('source_file_label'),
		value=fantasy.globals.source_path if is_source_image else None
	)
	SOURCE_IMAGE = gradio.Image(
		value=SOURCE_FILE.value['name'] if is_source_image else None,
		visible=is_source_image,
		show_label=False
	)
	
	ui.register_component('source_image', SOURCE_IMAGE)


def listen():
	SOURCE_FILE.change(update, inputs=SOURCE_FILE, outputs=SOURCE_IMAGE)


def update(file):
	if file and is_image(file.name):
		fantasy.globals.source_path = file.name

		return gradio.update(value=file.name, visible=True)

	fantasy.globals.source_path = None

	return gradio.update(value=None, visible=False)
