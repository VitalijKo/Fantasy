import gradio
import vitswap.choices
import vitswap.globals
from vitswap import wording
from vitswap.ui import core as ui

FACE_ANALYSER_DIRECTION_DROPDOWN = None
FACE_ANALYSER_AGE_DROPDOWN = None
FACE_ANALYSER_GENDER_DROPDOWN = None


def render():
	global FACE_ANALYSER_DIRECTION_DROPDOWN
	global FACE_ANALYSER_AGE_DROPDOWN
	global FACE_ANALYSER_GENDER_DROPDOWN

	FACE_ANALYSER_DIRECTION_DROPDOWN = gradio.Dropdown(
		label = wording.get('face_analyser_direction_dropdown_label'),
		choices = vitswap.choices.face_analyser_direction,
		value = vitswap.globals.face_analyser_direction
	)
	FACE_ANALYSER_AGE_DROPDOWN = gradio.Dropdown(
		label = wording.get('face_analyser_age_dropdown_label'),
		choices = ['none'] + vitswap.choices.face_analyser_age,
		value = vitswap.globals.face_analyser_age or 'none'
	)
	FACE_ANALYSER_GENDER_DROPDOWN = gradio.Dropdown(
		label = wording.get('face_analyser_gender_dropdown_label'),
		choices = ['none'] + vitswap.choices.face_analyser_gender,
		value = vitswap.globals.face_analyser_gender or 'none'
	)

	ui.register_component('face_analyser_direction_dropdown', FACE_ANALYSER_DIRECTION_DROPDOWN)
	ui.register_component('face_analyser_age_dropdown', FACE_ANALYSER_AGE_DROPDOWN)
	ui.register_component('face_analyser_gender_dropdown', FACE_ANALYSER_GENDER_DROPDOWN)


def listen():
	FACE_ANALYSER_DIRECTION_DROPDOWN.select(lambda value: update_dropdown('face_analyser_direction', value), inputs=FACE_ANALYSER_DIRECTION_DROPDOWN, outputs=FACE_ANALYSER_DIRECTION_DROPDOWN)
	FACE_ANALYSER_AGE_DROPDOWN.select(lambda value: update_dropdown('face_analyser_age', value), inputs=FACE_ANALYSER_AGE_DROPDOWN, outputs=FACE_ANALYSER_AGE_DROPDOWN)
	FACE_ANALYSER_GENDER_DROPDOWN.select(lambda value: update_dropdown('face_analyser_gender', value), inputs=FACE_ANALYSER_GENDER_DROPDOWN, outputs=FACE_ANALYSER_GENDER_DROPDOWN)


def update_dropdown(name, value):
	if value == 'none':
		setattr(vitswap.globals, name, None)

	else:
		setattr(vitswap.globals, name, value)

	return gradio.update(value=value)
