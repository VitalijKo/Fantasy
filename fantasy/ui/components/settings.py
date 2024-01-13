import gradio
import fantasy.globals
from fantasy import wording
from fantasy.ui import choices

SETTINGS_CHECKBOX_GROUP = None


def render():
	global SETTINGS_CHECKBOX_GROUP

	value = []

	if fantasy.globals.keep_fps:
		value.append('keep-fps')

	if fantasy.globals.keep_temp:
		value.append('keep-temp')

	if fantasy.globals.skip_audio:
		value.append('skip-audio')

	if fantasy.globals.skip_download:
		value.append('skip-download')

	SETTINGS_CHECKBOX_GROUP = gradio.Checkboxgroup(
		label=wording.get('settings_checkbox_group_label'),
		choices=choices.settings,
		value=value
	)


def listen():
	SETTINGS_CHECKBOX_GROUP.change(update, inputs=SETTINGS_CHECKBOX_GROUP, outputs=SETTINGS_CHECKBOX_GROUP)


def update(settings):
	fantasy.globals.keep_fps = 'keep-fps' in settings
	fantasy.globals.keep_temp ='keep-temp' in settings
	fantasy.globals.skip_audio = 'skip-audio' in settings
	fantasy.globals.skip_download = 'skip-download' in settings

	return gradio.update(value=settings)
