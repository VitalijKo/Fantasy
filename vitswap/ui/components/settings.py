import gradio
import vitswap.globals
from vitswap import wording
from vitswap.ui import choices

SETTINGS_CHECKBOX_GROUP = None


def render():
	global SETTINGS_CHECKBOX_GROUP

	value = []

	if vitswap.globals.keep_fps:
		value.append('keep-fps')

	if vitswap.globals.keep_temp:
		value.append('keep-temp')

	if vitswap.globals.skip_audio:
		value.append('skip-audio')

	if vitswap.globals.skip_download:
		value.append('skip-download')

	SETTINGS_CHECKBOX_GROUP = gradio.Checkboxgroup(
		label=wording.get('settings_checkbox_group_label'),
		choices=choices.settings,
		value=value
	)


def listen():
	SETTINGS_CHECKBOX_GROUP.change(update, inputs=SETTINGS_CHECKBOX_GROUP, outputs=SETTINGS_CHECKBOX_GROUP)


def update(settings):
	vitswap.globals.keep_fps = 'keep-fps' in settings
	vitswap.globals.keep_temp ='keep-temp' in settings
	vitswap.globals.skip_audio = 'skip-audio' in settings
	vitswap.globals.skip_download = 'skip-download' in settings

	return gradio.update(value=settings)
