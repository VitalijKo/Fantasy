import onnxruntime
import gradio
import vitswap.globals
from vitswap import wording
from vitswap.face_analyser import clear_face_analyser
from vitswap.processors.frame.core import clear_frame_processors_modules
from vitswap.utilities import encode_execution_providers, decode_execution_providers

EXECUTION_PROVIDERS_CHECKBOX_GROUP = None


def render():
	global EXECUTION_PROVIDERS_CHECKBOX_GROUP

	EXECUTION_PROVIDERS_CHECKBOX_GROUP = gradio.CheckboxGroup(
		label=wording.get('execution_providers_checkbox_group_label'),
		choices=encode_execution_providers(onnxruntime.get_available_providers()),
		value=encode_execution_providers(vitswap.globals.execution_providers)
	)


def listen():
	EXECUTION_PROVIDERS_CHECKBOX_GROUP.change(update_execution_providers, inputs=EXECUTION_PROVIDERS_CHECKBOX_GROUP, outputs=EXECUTION_PROVIDERS_CHECKBOX_GROUP)


def update_execution_providers(execution_providers):
	clear_face_analyser()
	clear_frame_processors_modules()

	if not execution_providers:
		execution_providers = encode_execution_providers(onnxruntime.get_available_providers())

	vitswap.globals.execution_providers = decode_execution_providers(execution_providers)

	return gradio.update(value=execution_providers)
