import gradio
import vitswap.globals
from vitswap import wording
from vitswap.ui import core as ui
from vitswap.utilities import is_image

SOURCE_FILE = None
SOURCE_IMAGE = None


def render():
	global SOURCE_FILE
	global SOURCE_IMAGE

	is_source_image = is_image(vitswap.globals.source_path)

	SOURCE_FILE = gradio.File(
		file_count='single',
		file_types=[
			'.png',
			'.jpg',
			'.webp'
		],
		label=wording.get('source_file_label'),
		value=vitswap.globals.source_path if is_source_image else None
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
		vitswap.globals.source_path = file.name

		return gradio.update(value=file.name, visible=True)

	vitswap.globals.source_path = None

	return gradio.update(value=None, visible=False)
