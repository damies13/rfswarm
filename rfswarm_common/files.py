import hashlib
import os


class FilesTransfers():
	def __init__(self):
		pass

	def hash_file(self, file, relpath):
		BLOCKSIZE = 65536
		hasher = hashlib.md5()
		hasher.update(str(os.path.getmtime(file)).encode('utf-8'))
		hasher.update(relpath.encode('utf-8'))
		with open(file, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		self.debugmsg(3, "file:", file, "	hash:", hasher.hexdigest())
		return hasher.hexdigest()
