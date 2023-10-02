import numpy
import insightface
import threading
import vitswap.globals
from vitswap.face_cache import get_faces_cache, set_faces_cache

FACE_ANALYSER = None
THREAD_LOCK = threading.Lock()


def get_face_analyser():
	global FACE_ANALYSER

	with THREAD_LOCK:
		if FACE_ANALYSER is None:
			FACE_ANALYSER = insightface.app.FaceAnalysis(name='buffalo_l', providers=vitswap.globals.execution_providers)
			FACE_ANALYSER.prepare(ctx_id=0)

	return FACE_ANALYSER


def clear_face_analyser():
	global FACE_ANALYSER

	FACE_ANALYSER = None


def get_one_face(frame, position = 0):
	many_faces = get_many_faces(frame)

	if many_faces:
		try:
			return many_faces[position]
		except IndexError:
			return many_faces[-1]


def get_many_faces(frame):
	try:
		faces_cache = get_faces_cache(frame)

		if faces_cache:
			faces = faces_cache

		else:
			faces = get_face_analyser().get(frame)

			set_faces_cache(frame, faces)

		if vitswap.globals.face_analyser_direction:
			faces = sort_by_direction(faces, vitswap.globals.face_analyser_direction)

		if vitswap.globals.face_analyser_age:
			faces = filter_by_age(faces, vitswap.globals.face_analyser_age)

		if vitswap.globals.face_analyser_gender:
			faces = filter_by_gender(faces, vitswap.globals.face_analyser_gender)

		return faces
	except (AttributeError, ValueError):
		return []


def find_similar_faces(frame, reference_face, face_distance):
	many_faces = get_many_faces(frame)

	similar_faces = []

	if many_faces:
		for face in many_faces:
			if hasattr(face, 'normed_embedding') and hasattr(reference_face, 'normed_embedding'):
				current_face_distance = numpy.sum(numpy.square(face.normed_embedding - reference_face.normed_embedding))

				if current_face_distance < face_distance:
					similar_faces.append(face)

	return similar_faces


def sort_by_direction(faces, direction):
	if direction == 'left-right':
		return sorted(faces, key=lambda face: face['bbox'][0])

	if direction == 'right-left':
		return sorted(faces, key=lambda face: face['bbox'][0], reverse=True)

	if direction == 'top-bottom':
		return sorted(faces, key=lambda face: face['bbox'][1])

	if direction == 'bottom-top':
		return sorted(faces, key=lambda face: face['bbox'][1], reverse=True)

	if direction == 'small-large':
		return sorted(faces, key=lambda face: (face['bbox'][2] - face['bbox'][0]) * (face['bbox'][3] - face['bbox'][1]))

	if direction == 'large-small':
		return sorted(faces, key=lambda face: (face['bbox'][2] - face['bbox'][0]) * (face['bbox'][3] - face['bbox'][1]), reverse=True)

	return faces


def filter_by_age(faces, age):
	filter_faces = []

	for face in faces:
		if face['age'] < 13 and age == 'child':
			filter_faces.append(face)

		elif face['age'] < 19 and age == 'teen':
			filter_faces.append(face)

		elif face['age'] < 60 and age == 'adult':
			filter_faces.append(face)

		elif face['age'] > 59 and age == 'senior':
			filter_faces.append(face)

	return filter_faces


def filter_by_gender(faces, gender):
	filter_faces = []

	for face in faces:
		if face['gender'] == 1 and gender == 'male':
			filter_faces.append(face)

		if face['gender'] == 0 and gender == 'female':
			filter_faces.append(face)

	return filter_faces
