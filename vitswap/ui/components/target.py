import gradio
import vitswap.globals
from vitswap import wording
from vitswap.face_reference import clear_face_reference
from vitswap.ui import core as ui
from vitswap.utilities import is_image, is_video

TARGET_FILE = None
TARGET_IMAGE = None
TARGET_VIDEO = None


def render():
	global TARGET_FILE
	global TARGET_IMAGE
	global TARGET_VIDEO

	is_target_image = is_image(vitswap.globals.target_path)
	is_target_video = is_video(vitswap.globals.target_path)

	TARGET_FILE = gradio.File(
		label=wording.get('target_file_label'),
		file_count='single',
		file_types=[
			'.png',
			'.jpg',
			'.webp',
			'.mp4'
		],
		value = vitswap.globals.target_path if is_target_image or is_target_video else None
	)
	TARGET_IMAGE = gradio.Image(
		value=TARGET_FILE.value['name'] if is_target_image else None,
		visible=is_target_image,
		show_label=False
	)
	TARGET_VIDEO = gradio.Video(
		value=TARGET_FILE.value['name'] if is_target_video else None,
		visible=is_target_video,
		show_label=False
	)

	ui.register_component('target_image', TARGET_IMAGE)
	ui.register_component('target_video', TARGET_VIDEO)


def listen():
	TARGET_FILE.change(update, inputs=TARGET_FILE, outputs=[TARGET_IMAGE, TARGET_VIDEO])


def update(file):
	clear_face_reference()

	if file and is_image(file.name):
		vitswap.globals.target_path = file.name

		return gradio.update(value=file.name, visible=True), gradio.update(value=None, visible=False)

	if file and is_video(file.name):
		vitswap.globals.target_path = file.name

		return gradio.update(value=None, visible=False), gradio.update(value=file.name, visible=True)

	vitswap.globals.target_path = None

	return gradio.update(value=None, visible=False), gradio.update(value=None, visible=False)
