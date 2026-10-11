import base64
import gc
import json
import lzma
import os
import random
import threading
import time
import uuid
from typing import Any

import psutil
import requests
from rfswarm_common.debug import debug
from rfswarm_common.filestransfers import FilesTransfers

from rfswarm_agent.client.manager_client import ManagerClient


class FilesManager:
	"""
	Manages file transfers (uploads and downloads) between the Agent and RFSwarm Manager.

	Note on queue semantics:
	- download_queue: Items are popped immediately upon processing.
	- upload_queue: Items remain in the queue until upload succeeds, allowing
	  automatic retry/resumption if the connection to Manager is lost.
	"""

	def __init__(self, manager: ManagerClient, timeout: int, agentname: str, scriptdir: str):
		self.manager = manager
		self.timeout = timeout
		self.agentname = agentname

		self.upload_queue: list[dict[str, str]] = []
		self.upload_threads: dict[str, threading.Thread] = {}

		self.download_queue: list[str] = []
		self.download_threads: dict[str, threading.Thread] = {}

		self.scriptdir: str = scriptdir
		self.scriptlist: dict[str, dict[str, Any]] = {}

	def file_upload(self, fileobj: dict[str, str]) -> None:
		debug.debugmsg(7, "fileobj", fileobj)

		hash = FilesTransfers.hash_file(fileobj['LocalFilePath'], fileobj['RelFilePath'])
		debug.debugmsg(7, "hash", hash)

		# 	check file exists on manager?

		uri = self.manager.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Status",
			"Hash": hash
		}
		debug.debugmsg(9, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(7, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				self.manager.mark_disconnected()

		except Exception as e:
			debug.debugmsg(8, "Exception:", e)
			self.manager.mark_disconnected()

		if not self.manager.isconnected:
			# Manager disconnected; leave fileobj in upload_queue to retry after reconnect
			return

		jsonresp = {}
		try:
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)
			return

		# 	If file not exists upload the file
		if jsonresp["Exists"] == "False":
			debug.debugmsg(6, "file not there, so lets upload")

			payload = {
				"AgentName": self.agentname,
				"Action": "Upload",
				"Hash": hash,
				"File": fileobj['RelFilePath']
			}

			localpath = fileobj['LocalFilePath']
			buf = "\n"
			with open(localpath, 'rb') as afile:
				buf = afile.read()
			debug.debugmsg(9, "buf:", buf)
			compressed = lzma.compress(buf)
			debug.debugmsg(9, "compressed:", compressed)
			encoded = base64.b64encode(compressed)
			debug.debugmsg(9, "encoded:", encoded)

			payload["FileData"] = encoded.decode('ASCII')

			debug.debugmsg(8, "payload: ", payload)

			try:
				r = requests.post(uri, json=payload, timeout=self.timeout)
				debug.debugmsg(7, "resp: ", r.status_code, r.text)
				if r.status_code != requests.codes.ok:
					debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
					self.manager.mark_disconnected()

			except Exception as e:
				debug.debugmsg(8, "Exception:", e)
				self.manager.mark_disconnected()

			if not self.manager.isconnected:
				# Manager disconnected; leave fileobj in upload_queue to retry after reconnect
				return

			jsonresp = {}
			try:
				# self.scriptlist
				jsonresp = json.loads(r.text)
				debug.debugmsg(7, "jsonresp:", jsonresp)
			except Exception as e:
				debug.debugmsg(1, "Exception:", e)
				return

		# Remove from queue only after confirmed success
		if fileobj in self.upload_queue:
			self.upload_queue.remove(fileobj)

	def process_file_upload_queue(self) -> None:
		corecount = psutil.cpu_count() or 1
		threadcount = corecount * 3
		debug.debugmsg(7, "upload_queue", self.upload_queue)
		debug.debugmsg(5, "corecount", corecount, "\tthreadcount:", threadcount)
		# Note: We iterate over a copy of upload_queue without popping items upfront.
		# Items are removed only upon successful upload in file_upload(), so that
		# un-uploaded files are preserved and automatically retried upon reconnection.
		for fobj in list(self.upload_queue):
			# limit the number of upload threads so we don't max out the agent and cause it
			# to go into critical/offline? mode
			debug.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
			while len(list(self.upload_threads.keys())) > threadcount - 1:
				debug.debugmsg(5, "upload_threads count:", len(list(self.upload_threads.keys())))
				# key = list(self.upload_threads.keys())[0]
				key = random.choice(list(self.upload_threads.keys()))
				debug.debugmsg(5, "key:", key)
				if key in self.upload_threads and self.upload_threads[key].is_alive():
					self.upload_threads[key].join()
				if key in self.upload_threads:
					del self.upload_threads[key]
			key = str(uuid.uuid4())
			debug.debugmsg(5, "key:", key)
			self.upload_threads[key] = threading.Thread(target=self.file_upload, args=(fobj,))
			self.upload_threads[key].start()
			time.sleep(0.5)
		for key in list(self.upload_threads.keys()):
			debug.debugmsg(5, "key:", key)
			if key in self.upload_threads and self.upload_threads[key].is_alive():
				self.upload_threads[key].join()
			if key in self.upload_threads:
				del self.upload_threads[key]
		gc.collect()

	def queue_file_upload(self, mode: str, retcode: int, filedir: str, rundir: str) -> None:
		reldir = os.path.basename(filedir)
		debug.debugmsg(7, mode, retcode, reldir, filedir)

		filelst = self.file_upload_list(filedir)
		debug.debugmsg(7, "filelst", filelst)
		# filelst
		# [
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1.log',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/log.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/report.html',
		# 	'/var/folders/7l/k7w46dm91y3gscxlswd_jm2r0000gn/T/rfswarmagent/logs/20201219_113254_11u_test_quick/OC_Demo_2_1_5_1608341588_1_1608341594/Browse_Store_Product_1_output.xml'
		# ]
		#

		debug.debugmsg(5, "mode:", mode, "\tretcode:", retcode)
		# 	uploadmodes = {'imm':"Immediately", 'err':"On Error Only", 'def':"All Defered"}

		for file in filelst:
			fobj = {
				"LocalFilePath": file,
				"RelFilePath": os.path.relpath(file, start=rundir)
			} 
			self.upload_queue.append(fobj)
			debug.debugmsg(7, "added to upload_queue", fobj)
			if mode == "err" and retcode > 0:
				# upload now
				self.file_upload(fobj)
			if mode == "imm":
				# upload now
				self.file_upload(fobj)

	@staticmethod
	def file_upload_list(filedir: str) -> list[str]:
		retlst: list[str] = []
		dirlst = os.listdir(path=filedir)
		debug.debugmsg(7, "dirlst", dirlst)
		for item in dirlst:
			fullpath = os.path.join(filedir, item)
			if os.path.isfile(fullpath):
				retlst.append(fullpath)
			else:
				files = FilesManager.file_upload_list(fullpath)
				retlst.extend(files)
		return retlst

	def getfile(self, hash: str) -> None:
		debug.debugmsg(6, "hash: ", hash)
		uri = self.manager.swarmmanager + "File"
		payload = {
			"AgentName": self.agentname,
			"Action": "Download",
			"Hash": hash
		}
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(8, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				debug.debugmsg(5, "resp: ", r.status_code, r.text)
				self.manager.mark_disconnected()

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			self.manager.mark_disconnected()

		if not self.manager.isconnected:
			return

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(7, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)
			return

		try:
			relpath_parts = jsonresp['File'].replace('\\', '/').split('/')
			debug.debugmsg(7, 'scriptdir', self.scriptdir)
			localfile = os.path.abspath(os.path.join(self.scriptdir, *relpath_parts))
			debug.debugmsg(5, 'localfile', localfile)

		except Exception as e:
			debug.debugmsg(0, "Exception:", e)
			return

		try:
			if hash not in self.scriptlist:
				self.scriptlist[hash] = {'id': hash}
			self.scriptlist[hash]['localfile'] = localfile
			self.scriptlist[hash]['file'] = jsonresp['File']

			# self.scriptlist[hash][]

			filedata = jsonresp['FileData']
			debug.debugmsg(6, "filedata:", filedata)
			debug.debugmsg(6, "filedata:")

			decoded = base64.b64decode(filedata)
			debug.debugmsg(6, "b64decode: decoded:", decoded)
			debug.debugmsg(6, "b64decode:")

			uncompressed = lzma.decompress(decoded)
			debug.debugmsg(6, "uncompressed:", uncompressed)
			debug.debugmsg(6, "uncompressed:")

			localfiledir = os.path.dirname(localfile)
			debug.debugmsg(6, "localfiledir:", localfiledir)
			FilesTransfers.ensuredir(localfiledir)
			debug.debugmsg(6, "ensuredir:")

			with open(localfile, 'wb') as afile:
				debug.debugmsg(6, "afile:")
				afile.write(uncompressed)
				debug.debugmsg(6, "write:")
			debug.debugmsg(1, 'Downloaded:', localfile)

		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

	def process_file_download_queue(self) -> None:

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return

		corecount = psutil.cpu_count() or 1
		threadcount = corecount * 32
		debug.debugmsg(7, "download_queue", self.download_queue)
		debug.debugmsg(5, "corecount", corecount, "\tthreadcount:", threadcount)
		# for hash in self.download_queue:
		while len(self.download_queue) > 0:
			# limit the number of download threads so we don't max out the agent and cause it
			# to go into critical/offline? mode

			hash = self.download_queue.pop(0)

			debug.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
			while len(list(self.download_threads.keys())) > threadcount - 1:
				debug.debugmsg(5, "download_threads count:", len(list(self.download_threads.keys())))
				# key = list(self.download_threads.keys())[0]
				key = random.choice(list(self.download_threads.keys()))
				debug.debugmsg(5, "key:", key)
				if key in self.download_threads and self.download_threads[key].is_alive():
					self.download_threads[key].join()
				if key in self.download_threads:
					del self.download_threads[key]
			key = str(uuid.uuid4())
			debug.debugmsg(6, "New download thread key:", key)
			while hash in self.download_queue:
				self.download_queue.remove(hash)
			self.download_threads[key] = threading.Thread(target=self.getfile, args=(hash,))
			self.download_threads[key].start()
			time.sleep(0.02)
		for key in list(self.download_threads.keys()):
			debug.debugmsg(6, "download thread key:", key)
			if key in self.download_threads and self.download_threads[key].is_alive():
				self.download_threads[key].join()
			if key in self.download_threads:
				del self.download_threads[key]
			debug.debugmsg(6, "Finished download thread key:", key)
		gc.collect()

	def getscripts(self) -> None:
		debug.debugmsg(6, "getscripts")

		if len(list(self.download_threads.keys())) > 0:
			# already processing the queue, don't double up
			debug.debugmsg(5, "already processing the queue, don't double up")
			return

		uri = self.manager.swarmmanager + "Scripts"
		payload = {
			"AgentName": self.agentname
		}
		debug.debugmsg(6, "payload: ", payload)
		try:
			r = requests.post(uri, json=payload, timeout=self.timeout)
			debug.debugmsg(6, "resp: ", r.status_code, r.text)
			if r.status_code != requests.codes.ok:
				debug.debugmsg(5, "r.status_code:", r.status_code, requests.codes.ok)
				self.manager.mark_disconnected()

		except Exception as e:
			debug.debugmsg(5, "Exception:", e)
			self.manager.mark_disconnected()

		if not self.manager.isconnected:
			return

		try:
			jsonresp = {}
			# self.scriptlist
			jsonresp = json.loads(r.text)
			debug.debugmsg(6, "jsonresp:", jsonresp)
		except Exception as e:
			debug.debugmsg(1, "Exception:", e)

		if "Scripts" in jsonresp:
			for s in jsonresp["Scripts"]:
				hash = s['Hash']
				debug.debugmsg(6, "hash:", hash)
				if hash not in self.scriptlist:
					debug.debugmsg(6, "getfile")
					self.scriptlist[hash] = {'id': hash}
					if hash not in self.download_queue:
						self.download_queue.append(hash)
				else:
					debug.debugmsg(6, "Check file")
					if 'localfile' in self.scriptlist[hash]:
						if (
							not os.path.isfile(self.scriptlist[hash]['localfile'])
							and hash not in self.download_queue
						):
							self.download_queue.append(hash)
					else:
						debug.debugmsg(6, "getfile")
						self.scriptlist[hash] = {'id': hash}
						if hash not in self.download_queue:
							self.download_queue.append(hash)

			if len(self.download_queue):
				self.process_file_download_queue()
