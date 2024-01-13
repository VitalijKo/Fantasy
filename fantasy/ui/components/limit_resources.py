import gradio
import fantasy.globals
from fantasy import wording

MAX_MEMORY_SLIDER = None


def render():
	global MAX_MEMORY_SLIDER

	MAX_MEMORY_SLIDER = gradio.Slider(
		label=wording.get('max_memory_slider_label'),
		minimum=0,
		maximum=128,
		step=1
	)


def listen():
	MAX_MEMORY_SLIDER.change(update_max_memory, inputs=MAX_MEMORY_SLIDER, outputs=MAX_MEMORY_SLIDER)


def update_max_memory(max_memory):
	fantasy.globals.max_memory = max_memory if max_memory > 0 else None

	return gradio.update(value=max_memory)
