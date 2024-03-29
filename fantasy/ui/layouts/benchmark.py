import gradio
import fantasy.globals
from fantasy.ui.components import about, processors, execution, execution_thread_count, execution_queue_count, limit_resources, benchmark_settings, benchmark
from fantasy.utilities import conditional_download


def pre_check():
	if not fantasy.globals.skip_download:
		conditional_download('.assets/examples',
		[
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/source.jpg',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-240p.mp4',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-360p.mp4',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-540p.mp4',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-720p.mp4',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-1080p.mp4',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-1440p.mp4',
			'https://github.com/fantasy/fantasy-assets/releases/download/examples/target-2160p.mp4'
		])

		return True

	return False


def pre_render():
	return True


def render():
	with gradio.Blocks() as layout:
		with gradio.Row():
			with gradio.Column(scale=2):
				with gradio.Box():
					about.render()

				with gradio.Blocks():
					processors.render()

				with gradio.Blocks():
					execution.render()
					execution_thread_count.render()
					execution_queue_count.render()

				with gradio.Blocks():
					limit_resources.render()

				with gradio.Blocks():
					benchmark_settings.render()

			with gradio.Column(scale=5):
				with gradio.Blocks():
					benchmark.render()

	return layout


def listen():
	processors.listen()
	execution.listen()
	execution_thread_count.listen()
	execution_queue_count.listen()
	limit_resources.listen()
	benchmark_settings.listen()
	benchmark.listen()


def run(ui):
	ui.queue(concurrency_count=2, api_open=False)
	ui.launch(show_api=False)
