import gradio
import vitswap.globals
from vitswap import wording

EXECUTION_THREAD_COUNT_SLIDER = None


def render():
	global EXECUTION_THREAD_COUNT_SLIDER

	EXECUTION_THREAD_COUNT_SLIDER = gradio.Slider(
		label=wording.get('execution_thread_count_slider_label'),
		value=vitswap.globals.execution_thread_count,
		step=1,
		minimum=1,
		maximum=128
	)


def listen():
	EXECUTION_THREAD_COUNT_SLIDER.change(update_execution_thread_count, inputs=EXECUTION_THREAD_COUNT_SLIDER, outputs=EXECUTION_THREAD_COUNT_SLIDER)


def update_execution_thread_count(execution_thread_count=1):
	vitswap.globals.execution_thread_count = execution_thread_count

	return gradio.update(value = execution_thread_count)
