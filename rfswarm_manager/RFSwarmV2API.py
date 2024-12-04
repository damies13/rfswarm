
import bottle
# from beaker.middleware import SessionMiddleware

app = bottle.Bottle()



class RFSwarmV2API(bottle.Bottle):

	def __init__(self):
		self.app = app

	def api_object(self):
		return self.app


	# these examples below are just demo's, should be removed before V2 goes to prod
	@app.route('/hello')
	def custom_route():
		return 'Hello, World!'

	@app.route('/page2')
	def page_2():

		pg2html = """
		<!DOCTYPE html>
		<html>

		<head>
			<title>Page 2</title>
		</head>
		<body>
			<h1> Page 2 </h1>
			<a href="/">Home</a>
		</body>
		</html>
		"""
		return pg2html
