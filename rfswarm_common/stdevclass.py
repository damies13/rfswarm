
import math


class stdevclass:
	def __init__(self):
		self.M = 0.0
		self.S = 0.0
		self.k = 1

	def step(self, value):
		try:
			if value is None:
				return
			value = float(value)
			tM = self.M
			self.M += (value - tM) / self.k
			self.S += (value - tM) * (value - self.M)
			self.k += 1
		except Exception as e:
			# base.debugmsg(5, "Exception:", e)
			print("stdevclass: step: Exception:", e)

	def finalize(self):
		# base.debugmsg(9, "self.k:", self.k, "	self.S:", self.S, "	self.M:", self.M)
		if self.k < 3:
			return None
		try:
			res = math.sqrt(self.S / (self.k - 2))
			# base.debugmsg(8, "res:", res)
			return res
		except Exception as e:
			# base.debugmsg(5, "Exception:", e)
			print("stdevclass: finalize: Exception:", e)
