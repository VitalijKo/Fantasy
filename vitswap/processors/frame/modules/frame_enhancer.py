import threading
import vitswap.globals
import vitswap.processors.frame.core as frame_processors
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from vitswap import wording, utilities
from vitswap.core import update_status
from vitswap.face_analyser import clear_face_analyser
from vitswap.utilities import conditional_download, resolve_relative_path, is_file, is_download_done
from vitswap.vision import read_image, read_static_image, write_image

FRAME_PROCESSOR = None
THREAD_SEMAPHORE = threading.Semaphore()
THREAD_LOCK = threading.Lock()
NAME = 'VITSWAP.FRAME_PROCESSOR.FRAME_ENHANCER'
MODEL_URL = 'https://github.com/vitswap/vitswap-assets/releases/download/models/RealESRGAN_x4plus.pth'
MODEL_PATH = resolve_relative_path('../.assets/models/RealESRGAN_x4plus.pth')


def get_frame_processor():
	global FRAME_PROCESSOR

	with THREAD_LOCK:
		if FRAME_PROCESSOR is None:
			FRAME_PROCESSOR = RealESRGANer(
				model_path = MODEL_PATH,
				model = RRDBNet(
					num_in_ch = 3,
					num_out_ch = 3,
					num_feat = 64,
					num_block = 23,
					num_grow_ch = 32,
					scale = 4
				),
				device = utilities.get_device(vitswap.globals.execution_providers),
				tile = 512,
				tile_pad = 32,
				pre_pad = 0,
				scale = 4
			)

	return FRAME_PROCESSOR


def clear_frame_processor():
	global FRAME_PROCESSOR

	FRAME_PROCESSOR = None


def pre_check():
	if not vitswap.globals.skip_download:
		download_directory_path = resolve_relative_path('../.assets/models')
		conditional_download(download_directory_path, [MODEL_URL])

	return True


def pre_process(mode):
	if not vitswap.globals.skip_download and not vitswap.globals.skip_download and not is_download_done(MODEL_URL, MODEL_PATH):
		update_status(wording.get('model_download_not_done') + wording.get('exclamation_mark'), NAME)

		return False

	elif not is_file(MODEL_PATH):
		update_status(wording.get('model_file_not_present') + wording.get('exclamation_mark'), NAME)

		return False

	if mode == 'output' and not vitswap.globals.output_path:
		update_status(wording.get('select_file_or_directory_output') + wording.get('exclamation_mark'), NAME)

		return False

	return True


def post_process():
	clear_frame_processor()
	clear_face_analyser()

	read_static_image.cache_clear()


def enhance_frame(temp_frame):
	with THREAD_SEMAPHORE:
		temp_frame, _ = get_frame_processor().enhance(temp_frame, outscale=1)

	return temp_frame


def process_frame(source_face, reference_face, temp_frame):
	return enhance_frame(temp_frame)


def process_frames(source_path, temp_frame_paths, update_progress):
	for temp_frame_path in temp_frame_paths:
		temp_frame = read_image(temp_frame_path)
		result_frame = process_frame(None, None, temp_frame)

		write_image(temp_frame_path, result_frame)

		update_progress()


def process_image(source_path, target_path, output_path):
	target_frame = read_static_image(target_path)
	result = process_frame(None, None, target_frame)

	write_image(output_path, result)


def process_video(source_path, temp_frame_paths):
	frame_processors.multi_process_frames(None, temp_frame_paths, process_frames)
