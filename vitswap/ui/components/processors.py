import gradio
import vitswap.globals
from vitswap import wording
from vitswap.processors.frame.core import load_frame_processor_module, clear_frame_processors_modules
from vitswap.ui import core as ui
from vitswap.utilities import list_module_names

FRAME_PROCESSORS_CHECKBOX_GROUP = None


def render():
	global FRAME_PROCESSORS_CHECKBOX_GROUP

	FRAME_PROCESSORS_CHECKBOX_GROUP = gradio.CheckboxGroup(
		label = wording.get('frame_processors_checkbox_group_label'),
		choices = sort_frame_processors(vitswap.globals.frame_processors),
		value = vitswap.globals.frame_processors
	)

	ui.register_component('frame_processors_checkbox_group', FRAME_PROCESSORS_CHECKBOX_GROUP)


def listen():
	FRAME_PROCESSORS_CHECKBOX_GROUP.change(update_frame_processors, inputs=FRAME_PROCESSORS_CHECKBOX_GROUP, outputs=FRAME_PROCESSORS_CHECKBOX_GROUP)


def update_frame_processors(frame_processors):
	clear_frame_processors_modules()

	vitswap.globals.frame_processors = frame_processors

	for frame_processor in frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)

		if not frame_processor_module.pre_check():
			return gradio.update()

	return gradio.update(value=frame_processors, choices=sort_frame_processors(frame_processors))


def sort_frame_processors(frame_processors):
	frame_processors_names = list_module_names('vitswap/processors/frame/modules')

	return sorted(frame_processors_names, key=lambda frame_processor: frame_processors.index(frame_processor) if frame_processor in frame_processors else len(frame_processors))
