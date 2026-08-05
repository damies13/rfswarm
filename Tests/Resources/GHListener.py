
from robot.libraries.BuiltIn import BuiltIn
from robot import result, running

class GHListener:
	ROBOT_LISTENER_API_VERSION = 3

	def end_test(self, data: running.TestCase, result: result.TestCase):

		infomessage = f"\n{result.name} \n\tStarted: {result.start_time} Ended: {result.end_time} \n\tElapsed: {result.elapsed_time}"
		BuiltIn().run_keyword('Log', infomessage, "console=yes")

# 