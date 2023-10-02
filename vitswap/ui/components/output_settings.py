import gradio
import vitswap.choices
import vitswap.globals
from vitswap import wording
from vitswap.ui import core as ui
from vitswap.utilities import is_image, is_video

OUTPUT_IMAGE_QUALITY_SLIDER = None
OUTPUT_VIDEO_ENCODER_DROPDOWN = None
OUTPUT_VIDEO_QUALITY_SLIDER = None


def render():
	global OUTPUT_IMAGE_QUALITY_SLIDER
	global OUTPUT_VIDEO_ENCODER_DROPDOWN
	global OUTPUT_VIDEO_QUALITY_SLIDER

	OUTPUT_IMAGE_QUALITY_SLIDER = gradio.Slider(
		label=wording.get('output_image_quality_slider_label'),
		value=vitswap.globals.output_image_quality,
		step=1,
		visible=is_image(vitswap.globals.target_path)
	)
	OUTPUT_VIDEO_ENCODER_DROPDOWN = gradio.Dropdown(
		label=wording.get('output_video_encoder_dropdown_label'),
		choices=vitswap.choices.output_video_encoder,
		value=vitswap.globals.output_video_encoder,
		visible=is_video(vitswap.globals.target_path)
	)
	OUTPUT_VIDEO_QUALITY_SLIDER = gradio.Slider(
		label=wording.get('output_video_quality_slider_label'),
		value=vitswap.globals.output_video_quality,
		step=1,
		visible=is_video(vitswap.globals.target_path)
	)


def listen():
	OUTPUT_IMAGE_QUALITY_SLIDER.change(update_output_image_quality, inputs=OUTPUT_IMAGE_QUALITY_SLIDER, outputs=OUTPUT_IMAGE_QUALITY_SLIDER)
	OUTPUT_VIDEO_ENCODER_DROPDOWN.select(update_output_video_encoder, inputs=OUTPUT_VIDEO_ENCODER_DROPDOWN, outputs=OUTPUT_VIDEO_ENCODER_DROPDOWN)
	OUTPUT_VIDEO_QUALITY_SLIDER.change(update_output_video_quality, inputs=OUTPUT_VIDEO_QUALITY_SLIDER, outputs=OUTPUT_VIDEO_QUALITY_SLIDER)

	multi_component_names = [
		'source_image',
		'target_image',
		'target_video'
	]

	for component_name in multi_component_names:
		component = ui.get_component(component_name)

		if component:
			for method in ['upload', 'change', 'clear']:
				getattr(component, method)(remote_update, outputs=[OUTPUT_IMAGE_QUALITY_SLIDER, OUTPUT_VIDEO_ENCODER_DROPDOWN, OUTPUT_VIDEO_QUALITY_SLIDER])


def remote_update():
	if is_image(vitswap.globals.target_path):
		return gradio.update(visible=True), gradio.update(visible=False), gradio.update(visible=False)

	if is_video(vitswap.globals.target_path):
		return gradio.update(visible=False), gradio.update(visible=True), gradio.update(visible=True)

	return gradio.update(visible=False), gradio.update(visible=False), gradio.update(visible=False)


def update_output_image_quality(output_image_quality):
	vitswap.globals.output_image_quality = output_image_quality

	return gradio.update(value = output_image_quality)


def update_output_video_encoder(output_video_encoder):
	vitswap.globals.output_video_encoder = output_video_encoder

	return gradio.update(value = output_video_encoder)


def update_output_video_quality(output_video_quality):
	vitswap.globals.output_video_quality = output_video_quality

	return gradio.update(value = output_video_quality)
