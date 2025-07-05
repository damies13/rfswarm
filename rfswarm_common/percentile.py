
class percentile:

	def __init__(self):
		self.count = 0
		self.percent = 90
		self.values = []

	def step(self, value, percent):
		# base.debugmsg(9, "value:", value, "	percent:", percent)
		if value is None:
			return
		self.count += 1
		self.values.append(value)
		self.percent = percent

	def finalize(self):
		try:
			mincount = 100 / (100 - self.percent)
			if self.count < mincount:
				# Need at least 10 samples to get a useful percentile
				return None
			# base.debugmsg(9, "percentile: finalize: mincount:", mincount, "	self.count:", self.count, "	self.percent:", self.percent, "	self.values:", self.values)
			nth = self.count * (self.percent / 100)
			# base.debugmsg(9, "percentile: finalize: nth:", nth)
			nthi = int(nth)
			# nthi = int(math.ceil(self.count * (self.percent/100)))
			self.values.sort()
			# base.debugmsg(8, "percentile: finalize: nthi:", nthi, "	self.values[nthi]:", self.values[nthi], "	self.values:", self.values)
			return self.values[nthi]
			# return self.count
		except Exception as e:
			# base.debugmsg(5, "Exception:", e)
			print("Exception:", e)
