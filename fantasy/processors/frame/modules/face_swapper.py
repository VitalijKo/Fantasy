import insightface
import threading
import fantasy.globals
import fantasy.processors.frame.core as frame_processors
from fantasy import wording
from fantasy.core import update_status
from fantasy.face_analyser import get_one_face, get_many_faces, find_similar_faces, clear_face_analyser
from fantasy.face_reference import get_face_reference, set_face_reference
from fantasy.utilities import conditional_download, resolve_relative_path, is_image, is_video, is_file, is_download_done
from fantasy.vision import read_image, read_static_image, write_image

FRAME_PROCESSOR = None
THREAD_LOCK = threading.Lock()
NAME = 'FANTASY.FRAME_PROCESSOR.FACE_SWAPPER'
MODEL_URL = 'https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx'
MODEL_PATH = resolve_relative_path('../.assets/models/inswapper_128.onnx')


def get_frame_processor():
	global FRAME_PROCESSOR

	with THREAD_LOCK:
		if FRAME_PROCESSOR is None:
			FRAME_PROCESSOR = insightface.model_zoo.get_model(MODEL_PATH, providers=fantasy.globals.execution_providers)

	return FRAME_PROCESSOR


def clear_frame_processor():
	global FRAME_PROCESSOR

	FRAME_PROCESSOR = None


def pre_check():
	if not fantasy.globals.skip_download:
		download_directory_path = resolve_relative_path('../.assets/models')

		conditional_download(download_directory_path, [ MODEL_URL ])

	return True


def pre_process(mode):
	if not fantasy.globals.skip_download and not is_download_done(MODEL_URL, MODEL_PATH):
		update_status(wording.get('model_download_not_done') + wording.get('exclamation_mark'), NAME)

		return False

	elif not is_file(MODEL_PATH):
		update_status(wording.get('model_file_not_present') + wording.get('exclamation_mark'), NAME)

		return False

	if not is_image(fantasy.globals.source_path):
		update_status(wording.get('select_image_source') + wording.get('exclamation_mark'), NAME)

		return False

	elif not get_one_face(read_static_image(fantasy.globals.source_path)):
		update_status(wording.get('no_source_face_detected') + wording.get('exclamation_mark'), NAME)

		return False

	if mode in ['output', 'preview'] and not is_image(fantasy.globals.target_path) and not is_video(fantasy.globals.target_path):
		update_status(wording.get('select_image_or_video_target') + wording.get('exclamation_mark'), NAME)

		return False

	if mode == 'output' and not fantasy.globals.output_path:
		update_status(wording.get('select_file_or_directory_output') + wording.get('exclamation_mark'), NAME)

		return False

	return True


def post_process():
	clear_frame_processor()
	clear_face_analyser()

	read_static_image.cache_clear()


def swap_face(source_face, target_face, temp_frame):
	return get_frame_processor().get(temp_frame, target_face, source_face, paste_back=True)


def process_frame(source_face, reference_face, temp_frame):
	if 'reference' in fantasy.globals.face_recognition:
		similar_faces = find_similar_faces(temp_frame, reference_face, fantasy.globals.reference_face_distance)

		if similar_faces:
			for similar_face in similar_faces:
				temp_frame = swap_face(source_face, similar_face, temp_frame)

	if 'many' in fantasy.globals.face_recognition:
		many_faces = get_many_faces(temp_frame)

		if many_faces:
			for target_face in many_faces:
				temp_frame = swap_face(source_face, target_face, temp_frame)

	return temp_frame


def process_frames(source_path, temp_frame_paths, update_progress):
	source_face = get_one_face(read_static_image(source_path))

	reference_face = get_face_reference() if 'reference' in fantasy.globals.face_recognition else None

	for temp_frame_path in temp_frame_paths:
		temp_frame = read_image(temp_frame_path)
		result_frame = process_frame(source_face, reference_face, temp_frame)

		write_image(temp_frame_path, result_frame)

		update_progress()


def process_image(source_path, target_path, output_path):
	source_face = get_one_face(read_static_image(source_path))
	target_frame = read_static_image(target_path)
	reference_face = get_one_face(target_frame, fantasy.globals.reference_face_position) if 'reference' in fantasy.globals.face_recognition else None
	result_frame = process_frame(source_face, reference_face, target_frame)
	
	write_image(output_path, result_frame)


def process_video(source_path, temp_frame_paths):
	conditional_set_face_reference(temp_frame_paths)

	frame_processors.multi_process_frames(source_path, temp_frame_paths, process_frames)


def conditional_set_face_reference(temp_frame_paths):
	if 'reference' in fantasy.globals.face_recognition and not get_face_reference():
		reference_frame = read_static_image(temp_frame_paths[fantasy.globals.reference_frame_number])
		reference_face = get_one_face(reference_frame, fantasy.globals.reference_face_position)
		
		set_face_reference(reference_face)
