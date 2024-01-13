import hashlib

FACES_CACHE = {}


def get_faces_cache(frame):
	frame_hash = create_frame_hash(frame)

	if frame_hash in FACES_CACHE:
		return FACES_CACHE[frame_hash]


def set_faces_cache(frame, faces):
	frame_hash = create_frame_hash(frame)

	if frame_hash:
		FACES_CACHE[frame_hash] = faces


def clear_faces_cache():
	global FACES_CACHE

	FACES_CACHE = {}


def create_frame_hash(frame):
	return frame and hashlib.sha256(frame.tobytes()).hexdigest()
