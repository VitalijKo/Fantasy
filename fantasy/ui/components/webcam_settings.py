import gradio
from fantasy import wording
from fantasy.ui import choices
from fantasy.ui import core as ui

WEBCAM_MODE_RADIO = None
WEBCAM_RESOLUTION_DROPDOWN = None
WEBCAM_FPS_SLIDER = None


def render():
	global WEBCAM_MODE_RADIO
	global WEBCAM_RESOLUTION_DROPDOWN
	global WEBCAM_FPS_SLIDER

	WEBCAM_MODE_RADIO = gradio.Radio(
		label = wording.get('webcam_mode_radio_label'),
		choices = choices.webcam_mode,
		value = 'inline'
	)
	WEBCAM_RESOLUTION_DROPDOWN = gradio.Dropdown(
		label = wording.get('webcam_resolution_dropdown'),
		choices = choices.webcam_resolution,
		value = choices.webcam_resolution[0]
	)
	WEBCAM_FPS_SLIDER = gradio.Slider(
		label = wording.get('webcam_fps_slider'),
		minimum = 1,
		maximum = 60,
		step = 1,
		value = 25
	)

	ui.register_component('webcam_mode_radio', WEBCAM_MODE_RADIO)
	ui.register_component('webcam_resolution_dropdown', WEBCAM_RESOLUTION_DROPDOWN)
	ui.register_component('webcam_fps_slider', WEBCAM_FPS_SLIDER)


def update():
	return gradio.update(value=None)
