import gradio
import fantasy.globals
from fantasy import wording

EXECUTION_QUEUE_COUNT_SLIDER = None


def render():
	global EXECUTION_QUEUE_COUNT_SLIDER

	EXECUTION_QUEUE_COUNT_SLIDER = gradio.Slider(
		label=wording.get('execution_queue_count_slider_label'),
		value=fantasy.globals.execution_queue_count,
		step=1,
		minimum=1,
		maximum=16
	)


def listen():
	EXECUTION_QUEUE_COUNT_SLIDER.change(update_execution_queue_count, inputs=EXECUTION_QUEUE_COUNT_SLIDER, outputs=EXECUTION_QUEUE_COUNT_SLIDER)


def update_execution_queue_count(execution_queue_count=1):
	fantasy.globals.execution_queue_count = execution_queue_count

	return gradio.update(value=execution_queue_count)
