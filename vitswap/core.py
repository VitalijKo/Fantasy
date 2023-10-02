import os

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow
import onnxruntime
import shutil
import sys
import platform
import argparse
import signal
import warnings
import vitswap.choices
import vitswap.globals
from vitswap import wording, metadata
from vitswap.processors.frame.core import get_frame_processors_modules
from vitswap.utilities import is_image, is_video, detect_fps, compress_image, merge_video, extract_frames, get_temp_frame_paths, restore_audio, create_temp, move_temp, clear_temp, normalize_output_path, list_module_names, decode_execution_providers, encode_execution_providers

warnings.filterwarnings('ignore', category=FutureWarning, module='insightface')
warnings.filterwarnings('ignore', category= UserWarning, module='torchvision')


def parse_args():
	signal.signal(signal.SIGINT, lambda signal_number, frame: destroy())
	program = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=120))
	program.add_argument('-s', '--source', help=wording.get('source_help'), dest='source_path')
	program.add_argument('-t', '--target', help=wording.get('target_help'), dest='target_path')
	program.add_argument('-o', '--output', help=wording.get('output_help'), dest='output_path')
	program.add_argument('--frame-processors', help=wording.get('frame_processors_help').format(choices=', '.join(list_module_names('vitswap/processors/frame/modules'))), dest='frame_processors', default=['face_swapper'], nargs='+')
	program.add_argument('--ui-layouts', help=wording.get('ui_layouts_help').format(choices=', '.join(list_module_names('vitswap/ui/layouts'))), dest='ui_layouts', default=['default'], nargs='+')
	program.add_argument('--keep-fps', help=wording.get('keep_fps_help'), dest='keep_fps', action='store_true')
	program.add_argument('--keep-temp', help=wording.get('keep_temp_help'), dest='keep_temp', action='store_true')
	program.add_argument('--skip-audio', help=wording.get('skip_audio_help'), dest='skip_audio', action='store_true')
	program.add_argument('--face-recognition', help=wording.get('face_recognition_help'), dest='face_recognition', default='reference', choices=vitswap.choices.face_recognition)
	program.add_argument('--face-analyser-direction', help=wording.get('face_analyser_direction_help'), dest='face_analyser_direction', default='left-right', choices=vitswap.choices.face_analyser_direction)
	program.add_argument('--face-analyser-age', help=wording.get('face_analyser_age_help'), dest='face_analyser_age', choices=vitswap.choices.face_analyser_age)
	program.add_argument('--face-analyser-gender', help=wording.get('face_analyser_gender_help'), dest='face_analyser_gender', choices=vitswap.choices.face_analyser_gender)
	program.add_argument('--reference-face-position', help=wording.get('reference_face_position_help'), dest='reference_face_position', type=int, default=0)
	program.add_argument('--reference-face-distance', help=wording.get('reference_face_distance_help'), dest='reference_face_distance', type=float, default=1.5)
	program.add_argument('--reference-frame-number', help=wording.get('reference_frame_number_help'), dest='reference_frame_number', type=int, default=0)
	program.add_argument('--trim-frame-start', help=wording.get('trim_frame_start_help'), dest='trim_frame_start', type=int)
	program.add_argument('--trim-frame-end', help=wording.get('trim_frame_end_help'), dest='trim_frame_end', type=int)
	program.add_argument('--temp-frame-format', help=wording.get('temp_frame_format_help'), dest='temp_frame_format', default='jpg', choices=vitswap.choices.temp_frame_format)
	program.add_argument('--temp-frame-quality', help=wording.get('temp_frame_quality_help'), dest='temp_frame_quality', type=int, default=100, choices=range(101), metavar='[0-100]')
	program.add_argument('--output-image-quality', help=wording.get('output_image_quality_help'), dest='output_image_quality', type=int, default=90, choices=range(101), metavar='[0-100]')
	program.add_argument('--output-video-encoder', help=wording.get('output_video_encoder_help'), dest='output_video_encoder', default='libx264', choices=vitswap.choices.output_video_encoder)
	program.add_argument('--output-video-quality', help=wording.get('output_video_quality_help'), dest='output_video_quality', type=int, default=90, choices=range(101), metavar='[0-100]')
	program.add_argument('--max-memory', help=wording.get('max_memory_help'), dest='max_memory', type=int)
	program.add_argument('--execution-providers', help=wording.get('execution_providers_help').format(choices='cpu'), dest='execution_providers', default=['cpu'], choices=suggest_execution_providers_choices(), nargs='+')
	program.add_argument('--execution-thread-count', help=wording.get('execution_thread_count_help'), dest='execution_thread_count', type=int, default=suggest_execution_thread_count_default())
	program.add_argument('--execution-queue-count', help=wording.get('execution_queue_count_help'), dest='execution_queue_count', type=int, default=1)
	program.add_argument('--skip-download', help=wording.get('skip_download_help'), dest='skip_download', action='store_true')
	program.add_argument('--headless', help=wording.get('headless_help'), dest='headless', action='store_true')
	program.add_argument('-v', '--version', version=metadata.get('name') + ' ' + metadata.get('version'), action='version')

	args = program.parse_args()

	vitswap.globals.source_path = args.source_path
	vitswap.globals.target_path = args.target_path
	vitswap.globals.output_path = normalize_output_path(vitswap.globals.source_path, vitswap.globals.target_path, args.output_path)
	vitswap.globals.frame_processors = args.frame_processors
	vitswap.globals.ui_layouts = args.ui_layouts
	vitswap.globals.keep_fps = args.keep_fps
	vitswap.globals.keep_temp = args.keep_temp
	vitswap.globals.skip_audio = args.skip_audio
	vitswap.globals.face_recognition = args.face_recognition
	vitswap.globals.face_analyser_direction = args.face_analyser_direction
	vitswap.globals.face_analyser_age = args.face_analyser_age
	vitswap.globals.face_analyser_gender = args.face_analyser_gender
	vitswap.globals.reference_face_position = args.reference_face_position
	vitswap.globals.reference_frame_number = args.reference_frame_number
	vitswap.globals.reference_face_distance = args.reference_face_distance
	vitswap.globals.trim_frame_start = args.trim_frame_start
	vitswap.globals.trim_frame_end = args.trim_frame_end
	vitswap.globals.temp_frame_format = args.temp_frame_format
	vitswap.globals.temp_frame_quality = args.temp_frame_quality
	vitswap.globals.output_image_quality = args.output_image_quality
	vitswap.globals.output_video_encoder = args.output_video_encoder
	vitswap.globals.output_video_quality = args.output_video_quality
	vitswap.globals.max_memory = args.max_memory
	vitswap.globals.execution_providers = decode_execution_providers(args.execution_providers)
	vitswap.globals.execution_thread_count = args.execution_thread_count
	vitswap.globals.execution_queue_count = args.execution_queue_count
	vitswap.globals.skip_download = args.skip_download
	vitswap.globals.headless = args.headless


