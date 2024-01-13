import cv2
import gradio
import subprocess
import os
import platform
import fantasy.globals
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from tqdm import tqdm
from fantasy import wording
from fantasy.face_analyser import get_one_face
from fantasy.processors.frame.core import load_frame_processor_module
from fantasy.ui import core as ui
from fantasy.utilities import open_ffmpeg
from fantasy.vision import normalize_frame_color, read_static_image

WEBCAM_IMAGE = None
WEBCAM_START_BUTTON = None
WEBCAM_STOP_BUTTON = None


def render():
	global WEBCAM_IMAGE
	global WEBCAM_START_BUTTON
	global WEBCAM_STOP_BUTTON

	WEBCAM_IMAGE = gradio.Image(
		label=wording.get('webcam_image_label')
	)
	WEBCAM_START_BUTTON = gradio.Button(
		value=wording.get('start_button_label'),
		variant='primary'
	)
	WEBCAM_STOP_BUTTON = gradio.Button(
		value=wording.get('stop_button_label')
	)


def listen():
	start_event = None

	webcam_mode_radio = ui.get_component('webcam_mode_radio')
	webcam_resolution_dropdown = ui.get_component('webcam_resolution_dropdown')
	webcam_fps_slider = ui.get_component('webcam_fps_slider')

	if webcam_mode_radio and webcam_resolution_dropdown and webcam_fps_slider:
		start_event = WEBCAM_START_BUTTON.click(start, inputs=[webcam_mode_radio, webcam_resolution_dropdown, webcam_fps_slider], outputs=WEBCAM_IMAGE)

		webcam_mode_radio.change(stop, outputs=WEBCAM_IMAGE, cancels=start_event)
		webcam_resolution_dropdown.change(stop, outputs=WEBCAM_IMAGE, cancels=start_event)
		webcam_fps_slider.change(stop, outputs=WEBCAM_IMAGE, cancels=start_event)

	WEBCAM_STOP_BUTTON.click(stop, cancels=start_event)

	source_image = ui.get_component('source_image')

	if source_image:
		for method in ['upload', 'change', 'clear']:
			getattr(source_image, method)(stop, cancels=start_event)


def start(mode, resolution, fps):
	fantasy.globals.face_recognition = 'many'

	source_face = get_one_face(read_static_image(fantasy.globals.source_path))

	stream = None

	if mode == 'stream_udp':
		stream = open_stream('udp', resolution, fps)

	if mode == 'stream_v4l2':
		stream = open_stream('v4l2', resolution, fps)

	capture = capture_webcam(resolution, fps)

	if capture.isOpened():
		for capture_frame in multi_process_capture(source_face, capture):
			if stream is not None:
				stream.stdin.write(capture_frame.tobytes())

			yield normalize_frame_color(capture_frame)


def multi_process_capture(source_face, capture):
	progress = tqdm(desc=wording.get('processing'), unit='frame', dynamic_ncols=True)

	with ThreadPoolExecutor(max_workers=fantasy.globals.execution_thread_count) as executor:
		futures = []

		deque_capture_frames = deque()

		while True:
			_, capture_frame = capture.read()

			future = executor.submit(process_stream_frame, source_face, capture_frame)

			futures.append(future)

			for future_done in [future for future in futures if future.done()]:
				capture_frame = future_done.result()

				deque_capture_frames.append(capture_frame)

				futures.remove(future_done)

			while deque_capture_frames:
				yield deque_capture_frames.popleft()

				progress.update()


def stop():
	return gradio.update(value=None)


def capture_webcam(resolution, fps):
	width, height = resolution.split('x')

	if platform.system().lower() == 'windows':
		capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

	else:
		capture = cv2.VideoCapture(0)

	capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
	capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
	capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
	capture.set(cv2.CAP_PROP_FPS, fps)

	return capture


def process_stream_frame(source_face, temp_frame):
	for frame_processor in fantasy.globals.frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)

		if frame_processor_module.pre_process('stream'):
			temp_frame = frame_processor_module.process_frame(
				source_face,
				None,
				temp_frame
			)

	return temp_frame


def open_stream(mode, resolution, fps):
	commands = ['-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', resolution, '-r', str(fps), '-i', '-']

	if mode == 'udp':
		commands.extend(['-b:v', '2000k', '-f', 'mpegts', 'udp://localhost:27000?pkt_size=1316'])

	if mode == 'v4l2':
		device_name = os.listdir('/sys/devices/virtual/video4linux')[0]

		commands.extend(['-f', 'v4l2', f'/dev/{device_name}'])

	return open_ffmpeg(commands)
