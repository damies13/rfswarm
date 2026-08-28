import hashlib
import os
from rfswarm_common.debug import debug


class FilesTransfers:
	def __init__(self):
		pass

	@staticmethod
	def hash_file(file, relpath):
		BLOCKSIZE = 65536
		hasher = hashlib.md5()
		hasher.update(str(os.path.getmtime(file)).encode('utf-8'))
		hasher.update(relpath.encode('utf-8'))
		with open(file, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		debug.debugmsg(3, "file:", file, "	hash:", hasher.hexdigest())
		return hasher.hexdigest()

	@staticmethod
	def ensuredir(dir):
		if os.path.exists(dir):
			return True
		try:
			patharr = os.path.split(dir)
			debug.debugmsg(6, "patharr: ", patharr)
			FilesTransfers.ensuredir(patharr[0])
			os.mkdir(dir, mode=0o777)
			debug.debugmsg(5, "Directory Created: ", dir)
			return True
		except FileExistsError:
			debug.debugmsg(5, "Directory Exists: ", dir)
			return False
		except Exception as e:
			debug.debugmsg(1, "Directory Create failed: ", dir)
			debug.debugmsg(1, "with error: ", e)
			return False