def suggest_execution_providers_choices():
	return encode_execution_providers(onnxruntime.get_available_providers())


def suggest_execution_thread_count_default():
	if 'CUDAExecutionProvider' in onnxruntime.get_available_providers():
		return 8

	return 1


def limit_resources():
	gpus = tensorflow.config.experimental.list_physical_devices('GPU')

	for gpu in gpus:
		tensorflow.config.experimental.set_virtual_device_configuration(gpu, [
			tensorflow.config.experimental.VirtualDeviceConfiguration(memory_limit=512)
		])

	if vitswap.globals.max_memory:
		memory = vitswap.globals.max_memory * 1024 ** 3

		if platform.system().lower() == 'darwin':
			memory = vitswap.globals.max_memory * 1024 ** 6

		if platform.system().lower() == 'windows':
			import ctypes

			kernel32 = ctypes.windll.kernel32
			kernel32.SetProcessWorkingSetSize(-1, ctypes.c_size_t(memory), ctypes.c_size_t(memory))

		else:
			import resource

			resource.setrlimit(resource.RLIMIT_DATA, (memory, memory))


def update_status(message, scope):
	print(f'[{scope}] {message}')


def pre_check():
	if sys.version_info < (3, 9):
		update_status(wording.get('python_not_supported').format(version='3.9'))

		return False

	if not shutil.which('ffmpeg'):
		update_status(wording.get('ffmpeg_not_installed'))

		return False

	return True


