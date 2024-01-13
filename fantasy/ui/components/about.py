import gradio
from fantasy import metadata

ABOUT_HTML = None


def render():
	global ABOUT_HTML

	ABOUT_HTML = gradio.HTML('<center><a href="' + metadata.get('url') + '">' + metadata.get('name') + ' ' + metadata.get('version') + '</a></center>')
