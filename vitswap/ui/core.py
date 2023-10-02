import importlib
import gradio
import sys
import vitswap.globals
from vitswap import metadata, wording

COMPONENTS = {}
UI_LAYOUT_MODULES = []
UI_LAYOUT_METHODS = ['pre_check', 'pre_render', 'render', 'listen', 'run']


def load_ui_layout_module(ui_layout):
	try:
		ui_layout_module = importlib.import_module(f'vitswap.ui.layouts.{ui_layout}')

		for method_name in UI_LAYOUT_METHODS:
			if not hasattr(ui_layout_module, method_name):
				raise NotImplementedError
	except ModuleNotFoundError:
		sys.exit(wording.get('ui_layout_not_loaded').format(ui_layout=ui_layout))
	except NotImplementedError:
		sys.exit(wording.get('ui_layout_not_implemented').format(ui_layout=ui_layout))

	return ui_layout_module


def get_ui_layouts_modules(ui_layouts):
	global UI_LAYOUT_MODULES

	if not UI_LAYOUT_MODULES:
		for ui_layout in ui_layouts:
			ui_layout_module = load_ui_layout_module(ui_layout)
			UI_LAYOUT_MODULES.append(ui_layout_module)

	return UI_LAYOUT_MODULES


def launch():
	with gradio.Blocks(theme=get_theme(), title=metadata.get('name') + ' ' + metadata.get('version')) as ui:
		for ui_layout in vitswap.globals.ui_layouts:
			ui_layout_module = load_ui_layout_module(ui_layout)

			if ui_layout_module.pre_render():
				ui_layout_module.render()
				ui_layout_module.listen()

	for ui_layout in vitswap.globals.ui_layouts:
		ui_layout_module = load_ui_layout_module(ui_layout)
		ui_layout_module.run(ui)


def get_theme():
	return gradio.themes.Soft(
		primary_hue = gradio.themes.colors.red,
		secondary_hue = gradio.themes.colors.gray,
		font = gradio.themes.GoogleFont('Inter')
	).set(
		background_fill_primary = '*neutral_50',
		block_label_text_size = '*text_sm',
		block_title_text_size = '*text_sm'
	)


def get_component(name):
	if name in COMPONENTS:
		return COMPONENTS[name]


def register_component(name, component):
	COMPONENTS[name] = component
