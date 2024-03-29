import cv2
import gradio
import fantasy.globals
from fantasy import wording
from fantasy.vision import get_video_frame, count_video_frame_total, normalize_frame_color, resize_frame_dimension, read_static_image
from fantasy.face_analyser import get_one_face
from fantasy.face_reference import get_face_reference, set_face_reference
from fantasy.processors.frame.core import load_frame_processor_module
from fantasy.ui import core as ui
from fantasy.utilities import is_video, is_image

PREVIEW_IMAGE = None
PREVIEW_FRAME_SLIDER = None


def render():
	global PREVIEW_IMAGE
	global PREVIEW_FRAME_SLIDER

	preview_image_args = {
		'label': wording.get('preview_image_label')
	}
	preview_frame_slider_args = {
		'label': wording.get('preview_frame_slider_label'),
		'step': 1,
		'visible': False
	}

	conditional_set_face_reference()

	source_face = get_one_face(read_static_image(fantasy.globals.source_path))
	reference_face = get_face_reference() if 'reference' in fantasy.globals.face_recognition else None

	if is_image(fantasy.globals.target_path):
		target_frame = read_static_image(fantasy.globals.target_path)
		preview_frame = process_preview_frame(source_face, reference_face, target_frame)

		preview_image_args['value'] = normalize_frame_color(preview_frame)

	if is_video(fantasy.globals.target_path):
		temp_frame = get_video_frame(fantasy.globals.target_path, fantasy.globals.reference_frame_number)

		preview_frame = process_preview_frame(source_face, reference_face, temp_frame)

		preview_image_args['value'] = normalize_frame_color(preview_frame)
		preview_image_args['visible'] = True

		preview_frame_slider_args['value'] = fantasy.globals.reference_frame_number
		preview_frame_slider_args['maximum'] = count_video_frame_total(fantasy.globals.target_path)
		preview_frame_slider_args['visible'] = True

	PREVIEW_IMAGE = gradio.Image(**preview_image_args)
	PREVIEW_FRAME_SLIDER = gradio.Slider(**preview_frame_slider_args)
	ui.register_component('preview_frame_slider', PREVIEW_FRAME_SLIDER)


def listen():
	PREVIEW_FRAME_SLIDER.change(update_preview_image, inputs=PREVIEW_FRAME_SLIDER, outputs=PREVIEW_IMAGE)

	multi_component_names = [
		'source_image',
		'target_image',
		'target_video'
	]

	for component_name in multi_component_names:
		component = ui.get_component(component_name)

		if component:
			for method in ['upload', 'change', 'clear']:
				getattr(component, method)(update_preview_image, inputs=PREVIEW_FRAME_SLIDER, outputs=PREVIEW_IMAGE)
				getattr(component, method)(update_preview_frame_slider, inputs=PREVIEW_FRAME_SLIDER, outputs=PREVIEW_FRAME_SLIDER)

	update_component_names = [
		'face_recognition_dropdown',
		'frame_processors_checkbox_group'
	]

	for component_name in update_component_names:
		component = ui.get_component(component_name)

		if component:
			component.change(update_preview_image, inputs=PREVIEW_FRAME_SLIDER, outputs=PREVIEW_IMAGE)

	select_component_names = [
		'reference_face_position_gallery',
		'face_analyser_direction_dropdown',
		'face_analyser_age_dropdown',
		'face_analyser_gender_dropdown'
	]

	for component_name in select_component_names:
		component = ui.get_component(component_name)

		if component:
			component.select(update_preview_image, inputs=PREVIEW_FRAME_SLIDER, outputs=PREVIEW_IMAGE)

	reference_face_distance_slider = ui.get_component('reference_face_distance_slider')

	if reference_face_distance_slider:
		reference_face_distance_slider.change(update_preview_image, inputs=PREVIEW_FRAME_SLIDER, outputs=PREVIEW_IMAGE)


def update_preview_image(frame_number=0):
	conditional_set_face_reference()

	source_face = get_one_face(read_static_image(fantasy.globals.source_path))
	reference_face = get_face_reference() if 'reference' in fantasy.globals.face_recognition else None

	if is_image(fantasy.globals.target_path):
		target_frame = read_static_image(fantasy.globals.target_path)
		preview_frame = process_preview_frame(source_face, reference_face, target_frame)
		preview_frame = normalize_frame_color(preview_frame)

		return gradio.update(value=preview_frame)

	if is_video(fantasy.globals.target_path):
		fantasy.globals.reference_frame_number = frame_number

		temp_frame = get_video_frame(fantasy.globals.target_path, fantasy.globals.reference_frame_number)
		preview_frame = process_preview_frame(source_face, reference_face, temp_frame)
		preview_frame = normalize_frame_color(preview_frame)

		return gradio.update(value=preview_frame)

	return gradio.update(value=None)


def update_preview_frame_slider(frame_number=0):
	if is_image(fantasy.globals.target_path):
		return gradio.update(value=None, maximum=None, visible=False)

	if is_video(fantasy.globals.target_path):
		fantasy.globals.reference_frame_number = frame_number

		video_frame_total = count_video_frame_total(fantasy.globals.target_path)

		return gradio.update(maximum=video_frame_total, visible=True)

	return gradio.update(value=None, maximum=None, visible=False)


def process_preview_frame(source_face, reference_face, temp_frame):
	temp_frame = resize_frame_dimension(temp_frame, 480)

	for frame_processor in fantasy.globals.frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)

		if frame_processor_module.pre_process('preview'):
			temp_frame = frame_processor_module.process_frame(
				source_face,
				reference_face,
				temp_frame
			)

	return temp_frame


def conditional_set_face_reference():
	if 'reference' in fantasy.globals.face_recognition and not get_face_reference():
		reference_frame = get_video_frame(fantasy.globals.target_path, fantasy.globals.reference_frame_number)
		reference_face = get_one_face(reference_frame, fantasy.globals.reference_face_position)

		set_face_reference(reference_face)
