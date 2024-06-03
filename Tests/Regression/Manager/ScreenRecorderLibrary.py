import pyscreenrec
import os
from robot.api import logger


class ScreenRecorderLibrary:

	recorder = None
	filepath = None

	def __init__(self):
		self.recorder = pyscreenrec.ScreenRecorder()

	def video_start_recording(self, filepath, fps=24):
		try:
			if os.path.exists(filepath):
				os.remove(filepath)
		except Exception as e:
			pass
		self.recorder.start_recording(filepath, fps)
		self.filepath = filepath

	def video_stop_recording(self):
		self.recorder.stop_recording()
		logger.info(self.filepath)
		path2file, filename = os.path.split(self.filepath)
		logger.info('<video width="98%"><source src="./{}" type="video/mp4"></video>'.format(filename))

	def video_pause_recording(self):
		self.recorder.pause_recording()

	def video_resume_recording(self):
		self.recorder.resume_recording()