def process_image():
	shutil.copy2(vitswap.globals.target_path, vitswap.globals.output_path)

	for frame_processor_module in get_frame_processors_modules(vitswap.globals.frame_processors):
		update_status(wording.get('processing'), frame_processor_module.NAME)

		frame_processor_module.process_image(vitswap.globals.source_path, vitswap.globals.output_path, vitswap.globals.output_path)
		frame_processor_module.post_process()

	update_status(wording.get('compressing_image'))

	if not compress_image(vitswap.globals.output_path):
		update_status(wording.get('compressing_image_failed'))

	if is_image(vitswap.globals.target_path):
		update_status(wording.get('processing_image_succeed'))

	else:
		update_status(wording.get('processing_image_failed'))


def process_video():
	fps = detect_fps(vitswap.globals.target_path) if vitswap.globals.keep_fps else 25.0

	update_status(wording.get('creating_temp'))
	create_temp(vitswap.globals.target_path)
	update_status(wording.get('extracting_frames_fps').format(fps = fps))
	extract_frames(vitswap.globals.target_path, fps)

	temp_frame_paths = get_temp_frame_paths(vitswap.globals.target_path)

	if temp_frame_paths:
		for frame_processor_module in get_frame_processors_modules(vitswap.globals.frame_processors):
			update_status(wording.get('processing'), frame_processor_module.NAME)

			frame_processor_module.process_video(vitswap.globals.source_path, temp_frame_paths)
			frame_processor_module.post_process()

	else:
		update_status(wording.get('temp_frames_not_found'))

		return

	update_status(wording.get('merging_video_fps').format(fps = fps))

	if not merge_video(vitswap.globals.target_path, fps):
		update_status(wording.get('merging_video_failed'))

		return

	if vitswap.globals.skip_audio:
		update_status(wording.get('skipping_audio'))

		move_temp(vitswap.globals.target_path, vitswap.globals.output_path)

	else:
		update_status(wording.get('restoring_audio'))

		if not restore_audio(vitswap.globals.target_path, vitswap.globals.output_path):
			update_status(wording.get('restoring_audio_failed'))
			move_temp(vitswap.globals.target_path, vitswap.globals.output_path)

	update_status(wording.get('clearing_temp'))
	clear_temp(vitswap.globals.target_path)

	if is_video(vitswap.globals.target_path):
		update_status(wording.get('processing_video_succeed'))

	else:
		update_status(wording.get('processing_video_failed'))


def conditional_process():
	for frame_processor_module in get_frame_processors_modules(vitswap.globals.frame_processors):
		if not frame_processor_module.pre_process('output'):
			return

	if is_image(vitswap.globals.target_path):
		process_image()

	if is_video(vitswap.globals.target_path):
		process_video()


def run():
	parse_args()
	limit_resources()

	if not pre_check():
		return

	for frame_processor in get_frame_processors_modules(vitswap.globals.frame_processors):
		if not frame_processor.pre_check():
			return

	if vitswap.globals.headless:
		conditional_process()

	else:
		import vitswap.ui.core as ui

		for ui_layout in ui.get_ui_layouts_modules(vitswap.globals.ui_layouts):
			if not ui_layout.pre_check():
				return

		ui.launch()


def destroy():
	if vitswap.globals.target_path:
		clear_temp(vitswap.globals.target_path)

	sys.exit()
