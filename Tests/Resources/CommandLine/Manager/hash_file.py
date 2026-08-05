"""A module that provides a file hashing
function in the same way as the Manager does"""

import errno
import hashlib
import os
import platform


def get_relative_path(path1, path2):
	if os.path.isfile(path1) or not os.path.exists(path1):
		path1 = os.path.dirname(path1)

	if platform.system() == "Windows":
		if os.path.splitdrive(path1)[0] != os.path.splitdrive(path2)[0]:
			path1 = os.path.dirname(path2)

	relpath = os.path.relpath(path2, start=path1)

	return relpath

def hash_file(scriptdir, file):
	if not (os.path.exists(file) and os.path.isfile(file)):
		raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
	BLOCKSIZE = 65536

	relpath = get_relative_path(scriptdir, file)
	hasher = hashlib.md5()
	hasher.update(str(os.path.getmtime(file)).encode('utf-8'))
	hasher.update(relpath.encode('utf-8'))

	afile = open(file, 'rb')
	buf = afile.read(BLOCKSIZE)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(BLOCKSIZE)
	afile.close()

	return hasher.hexdigest()
