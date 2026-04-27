
from robot.libraries.BuiltIn import BuiltIn

import time
import os
import json
import requests

class RFSTestRepeater:
	ROBOT_LISTENER_API_VERSION = 3

	testname = None
	count = 0

	def end_test(self, test, result):

		jobdata = {}
		timeout = 600
		agent = test.parent.metadata['RFS_AGENTNAME']
		manager = test.parent.metadata['RFS_SWARMMANAGER']
		index = test.parent.metadata['RFS_INDEX']
		robot = test.parent.metadata['RFS_ROBOT']
		scriptdir = os.path.dirname(__file__)
		jobfile = os.path.join(scriptdir, "RFS_Job_{}_{}.json".format(index, robot))
		jobid = "{}_{}".format(index, robot)
		endtime = 0

		if os.path.exists(jobfile):
			with open(jobfile, 'r') as f:
				jobdata = json.load(f)
				endtime = jobdata['EndTime']
				jobid = jobdata['jobid']

		try:
			uri = manager + 'Jobs'
			payload = {'AgentName': agent}
			r = requests.post(uri, json=payload, timeout=timeout)
			if r.status_code == requests.codes.ok:
				jsonresp = json.loads(r.text)
				endtime = jsonresp['Schedule'][jobid]['EndTime']
		except:
			pass

		self.count += 1
		newiteration = "{}_{}".format(test.parent.metadata['RFS_ITERATION'], self.count)
		BuiltIn().set_suite_variable("${RFS_ITERATION}", newiteration)

		if int(time.time()) < endtime:
			if self.testname is None:
				self.testname = test.name
			newname = "{} {}".format(self.testname, newiteration)
			copy = test.copy(name=newname)
			copy = self.__remove_injected_sleeps(copy)
			test.parent.tests.append(copy)

	def __remove_injected_sleeps(self, testobj):
		# print('RFSTestRepeater', '__remove_injected_sleeps', 'testobj:', testobj)
		# print('RFSTestRepeater', '__remove_injected_sleeps', 'testobj.body:', testobj.body)
		testobj.body = [item for item in testobj.body if not (item.name=='Sleep' and len(item.args) > 1 and item.args[1]=='Sleep added by RFSwarm')]
		# print('RFSTestRepeater', '__remove_injected_sleeps', 'testobj.body:', testobj.body)
		return testobj

	# I beleive these are related to https://github.com/robotframework/robotframework/issues/5154 and are not needed now

	# def start_keyword(self, data, result):
	# 	# This prevents the error:
	# 	# [ ERROR ] Calling method 'start_keyword' of listener 'TestRepeater.py' failed: TypeError: end_suite() takes 2 positional arguments but 3 were given
	# 	pass

	# def end_keyword(self, data, result):
	# 	# This prevents the error:
	# 	# [ ERROR ] Calling method 'end_keyword' of listener 'TestRepeater.py' failed: TypeError: end_suite() takes 2 positional arguments but 3 were given
	# 	pass
