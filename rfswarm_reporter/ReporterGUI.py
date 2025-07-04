

import difflib
import os
import platform
import sys
import threading
import time
import tkinter as tk  # python3
import tkinter.colorchooser as tkac
import tkinter.filedialog as tkf  # python3
import tkinter.font as tkFont
import tkinter.simpledialog as tksd
import tkinter.ttk as ttk  # python3
import webbrowser
import zoneinfo  # says Requires python 3.9
from datetime import datetime  # , timezone
from typing import Any

import matplotlib  # required for matplot graphs

# required for matplot graphs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure  # required for matplot graphs

# required for company logo's (I beleive this is a depandancy of matplotlib anyway)
from PIL import Image, ImageTk

matplotlib.use("TkAgg") 	# required for matplot graphs


class ReporterGUI(tk.Frame):

	style_reportbg_colour = "white"
	style_feild_colour = "white"
	style_text_colour = "#000"
	style_head_colour = "#00F"
	imgdata: Any = {}
	b64: Any = {}
	contentdata: Any = {}
	t_preview: Any = {}

	DataTypes = [None, "Metric", "Result", "ResultSummary", "Plan", "Monitoring", "SQL"]

	titleprefix = "RFSwarm Reporter"

	icon = None

	c_preview = False

	base = None

	def __init__(self, base, master=None):

		self.base = base

		self.root = tk.Tk(className="RFSwarm Reporter")
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		tk.Frame.__init__(self, self.root)
		self.grid(sticky="news", ipadx=0, pady=0)
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		self.root.geometry(self.base.config['GUI']['win_width'] + "x" + self.base.config['GUI']['win_height'])

		self.root.resizable(True, True)

		self.base.debugmsg(6, "updateTitle")
		self.updateTitle()

		self.base.debugmsg(5, "self.root", self.root)
		self.base.debugmsg(5, "self.root[background]", self.root["background"])
		self.rootBackground = self.root["background"]

		self.set_app_icon()
		self.load_icons()

		self.base.debugmsg(5, "BuildUI")
		self.BuildUI()
		self.BuildMenu()
		# self.dispaly_donation_reminder()
		dr = threading.Thread(target=self.dispaly_donation_reminder)
		dr.start()

	def load_icons(self):
		# 	"New Report Template"	page_add.png
		self.imgdata["New Report Template"] = self.get_icon("page_add.gif")
		# 	"Open Report Template"	folder_page.png
		self.imgdata["Open Report Template"] = self.get_icon("folder_page.gif")
		# 	"Save Report Template"	page_save.png
		self.imgdata["Save Report Template"] = self.get_icon("page_save.gif")
		# 	"Open Scenario Results"	folder_table.png
		self.imgdata["Open Scenario Results"] = self.get_icon("folder_table.gif")
		# 	"Apply Report Template"	page_go.png
		self.imgdata["Apply Report Template"] = self.get_icon("page_go.gif")

		# Export buttons
		# "Export HTML"		page_white_world.gif			HTML - Issue #36
		self.imgdata["Export HTML"] = self.get_icon("page_white_world.gif")
		# "Export Excel"		page_excel.png				Excel - Issue #37
		self.imgdata["Export Excel"] = self.get_icon("page_excel.gif")
		# "Export Word"		page_word.png					Word - Issue #38
		self.imgdata["Export Word"] = self.get_icon("page_word.gif")
		# "Export PDF"		page_white_acrobat.png
		self.imgdata["Export PDF"] = self.get_icon("page_white_acrobat.gif")
		# "Export Calc"		page_calc.gif
		self.imgdata["Export Calc"] = self.get_icon("page_calc.gif")
		# "Export Writer"		page_writer.gif
		self.imgdata["Export Writer"] = self.get_icon("page_writer.gif")

		# "New Section"	add.gif
		self.imgdata["New Section"] = self.get_icon("add.gif")
		# Remove Section	 delete.gif
		self.imgdata["Remove Section"] = self.get_icon("delete.gif")
		# Move Section Up	 resultset_up.gif
		self.imgdata["Section Up"] = self.get_icon("resultset_up.gif")
		# Move Section Down	 resultset_down.gif
		self.imgdata["Section Down"] = self.get_icon("resultset_down.gif")

		# Content pane buttons
		self.imgdata["Preview"] = self.get_icon("report.gif")
		self.imgdata["Settings"] = self.get_icon("cog.gif")

		# settings buttons
		# "Select Image"	picture.gif
		self.imgdata["Select Image"] = self.get_icon("picture.gif")
		# "Select Colour"	color_swatch.gif
		self.imgdata["Select Colour"] = self.get_icon("color_swatch.gif")

	def get_icon(self, imagefile):
		if len(self.b64) < 1:
			self.load_b64()

		# files["New"] = "famfamfam_silk_icons/icons/page_white.edt.gif"

		if imagefile not in self.b64:
			self.base.debugmsg(6, "imagefile:", imagefile)
			scrdir = os.path.dirname(__file__)
			self.base.debugmsg(6, "scrdir:", scrdir)
			imgfile = os.path.join(scrdir, "../famfamfam_silk_icons/icons", imagefile)
			self.base.debugmsg(6, "imgfile:", imgfile)
			if os.path.isfile(imgfile):
				self.base.debugmsg(0, "isfile: imgfile:", imgfile)
				with open(imgfile, "rb") as f:
					img_raw = f.read()
				# 		self.b64["page_writer.gif"] =
				self.base.debugmsg(0, "img_raw:	", "self.b64[\"{}\"] =".format(imagefile), img_raw)
				# b64 = base64.encodestring(img_raw)
				# img_text = 'img_b64 = \\\n"""{}"""'.format(b64)

				self.b64[imagefile] = img_raw  # tk.PhotoImage(file=imgfile)
				# self.base.debugmsg(0, "self.b64[",imagefile,"]:", self.imgdata[icontext])

			else:
				self.base.debugmsg(6, "File not found imgfile:", imgfile)

		if imagefile in self.b64:
			return tk.PhotoImage(data=self.b64[imagefile])
		else:
			self.base.debugmsg(6, "File not found imagefile:", imagefile)

	def load_b64(self):

		# gif's
		self.b64["page_add.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa*d\xbb.ga1h>.i\xbe0i\xba3j\x124l\x1aIm\xb64q\xc18v\xc3?y\xbe;z\xc4AzzJ{,B~\xc3?\x80\xc7D\x83\xc6F\x88\xc7\\\x88HI\x89\xc7M\x8c\xc9Q\x8c"c\x8cKU\x8f(d\x93\xdcs\x99_\x81\xac`\x8e\xae\x86}\xb2\xe3R\xb4\xf8R\xb5\xf7\x84\xb7\xe3\x9c\xb9\xa7\x87\xbb_\x8d\xbcd\x8f\xbci\xa0\xbd\xaec\xbf\xfcg\xc0\xfdm\xc3\xfd\xb3\xd4\x94\xb5\xd4\xf2\xb7\xd5\x9d\x97\xd7\xff\x9c\xd7\xff\xbb\xd7\xf5\x9c\xd8\xff\xa1\xd9\xff\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc7\xe0\xfa\xcb\xe3\xfb\xd1\xe6\xbb\xd4\xe6\xfd\xd8\xe6\xf2\xd8\xe7\xfe\xd7\xe8\xfe\xd9\xe8\xfe\xde\xea\xf6\xe1\xeb\xf6\xe9\xef\xf5\xe6\xf0\xf7\xec\xf2\xf7\xec\xf3\xf9\xf1\xf5\xf9\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00E\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb9\x80E\x10\x16\x84\x85\x84\x15\x0bE\x8a\x8a\x12AB\x8f\x90A9\x1e\x1a\x8bE\x15C6\x9a654/D2\x94\x8b\x98\x9b\x9a\x9eD\x9a!\x0c\x8a\x988\xae\xa63>AC?\x10\xacC\xae\xaf6\x9e++C\x12\xacB:\xb98\xb03B\xc0E\x13B<\xcd\xb9\xa64\xc8\x8cB;<\xc4\xc5\x9cB\x11\xd3\xd7\xae&\x1b\x18\x18\x0e\x8a\x11B\xdd"\x1c*7%\x19\x07E\r@\x1f  \x1f\xf2\x14**D$$\xee\r>)1`\xb8\x80\xd1\xe2\x01\x0b"\x08U\xb8S\xe0\x03\xc5\x89\x87\x0f\x11\x90\x18Ad\x04\xbf"\x05\x84\xf8\xe8\xc1\xb1\x87\x90\x0e\x17H\xa8 q\xc1\x9d\x01\x01(S\xa2\x1c\x80\xe0\x00\x02\x02E\x02\x01\x00;'

		self.b64["folder_page.gif"] = b"GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00@j\xaa9q\xaaAu\xc6C{\xc3Q\x7f\xcbS\x84\xccS\x84\xd0\xd9\x86'\xd9\x87(\xd9\x89)\xdb\x941^\x97\xcd\xdb\x9b2l\x9f\xd1k\xa1\xd2\xdb\xa53\xe1\xa6K\xe3\xabS\xdb\xac2\xdb\xb22\xda\xb5/\x88\xbc\xea\x93\xbc\xe5\xe7\xbdp\xe9\xbdc\x97\xc0\xe6\x93\xc2\xec\xc7\xc2\x86\x9e\xc4\xea\xe3\xc4^\xd0\xc9\x8c\xeb\xca\x91\xd8\xcf\x90\xf2\xd2=\xb3\xd3\xf4\xdd\xd3\x93\xf3\xd5r\xf3\xd6L\xe4\xd8\x93\xf3\xd8z\xbd\xd9\xf7\xd7\xd9\xca\xf4\xda\\\xf4\xdb\x83\xe9\xdc\x93\xf5\xdcf\xf6\xddk\xc4\xde\xfa\xf5\xde\x8c\xf5\xde\x93\xf6\xdft\xf6\xe1\x94\xf7\xe1}\xcc\xe2\xfc\xf6\xe2\xad\xc5\xe3\xfa\xf5\xe3\xa0\xf7\xe3\x84\xf6\xe5\x9c\xf8\xe5\x8c\xf8\xe5\x93\xd4\xe6\xfd\xd8\xe7\xff\xdb\xe9\xff\xde\xe9\xf5\xf8\xea\xc3\xe5\xef\xfa\xe7\xf2\xfc\xe8\xf2\xef\xf9\xf2\xdc\xfb\xf2\xcc\xeb\xf4\xfc\xfb\xf6\xe8\xf1\xf7\xff\xf3\xf9\xfd\xfe\xfa\xef\xfe\xfc\xf4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00O\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbe\x80O\x82\x83\x1d\x1a\x17\x17\x0f\x0e\x0c\x04\x83\x8dO\x17NH\x92CD\x16\x07\x8e\x82\x17H060#K8\x1b\x8c\x8e\x17J6\xa7)AHK\x06\x98\xa5>>\x9d)#C\x06\x15\x1e\xb8\xb8\xaf\xb0\xb2D\x06\x14N\xc1\xc1\xbb\xbc0H\xbfM<297\x06J@\xd0?\xb1J\x06\x13M22\x19\x0b\xdb\xdc\xdc\xc7\x13I\x18\x12\x11 H\xc2\xc2\x0bE\x06\x10\xc1M\xee;\xf0\xf09F\x0b\xc7\x10M=\xf9=-'$!\x1f\x1cT,\x18P\xa0\x01\xbe|<t\xd4\x98\xf1b\x85\x89#\x0b\x04-`\xd2\x83G\xc2\x85.\x1c\x8a\x80(H\x81\x91\x1d4h\xc4\x88\xc1\x82\x05\x8a\x12%\x84D|\x82@A\x02\x050c\xc2|\x89@P \x00;"

		self.b64["page_save.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa\x1cZ\xaf)^\xa7+d\xbb6h\xab/i\xbc0i\xba;i\xacAl\xacIm\xb6Ap\xb14q\xc18v\xc3?y\xbe;z\xc4B~\xc3U~\xbcO\x7f\xc4Q\x7f\xc2D\x83\xc6T\x83\xc5\\\x84\xc0Z\x86\xc8F\x88\xc7I\x89\xc7^\x89\xcag\x8b\xd4k\x8b\xcel\x8b\xdbM\x8c\xc9c\x8c\xcbp\x8f\xe2k\x92\xced\x93\xdcm\x98\xd5s\x9a\xd2z\x9e\xd6z\x9e\xdcw\x9f\xda{\xa2\xdc\x82\xa5\xd7\x83\xa5\xde\x81\xa8\xe3\x85\xa9\xde\x8c\xb0\xe5}\xb2\xe3R\xb4\xf8R\xb6\xf7\x92\xb6\xe6\x84\xb7\xe3\x9a\xb7\xed\x9a\xb9\xeac\xbf\xfcg\xc0\xfd\x84\xc0O\x84\xc0R\xa2\xc0\xed\x9f\xc1\xefm\xc3\xfd\xb4\xc8\xe4\x99\xcao\x9a\xcaq\xb1\xce\xf3\xbb\xcf\xef\xb5\xd4\xf2\x9c\xd7\xff\xbb\xd7\xf5\x9c\xd8\xff\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc6\xe0\xf9\xcb\xe3\xfb\xd5\xe6\xfd\xd8\xe6\xf2\xd8\xe7\xfe\xd7\xe8\xfe\xd9\xe8\xfe\xde\xea\xf6\xe1\xeb\xf6\xc8\xee\x87\xc8\xee\x8c\xe9\xef\xf5\xe6\xf0\xf7\xe6\xf1\xee\xe8\xf3\xea\xec\xf3\xf5\xed\xf3\xf8\xe9\xf4\xe5\xd8\xf5\xa3\xf1\xf5\xf9\xf4\xfa\xff\xff\xff\xde\xff\xff\xe1\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00`\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xcd\x80\x10\x1e\x83\x84\x1e\x19\r`\x89\x8a\x14WX\x8e\x8eWK."\x8a\x89\x19[I\x99HGC_E\x93\x95\x97\x99\x99\x9c_\x992\x0e\x8a\x97JJ\xa4FPW[S\x10\xaa[\xac\xadI\x9cAA[\x14\xaaXL\xb7#%$)\x1f!$$\x1f`\x18XNN\xac\x1f?_<_\xd6_9\x1a\x14XM\xb7\x17:_!\xd6\\\\-\x1f\xdb\xb7J\x1a9\xd7\xd7,\x13\x0fT/0//\x1f4(*(\xfb(&\x16\x0fPv\x10\x11B\xe4C\x8c\x15+\xf8\x9d \x11\x81\x01\x14\x1b5"V\x98q\xa5\x8a\xc5*WJ,0\x80\x05\xca\x93\x8f\x12fX\xb9\xd1\xc3\x07\x8e,&\n\x1c \xc0\x92e\x05 ]\xa2h\xd1"\xc5\x8b\n\x04\x95\x12\x19\xa8\xb0\x01D\x87\x9f\x1c\x12\x0c\x08\x04\x00;'

		self.b64["folder_table.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00@w\xbcR\x85\xc5\xda\x86\'\xd9\x87(\xd9\x89)W\x8a\xc9\\\x8a\xc6^\x8f\xccc\x93\xcf\xdb\x941l\x9a\xd4\xdb\x9b2t\xa1\xd8|\xa5\xdc\xdb\xa53\xe2\xa9O\x80\xaa\xde\x98\xaa\xc1\xdb\xac2\x84\xad\xe1\xe0\xae`\xe4\xafZ\xdb\xb22\x8c\xb3\xe4\xda\xb5/\x94\xb8\xe7\xb3\xb9\x92\x9c\xbd\xea\xb6\xbd\x9c|\xbfv\x9f\xc0\xec\xe5\xc2\x91\x82\xc3|\xa6\xc3\xeb\xbe\xc4\xa5\xe3\xc4_\xc1\xc6\xa7\xea\xc6~\x89\xc7\x82\xac\xc7\xe9\xad\xc8\xe8\xb3\xcb\xe8\xc6\xcb\xae\x93\xcc\x8b\xb8\xcc\xe2\xf0\xcc \xf1\xce)\xf1\xd1j\xf2\xd15\xf1\xd3r\xf3\xd4D\xa4\xd5\x9b\xf2\xd5|\xf2\xd6\x81\xf3\xd7R\xf3\xd8\x86\xf4\xd8T\xf3\xd9\x8e\xf5\xdba\xd2\xdc\xdf\xf4\xdc\x9f\xf4\xde\x94\xf4\xde\xa8\xf6\xden\xf6\xdfr\xf5\xe1\xa0\xf7\xe1z\xf7\xe2\x82\xdb\xe5\xf1\xf8\xe5\x8c\xf8\xe6\x94\xf9\xe9\xa4\xf8\xea\xc3\xed\xeb\xe5\xfa\xec\xad\xfa\xed\xb4\xf3\xef\xe7\xfb\xef\xba\xfa\xf0\xdd\xeb\xf1\xf7\xfc\xf2\xca\xef\xf3\xf8\xf7\xf6\xed\xfb\xf6\xe8\xf4\xf7\xfb\xfd\xf8\xe7\xfe\xfa\xec\xfe\xfc\xf5\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00Z\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc6\x80Z\x82\x82"\x85\x1c\x1a\x18\x18\x14\x11\x0e\x0e\x83\x84U\x91\x92\x92\r\x8fZ\x1fU44,\'!!\x1eU\x0b\x96\x1cUY\xa6\xa7Y\xa1\xa3U\x85\xad\x85U\t\x19$\xb3$\x1a\xacY)\xa8P\x08\x17\xa8\x18U(())*\xc5E\x06\x17XF>B\xbf\xb9\xb9\xa7E\x02\x13X>>6\x12 \n\xdb\xdc\n\xd2\x13T&\x16\x10\x15SSMJ\xe9R\xde\x07\x0f\xa6XX<+%#\x1d\x1d\x1b-\n\x02\x01\x0fXQNK\x8c\x18!2\x04\xc8\x8e\x1cV\x14\x08b\x80\x85\t\x92#D\x08\x1a\xbc1\xe3\x8aB-\n\xae<$\x12\xe4\xe0\x8c\x18/\\D\xb9X\xe0\xc9\x8f\x1e>t\xe0\xa8QC\x06\x0c\x18I\n\x08\x1aP\x80@\x81\x9b8o\xda\x1c (\x10\x00;'

		self.b64["page_go.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa$_\xb8)b\xb7\'d\xb4*d\xbb.i\xbe0i\xbaIm\xb6\x1cq\x004q\xc18v\xc3?y\xbe\x1dz\x16\x17{\x02\x1b{\x0b;{\xc4B~\xc3\x1f\x7f\x00?\x80\xc7D\x83\xc61\x87\x08F\x88\xc7I\x89\xc77\x8b\r6\x8c\x10M\x8c\xc9@\x8f\x11F\x91\x15d\x93\xdcC\x94)H\x94.O\x98\x1dU\x99"Z\x9c#b\x9f.]\xa06c\xa0,[\xa18^\xa2@k\xa44d\xa5Dm\xa6<r\xa9Ct\xacM|\xb0S}\xb2\xe3\x81\xb4YS\xb5\xf8S\xb6\xf7\x82\xb6d\x84\xb7\xe3\x85\xb7i\x8c\xbam\x90\xbdte\xbf\xfcg\xc0\xfd\x97\xc2\x80m\xc3\xfd\x99\xc3\x83\x9f\xc6\x88\xa2\xc7\x8a\xa4\xc9\x8c\xac\xcd\x92\xb1\xcf\x97\xb5\xd4\xf2\xbb\xd7\xf5\x9f\xd8\xff\xa1\xd9\xff\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc6\xe0\xf9\xcc\xe3\xfb\xd4\xe6\xfd\xd8\xe6\xf2\xd8\xe7\xfe\xd7\xe8\xfe\xd9\xe8\xfe\xde\xea\xf6\xe1\xeb\xf6\xe9\xef\xf5\xe6\xf0\xf7\xec\xf2\xf7\xec\xf3\xf9\xf1\xf5\xf9\x00\xff\x00\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00X\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc5\x80X\x11\x1a\x84\x85\x84\x17\x0bX\x8a\x8a\x14ST\x8f\x90SK.\x1d\x8bX\x17UI\x9aIHGBWE\x94\x8b\x98\x9b\x9a\x9eW\x9a3\x0c\x8a\x98J\xae\xa6FPSUQ\x11\xacU\xae\xafI\x9eAAU\x14\xacTL\xb9J\xb0FT\xc0X\x16TN\xcd\xb9I+%G\xc8\x8cTMN\xc4J*/!T\x13\xd5\xb9*((#-?,\x1c\x10\x8a\x13T\xb9(@?\xf16>)\x15\x8a\x10R011%?552\x02\xee0!\x01\x0b\x04(:\x88\x0c\x11\xf1\xc3G\x0f\x1e4v\xa4h\xa0H\x01\x14\x1c7n\x80\xe0\xb0\x01\x03\x89\x1c)<\x10Pd\x80\n\x94\'(\x9f<\xcap\xe2\xc3\x15\x01\x8a\x0e\x14\x98Is\xe6\x03\x07\x05\x06\x0c\xc0\x12\x08\x00;'

		self.b64["add.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00,|\x1d+~"&\x80\x1e/\x81)0\x81\'3\x83)8\x87.=\x8a2A\x8e5E\x8f9K\x92?Q\x95CN\x9a>U\x9bE]\x9dLb\xa0Me\xa2Ri\xa5Zh\xa6Vj\xabVl\xab[f\xacRu\xacat\xad_z\xb2d~\xb3h\x83\xb5kn\xb6V\x88\xb8op\xb9W\x87\xbaqt\xbb\\}\xbbk\x8a\xbcr}\xbde\x8b\xbfzp\xc2by\xc2c\x8d\xc3{|\xc4i\x92\xc6\x80~\xc8o\x89\xc9\x7f\x86\xcbz\x99\xcc\x86\x81\xcdu\x8d\xcd\x83\x99\xcd\x8a\x93\xce\x88\xa5\xcf\x94\x8a\xd0}\xa7\xd1\x97\x8e\xd3\x83\x99\xd4\x8b\x96\xd5\x8a\xac\xd5\x9e\x9e\xd9\x92\xa1\xda\x97\xb5\xda\xa6\xb8\xdb\xab\xa6\xdc\x9c\xb5\xdd\xaa\xbb\xde\xb0\xb0\xe0\xa7\xb6\xe0\xad\xbc\xe3\xb5\xcc\xe6\xc4\xc6\xe8\xc1\xcf\xe9\xca\xd5\xeb\xd0\xd8\xee\xd3\xdd\xf1\xd9\xe1\xf2\xdd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00K\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb1\x80K\x82\x83\x84\x85\x86"\x1b\x1b\x19\x17\x17\x86\x82"\x1f2CFE?!\x13\x11\x85\x90?IB=:@D\'\x0f\x0f\x84\x1f<H91/775B!\x0e\x83\x1d-G:7+JJ,(*A\x0e\x0b\x82\x1b>@/,!\xba\x15  6)\n\x82\x1aB6,\xba\xd5J\x1e(8\x08\x82\x19>3.\xd6\xba\x1e#\xda\x82\x1807(%\x16\xe2\x1e -$\x06\x82\x15\x16>&\xcb\xe2\x1c ;\t\xf2\x82\x11!|,\xf3\xc0A\xdf\x8e\n\xfe\x04Ax\xd0\xad\xc5\x88\x11-vP( \xa0\x90\x03\x06\rN\xd0\xa0A\x02\x01EGK\x14$@p\xc0\x00\x01\x90(\t\x05\x02\x00;'

		self.b64["delete.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\xb9F$\xb5G"\xb9I&\xb5J\x1e\xbcK+\xc2K.\xd1M;\xbfN2\xc5N3\xcdP8\xbfR4\xc1R6\xc2S=\xc5TB\xdcTI\xe6UL\xcaVD\xceVJ\xe9WK\xce[L\xe7[T\xea[N\xd8\\O\xd5^T\xec^R\xd1aS\xdac]\xddcb\xf0cT\xd6d\\\xe1d[\xead[\xeeeP\xe3gg\xddie\xeei]\xe1jj\xe3kb\xe3pe\xf3s\\\xf2wb\xf3yb\xe4zs\xe9{s\xe9\x7fx\xf6\x82g\xf0\x83{\xed\x84}\xf6\x84k\xf0\x85p\xf8\x86p\xee\x8au\xee\x8c\x81\xf0\x8cw\xf8\x8cv\xf1\x8ez\xf4\x8e\x81\xee\x92\x8f\xf5\x92~\xf9\x93\x7f\xfa\x9b\x87\xf1\x9e\x97\xfa\x9e\x8b\xf4\xa2\x9f\xfa\xa4\x91\xf5\xa6\xa1\xf5\xab\xa3\xfb\xab\x9e\xf2\xae\xab\xf5\xb0\xa6\xf8\xb0\xa5\xf4\xb5\xab\xf8\xb7\xa9\xf9\xba\xb0\xfa\xbb\xaf\xf8\xc4\xbf\xfc\xc8\xbb\xf9\xcc\xc5\xfb\xd5\xce\xfd\xdc\xd5\xfd\xdd\xd9\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00S\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xaf\x80S\x82\x83\x84\x85\x86%#\x1c\x1b\x1b\x1e\x86\x82%%:LONH\'\x18\x14\x85\x90EQKA?DM,\x14\x11\x84%CP=;8<<7I&\xa5\x82"0O?;41\xba1*G\x07\r\x82&FD6\x19\xc6\xc7)9-\x0c\x82#J<2R\xd2\xd3\x13$>\x08\x82\x1bC3.\xd3\xd4 >\x05\xd95;(\x13\xe7\xe8\x16/+\xe2S\x18\x0fC\x1d!\xe8\x13\x10\x15B\t\x03\x83\x1a&C\x19\x16\xf5 @\x00\x82!\x00!\t\x11>\x08\x81\x01\xa2\x02\x0c \x17\x06\x08(\x14\xc1\x81\x02\x16:t\xac0 \xd1\xd1\x94\x04\x0b\x10\x14(\xa0\xcf\xa3\xc9A\x81\x00\x00;'

		self.b64["resultset_up.gif"] = b'GIF89a\x10\x00\x10\x00\xa5\x00\x00\x00\x00\x00\x14A\xb7\x15E\xb9\x16J\xbd\x16N\xc0\x17P\xbd\x18S\xc0\x19Y\xc5\x1ab\xc6\x1ab\xc9#n\xcd,r\xcd<s\xce5w\xd2=w\xd0?z\xd0C\x7f\xd3E\x84\xd6K\x88\xd6S\x8e\xdba\x96\xddb\x97\xe1n\xa0\xe2t\xa2\xdfu\xa3\xe1y\xa7\xe3}\xa9\xe1}\xa9\xe8\x80\xab\xe9\x82\xac\xe3\x87\xb0\xe8\x8a\xb1\xe4\x90\xb5\xe7\x92\xb7\xe8\x99\xbb\xea\xa2\xc2\xed\xa8\xc7\xee\xad\xc8\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\n\x00?\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06G\xc0\x9fpH,\x1a\x8f\xc8\xa4r\xc9L"\x0e\xcd\x85\x04bXF(\x9f\xce\xa3\x90\xa4`D\x1d\x8c\xc618b<\xa3P\xf8\x92a\x08\x8a\x9bM\x894\x12\x81:\x9a\x0b#@\xe4p2\x16\x15\x13\x11\r\n\t\x07\x04M\x8a\x8b\x8cHA\x00;'

		self.b64["resultset_down.gif"] = b'GIF89a\x10\x00\x10\x00\xa5\x00\x00\x00\x00\x00\x14A\xb7\x15E\xb9\x16J\xbd\x16N\xc0\x17P\xbd\x18S\xc0\x19Y\xc5\x1ab\xc6\x1ab\xc9#n\xcd,r\xcd<s\xce5w\xd2=w\xd0?z\xd0C\x7f\xd3E\x84\xd6K\x88\xd6S\x8e\xdba\x96\xddb\x97\xe1n\xa0\xe2t\xa2\xdfu\xa3\xe1y\xa7\xe3}\xa9\xe1}\xa9\xe8\x80\xab\xe9\x82\xac\xe3\x87\xb0\xe8\x8a\xb1\xe4\x90\xb5\xe7\x92\xb7\xe8\x99\xbb\xea\xa2\xc2\xed\xa8\xc7\xee\xad\xc8\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00?\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06G\xc0\x9fpH,\x1a\x8f\xc8\xa4rI8$\x14\x8d\xc8\xa4b\xc9p8\xc4\x00\xe3\xa2\xe9\x80D#Ri\xb3)\n\x18\x99\x0b\xa6\x13\x1ay0\xc7\x81C\xb3\x16a(\xc9\xc2\xa3\xf3\xa1D\x96\x06\x10\x12\x0bKB\x07\x08\x85\x89\x8a\x8b\x8c\x8dA\x00;'

		self.b64["report.gif"] = b'GIF89a\x10\x00\x10\x00\xc6\\\x00~1\x18\xabB!\xacC!\xaeF"\xaeI"\xa5K,\xafK#\xb1N#\xb2Q$\xb2R%\xb4U%\xb5V&\xb7Y&\xb7[&\xaf]5\xb8^\'\xb8_\'\xbaa(\xbexI\xb3yc\xb3|d\xb5\x7fe\xb5\x82f\xb7\x83gj\x93\xd4\xb9\x87gj\x98\xd9\xc2\x8bdk\x99\xdan\x9a\xdc\xbf\x8fao\x9b\xdcr\x9c\xdcq\x9d\xdd\xc1\x92cq\x9e\xdfs\x9e\xdf\xc2\x94ds\x9f\xe0t\xa0\xe0v\xa0\xe0\xc3\x96ev\xa2\xe0w\xa3\xe1x\xa3\xe1\xc4\x99f\xc5\x9agz\xa5\xe1\xa0\xbe\xea\xa1\xbf\xea\xa2\xc0\xea\xa3\xc0\xea\xca\xc6\xc4\xcc\xc6\xc0\xc7\xc7\xc7\xcd\xc6\xc0\xca\xc7\xc4\xcd\xc7\xc0\xcd\xc7\xc1\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd8\xd8\xd8\xdc\xdc\xdc\xe6\xe6\xe6\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xec\xec\xec\xed\xed\xed\xee\xee\xee\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff!\xfe\x11Created with GIMP\x00!\xf9\x04\x01\n\x00\x7f\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbf\x80\x7f\x7f\x1b\x12\x11\x82\x87\x88\x87>8:\x10Z\x8f\x90\x91\x87\x19.\x0fU\x97USR\x9bPY\x82\x8b9\r\x98\x97S\xa5QX\x87\x17-\x0cVV/,+*(\'R\xa8\x7f>49\x0bWW,3210#RU\x87\x16)\nXX\xb2\'$ \x1fPT\x9f\xb9\tYX\xadVUQPNM\x87\x15%\x08\xd7&!\x1d\x1c\x1a\x18JK\xd37\x07XW\xd9T\xcaXP@\x87\x14"\x06\xbcWT\xa7\xf4;H\xa6\xd5 \xa0\xcc\x8a\x94\'Y\xa0\xf08\xa2\xe5\xd0\x04\x0f\x03\x94\xf5k\x12ea\x96\x86\xb7h\xd4\x10\xb0%\x8bA&D\x92p\x19y\xa8\x80\x83\x00F\x8a\x0c\t\x02D\x08\x90\x1e?l \x02\x90\xa8\xe6\x9f@\x00;'

		self.b64["cog.gif"] = b'GIF87a\x10\x00\x10\x00\xc4\x00\x00\x00\x00\x00GGGMMMTTT[[[ccclllpppyyy\x82\x82\x82\x8d\x8d\x8d\x94\x94\x94\x9c\x9c\x9c\xa5\xa5\xa5\xac\xac\xac\xb4\xb4\xb4\xbc\xbc\xbc\xc4\xc4\xc4\xcb\xcb\xcb\xd4\xd4\xd4\xdc\xdc\xdc\xe5\xe5\xe5\xeb\xeb\xeb\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00\x18\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x05\x91 &\x8e\x92\x14Ac\xaaFU\xe5\xa8\xe3Tb\x11E=\x98\xd341eQ\xa7\xc9\xe4\xe1\x90T \n\x91\x892\xb1\t\x99%\xc4a\x14\x91I \x8cFd\x8bTn)\xd7\x04"\xa1\xd8J\x14\x89D\xc4bm$D\x0c\xc7\xa9f`M"\x92\xc7B\xb4\x90C\xaa\x05\r\x0b\rw\x12\x0c\x0c\x0be\x10\x10\x05\x03\x03"rf\x0e~D\x06#:\x85V&\x10\x12\x06\x05"\r\x10\x14nj\x11\x06\x06\x84\t\x8f"\t\x9e\x18\t%\x9f\x03\x02\x010\xac\x10\x0f\x04\xb6*\x06\xb3\xab)!\x00;'

		self.b64["page_white_world.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00=[0B\x89\xc1M\x91\xc1\x95\x95\x95d\x97SK\x99\xbd\x9b\x9b\x9bj\x9cVk\x9fZm\xa0Wl\xa1ZN\xa2\xd4T\xa2\x8ae\xa4\x83P\xa6cV\xa6\xd6f\xa6\xa3W\xa7\xce\x7f\xa8iT\xaa\xe2U\xac\xdc|\xactg\xad\xda\x80\xadk\x82\xadsb\xaf\xc9m\xaf\xcf\x85\xafy\x86\xb0x\x88\xb3|\x82\xb4\x84i\xb5\xcdi\xb6\xab\x8b\xb6\xa7\x8d\xb7\xbc\x8d\xb9xS\xba\x9d\x8a\xbal\x92\xbb\x91\x97\xbb{f\xbd\xb8p\xbd\xc1z\xc1\xd7\xa0\xc3\x88Z\xc4`\x84\xc4\xdb\x8c\xc4\xd2\x9b\xc4\x7f\x9c\xc4\x85\xa4\xc5\x91|\xc6t\xaa\xc6\xa0\x82\xc7\xcbw\xc9\xc6\xaa\xc9\x8f\xac\xc9\xa2\x8e\xcb\xb0\xa3\xcb\x9b\xa0\xcc\xbbk\xd0\xad\xa2\xd2\x8d\xc3\xd5\xbc\x83\xd6\xb1\x9b\xd6\xd9q\xd7\x93\xa4\xd8\x94y\xda\x96\xc8\xda\xc2B\xdb^\xbd\xdb\xbaZ\xdc}\xa0\xdc\x8f\xa4\xdc\xdc\xb6\xdd\xd5\xd3\xde\xce\x91\xe0\x8b\xd4\xe0\xd0\xc3\xe3\xaf\xbf\xe5\xd5\xdb\xe6\xd6\x8c\xe7\xa2\xe7\xe7\xe7\xbe\xea\xd6\xbb\xec\xca\xec\xec\xec\xac\xf1\xbc\xd0\xf2\xce\xf4\xf4\xf4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00Z\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xa8\x80Z\x82\x83\x84\x85\x84Y\x88\x89\x89\x04\x86YX\x8f\x8fUUYR\x8c\x83\x018\x19\x0b\x194MX\x93\x8f\x07\x82\x08\x082FJ;\x1f\x1d>\x93\x89\x82\x0bNWOI./:\x19K\x92RYZ\n1VT@+)AL\x184\x9f\x93Z\x0bBQS 6GE-,\x19\x90\xbc\x0bHC5\x12*<%\x0f7\t\x8eX\xd8=?\x1a\x15\x0c\x02\x03\x0e(\x19\x8a\xcb$3!\x10\x14\x06\r\x1e\t8\xf1Z\x08096\\\x88`b\x02\x07(\xfd\x10\x14\xb0 b\xc4\x89\x04\x1c\x88(\xe2%\x08S\x86\x04\x19p \x9cxh\xa2GC \t\x05\x02\x00;'

		self.b64["page_excel.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00+U\xaa$_\xb8)b\xb7*d\xbb.i\xbe0i\xbaIm\xb62o\xc06t\xc2.u\x138v\xc33x\x18?y\xbe;{\xc4<~\x80B~\xc3?\x7f)?\x80\xc7D\x834D\x83\xc6F\x88\xc3I\x89\xc6Q\x8boM\x8c\xc9T\x8cSU\x8dAI\x92I[\x93E_\x93Sd\x93\xdc_\x95Ic\x97Sc\x98Oe\x98Wd\x9adj\x9c`q\x9fdm\xa1Zs\xa1km\xa2Wt\xa5\\i\xac`u\xaff\x83\xaf\x8d}\xb2\xe3\x90\xb5\x90q\xb7\\\x82\xb7q\x84\xb7\xe3\x96\xba\xa2\x84\xbcx\x87\xbds\x84\xc1i\x8a\xc2l\xa2\xc2\xb2\x96\xc9t\x98\xcav\xb5\xd2\xe9\xa4\xd4\x82\xb5\xd4\xf2\xbf\xd4\xb6\xba\xd7\xf5\xc4\xd7\xbc\xb5\xd9\xf6\xbd\xda\xf6\xc3\xda\xe5\xb6\xdb\x9d\xcb\xdc\xc4\xc3\xdd\xf8\xc4\xdd\xf4\xce\xde\xc8\xc7\xe0\xfa\xcd\xe1\xf5\xcb\xe3\xfb\xd2\xe5\xfc\xd8\xe6\xf2\xde\xea\xf6\xe1\xec\xf6\xe9\xef\xf5\xe6\xf0\xf7\xec\xf2\xf7\xec\xf3\xf9\xf2\xf6\xfa\xf5\xf9\xfc\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00V\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc5\x80V\x10\x18\x84\x85\x84\x16\x0bV\x8a\x8a\x14QR\x8f\x90QL-\x1e\x8bV\x16SJ\x9aJHE>U@\x94\x8b\x98\x9b\x9a\x9eU\x9a1\rV\x1a\x19  2,\x11\x11\x13\x13.QSO\x10\xac=C8 \x1f)(!#:<<S\x14\x8a\x17D;6\xc0\xc4FEAAR\xcaV\x15%D94\x1a\x1dI\xa6E\xd6\x8a\x0f\x0c\x1cG50\x1a7K\x9aHR\x12V\n\n&\x1c\xe7/+\x1a\n\x9bS\x0e\xf2\xf3\n4\x90\xf81C\x05\x88MT\x12(r\x00e\xc9\x12!%@\x888\xe1p\t\x15\x04\x0b\x9dT\xdcXq\n\x01E\t4r\xdcX\xe5\xa3\x95\x02R\x9c4Y\xd9\x04\xd2\x14*U\x04(2@\xa0\xa6\xcd\x9b\x04\x06\x0c\xb0\x12\x08\x00;'

		self.b64["page_word.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x1bN\xd3\x1dS\xd4+U\xaa ^\xd3$_\xb8)b\xb7*d\xbb\x1ee\xd3!g\xd4.i\xbe0i\xbaIm\xb62o\xc0%p\xd66t\xc28v\xc3=v\xd2?y\xbe:z\xc4=z\xd2I}\xd2A~\xd2B~\xc3?\x80\xc7C\x82\xd3D\x83\xc6L\x84\xd5]\x87\xe3I\x89\xc6M\x8c\xc9l\x8c\xe5H\x8d\xe4T\x8e\xe3a\x92\xe5d\x93\xdcN\x96\xe4o\x99\xe5T\x9a\xe5f\x9d\xe6v\x9d\xe7|\x9d\xe8Z\xa1\xe5\x88\xa1\xe9c\xa2\xe6l\xa2\xe8\x85\xa2\xe9i\xa5\xe7p\xa7\xe8\x84\xa7\xe6\x8a\xac\xebq\xad\xe8}\xb2\xe3\x8e\xb3\xed\x91\xb5\xed\x9c\xb5\xef\x84\xb7\xe3\xb6\xcb\xef\xb5\xd4\xf2\xbb\xd7\xf5\xb5\xd9\xf6\xbd\xda\xf6\xc3\xdd\xf8\xc7\xe0\xfa\xd4\xe1\xf3\xcb\xe2\xfb\xd2\xe5\xfc\xd8\xe6\xf2\xd8\xe7\xfe\xde\xea\xf6\xe1\xeb\xf6\xe9\xef\xf5\xec\xf2\xf7\xec\xf3\xf9\xf2\xf6\xfa\xf5\xf9\xfc\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00M\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xc5\x80M\x17\x1e\x84\x85\x84\x1d\x10M\x8a\x8a\x1aHI\x8f\x90HC4#\x8bM\x1dJA\x9aA?>;L<\x94\x8b\x98\x9b\x9a\x9eL\x9a8\x12M\x0e**56&52\x19!FHJG\x17M\t3,B&$B%\x19=;::J\x1a\x8a,9D\x19(B\x162A>==I\xcb\x08/1\x19/" \x16B\xa6>\xd9M\x04/0\x16)-\x1b7B\xe3\x9cI\x18M\x02,\x19A.\'\x14\xf0\xf1AJ\x13\xea\xbd\xa8 \x84\xc3\x86\x15\xf0J-y\xd0$\x80\x05 B>D\xe8GqI\x03E\x13\x8cP\xdc(D\xc9\x01E\x0f4r\xec\xc7\xe4c\x13\x05I\x8c\x14YY\x04\x92\x92%L\n(Zp\xa0\xa6\xcd\x9b\x07\x0c\x18h\x12\x08\x00;'

		self.b64["page_white_acrobat.gif"] = b'GIF87a\x10\x00\x10\x00\xd5\x00\x00\x00\x00\x00\x97\n\x08\x9b\x0e\n\xc1\x10\x0e\xcc\x10\x0c\xd0\x13\r\xc3\x1e\x0f\xdb4(\xe0NC\xdcSM\xe0SJ\xe6]Q\xe3d\\\xeag\\\xe5h_\xe8i_\xe4le\xe7ul\xedvj\xe5{u\xee\x7ft\xf1\x7fs\xe5\x81z\xf1\x84x\xe6\x87\x81\x95\x95\x95\x9b\x9b\x9b\xed\x9d\x98\xe9\xa1\x9c\xeb\xa4\xa0\xf2\xa7\x9f\xed\xac\xa8\xf3\xae\xa7\xef\xb9\xb5\xf3\xc0\xba\xf1\xc4\xc1\xf2\xcc\xca\xf5\xd1\xcd\xf6\xd7\xd5\xf7\xdd\xdb\xf8\xdf\xdd\xf8\xe5\xe5\xe7\xe7\xe7\xf7\xe9\xe8\xf9\xe9\xe7\xec\xec\xec\xf9\xee\xed\xf9\xf3\xf3\xf4\xf4\xf4\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x002\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06r@\x99pH,\x12c\xc8d2c\x8c\xc1."\x18\xac\xd5\x8a\xa9\x98GX\xa5$\x9d:a\x9acL\xe2\xe9V\x93b\n\x08)\xa5\xaab\xe2\x86$\xd9\xae\x1eQ\x8b\x87\x89.\x85\x0fc\x11\x1b\'\x0e\'|~B,\n)\'\x10\x07\x08\x0c\x13\x1fHD\x13\x16!\x1d#&\x18\x10\x13\x1c\x93B\x02\t.JH+/\x9f\x05\x03$\xa4\xac2\x04\x04\x01\xac\xad\x7f\xb2JF\xb7DA\x00;'

		self.b64["page_calc.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x00\x00>\x00\x00A\x00%O\x00\'P\x146S\x007\\\x19;X\t<[!Cb,Ge-He7Md.Nt\'Ol*On?Rs\x00S{1Sl\x00UUAUmUUUUU\xaa4\\y&^\x82:_}?_\x83fff;k\x8bEk\x8bFk\x86Jk\x86bo~ir\x89Zs\x8cVt\x95Ew\x9aVz\x94i}\x92\x80\x80\x80Y\x82\xa2{\x88\x95\x86\x98\xa9\x89\x99\xa5\x82\x9b\xb1\x9f\xa3\xaf\x9a\xa9\xb6U\xaa\xaa\x9e\xb0{\xa6\xb1\xbc\xa3\xb3t\xaa\xb3\xbb\x92\xb6\xb6\xb0\xb8\xc1\x80\xbf@\xb7\xbf\x8f\xbf\xbf@\xb0\xc2m\xaf\xc5?\xac\xc6\x1f\xaf\xc7%\xba\xc7\xd1\xae\xce\x00\xbc\xce\xda\xc4\xd1\xdc\xbc\xd2\x85\xd1\xd3\xd6\xc1\xd6g\xca\xd6\x91\xcc\xd6\xe0\xcf\xd6\xdb\xc5\xd7\xe4\xd2\xd7\xda\xcc\xd8\xb4\xcf\xda\xe1\xd3\xda\xd3\xd4\xda\xdf\xd2\xde\xa6\xd5\xde\xe4\xd7\xde\xe8\xd3\xdf\xaa\xd9\xdf\xd2\xcc\xe0\xef\xd6\xe0\xae\xd6\xe1\xea\xd8\xe1\xb6\xdb\xe1\xd4\xdc\xe3\xe7\xd1\xe4\x8a\xdc\xe4\xea\xdc\xe5\xba\xde\xe5\xc3\xe0\xe6\xc6\xe1\xe6\xdc\xe1\xe7\xc9\xe1\xe7\xeb\xdf\xe8\xbd\xe4\xe9\xed\xe5\xea\xcc\xe2\xeb\xc5\xe5\xec\xf3\xe6\xec\xe5\xe7\xec\xd0\xe0\xed\xf8\xe9\xed\xd3\xe9\xee\xf3\xeb\xef\xea\xe7\xf1\xc4\xe8\xf1\xc7\xec\xf1\xf9\xed\xf2\xe7\xed\xf2\xe8\xed\xf2\xf5\xf0\xf3\xec\xf3\xf5\xf9\xf7\xf7\xf7\xf3\xf9\xfb\xfa\xfc\xf6\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00w\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xbf\x80w\x82\x18\x11Hvd_rjD\x82\x8dwFE@gYJYttX<2\x8d53&*?LpiLOA>;\x8ew"1idNFNdI9C:\x8dYTNRGWp\xbf\xaemKw==+\x04 Navr\x97\x97\xcc\x8e\x06\x14sv\xd5\xd6\xd6\x8e\x0b\x02B\xd7uv\xdev\x8e\n\x01-uUcSb\xe9lq\x8e\t\x03!nZbPhMfkn\xee\x08\x10]\xf3\xf5M\xc4\xacy\xe3\xe8\x81\x83\x06Q\xc0\xd0\xb3\'P_\xa3\x0c\x174XQ\x08\x10M>G\x1d8\x8c\xf0\xb7\x05\x8a\x17(\\\xc6\x94q\x84\x82\x04\x0bg\xce\xe0\xd8\xf9\xe2\xa8\x04\x07\x17a\xb2\xc8\x9c\x99\xc5\xc9\x9d@\x00;'

		self.b64["page_writer.gif"] = b'GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x00\x00C\x00)R\x146S\x007\\\x19;X\x16?_\x00@d"Db,Ge-He7Md)On,Qo1Sl#Tu\x00UU\x00U|AUmUUUUU\xaa:^}&_\x83\x00c\x8ffff]j|Ck\x8cFk\x86Jk\x869m\x8cKo\x8cbo~ar\x84Zs\x8cOw\x96Ex\x9bVz\x94i}\x92@\x80\x80\x80\x80\x80Y\x83\xa3c\x85\x9e{\x88\x95y\x8a\x9a\x86\x98\xa9\x89\x99\xa5~\x9a\xb1\x85\x9c\xb1\x99\x9f\xa7\x8c\xa8\xbfU\xaa\xaa\x9d\xac\xb7\xa6\xb1\xbd\xaa\xb3\xbb\x92\xb6\xb6\xa0\xb6\xc8\xb1\xbb\xc4\xb9\xc6\xd1\xbe\xca\xd4\xc3\xcc\xd5\xbc\xce\xda\xc6\xd0\xdb\xcc\xd3\xda\xd1\xd3\xd6\xc5\xd7\xe4\xcc\xd7\xe0\xd1\xd7\xdc\xd2\xd9\xde\xcf\xda\xe1\xd5\xde\xe4\xcc\xe0\xef\xd6\xe1\xea\xdb\xe1\xe7\xda\xe4\xec\xe0\xe6\xea\xe3\xe9\xed\xe9\xec\xee\xe0\xed\xf8\xe7\xed\xf3\xeb\xee\xf1\xee\xf2\xf6\xf3\xf4\xf6\xf5\xf7\xf9\xf5\xfa\xfd\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00U\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb8\x80U\x82\x16\x11BTNJQL8\x82\x8dU>A=MIDISS7)\x8e85%,<CPOCH/\x17"\x8eU!4ONE>EK9/1.\x8dIGEF@HP\xbe\xa2PCU99-\x02\x1f\xb1TRR\x97S\xca\x8e\x04\x12QT\xd4\xd5\xd5\x8e\n\x01?\xcaQ\xdd\xdd\xd4\x8e\t\x010TJ;>\xe8;\xe0\x8d\x08\x02\x19TL>C\xf3\xd7\xec\x06\x08\x8a>BB\xe8\xeb\x82\x0c\r\x0e0y\x82\x0e\x1d\x13\x7fU*Tx\xf0\x84\xe0\x90}\xd3\xa88\xd2\xa0\xc1\xc3\x13s>z\xf4\xd0A%\x8a#\x14#^4\x1bY\xce\x11\x89\x0e3\x96 Y\xc92I\x91*\x81\x00\x00;'

		self.b64["picture.gif"] = b"GIF87a\x10\x00\x10\x00\xe6\x00\x00\x00\x00\x00\x9b{1v\x82]\x80\x83T\xb0\x86<\x87\x8b>\x86\x8eA^\x91\x8bc\x93\x91b\x978i\x97\xa4e\x9a<i\x9a\xa6s\x9e\xc4w\x9e\xd7h\x9f\x9b\xd3\xa0R|\xa2\xd9}\xa3\xc6\x81\xa5\xdbt\xa7H\x82\xa7\xc8\x8e\xa7\xce\x84\xa8\xdd\x8e\xa8\xcew\xa9Jx\xab\xa0z\xabL\x94\xab\xcf{\xacj\x8a\xac\xdf\x94\xac\xd0\x9a\xae\xce\x8e\xaf\xe1\x9b\xaf\xd0\xd2\xb0m|\xb1x\x9b\xb1\xce\x87\xb3o\xa0\xb3\xd0\x7f\xb4\xa2\x87\xb4\xb7\x8d\xb5\xd1\x96\xb5\xe4\xa3\xb5\xce\x80\xb6\xaa\x93\xb6\xd2\x98\xb6\xe4\x80\xb7\xa4\x87\xb8\xb9\x9c\xb9\xe5z\xbbM\x87\xbc`\x8b\xbc\x83\xa0\xbc\xe7\x7f\xbeS\x87\xbek\x8a\xbed\xa2\xbe\xe8\x81\xbfQ\x87\xc2U\x8b\xc3W\x8e\xc3q\x94\xc3\x8a\x8f\xc6b\x91\xc7]\xca\xc9\x9d\x99\xcai\x9a\xcad\xa2\xcd\x93\xa1\xce}\xa7\xd1\x82\xaa\xd2\x83\xa9\xd3t\xc6\xd4\xb0\xc4\xda\xbb\xc3\xdd\xc0\xeb\xec\xec\xe6\xee\xf6\xeb\xef\xf2\xed\xf2\xf7\xef\xf3\xf8\xf1\xf4\xf8\xf3\xf5\xf7\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00U\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x07\xb5\x80U\x82\x83\x84\x85\x82,'\x1c\x18\x8b\x8b\x16\x8e\x16\x1c%\x82'MS\x96\x97\x97PO \x82\x1cS+*-EHG?\x0f\r\x0eP\x1f\x82\x18S/1EIDDC5\x0c\x11\xaa\xacS20HDA=<>\x07\xb8\x1c\xba2(FA<;78\x07\x13N\xc6U\x18P2)?@;37$\n\x17\xd2\xacP6.\x1a&94\x1d\x08\x12\x1e\xe1\xd4P:\xe4\x02\x06\x05\x03\x15!\xed\xd3\xd5\x1b\x19\x14\x01\x10\x10\x08,X\x90\xc0\x9d\x05(L\x12*\x112bIB&\x06\x11>\x9c\x98\xd0\x1d\x87'S\xa4H\xb1\x04\xa5#\x94(OD\x08*!\x82\x83\xc9\x93(Ap2\xc4rP \x00;"

		self.b64["color_swatch.gif"] = b'GIF87a\x10\x00\x10\x00\xb3\x00\x00\x00\x00\x00\xfeoj\xffw\xb2Vz\xb1\xda\x9c\xde\xff\xabs_\xb1\xebN\xcdl\xf0\xd6f\xd1\xeb\xb3\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\t\x00\x00\x0b\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x04@p\xc9I\xab\xbd6\xe8U\xfaB`\xa5\x05\x9c\x07"\xe2\xd6\x15_\x88\xbdS"/G\xbd\x18x%\'\xb4\x8d\x1b\xbaY\xedp\xcb\xc1`\x83\xe4\x82\xc0\\\x08\x9e\x95\xe4`\xd9|\n\xa2J&\xc1\t=z\xbf\xe0\x08\x00;'

	def set_app_icon(self):
		script_dir = os.path.dirname(os.path.abspath(__file__))
		icon_dir = os.path.join(script_dir, "icons")
		self.base.debugmsg(5, "icon_dir:", icon_dir)
		icon_file = os.path.join(icon_dir, "rfswarm-reporter-128.png")
		self.icon = tk.PhotoImage(file=icon_file)
		self.root.wm_iconphoto(False, self.icon)

	def updateTitle(self):
		titletext = "{} v{} - {}".format(self.titleprefix, self.base.version, "Please Select")
		# ['Reporter']['ResultDir']
		if 'Reporter' in self.base.config and 'Results' in self.base.config['Reporter']:
			if len(self.base.config['Reporter']['Results']) > 0:
				path, filename = os.path.split(self.base.config['Reporter']['Results'])
				basepath, dirname = os.path.split(path)
				titletext = "{} v{} - {}".format(self.titleprefix, self.base.version, dirname)

		self.master.title(titletext)

	def updateStatus(self, newstatus):
		# newstatus = "Template: Untitled"
		self.statusmsg.set(newstatus)

	def updateResults(self):
		# self.stsResults.set(self.base.config['Reporter']['Results'])
		if self.base.config['Reporter']['Results']:
			sres = "Results: {}".format(self.base.config['Reporter']['Results'])
			self.stsResults.set(sres)
		else:
			sres = "Results: Please select a result file"
			self.stsResults.set(sres)

	def updateTemplate(self):
		# self.stsTemplate.set(self.base.config['Reporter']['Results'])
		if self.base.whitespace_get_ini_value(self.base.config['Reporter']['Template']):
			stem = "Template: {}".format(self.base.whitespace_get_ini_value(self.base.config['Reporter']['Template']))
			self.stsTemplate.set(stem)
		else:
			stem = "Template: Untitled"
			self.stsTemplate.set(stem)

	def save_window_size(self, event):
		self.base.debugmsg(6, "save_window_size")
		try:
			self.base.debugmsg(6, "winfo_width:", self.winfo_width(), "	winfo_height:", self.winfo_height())
			self.base.config['GUI']['win_width'] = str(self.winfo_width())
			self.base.config['GUI']['win_height'] = str(self.winfo_height())
			self.base.saveini()
		except Exception as e:
			self.base.debugmsg(6, "save_window_size except:", e)
			return False

	def BuildMenu(self):
		window = self.master
		self.root.option_add('*tearOff', False)
		root_menu = tk.Menu(window)

		if sys.platform.startswith('darwin'):
			appmenu = tk.Menu(root_menu, name='apple')
			root_menu.add_cascade(menu=appmenu)
			appmenu.add_command(label='About rfswarm Reporter')
			appmenu.add_separator()
			self.base.debugmsg(5, "appmenu:", appmenu)

		window.config(menu=root_menu)
		results_menu = tk.Menu(root_menu)  # it intializes a new sub menu in the root menu
		root_menu.add_cascade(label="Results", menu=results_menu)  # it creates the name of the sub menu

		# accelkey = "Ctrl"
		accelkey = "Control"
		if sys.platform.startswith('darwin'):
			accelkey = "Command"
		shifkey = "Shift"

		results_menu.add_command(label="Open", command=self.mnu_results_Open, accelerator="{}-o".format(accelkey))
		window.bind("<{}-o>".format(accelkey), self.mnu_results_Open)
		results_menu.add_separator()  # it adds a line after the 'Open files' option

		if sys.platform.startswith('darwin'):
			# https://tkdocs.com/tutorial/menus.html
			# root.createcommand('tk::mac::ShowPreferences', showMyPreferencesDialog)
			self.root.createcommand('tk::mac::Quit', self.on_closing)
		else:
			results_menu.add_command(label="Exit", command=self.on_closing, accelerator="{}-x".format(accelkey))
			window.bind("<{}-x>".format(accelkey), self.on_closing)

		self.template_menu = tk.Menu(root_menu)
		root_menu.add_cascade(label="Template", menu=self.template_menu)

		self.template_menu.add_command(label="New", command=self.mnu_template_New, accelerator="{}-n".format(accelkey))  # it adds a option to the sub menu 'command' parameter is used to do some action
		window.bind("<{}-n>".format(accelkey), self.mnu_template_New)
		self.template_menu.add_command(label="Open", command=self.mnu_template_Open, accelerator="{}-t".format(accelkey))
		window.bind("<{}-t>".format(accelkey), self.mnu_template_Open)
		self.template_menu.add_command(label="Save", command=self.mnu_template_Save, accelerator="{}-s".format(accelkey))
		window.bind("<{}-s>".format(accelkey), self.mnu_template_Save)
		self.template_menu.add_command(label="Save As", command=self.mnu_template_SaveAs, accelerator="{}-{}-s".format(accelkey, shifkey))
		window.bind("<{}-S>".format(accelkey), self.mnu_template_SaveAs)

	def BuildUI(self):

		self.bind("<Configure>", self.save_window_size)

		self.ConfigureStyle()

		self.bbar = tk.Frame(self)
		self.bbar.grid(column=0, row=0, sticky="nsew")
		# self.bbar.config(bg="red")

		self.mainframe = tk.Frame(self)
		self.mainframe.grid(column=0, row=1, sticky="nsew")
		# self.mainframe.config(bg="green")

		self.stsbar = tk.Frame(self)
		self.stsbar.grid(column=0, row=9, sticky="nsew")
		# self.stsbar.config(bg="pink")

		# statusmsg
		self.stsTemplate = tk.StringVar()
		self.stsResults = tk.StringVar()
		self.statusmsg = tk.StringVar()

		self.ststmpl = ttk.Label(self.stsbar, textvariable=self.stsTemplate)
		self.ststmpl.grid(column=0, row=0, sticky="nsew")
		self.stsres = ttk.Label(self.stsbar, textvariable=self.stsResults)
		self.stsres.grid(column=0, row=1, sticky="nsew")
		self.stslbl = ttk.Label(self.stsbar, textvariable=self.statusmsg)
		self.stslbl.grid(column=0, row=3, sticky="nsew")

		self.stsbar.columnconfigure(0, weight=1)
		self.stsbar.rowconfigure(0, weight=1)
		self.updateStatus("")
		self.updateResults()
		self.updateTemplate()

		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.mainframe.rowconfigure(1, weight=1)

		self.sbbar = tk.Frame(self.mainframe)
		self.sbbar.grid(column=0, row=0, sticky="nsew")
		# self.sbbar.config(bg="blue")

		self.sections = tk.Frame(self.mainframe, relief=tk.SUNKEN, bd=3)
		self.sections.grid(column=0, row=1, sticky="nsew")
		# self.sections.config(bg="cyan")
		# self.mainframe.columnconfigure(0, weight=1)
		self.sections.columnconfigure(0, weight=1)
		self.sections.rowconfigure(0, weight=1)

		# self.btnShowHide = tk.StringVar()
		# btnShowHide = tk.Button(self.mainframe, textvariable=self.btnShowHide, command=self.sections_show_hide, width=1, padx=0, pady=0, bd=0, relief=tk.FLAT, fg=self.style_text_colour)
		# self.btnShowHide.set("<")
		# btnShowHide.grid(column=1, row=1, sticky="nsew")
		# btnShowHide.rowconfigure(1, weight=1)

		self.content = tk.Frame(self.mainframe, bd=0)
		self.content.grid(column=2, row=0, columnspan=2, rowspan=2, sticky="nsew")
		# self.content.config(bg="lightblue")
		self.content.columnconfigure(0, weight=1)
		self.content.rowconfigure(0, weight=1)

		self.mainframe.columnconfigure(2, weight=1)
		self.mainframe.columnconfigure(3, weight=1)

		self.ConfigureStyle()

		self.BuildToolBar()
		self.BuildSections()
		self.BuildContent()

	def ConfigureStyle(self):

		self.style_head_colour = self.base.rs_setting_get_hcolour()

		fontname = self.base.rs_setting_get_font()
		fontsize = self.base.rs_setting_get_fontsize()
		sizeup = int(fontsize * 0.1)
		if sizeup < 1:
			sizeup = int(1)
		self.base.debugmsg(8, "sizeup:", sizeup)

		# Theme settings for ttk
		self.style = ttk.Style()

		self.style.configure("TFrame", borderwidth=0)

		if sys.platform.startswith('darwin'):
			release, _, machine = platform.mac_ver()
			split_ver = release.split('.')
			if int(split_ver[0]) > 10:
				# we really only seem to need this for MacOS 11 and up for now
				# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-style-layer.html
				# https://tkdocs.com/tutorial/styles.html#usetheme

				self.style.configure("TLabel", foreground=self.style_text_colour)
				self.style.configure("TEntry", foreground="systemPlaceholderTextColor")
				self.style.configure("TEntry", insertcolor=self.style_text_colour)

				self.style.configure("TButton", foreground=self.style_text_colour)
				self.style.configure("TMenubutton", foreground=self.style_text_colour)

				self.style.configure("Canvas", fill=self.style_text_colour)
				self.style.configure("Canvas", activefill=self.style_text_colour)

				self.style.configure("TSpinbox", foreground=self.style_text_colour)

				self.style.configure("TRadiobutton", foreground=self.style_text_colour)

				self.style.configure("Treeview", foreground=self.style_text_colour)
				self.style.configure("Treeview", background=self.rootBackground)
				self.style.configure("Treeview", fieldbackground=self.rootBackground)

				self.base.debugmsg(9, "self.style_text_colour:	", self.style_text_colour)
				self.base.debugmsg(9, "self.rootBackground:		", self.rootBackground)

		layout = self.style.layout('TLabel')
		self.base.debugmsg(9, "TLabel 	layout:", layout)
		self.style.configure("Head.TLabel", foreground=self.style_head_colour)

		layout = self.style.layout('Head.TLabel')
		self.base.debugmsg(9, "Head.TLabel 	layout:", layout)

		matplotlib.rcParams['font.family'] = fontname

		self.style.configure('Report.TLabel', font=(fontname, fontsize))

		self.base.debugmsg(9, "fontsize:", fontsize, "	sizeup:", sizeup, "	5*sizeup:", 5 * sizeup, "	H1 size:", fontsize + (5 * sizeup))

		self.style.configure("Report.H1.TLabel", foreground=self.style_head_colour)
		# self.style.configure("Report.H1.TLabel", foreground=self.style_head_colour, background=self.style_reportbg_colour)
		self.style.configure('Report.H1.TLabel', font=(fontname, fontsize + (5 * sizeup)))
		# self.style.configure('Report.H1.TLabel', background=self.style_reportbg_colour)
		# self.style.configure('Report.H1.TLabel', activebackground=self.style_reportbg_colour)
		layout = self.style.layout('Report.H1.TLabel')
		self.base.debugmsg(9, "Report.H1.TLabel 	layout:", layout)

		self.style.configure("Report.H2.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H2.TLabel', font=(fontname, fontsize + (4 * sizeup)))

		self.style.configure("Report.H3.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H3.TLabel', font=(fontname, fontsize + (3 * sizeup)))

		self.style.configure("Report.H4.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H4.TLabel', font=(fontname, fontsize + (2 * sizeup)))

		self.style.configure("Report.H5.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H5.TLabel', font=(fontname, fontsize + (1 * sizeup)))

		self.style.configure("Report.H6.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.H6.TLabel', font=(fontname, fontsize))

		self.style.configure('Report.Title1.TLabel', font=(fontname, fontsize + (10 * sizeup)))
		self.style.configure('Report.Title2.TLabel', font=(fontname, fontsize + (5 * sizeup)))

		self.style.configure("Report.THead.TLabel", foreground=self.style_head_colour)
		self.style.configure('Report.THead.TLabel', font=(fontname, fontsize + (1 * sizeup)))
		self.style.configure('Report.THead.TLabel', relief="raised")

		self.style.configure('Report.TBody.TLabel', font=(fontname, fontsize))
		# self.style.configure('Report.TBody.TLabel', relief="sunken")
		# self.style.configure('Report.TBody.TLabel', relief="ridge")
		self.style.configure('Report.TBody.TLabel', relief="groove")

		self.style.configure('Report.Settings.FileInput.TLabel', relief="sunken")

	def BuildToolBar(self):
		btnno = 0

		# Open Scenario Results
		# 	"Open Scenario Results"	folder_table.png
		icontext = "Open Scenario Results"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_results_Open)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		btnno += 1
		# New Report Template
		# 	"New Report Template"	page_add.png
		icontext = "New Report Template"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_template_New)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# Open Report Template
		# 	self.imgdata["Open Report Template"] = folder_page.png
		btnno += 1
		icontext = "Open Report Template"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_template_Open)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# Save Report Template
		# 	"Save Report Template"	page_save.png
		btnno += 1
		icontext = "Save Report Template"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_template_Save)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# # Apply Report Template
		# # 	"Apply Report Template"	page_go.png
		# btnno += 1
		# icontext = "Apply Report Template"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_do_nothing)
		# bnew.grid(column=btnno, row=0, sticky="nsew")

		btnno = 9
		self.bbar.columnconfigure(btnno, weight=1)

		# "Export HTML"		page_white_world.gif			HTML - Issue #36
		btnno += 1
		icontext = "Export HTML"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_html)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# https://github.com/eea/odfpy		MHT and HTML
		# https://docs.python.org/3/library/markup.html
		# https://github.com/CenterForOpenScience/pydocx

		# # "Export PDF"		page_white_acrobat.png
		# btnno += 1
		# icontext = "Export PDF"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_pdf)
		# bnew.grid(column=btnno, row=0, sticky="nsew")

		# # "Export Writer"		page_writer.gif
		# btnno += 1
		# icontext = "Export Writer"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_writer)
		# bnew.grid(column=btnno, row=0, sticky="nsew")
		# # https://github.com/eea/odfpy
		# # https://en.wikipedia.org/wiki/OpenDocument_technical_specification
		# # https://docs.python.org/3/library/zipfile.html

		# "Export Word"		page_word.png					Word - Issue #38
		btnno += 1
		icontext = "Export Word"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_word)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# https://python-docx.readthedocs.io/en/latest/
		# https://github.com/python-openxml/python-docx
		# http://officeopenxml.com/
		# https://docs.python.org/3/library/zipfile.html

		# # "Export Calc"		page_calc.gif
		# btnno += 1
		# icontext = "Export Calc"
		# bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_calc)
		# bnew.grid(column=btnno, row=0, sticky="nsew")
		# # https://github.com/pyexcel/pyexcel
		# # https://github.com/pyexcel/pyexcel-ods

		# "Export Excel"		page_excel.png				Excel - Issue #37
		btnno += 1
		icontext = "Export Excel"
		bnew = ttk.Button(self.bbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_export_excel)
		bnew.grid(column=btnno, row=0, sticky="nsew")
		# https://xlsxwriter.readthedocs.io/introduction.html
		# https://openpyxl.readthedocs.io/en/stable/index.html
		# https://github.com/pyexcel/pyexcel
		# https://github.com/python-openxml/python-xlsx - seems doesn't exist

	def BuildSections(self):

		# self.sbbar
		btnno = 0
		# New Section
		# 	"New Section"	add.gif
		icontext = "New Section"
		bnew = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_new_rpt_sect)
		bnew.grid(column=btnno, row=0, sticky="nsew")

		# Remove Section
		# delete.gif
		btnno += 1
		icontext = "Remove Section"
		brem = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_rem_rpt_sect)
		brem.grid(column=btnno, row=0, sticky="nsew")

		# Move Section Up
		# resultset_up.gif
		btnno += 1
		icontext = "Section Up"
		bup = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_rpt_sect_up)
		bup.grid(column=btnno, row=0, sticky="nsew")

		# Move Section Down
		# resultset_down.gif
		btnno += 1
		icontext = "Section Down"
		bdwn = ttk.Button(self.sbbar, image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, command=self.mnu_rpt_sect_down)
		bdwn.grid(column=btnno, row=0, sticky="nsew")

		# 	https://pythonguides.com/python-tkinter-treeview/
		self.sectionstree = ttk.Treeview(self.sections, selectmode='browse', show='tree')

		self.sectionstree.grid(column=0, row=0, sticky="nsew")
		# ttk.Style().configure("Treeview", background="pink")
		# ttk.Style().configure("Treeview", fieldbackground="orange")

		self.sections.vsb = ttk.Scrollbar(self.sections, orient="vertical", command=self.sectionstree.yview)
		self.sectionstree.configure(yscrollcommand=self.sections.vsb.set)
		self.sections.vsb.grid(column=1, row=0, sticky="nsew")

		self.sections.hsb = ttk.Scrollbar(self.sections, orient="horizontal", command=self.sectionstree.xview)
		self.sectionstree.configure(xscrollcommand=self.sections.hsb.set)
		self.sections.hsb.grid(column=0, row=1, sticky="nsew")

		self.sectionstree.bind("<Button-1>", self.sect_click_sect)

		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)
		if len(selected) > 0:
			self.LoadSections(selected)
		else:
			self.LoadSections("TOP")

	def LoadSections(self, ParentID):
		if ParentID == "TOP":
			items = self.sectionstree.get_children("")
			self.base.debugmsg(9, "items:", items)
			if len(items) > 0:
				for itm in items:
					self.sectionstree.delete(itm)
			self.sectionstree.insert("", "end", ParentID, text="Report", open=True, tags=ParentID)
		else:
			items = self.sectionstree.get_children(ParentID)
			self.base.debugmsg(9, "items:", items)
			if len(items) > 0:
				for itm in items:
					self.sectionstree.delete(itm)

		sections = self.base.report_get_order(ParentID)
		self.base.debugmsg(9, "sections:", sections)
		for sect in sections:
			self.LoadSection(ParentID, sect)

		self.sectionstree.tag_bind("Sect", callback=self.sect_click_sect)

	def LoadSection(self, ParentID, sectionID):
		self.base.debugmsg(9, "ParentID:", ParentID, "	sectionID:", sectionID)
		sect_name = "{}".format(self.base.whitespace_get_ini_value(self.base.report[sectionID]["Name"]))
		self.base.debugmsg(9, "sect_name:", sect_name)
		items = list(self.sectionstree.get_children(ParentID))
		self.base.debugmsg(9, "items:", items)
		if sectionID not in items:
			self.sectionstree.insert(ParentID, "end", sectionID, text=sect_name, tags="Sect")
		if "Order" in self.base.report[sectionID]:
			self.LoadSections(sectionID)
		# self.sectionstree.see(sectionID)

	def on_closing(self, _event=None, *extras):
		self.base.running = False
		try:
			self.base.debugmsg(5, "close window")
			self.destroy()
		except Exception:
			# were closing the application anyway, ignore any error
			pass
		self.base.debugmsg(5, "self.base.core.on_closing")
		self.base.core.on_closing()

	def sect_click_top(self, *args):
		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)

	def sect_click_sect(self, *args):
		self.base.debugmsg(5, "args:", args, args[0].x, args[0].y)
		# self.base.debugmsg(5, "clicked:", clicked)
		clicked = self.sectionstree.identify_row(args[0].y)
		self.base.debugmsg(5, "clicked:", clicked, type(clicked), id(clicked))
		if len(clicked) < 1:
			# unselect
			clicked = "TOP"
			self.sectionstree.selection_set('')
			self.sectionstree.focus('')
			return

		# load section pane

		self.content_load(clicked)

	def BuildContent(self):

		# this removes a lot of wasted space and gives it back to the data in each tab
		# 	I think the system default is ~20 on macos 11
		self.tabs = ttk.Notebook(self.content, padding=0)

		# first page, which would get widgets gridded into it
		icontext = "Preview"
		self.base.debugmsg(8, icontext)

		self.contentframe = tk.Frame(self.tabs, padx=0, pady=0, bd=0)
		# self.contentframe.config(bg="salmon")
		self.contentframe.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)

		self.contentcanvas = tk.Canvas(self.contentframe)
		self.contentcanvas.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)
		self.contentframe.columnconfigure(0, weight=1)
		self.contentframe.rowconfigure(0, weight=1)
		self.contentcanvas.columnconfigure(0, weight=1)
		self.contentcanvas.rowconfigure(0, weight=1)

		self.contentpreview = tk.Frame(self.contentcanvas, padx=0, pady=0)
		# self.contentpreview.config(bg="cyan")
		self.contentpreview.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)
		self.contentpreview.columnconfigure(0, weight=1)
		self.contentpreview.rowconfigure(0, weight=1)

		self.contentcanvas.create_window((0, 0), window=self.contentpreview, anchor='nw')

		# Vertical Scroolbar
		self.content.vsb = ttk.Scrollbar(self.contentframe, orient="vertical", command=self.contentcanvas.yview)
		self.contentcanvas.configure(yscrollcommand=self.content.vsb.set)
		self.content.vsb.grid(column=1, row=0, sticky="ns")

		# Horizontal Scroolbar
		hsb = ttk.Scrollbar(self.contentframe, orient="horizontal", command=self.contentcanvas.xview)
		self.contentcanvas.configure(xscrollcommand=hsb.set)
		hsb.grid(column=0, row=1, sticky="ew")

		self.tabs.add(self.contentframe, image=self.imgdata[icontext], text=icontext, compound=tk.LEFT, padding=0, sticky="nsew")

		self.base.debugmsg(9, "self.tabs:", self.tabs)
		self.base.debugmsg(9, "self.tabs.tab(0):", self.tabs.tab(0))
		self.base.debugmsg(9, "self.contentpreview:", self.contentpreview)

		# second page
		icontext = "Settings"
		self.base.debugmsg(6, icontext)
		self.contentsettings = tk.Frame(self.tabs, padx=0, pady=0, bd=0)
		# self.contentsettings.config(bg="linen")
		self.contentsettings.grid(column=0, row=0, sticky="nsew", padx=0, pady=0)
		self.contentsettings.columnconfigure(0, weight=1)
		self.contentsettings.rowconfigure(0, weight=1)
		self.tabs.add(self.contentsettings, image=self.imgdata[icontext], text=icontext, compound=tk.LEFT, padding=0, sticky="nsew")

		self.tabs.grid(column=0, row=0, sticky="nsew")
		self.tabs.select(1)
		# self.c_preview
		# selected = self.sectionstree.focus()
		# self.base.debugmsg(5, "selected:", selected)
		# if len(selected) > 0:
		# 	self.content_load(selected)
		# else:
		self.content_load("TOP")

	def content_load(self, id):
		self.base.debugmsg(8, "id:", id)
		# self.content_settings(id)
		cs = threading.Thread(target=lambda: self.content_settings(id))
		cs.start()

		# self.content_preview(id)
		cp = threading.Thread(target=lambda: self.content_preview(id))
		cp.start()

	def dispaly_donation_reminder(self):
		if 'donation_reminder' not in self.base.config['GUI']:
			self.base.config['GUI']['donation_reminder'] = "0"
			self.base.saveini()

		lastreminder = int(self.base.config['GUI']['donation_reminder'])
		timenow = int(datetime.now().timestamp())
		timesincereminder = timenow - lastreminder
		yearseconds = 60 * 60 * 24 * 365

		# display donation reminder on first launch and then once per year
		if timesincereminder > yearseconds:

			titlemsg = self.titleprefix + " - Donation Reminder"

			donatemsg = "RFSwarm's mission is to give you a an industry leading performance test tool, that is easy to use, "
			donatemsg += "quick to develop test scripts and free from limitations so that you can just get on with testing."
			donatemsg += "\n\n"
			donatemsg += "Accomplishing this mission costs us resources, and requires the time of many talented people to fix "
			donatemsg += "bugs and develop new features and generally improve RFSwarm."
			donatemsg += "\n\n"
			donatemsg += "RFSwarm is proud to be a completely open source application that is 100% community funded and "
			donatemsg += "does not harvest and sell your data in any way."
			donatemsg += "\n\n"
			donatemsg += "So today we're asking for you help to make RFSwarm better, please consider giving a donation "
			donatemsg += "to support RFSwarm."

			self.drWindow = tk.Toplevel(self.root)
			self.drWindow.wm_iconphoto(False, self.icon)
			self.drWindow.columnconfigure(0, weight=1)
			self.drWindow.columnconfigure(2, weight=1)
			self.drWindow.title(titlemsg)
			self.drWindow.attributes('-topmost', 'true')

			row = 0
			self.drWindow.rowconfigure(row, weight=1)

			self.drWindow.lblDR00 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR00.grid(column=0, row=row, sticky="nsew")

			self.drWindow.lblDR01 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR01.grid(column=1, row=row, sticky="nsew")

			self.drWindow.lblDR02 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR02.grid(column=2, row=row, sticky="nsew")

			row += 1
			self.drWindow.lblDR11 = ttk.Label(self.drWindow, text=donatemsg, wraplength=600)
			self.drWindow.lblDR11.grid(column=1, row=row, sticky="nsew")

			row += 1
			self.drWindow.rowconfigure(row, weight=1)
			self.drWindow.lblDR21 = ttk.Label(self.drWindow, text=" ")
			self.drWindow.lblDR21.grid(column=1, row=row, sticky="nsew")

			row += 1

			self.drWindow.fmeBBar = tk.Frame(self.drWindow)
			self.drWindow.fmeBBar.grid(column=0, row=row, columnspan=5, sticky="nsew")

			self.drWindow.fmeBBar.columnconfigure(0, weight=1)

			self.drWindow.bind('<Return>', self.close_donation_reminder)
			self.drWindow.bind('<Key-Escape>', self.drWindow.destroy)

			bdonate = ttk.Button(self.drWindow.fmeBBar, text="Donate", padding='3 3 3 3', command=self.close_donation_reminder)
			bdonate.grid(column=9, row=0, sticky="nsew")

			blater = ttk.Button(self.drWindow.fmeBBar, text="Maybe Later", padding='3 3 3 3', command=self.drWindow.destroy)
			blater.grid(column=8, row=0, sticky="nsew")

			self.base.config['GUI']['donation_reminder'] = str(int(datetime.now().timestamp()))
			self.base.saveini()

	def close_donation_reminder(self, *args):
		self.base.debugmsg(5, "args:", args)
		self.drWindow.destroy()

		url = "https://github.com/sponsors/damies13"
		webbrowser.open(url, new=0, autoraise=True)

	#
	# Settings
	#

	def content_settings(self, id):
		self.base.debugmsg(9, "id:", id)
		# self.content
		if id not in self.contentdata:
			self.contentdata[id] = {}
		if id + 'L' not in self.contentdata:
			self.contentdata[id + 'L'] = {}
		if id + 'R' not in self.contentdata:
			self.contentdata[id + 'R'] = {}
		if "Settings" not in self.contentdata[id]:
			self.contentdata[id]["Settings"] = tk.Frame(self.contentsettings, padx=0, pady=0, bd=0)
			# self.contentdata[id]["Settings"].config(bg="rosy brown")
			if id == "TOP":
				self.cs_reportsettings()
			else:
				rownum = 0
				# Input field headding / name
				self.contentdata[id]["lblHeading"] = ttk.Label(self.contentdata[id]["Settings"], text="Heading:")
				self.contentdata[id]["lblHeading"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["Heading"] = tk.StringVar()
				self.contentdata[id]["Heading"].set(self.base.report_item_get_name(id))
				self.contentdata[id]["eHeading"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["Heading"])
				self.contentdata[id]["eHeading"].grid(column=1, row=rownum, sticky="nsew")
				# https://pysimplegui.readthedocs.io/en/latest/
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["eHeading"].bind('<Leave>', self.cs_rename_heading)
				self.contentdata[id]["eHeading"].bind('<FocusOut>', self.cs_rename_heading)

				rownum += 1
				# option list - heading / text / graph / table
				self.contentdata[id]["lblType"] = ttk.Label(self.contentdata[id]["Settings"], text="Type:")
				self.contentdata[id]["lblType"].grid(column=0, row=rownum, sticky="nsew")

				ContentTypes = [None] + list(self.base.settings["ContentTypes"].values())
				self.contentdata[id]["Type"] = tk.StringVar()
				self.contentdata[id]["Type"].set(self.base.report_item_get_type_lbl(id))
				self.contentdata[id]["omType"] = ttk.OptionMenu(
					self.contentdata[id]["Settings"],
					self.contentdata[id]["Type"],
					command=self.cs_change_type,
					*ContentTypes
				)
				self.contentdata[id]["omType"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# Left and right frames
				# Left frame
				self.contentdata[id]["LFrame"] = tk.Frame(self.contentdata[id]["Settings"], padx=0, pady=0, bd=0)
				self.contentdata[id]["LFrame"].grid(column=0, row=rownum, columnspan=10, sticky="nsew")

				# Left frame padding
				self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Settings"], text="")
				self.contentdata[id]["lblSpacer"].grid(column=9, row=rownum - 1, sticky="nsew")
				self.contentdata[id]["Settings"].columnconfigure(9, weight=1)

				# Right frame
				self.contentdata[id]["RFrame"] = tk.Frame(self.contentdata[id]["Settings"], padx=0, pady=0, bd=0)
				self.contentdata[id]["RFrame"].grid(column=10, row=rownum, columnspan=10, sticky="nsew")

				# Right frame padding
				self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Settings"], text="")
				self.contentdata[id]["lblSpacer"].grid(column=19, row=rownum - 1, sticky="nsew")
				self.contentdata[id]["Settings"].columnconfigure(19, weight=1)

				self.contentdata[id]["Settings"].rowconfigure(rownum, weight=1)

				# call function to load settings for option selected (heading doesn't need)
				type = self.base.report_item_get_type(id)
				self.base.debugmsg(5, "type:", type)
				if type == 'contents':
					self.cs_contents(id)
				if type == 'note':
					self.cs_note(id)
				if type == 'table':
					self.cs_datatable(id)
				if type == 'graph':
					self.cs_graph(id)
				if type == 'errors':
					self.cs_errors(id)

		curritem = self.contentsettings.grid_slaves(column=0, row=0)
		self.base.debugmsg(5, "curritem:", curritem)
		if len(curritem) > 0:
			curritem[0].grid_forget()
		self.base.debugmsg(5, "newitem:", self.contentdata[id]["Settings"])
		self.contentdata[id]["Settings"].grid(column=0, row=0, sticky="nsew")

	def cs_reportsettings(self):
		rownum = 0
		id = "TOP"

		if "Settings" in self.contentdata[id]:
			self.contentdata[id]["Settings"].grid_forget()
			del self.contentdata[id]["Settings"]
			self.contentdata[id]["Settings"] = tk.Frame(self.contentsettings, padx=0, pady=0, bd=0)
			self.contentdata[id]["Settings"].grid(column=0, row=0, sticky="nsew")

		self.contentdata[id]["lblRS"] = ttk.Label(self.contentdata[id]["Settings"], text="Report Settings:")
		self.contentdata[id]["lblRS"].grid(column=0, row=rownum, sticky="nsew")

		# Report Title
		rownum += 1
		self.contentdata[id]["lblTitle"] = ttk.Label(self.contentdata[id]["Settings"], text="Title:")
		self.contentdata[id]["lblTitle"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strTitle"] = tk.StringVar()
		self.contentdata[id]["strTitle"].set(self.base.rs_setting_get_title())
		self.contentdata[id]["eTitle"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strTitle"])
		self.contentdata[id]["eTitle"].grid(column=1, columnspan=9, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eTitle"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["eTitle"].bind('<FocusOut>', self.cs_report_settings_update)

		# chkbox display start and end time of test
		rownum += 1
		self.contentdata[id]["lblDF"] = ttk.Label(self.contentdata[id]["Settings"], text="Date Format")
		self.contentdata[id]["lblDF"].grid(column=0, row=rownum, sticky="nsew")

		DFormats = [None, "yyyy-mm-dd", "dd/mm/yyyy", "dd-mm-yyyy", "dd.mm.yyyy", "mm/dd/yyyy"]
		self.contentdata[id]["strDF"] = tk.StringVar()
		self.contentdata[id]["strDF"].set(self.base.rs_setting_get_dateformat())
		self.contentdata[id]["omDF"] = ttk.OptionMenu(self.contentdata[id]["Settings"], self.contentdata[id]["strDF"], command=self.cs_report_settings_update, *DFormats)
		self.contentdata[id]["omDF"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblTF"] = ttk.Label(self.contentdata[id]["Settings"], text="Time Format")
		self.contentdata[id]["lblTF"].grid(column=0, row=rownum, sticky="nsew")

		TFormats = [None, "HH:MM", "HH:MM:SS", "HH.MM", "HH.MM.SS", "h:MM AMPM", "h:MM:SS AMPM", "h.MM AMPM", "h.MM.SS AMPM"]
		self.contentdata[id]["strTF"] = tk.StringVar()
		self.contentdata[id]["strTF"].set(self.base.rs_setting_get_timeformat())
		self.contentdata[id]["omTF"] = ttk.OptionMenu(self.contentdata[id]["Settings"], self.contentdata[id]["strTF"], command=self.cs_report_settings_update, *TFormats)
		self.contentdata[id]["omTF"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblTZ"] = ttk.Label(self.contentdata[id]["Settings"], text="Time Zone")
		self.contentdata[id]["lblTZ"].grid(column=0, row=rownum, sticky="nsew")

		TZones = [""]
		ZL = list(self.base.rs_setting_get_timezone_list())
		LTZ = self.base.rs_setting_get_timezone()
		if LTZ not in ZL:
			TZones.append(LTZ)
		TZones = TZones + ZL
		TZones.sort()
		self.contentdata[id]["strTZ"] = tk.StringVar()
		self.contentdata[id]["strTZ"].set(LTZ)
		self.contentdata[id]["omTZ"] = ttk.Combobox(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strTZ"])
		self.contentdata[id]["omTZ"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["omTZ"]['values'] = TZones
		self.contentdata[id]["omTZ"].bind('<<ComboboxSelected>>', self.cs_report_settings_update)

		rownum += 1
		col_disp = 3
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["Settings"], text="Display")
		self.contentdata[id]["lblST"].grid(column=col_disp, row=rownum, sticky="nsew")

		# 		start time
		rownum += 1
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["Settings"], text="Start Time:")
		self.contentdata[id]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strST"] = tk.StringVar()
		iST = self.base.rs_setting_get_starttime()
		fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
		self.contentdata[id]["strST"].set(fST)

		self.contentdata[id]["eST"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strST"])
		self.contentdata[id]["eST"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eST"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["eST"].bind('<FocusOut>', self.cs_report_settings_update)

		self.contentdata[id]["intST"] = tk.IntVar()
		self.contentdata[id]["intST"].set(self.base.rs_setting_get_int("showstarttime"))
		self.contentdata[id]["chkST"] = ttk.Checkbutton(self.contentdata[id]["Settings"], variable=self.contentdata[id]["intST"], command=self.cs_report_settings_update)
		self.contentdata[id]["chkST"].grid(column=col_disp, row=rownum, sticky="nsew")

		# 		end time
		rownum += 1
		self.contentdata[id]["lblET"] = ttk.Label(self.contentdata[id]["Settings"], text="End Time:")
		self.contentdata[id]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strET"] = tk.StringVar()
		iET = self.base.rs_setting_get_endtime()
		fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
		self.contentdata[id]["strET"].set(fET)

		self.contentdata[id]["eET"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strET"])
		self.contentdata[id]["eET"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eET"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["eET"].bind('<FocusOut>', self.cs_report_settings_update)

		self.contentdata[id]["intET"] = tk.IntVar()
		self.contentdata[id]["intET"].set(self.base.rs_setting_get_int("showendtime"))
		self.contentdata[id]["chkET"] = ttk.Checkbutton(self.contentdata[id]["Settings"], variable=self.contentdata[id]["intET"], command=self.cs_report_settings_update)
		self.contentdata[id]["chkET"].grid(column=col_disp, row=rownum, sticky="nsew")

		# Logo image
		# picture.gif
		rownum += 1
		self.contentdata[id]["lblLI"] = ttk.Label(self.contentdata[id]["Settings"], text="Logo Image:")
		self.contentdata[id]["lblLI"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strLIPath"] = self.base.rs_setting_get_file("tlogo")
		self.base.debugmsg(5, "tlogo:", self.contentdata[id]["strLIPath"])

		self.contentdata[id]["strLIName"] = tk.StringVar()
		self.contentdata[id]["eLIName"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strLIName"], state="readonly", justify="right", style='TEntry')
		self.contentdata[id]["eLIName"].grid(column=1, row=rownum, sticky="nsew")

		icontext = "Select Image"
		# "Select Image"	picture.gif
		self.contentdata[id]["btnLIName"] = ttk.Button(self.contentdata[id]["Settings"], image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, width=1)
		self.contentdata[id]["btnLIName"].config(command=self.cs_select_logoimage)
		self.contentdata[id]["btnLIName"].grid(column=2, row=rownum, sticky="nsew")

		# flogo = self.base.rs_setting_get_file("tlogo")
		# if flogo is not None:
		if len(self.contentdata[id]["strLIPath"]) > 0:
			self.base.debugmsg(5, "strLIPath:", self.contentdata[id]["strLIPath"])
			path, filename = os.path.split(self.contentdata[id]["strLIPath"])
			self.base.debugmsg(5, "filename:", filename, type(filename))
			self.contentdata[id]["strLIName"].set(filename)

		self.contentdata[id]["intLI"] = tk.IntVar()
		self.contentdata[id]["intLI"].set(self.base.rs_setting_get_int("showtlogo"))
		self.contentdata[id]["chkLI"] = ttk.Checkbutton(self.contentdata[id]["Settings"], variable=self.contentdata[id]["intLI"], command=self.cs_report_settings_update)
		self.contentdata[id]["chkLI"].grid(column=col_disp, row=rownum, sticky="nsew")

		# wattermark image
		# rownum += 1
		# self.contentdata[id]["lblWM"] = ttk.Label(self.contentdata[id]["Settings"], text="Watermark Image:")
		# self.contentdata[id]["lblWM"].grid(column=0, row=rownum, sticky="nsew")

		# report font
		rownum += 1
		self.contentdata[id]["lblFont"] = ttk.Label(self.contentdata[id]["Settings"], text="Font:")
		self.contentdata[id]["lblFont"].grid(column=0, row=rownum, sticky="nsew")

		self.base.debugmsg(9, "tkFont.families()", tkFont.families())
		fontlst = list(tkFont.families())

		Fonts = [""] + fontlst
		Fonts.sort()
		self.contentdata[id]["strFont"] = tk.StringVar()
		self.contentdata[id]["omFont"] = ttk.Combobox(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["strFont"])
		self.contentdata[id]["strFont"].set(self.base.rs_setting_get_font())
		self.contentdata[id]["omFont"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["omFont"]['values'] = Fonts
		self.contentdata[id]["omFont"].bind('<<ComboboxSelected>>', self.cs_report_settings_update)

		Fontsize = [None]
		fs = 6
		while fs < 70:
			Fontsize.append(fs)
			if fs > 1:
				fs += 1
			if fs > 10:
				fs += 1
			if fs > 50:
				fs += 2
		self.contentdata[id]["intFontSz"] = tk.IntVar()
		self.contentdata[id]["omFontSz"] = ttk.OptionMenu(self.contentdata[id]["Settings"], self.contentdata[id]["intFontSz"], command=self.cs_report_settings_update, *Fontsize)
		self.contentdata[id]["intFontSz"].set(self.base.rs_setting_get_fontsize())
		self.contentdata[id]["omFontSz"].grid(column=2, row=rownum, sticky="nsew")

		# highlight colour
		# color_swatch.gif
		# https://www.pythontutorial.net/tkinter/tkinter-color-chooser/
		rownum += 1
		self.contentdata[id]["lblHColour"] = ttk.Label(self.contentdata[id]["Settings"], text="Highlight Colour:")
		self.contentdata[id]["lblHColour"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblHColourPrev"] = tk.Label(self.contentdata[id]["Settings"], text=" ", bg=self.style_head_colour)
		self.contentdata[id]["lblHColourPrev"].grid(column=1, row=rownum, sticky="nsew")

		icontext = "Select Colour"
		# "Select Colour"	color_swatch.gif
		self.contentdata[id]["btnHColour"] = ttk.Button(self.contentdata[id]["Settings"], image=self.imgdata[icontext], padding='3 3 3 3', text=icontext, width=1)
		self.contentdata[id]["btnHColour"].config(command=self.cs_select_hcolour)
		self.contentdata[id]["btnHColour"].grid(column=2, row=rownum, sticky="nsew")

		# report %ile

		rownum += 1
		self.contentdata[id]["lblPctile"] = ttk.Label(self.contentdata[id]["Settings"], text="Percentile:")
		self.contentdata[id]["lblPctile"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intPctile"] = tk.IntVar()
		self.contentdata[id]["intPctile"].set(self.base.rs_setting_get_pctile())
		self.contentdata[id]["ePctile"] = ttk.Entry(self.contentdata[id]["Settings"], textvariable=self.contentdata[id]["intPctile"])
		self.contentdata[id]["ePctile"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["ePctile"].bind('<Leave>', self.cs_report_settings_update)
		self.contentdata[id]["ePctile"].bind('<FocusOut>', self.cs_report_settings_update)

		self.contentdata[id]["lblPctile"] = ttk.Label(self.contentdata[id]["Settings"], text="%")
		self.contentdata[id]["lblPctile"].grid(column=2, row=rownum, sticky="nsew")

	def cs_report_settings_update(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		# id = self.sectionstree.focus()
		# self.base.debugmsg(9, "id:", id)
		changes = 0
		id = "TOP"

		if "strTitle" in self.contentdata[id]:
			changes += self.base.rs_setting_set("title", self.contentdata[id]["strTitle"].get())

		# self.base.rs_setting_set_file("tlogo", fpath)
		if "strLIPath" in self.contentdata[id]:
			changes += self.base.rs_setting_set_file("tlogo", self.contentdata[id]["strLIPath"])

		# showlogo
		if "intLI" in self.contentdata[id]:
			changes += self.base.rs_setting_set_int("showtlogo", self.contentdata[id]["intLI"].get())

		if "strDF" in self.contentdata[id]:
			changes += self.base.rs_setting_set("dateformat", self.contentdata[id]["strDF"].get())

		if "strTF" in self.contentdata[id]:
			changes += self.base.rs_setting_set("timeformat", self.contentdata[id]["strTF"].get())

		if "strTZ" in self.contentdata[id]:
			changed = self.base.rs_setting_set("timezone", self.contentdata[id]["strTZ"].get())
			changes += changed
			if changed:
				# update the start and end time fields for new timezone
				iST = self.base.rs_setting_get_starttime()
				fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
				self.contentdata[id]["strST"].set(fST)
				iET = self.base.rs_setting_get_endtime()
				fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
				self.contentdata[id]["strET"].set(fET)

				update_section_times = threading.Thread(target=self.cs_update_start_and_end_times(id, fST, fET))
				update_section_times.start()

		# strST
		if "strST" in self.contentdata[id]:
			st = self.contentdata[id]["strST"].get()
			self.base.debugmsg(8, "st:", st)
			ist = self.base.report_formateddatetimetosec(st)
			self.base.debugmsg(8, "ist:", ist)
			if ist > 0:
				ios = ist - self.base.report_starttime()
				changes += self.base.rs_setting_set_int("startoffset", ios)

		if "intST" in self.contentdata[id]:
			changes += self.base.rs_setting_set_int("showstarttime", self.contentdata[id]["intST"].get())

		# strET
		if "strET" in self.contentdata[id]:
			et = self.contentdata[id]["strET"].get()
			self.base.debugmsg(8, "et:", et)
			iet = self.base.report_formateddatetimetosec(et)
			self.base.debugmsg(8, "iet:", iet)
			if iet > 0:
				ios = self.base.report_endtime() - iet
				changes += self.base.rs_setting_set_int("endoffset", ios)

		if "intET" in self.contentdata[id]:
			changes += self.base.rs_setting_set_int("showendtime", self.contentdata[id]["intET"].get())

		if "strFont" in self.contentdata[id]:
			changes += self.base.rs_setting_set("font", self.contentdata[id]["strFont"].get())

		if "intFontSz" in self.contentdata[id]:
			fsz = self.contentdata[id]["intFontSz"].get()
			self.base.debugmsg(5, "fsz:", fsz, "	", type(fsz))
			changes += self.base.rs_setting_set_int("fontsize", fsz)

		if "intPctile" in self.contentdata[id]:
			pct = int(self.contentdata[id]["intPctile"].get())
			if pct > 0:
				self.base.debugmsg(5, "pct:", pct, "	", type(pct))
				changes += self.base.rs_setting_set_int("percentile", pct)

		if changes > 0:
			self.cs_reportsettings()

			self.ConfigureStyle()
			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cs_select_logoimage(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		id = "TOP"

		opendir = self.base.config['Reporter']['ResultDir']
		if len(self.contentdata[id]["strLIPath"]) > 0:
			opendir, filename = os.path.split(self.contentdata[id]["strLIPath"])

		imagefile = str(
			tkf.askopenfilename(
				initialdir=opendir,
				title="Select Logo Image",
				filetypes=(
					("JPEG", "*.jpg"),
					("JPEG", "*.jpeg"),
					("PNG", "*.png"),
					("GIF", "*.gif"),
					("Bitmap", "*.bmp"),
					("all files", "*.*")
				)
			)
		)
		self.base.debugmsg(5, "imagefile:", imagefile)

		if imagefile is not None and len(imagefile) > 0:
			self.contentdata[id]["strLIPath"] = imagefile
			self.base.debugmsg(5, "strLIPath:", self.contentdata[id]["strLIPath"])
			self.base.rs_setting_set_file("tlogo", self.contentdata[id]["strLIPath"])
			path, filename = os.path.split(self.contentdata[id]["strLIPath"])
			self.base.debugmsg(5, "filename:", filename, type(filename))
			self.contentdata[id]["strLIName"].set(filename)

			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cs_select_watermarkimage(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)

	def cs_select_hfimage(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)

	def cs_select_hcolour(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		# https://www.pythontutorial.net/tkinter/tkinter-color-chooser/
		newcolour = tkac.askcolor(self.style_head_colour, title="Choose Heading Colour")
		self.base.debugmsg(5, "newcolour:", newcolour)
		newcolourhx = newcolour[-1]
		self.base.debugmsg(5, "newcolourhx:", newcolourhx)
		if newcolourhx is not None:
			self.style_head_colour = newcolourhx
			self.base.rs_setting_set("hcolour", newcolourhx)

			# refresh
			self.cs_reportsettings()

			self.ConfigureStyle()
			# self.cp_regenerate_preview()
			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cs_rename_heading(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		self.base.debugmsg(9, "id:", id)
		curhead = self.base.report_item_get_name(id)
		newhead = curhead
		if id in self.contentdata:
			if "Heading" in self.contentdata[id]:
				newhead = self.contentdata[id]["Heading"].get()
		self.base.debugmsg(5, "curhead:", curhead, "	newhead:", newhead)
		if newhead != curhead:
			self.base.debugmsg(5, "rename :", curhead, "	to:", newhead)
			self.base.report_item_set_name(id, newhead)
			parent = self.base.report_item_parent(id)
			self.LoadSections(parent)
			self.sectionstree.selection_set(id)
			self.sectionstree.focus(id)
			self.content_preview(id)

	def cs_change_type(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		self.base.debugmsg(9, "id:", id)

		# I might need to remove this ? self.contentdata[id]["Settings"]
		# https://www.w3schools.com/python/gloss_python_remove_dictionary_items.asp
		del self.contentdata[id]["Settings"]

		keys = list(self.base.settings["ContentTypes"].keys())
		vals = list(self.base.settings["ContentTypes"].values())
		idx = 0
		if _event in vals:
			idx = vals.index(_event)

		type = keys[idx]
		self.base.report_item_set_type(id, type)
		self.content_load(id)

	#
	# Settings	-	Contents
	#

	def cs_contents(self, id):
		self.base.debugmsg(5, "id:", id)
		rownum = 0

		rownum += 1
		self.contentdata[id]["lblCM"] = ttk.Label(self.contentdata[id]["LFrame"], text="Mode:")
		self.contentdata[id]["lblCM"].grid(column=0, row=rownum, sticky="nsew")

		ContentsModes = [None, "Table Of Contents", "Table of Graphs", "Table Of Tables"]
		self.contentdata[id]["strCM"] = tk.StringVar()
		self.contentdata[id]["omCM"] = ttk.OptionMenu(self.contentdata[id]["LFrame"], self.contentdata[id]["strCM"], command=self.cs_contents_update, *ContentsModes)

		self.contentdata[id]["strCM"].set(self.base.rt_contents_get_mode(id))
		self.contentdata[id]["omCM"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblCL"] = ttk.Label(self.contentdata[id]["LFrame"], text="Level:")
		self.contentdata[id]["lblCL"].grid(column=0, row=rownum, sticky="nsew")

		Levels = [None]
		for i in range(6):
			Levels.append(i + 1)
		self.contentdata[id]["intCL"] = tk.IntVar()
		self.contentdata[id]["omCL"] = ttk.OptionMenu(self.contentdata[id]["LFrame"], self.contentdata[id]["intCL"], command=self.cs_contents_update, *Levels)
		self.contentdata[id]["intCL"].set(self.base.rt_contents_get_level(id))
		self.contentdata[id]["omCL"].grid(column=1, row=rownum, sticky="nsew")

	def cs_contents_update(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		self.base.debugmsg(9, "id:", id)
		changes = 0

		if "strCM" in self.contentdata[id]:
			value = self.contentdata[id]["strCM"].get()
			changes += self.base.rt_contents_set_mode(id, value)

		if "intCL" in self.contentdata[id]:
			value = self.contentdata[id]["intCL"].get()
			changes += self.base.rt_contents_set_level(id, value)

		if changes > 0:
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	#
	# Settings	-	Note
	#

	def cs_note(self, id):
		self.base.debugmsg(9, "id:", id)
		# self.base.rt_note_get(id)
		self.contentdata[id]["tNote"] = tk.Text(self.contentdata[id]["LFrame"])
		# background="yellow", foreground="blue"
		# self.contentdata[id]["tNote"].config(bg="SlateBlue2")
		self.contentdata[id]["tNote"].config(background=self.style_feild_colour, foreground=self.style_text_colour, insertbackground=self.style_text_colour)

		self.contentdata[id]["tNote"].insert('0.0', self.base.rt_note_get(id))
		self.contentdata[id]["tNote"].grid(column=0, row=0, sticky="nsew")
		self.contentdata[id]["LFrame"].rowconfigure(0, weight=1)
		self.contentdata[id]["LFrame"].columnconfigure(0, weight=1)
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["tNote"].bind('<Leave>', self.cs_note_update)
		self.contentdata[id]["tNote"].bind('<FocusOut>', self.cs_note_update)

	def cs_note_update(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		self.base.debugmsg(9, "id:", id)
		if "tNote" in self.contentdata[id]:
			data = self.contentdata[id]["tNote"].get('0.0', tk.END)
			self.base.debugmsg(5, "data:", data)
			self.base.rt_note_set(id, data)
			# self.content_preview(id)
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	#
	# Settings	-	DataTable
	#

	def cs_datatable(self, id):
		self.base.debugmsg(8, "id:", id)
		colours = self.base.rt_table_get_colours(id)
		datatype = self.base.rt_table_get_dt(id)
		self.contentdata[id]["LFrame"].columnconfigure(99, weight=1)
		rownum = 0

		rownum += 1
		self.contentdata[id]["lblColours"] = ttk.Label(self.contentdata[id]["LFrame"], text="Show graph colours:")
		self.contentdata[id]["lblColours"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intColours"] = tk.IntVar()
		self.contentdata[id]["chkColours"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intColours"], command=self.cs_datatable_update)
		self.contentdata[id]["intColours"].set(colours)
		self.contentdata[id]["chkColours"].grid(column=1, row=rownum, sticky="nsew")

		# 		start time
		rownum += 1
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["LFrame"], text="Start Time:")
		self.contentdata[id]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strST"] = tk.StringVar()
		iST = self.base.rt_setting_get_starttime(id)
		fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
		self.contentdata[id]["strST"].set(fST)
		self.contentdata[id]["fST"] = fST

		self.contentdata[id]["eST"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strST"])
		self.contentdata[id]["eST"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eST"].bind('<Leave>', self.cs_datatable_update)
		self.contentdata[id]["eST"].bind('<FocusOut>', self.cs_datatable_update)

		# 		end time
		rownum += 1
		self.contentdata[id]["lblET"] = ttk.Label(self.contentdata[id]["LFrame"], text="End Time:")
		self.contentdata[id]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strET"] = tk.StringVar()
		iET = self.base.rt_setting_get_endtime(id)
		fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
		self.contentdata[id]["strET"].set(fET)
		self.contentdata[id]["fET"] = fET

		self.contentdata[id]["eET"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strET"])
		self.contentdata[id]["eET"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["eET"].bind('<Leave>', self.cs_datatable_update)
		self.contentdata[id]["eET"].bind('<FocusOut>', self.cs_datatable_update)

		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[id]["LFrame"], text="Data Type:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strDT"] = tk.StringVar()
		self.contentdata[id]["omDT"] = ttk.OptionMenu(self.contentdata[id]["LFrame"], self.contentdata[id]["strDT"], command=self.cs_datatable_switchdt, *self.DataTypes)
		self.contentdata[id]["strDT"].set(datatype)
		self.contentdata[id]["omDT"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["DTFrame"] = rownum
		self.cs_datatable_switchdt(id)

	def cs_datatable_update(self, _event=None, *args):
		self.base.debugmsg(5, "_event:", _event, "	args:", args)
		changes = 0
		# if len(args) > 0:
		# 	self.base.debugmsg(8, "args[0]:", args[0])
		# 	changes += args[0]
		id = self.sectionstree.focus()
		if _event is not None:
			name = self.base.report_item_get_name(_event)
			if name is not None:
				id = _event
		self.base.debugmsg(9, "id:", id)
		if "intColours" in self.contentdata[id]:
			colours = self.contentdata[id]["intColours"].get()
			changes += self.base.rt_table_set_colours(id, colours)

		# 		start time
		if "strST" in self.contentdata[id]:
			pass
			st = self.contentdata[id]["strST"].get()
			self.base.debugmsg(5, "st:", st)
			if st != self.contentdata[id]["fST"]:
				ist = self.base.report_formateddatetimetosec(st)
				self.base.debugmsg(5, "ist:", ist)
				if ist > 0:
					ios = ist - self.base.rs_setting_get_starttime()
					self.base.debugmsg(5, "ios:", ios)
					changes += self.base.report_item_set_int(id, "startoffset", ios)

			iST = self.base.rt_setting_get_starttime(id)
			fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
			self.contentdata[id]["strST"].set(fST)
			self.contentdata[id]["fST"] = fST

		# 		end time
		if "strET" in self.contentdata[id]:
			pass
			et = self.contentdata[id]["strET"].get()
			self.base.debugmsg(5, "et:", et)
			if et != self.contentdata[id]["fET"]:
				iet = self.base.report_formateddatetimetosec(et)
				self.base.debugmsg(5, "iet:", iet)
				if iet > 0:
					ios = self.base.rs_setting_get_endtime() - iet
					self.base.debugmsg(5, "ios:", ios)
					changes += self.base.report_item_set_int(id, "endoffset", ios)

			iET = self.base.rt_setting_get_endtime(id)
			fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
			self.contentdata[id]["strET"].set(fET)
			self.contentdata[id]["fET"] = fET

		self.base.debugmsg(5, "changes:", changes)
		if "intIsNum" in self.contentdata[id]:
			value = self.contentdata[id]["intIsNum"].get()
			changes += self.base.rt_table_set_isnumeric(id, value)
		if "intShCnt" in self.contentdata[id]:
			value = self.contentdata[id]["intShCnt"].get()
			changes += self.base.rt_table_set_showcount(id, value)
		# self.contentdata[id]["MType"].set(self.base.rt_table_get_mt(id))
		if "MType" in self.contentdata[id]:
			value = self.contentdata[id]["MType"].get()
			changes += self.base.rt_table_set_mt(id, value)
		# self.contentdata[id]["PMetric"].set(self.base.rt_table_get_pm(id))
		if "PMetric" in self.contentdata[id]:
			value = self.contentdata[id]["PMetric"].get()
			changes += self.base.rt_table_set_pm(id, value)
		# self.contentdata[id]["SMetric"].set(self.base.rt_table_get_sm(id))
		if "SMetric" in self.contentdata[id]:
			value = self.contentdata[id]["SMetric"].get()
			changes += self.base.rt_table_set_sm(id, value)

		self.base.debugmsg(5, "changes:", changes)
		# self.contentdata[id]["RType"].set(self.base.rt_table_get_rt(id))
		if "RType" in self.contentdata[id]:
			value = self.contentdata[id]["RType"].get()
			changes += self.base.rt_table_set_rt(id, value)
		# self.contentdata[id]["FRType"].set(self.base.rt_table_get_fr(id))
		if "FRType" in self.contentdata[id]:
			value = self.contentdata[id]["FRType"].get()
			changes += self.base.rt_table_set_fr(id, value)
		# self.contentdata[id]["intFR"] = tk.IntVar()
		if "intFR" in self.contentdata[id]:
			value = self.contentdata[id]["intFR"].get()
			changes += self.base.rt_table_set_enfr(id, value)

		if "intFA" in self.contentdata[id]:
			value = self.contentdata[id]["intFA"].get()
			changes += self.base.rt_table_set_enfa(id, value)
		# self.contentdata[id]["FAType"] = tk.StringVar()
		if "FAType" in self.contentdata[id]:
			value = self.contentdata[id]["FAType"].get()
			changes += self.base.rt_table_set_fa(id, value)

		self.base.debugmsg(5, "changes:", changes)
		# self.contentdata[id]["FNType"].set(self.base.rt_table_get_fn(id))
		if "FNType" in self.contentdata[id]:
			value = self.contentdata[id]["FNType"].get()
			changes += self.base.rt_table_set_fn(id, value)

		self.base.debugmsg(5, "changes:", changes)
		# self.contentdata[id]["FPattern"].set(self.base.rt_table_get_fp(id))
		if "FPattern" in self.contentdata[id]:
			value = self.contentdata[id]["FPattern"].get()
			changes += self.base.rt_table_set_fp(id, value)

		self.base.debugmsg(5, "changes:", changes)
		if "strDT" in self.contentdata[id]:
			datatype = self.contentdata[id]["strDT"].get()
			changes += self.base.rt_table_set_dt(id, datatype)

			self.base.debugmsg(8, "datatype:", datatype)

			if datatype == "Plan":
				self.cs_datatable_update_plan(id)

			if datatype == "Metric":
				self.cs_datatable_update_metrics(id)

			if datatype != "SQL":
				time.sleep(0.1)
				self.base.rt_table_generate_sql(id)

			# if changes > 0:
			# 	self.cs_datatable_switchdt(id)

		self.base.debugmsg(5, "changes:", changes)
		if "tSQL" in self.contentdata[id]:
			data = self.contentdata[id]["tSQL"].get('0.0', tk.END).strip()
			self.base.debugmsg(5, "data:", data)
			changes += self.base.rt_table_set_sql(id, data)
		else:
			time.sleep(0.1)
			self.base.rt_table_generate_sql(id)

		self.base.debugmsg(5, "changes:", changes)
		if "renamecolumns" in self.contentdata[id] and "colnames" in self.contentdata[id]["renamecolumns"]:
			for colname in self.contentdata[id]["renamecolumns"]["colnames"]:
				value = self.contentdata[id]["renamecolumns"][colname].get()
				changes += self.base.rt_table_set_colname(id, colname, value)

				value = self.contentdata[id]["renamecolumns"][f"{colname} Show"].get()
				changes += self.base.report_item_set_bool(id, self.base.rt_table_ini_colname(f"{colname} Show"), value)

				if f"{colname} Opt" in self.contentdata[id]["renamecolumns"]:
					value = self.contentdata[id]["renamecolumns"][f"{colname} Opt"].get()
					changes += self.base.report_item_set_value(id, self.base.rt_table_ini_colname(f"{colname} Opt"), value)

		self.base.debugmsg(5, "content_preview id:", id)
		# self.content_preview(id)
		self.base.debugmsg(5, "changes:", changes)
		if changes > 0:
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()
			self.cs_datatable_add_renamecols(id)

		# rt_table_get_alst

	def cs_datatable_update_result(self, id):
		self.base.debugmsg(5, "id:", id)
		tag = threading.Thread(target=lambda: self.cs_datatable_update_resultagents(id))
		tag.start()

	def cs_datatable_update_resultagents(self, id):
		self.base.debugmsg(5, "id:", id)
		self.contentdata[id]["FATypes"] = self.base.rt_table_get_alst(id)
		if "omFA" in self.contentdata[id]:
			try:
				self.contentdata[id]["omFA"].set_menu(*self.contentdata[id]["FATypes"])
			except Exception as e:
				self.base.debugmsg(5, "e:", e)

	def cs_datatable_update_metricagents(self, id):
		self.base.debugmsg(5, "id:", id)
		self.contentdata[id]["FATypes"] = self.base.rt_table_get_malst(id)
		if "omFA" in self.contentdata[id]:
			try:
				self.contentdata[id]["omFA"].set_menu(*self.contentdata[id]["FATypes"])
			except Exception as e:
				self.base.debugmsg(5, "e:", e)

	def cs_datatable_update_plan(self, id):
		pass

	def cs_datatable_update_metrics(self, id):
		self.base.debugmsg(5, "id:", id)
		tmt = threading.Thread(target=lambda: self.cs_datatable_update_metricstype(id))
		tmt.start()
		self.base.debugmsg(6, "tmt")
		tpm = threading.Thread(target=lambda: self.cs_datatable_update_pmetrics(id))
		tpm.start()
		self.base.debugmsg(6, "tpm")
		tsm = threading.Thread(target=lambda: self.cs_datatable_update_smetrics(id))
		tsm.start()
		self.base.debugmsg(6, "tsm")

		showmetricagents = 0
		if "DBTable" in self.base.settings and "Metrics" in self.base.settings["DBTable"] and "DataSource" in self.base.settings["DBTable"]["Metrics"]:
			showmetricagents = self.base.settings["DBTable"]["Metrics"]["DataSource"]
		if showmetricagents:
			tag = threading.Thread(target=lambda: self.cs_datatable_update_metricagents(id))
			tag.start()
			self.base.debugmsg(6, "tag")

	def cs_datatable_update_metricstype(self, id):
		self.base.debugmsg(5, "id:", id)
		self.contentdata[id]["Metrics"] = self.base.rt_table_get_mlst(id)
		if "omMT" in self.contentdata[id]:
			try:
				self.contentdata[id]["omMT"].set_menu(*self.contentdata[id]["Metrics"])
			except Exception as e:
				self.base.debugmsg(5, "e:", e)

	def cs_datatable_update_pmetrics(self, id):
		self.base.debugmsg(5, "id:", id)
		self.contentdata[id]["PMetrics"] = self.base.rt_table_get_pmlst(id)
		if "omPM" in self.contentdata[id]:
			try:
				self.contentdata[id]["omPM"].set_menu(*self.contentdata[id]["PMetrics"])
			except Exception as e:
				self.base.debugmsg(5, "e:", e)

	def cs_datatable_update_smetrics(self, id):
		self.base.debugmsg(5, "id:", id)
		self.contentdata[id]["SMetrics"] = self.base.rt_table_get_smlst(id)
		if "omSM" in self.contentdata[id]:
			try:
				self.contentdata[id]["omSM"].set_menu(*self.contentdata[id]["SMetrics"])
			except Exception as e:
				self.base.debugmsg(5, "e:", e)

	def cs_datatable_switchdt(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		rownum = 0
		id = self.sectionstree.focus()
		if _event is not None:
			name = self.base.report_item_get_name(_event)
			if name is not None:
				id = _event
		self.base.debugmsg(8, "id:", id)
		# self.cs_datatable_update(id, 1)
		self.cs_datatable_update(id)
		datatype = self.contentdata[id]["strDT"].get()
		self.base.debugmsg(5, "datatype:", datatype)
		if "Frames" not in self.contentdata[id]:
			self.contentdata[id]["Frames"] = {}

		# Forget
		for frame in self.contentdata[id]["Frames"].keys():
			self.contentdata[id]["Frames"][frame].grid_forget()
			# self.contentdata[id]["Frames"] = {}
			# del self.contentdata[id]["Frames"][frame]
		self.contentdata[id]["Frames"] = {}

		self.base.debugmsg(8, "id:", id, "Frames:", self.contentdata[id]["Frames"])

		self.base.debugmsg(8, "id:", id, "Construct")
		# Construct
		if datatype not in self.contentdata[id]["Frames"]:
			rownum = 0
			self.contentdata[id]["Frames"][datatype] = tk.Frame(self.contentdata[id]["LFrame"])
			# self.contentdata[id]["Frames"][datatype].config(bg="SlateBlue3")
			# self.contentdata[id]["Frames"][datatype].columnconfigure(0, weight=1)
			self.contentdata[id]["Frames"][datatype].columnconfigure(99, weight=1)

			self.base.debugmsg(8, "datatype:", datatype)

			if datatype == "Metric":

				showmetricagents = 0
				if "DBTable" in self.base.settings and "Metrics" in self.base.settings["DBTable"] and "DataSource" in self.base.settings["DBTable"]["Metrics"]:
					showmetricagents = self.base.settings["DBTable"]["Metrics"]["DataSource"]

				rownum += 1
				self.contentdata[id]["lblIsNum"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Number Value:")
				self.contentdata[id]["lblIsNum"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["intIsNum"] = tk.IntVar()
				self.contentdata[id]["chkIsNum"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intIsNum"], command=self.cs_datatable_update)
				self.contentdata[id]["chkIsNum"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["lblShCnt"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Show Counts:")
				self.contentdata[id]["lblShCnt"].grid(column=2, row=rownum, sticky="nsew")

				self.contentdata[id]["intShCnt"] = tk.IntVar()
				self.contentdata[id]["chkShCnt"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intShCnt"], command=self.cs_datatable_update)
				self.contentdata[id]["chkShCnt"].grid(column=3, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[id]["lblEnabled"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Enabled")
					self.contentdata[id]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblMT"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Metric Type:")
				self.contentdata[id]["lblMT"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["MTypes"] = [None, "", "Loading..."]
				self.contentdata[id]["MType"] = tk.StringVar()
				self.contentdata[id]["omMT"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["MType"], command=self.cs_datatable_update, *self.contentdata[id]["MTypes"])
				self.contentdata[id]["omMT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblPM"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Primrary Metric:")
				self.contentdata[id]["lblPM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["PMetrics"] = [None, "", "Loading..."]
				self.contentdata[id]["PMetric"] = tk.StringVar()
				self.contentdata[id]["omPM"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["PMetric"], command=self.cs_datatable_update, *self.contentdata[id]["PMetrics"])
				self.contentdata[id]["omPM"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblSM"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Secondary Metric:")
				self.contentdata[id]["lblSM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["SMetrics"] = [None, "", "Loading..."]
				self.contentdata[id]["SMetric"] = tk.StringVar()
				self.contentdata[id]["omSM"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["SMetric"], command=self.cs_datatable_update, *self.contentdata[id]["SMetrics"])
				self.contentdata[id]["omSM"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[id]["lblFA"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Agent:")
					self.contentdata[id]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

					self.contentdata[id]["FATypes"] = [None, "", "Loading..."]
					self.contentdata[id]["FAType"] = tk.StringVar()
					self.contentdata[id]["omFA"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FAType"], command=self.cs_datatable_update, *self.contentdata[id]["FATypes"])
					self.contentdata[id]["omFA"].grid(column=1, row=rownum, sticky="nsew")

					self.contentdata[id]["intFA"] = tk.IntVar()
					self.contentdata[id]["chkFA"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFA"], command=self.cs_datatable_update)
					self.contentdata[id]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFN"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Type:")
				self.contentdata[id]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[id]["FNType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FNType"], command=self.cs_datatable_update, *FNTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFP"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Pattern:")
				self.contentdata[id]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FPattern"] = tk.StringVar()
				self.contentdata[id]["inpFP"] = ttk.Entry(self.contentdata[id]["Frames"][datatype], textvariable=self.contentdata[id]["FPattern"])
				self.contentdata[id]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["inpFP"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["inpFP"].bind('<FocusOut>', self.cs_datatable_update)

			if datatype == "Result":
				rownum += 1
				self.contentdata[id]["lblEnabled"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Enabled")
				self.contentdata[id]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblRT"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Result Type:")
				self.contentdata[id]["lblRT"].grid(column=0, row=rownum, sticky="nsew")

				RTypes = [None, "Response Time", "TPS", "Total TPS"]
				self.contentdata[id]["RType"] = tk.StringVar()
				self.contentdata[id]["omRT"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["RType"], command=self.cs_datatable_update, *RTypes)
				self.contentdata[id]["omRT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# result filtered by PASS, FAIL, None
				self.contentdata[id]["lblFR"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Result:")
				self.contentdata[id]["lblFR"].grid(column=0, row=rownum, sticky="nsew")

				FRTypes = [None, "None", "Pass", "Fail"]
				self.contentdata[id]["FRType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FRType"], command=self.cs_datatable_update, *FRTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["intFR"] = tk.IntVar()
				self.contentdata[id]["chkFR"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFR"], command=self.cs_datatable_update)
				self.contentdata[id]["chkFR"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFA"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Agent:")
				self.contentdata[id]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[id]["FAType"] = tk.StringVar()
				self.contentdata[id]["omFA"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FAType"], command=self.cs_datatable_update, *self.contentdata[id]["FATypes"])
				self.contentdata[id]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["intFA"] = tk.IntVar()
				self.contentdata[id]["chkFA"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFA"], command=self.cs_datatable_update)
				self.contentdata[id]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFN"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Type:")
				self.contentdata[id]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[id]["FNType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FNType"], command=self.cs_datatable_update, *FNTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFP"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Pattern:")
				self.contentdata[id]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FPattern"] = tk.StringVar()
				self.contentdata[id]["inpFP"] = ttk.Entry(self.contentdata[id]["Frames"][datatype], textvariable=self.contentdata[id]["FPattern"])
				self.contentdata[id]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["inpFP"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["inpFP"].bind('<FocusOut>', self.cs_datatable_update)

			if datatype == "ResultSummary":
				rownum += 1
				self.contentdata[id]["lblEnabled"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Enabled")
				self.contentdata[id]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFA"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Agent:")
				self.contentdata[id]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[id]["FAType"] = tk.StringVar()
				self.contentdata[id]["omFA"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FAType"], command=self.cs_datatable_update, *self.contentdata[id]["FATypes"])
				self.contentdata[id]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[id]["intFA"] = tk.IntVar()
				self.contentdata[id]["chkFA"] = ttk.Checkbutton(self.contentdata[id]["Frames"][datatype], variable=self.contentdata[id]["intFA"], command=self.cs_datatable_update)
				self.contentdata[id]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFN"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Type:")
				self.contentdata[id]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[id]["FNType"] = tk.StringVar()
				self.contentdata[id]["omFR"] = ttk.OptionMenu(self.contentdata[id]["Frames"][datatype], self.contentdata[id]["FNType"], command=self.cs_datatable_update, *FNTypes)
				self.contentdata[id]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["lblFP"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="Filter Pattern:")
				self.contentdata[id]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[id]["FPattern"] = tk.StringVar()
				self.contentdata[id]["inpFP"] = ttk.Entry(self.contentdata[id]["Frames"][datatype], textvariable=self.contentdata[id]["FPattern"])
				self.contentdata[id]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["inpFP"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["inpFP"].bind('<FocusOut>', self.cs_datatable_update)

			if datatype == "SQL":
				rownum += 1
				self.contentdata[id]["lblSQL"] = ttk.Label(self.contentdata[id]["Frames"][datatype], text="SQL:")
				self.contentdata[id]["lblSQL"].grid(column=0, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[id]["tSQL"] = tk.Text(self.contentdata[id]["Frames"][datatype])
				self.contentdata[id]["tSQL"].grid(column=0, row=rownum, columnspan=100, sticky="nsew")
				# data = self.contentdata[id]["tSQL"].insert('0.0', sql)
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["tSQL"].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["tSQL"].bind('<FocusOut>', self.cs_datatable_update)

		self.base.debugmsg(8, "id:", id, "renamecols 1")
		if "renamecols" not in self.contentdata[id]["Frames"] and datatype not in ["SQL"]:
			self.base.debugmsg(5, "create renamecols frame")
			rownum = 0
			self.contentdata[id]["Frames"]["renamecols"] = tk.Frame(self.contentdata[id]["LFrame"])
			self.contentdata[id]["Frames"]["renamecols"].columnconfigure(99, weight=1)

			self.contentdata[id]["lblspacer"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text=" ")
			self.contentdata[id]["lblspacer"].grid(column=0, row=rownum, sticky="nsew")

			rownum += 1
			self.contentdata[id]["lblcolren"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Rename Columns")
			self.contentdata[id]["lblcolren"].grid(column=0, row=rownum, sticky="nsew")

			rownum += 1
			self.contentdata[id]["lblcolnme"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Column Name")
			self.contentdata[id]["lblcolnme"].grid(column=0, row=rownum, sticky="nsew")

			self.contentdata[id]["lbldispnme"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Display Name")
			self.contentdata[id]["lbldispnme"].grid(column=1, row=rownum, sticky="nsew")

			self.contentdata[id]["lblshowcol"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Show Column")
			self.contentdata[id]["lblshowcol"].grid(column=2, row=rownum, sticky="nsew")

			if datatype in ["Plan", "Monitoring"]:
				self.contentdata[id]["lblcolopt"] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text="Options")
				self.contentdata[id]["lblcolopt"].grid(column=3, row=rownum, sticky="nsew")

			self.contentdata[id]["renamecolumns"] = {}
			self.contentdata[id]["renamecolumns"]["startrow"] = rownum + 1
			self.contentdata[id]["renamecolumns"]["rownum"] = rownum + 1

		self.base.debugmsg(8, "id:", id, "renamecols 2")
		if datatype not in ["SQL"]:
			self.cs_datatable_add_renamecols(id)
			self.base.debugmsg(8, "id:", id, "renamecols 2 debug 1")
			# cp = threading.Thread(target=lambda: self.cs_datatable_add_renamecols(id))
			# cp.start()
			self.contentdata[id]["Frames"]["renamecols"].grid(column=0, row=self.contentdata[id]["DTFrame"] + 1, columnspan=100, sticky="nsew")
			self.base.debugmsg(8, "id:", id, "renamecols 2 debug 2")

		self.base.debugmsg(8, "id:", id, "Update")
		# Update
		if datatype == "SQL":
			sql = self.base.rt_table_get_sql(id)
			self.contentdata[id]["tSQL"].delete('0.0', tk.END)
			self.contentdata[id]["tSQL"].insert('0.0', sql)

		if datatype == "Result":
			self.cs_datatable_update_result(id)
			self.contentdata[id]["RType"].set(self.base.rt_table_get_rt(id))
			self.contentdata[id]["intFR"].set(self.base.rt_table_get_enfr(id))
			self.contentdata[id]["FRType"].set(self.base.rt_table_get_fr(id))
			self.contentdata[id]["intFA"].set(self.base.rt_table_get_enfa(id))
			self.contentdata[id]["FAType"].set(self.base.rt_table_get_fa(id))
			self.contentdata[id]["FNType"].set(self.base.rt_table_get_fn(id))
			self.contentdata[id]["FPattern"].set(self.base.rt_table_get_fp(id))

		if datatype == "ResultSummary":
			self.cs_datatable_update_result(id)
			self.contentdata[id]["FNType"].set(self.base.rt_table_get_fn(id))
			self.contentdata[id]["FPattern"].set(self.base.rt_table_get_fp(id))

		if datatype == "Metric":
			self.base.debugmsg(5, "Update Options")
			self.cs_datatable_update_metrics(id)
			self.base.debugmsg(5, "Set Options")
			while "SMetric" not in self.contentdata[id]:
				time.sleep(0.1)
			self.contentdata[id]["intIsNum"].set(self.base.rt_table_get_isnumeric(id))
			self.contentdata[id]["intShCnt"].set(self.base.rt_table_get_showcount(id))
			self.contentdata[id]["MType"].set(self.base.rt_table_get_mt(id))
			self.contentdata[id]["PMetric"].set(self.base.rt_table_get_pm(id))
			self.contentdata[id]["SMetric"].set(self.base.rt_table_get_sm(id))
			self.contentdata[id]["intFA"].set(self.base.rt_table_get_enfa(id))
			self.contentdata[id]["FAType"].set(self.base.rt_table_get_fa(id))
			self.contentdata[id]["FNType"].set(self.base.rt_table_get_fn(id))
			self.contentdata[id]["FPattern"].set(self.base.rt_table_get_fp(id))

		self.base.debugmsg(8, "id:", id, "Show")
		# Show
		self.contentdata[id]["Frames"][datatype].grid(column=0, row=self.contentdata[id]["DTFrame"], columnspan=100, sticky="nsew")

	def cs_datatable_add_renamecols(self, id):
		self.base.debugmsg(5, "id:", id)
		if "renamecolumns" in self.contentdata[id]:
			datatype = self.base.rt_table_get_dt(id)

			if datatype == "SQL":
				sql = self.base.rt_table_get_sql(id)
				if len(sql.strip()) < 1:
					return None
			else:
				sql = self.base.rt_table_generate_sql(id)
				if len(sql.strip()) < 1:
					return None
				if datatype not in ["Plan", "Monitoring"]:
					sql += " LIMIT 1 "

			self.base.debugmsg(5, "sql:", sql)
			key = "{}_{}_{}".format(id, self.base.report_item_get_changed(id), datetime.now().timestamp())
			self.base.dbqueue["Read"].append({"SQL": sql, "KEY": key})

			if "colnames" not in self.contentdata[id]["renamecolumns"]:
				self.contentdata[id]["renamecolumns"]["colnames"] = []
			else:
				self.cs_datatable_reset_renamecols(id)
				self.contentdata[id]["renamecolumns"]["colnames"] = []
			self.contentdata[id]["renamecolumns"]["rownum"] = self.contentdata[id]["renamecolumns"]["startrow"]

			while key not in self.base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = self.base.dbqueue["ReadResult"][key]
			if datatype == "Plan":
				self.base.debugmsg(9, "tdata before:", tdata)
				tdata = self.base.table_postprocess_data_plan(id, tdata)
			if datatype == "Monitoring":
				self.base.debugmsg(9, "tdata before:", tdata)
				tdata = self.base.table_postprocess_data_monitoring(id, tdata)
			self.base.debugmsg(8, "tdata:", tdata)

			if len(tdata) > 0:
				cols = list(tdata[0].keys())
				self.base.debugmsg(7, "cols:", cols)
				for col in cols:
					if col not in ["Colour"]:
						self.cs_datatable_add_renamecol(id, col)

	def cs_datatable_reset_renamecols(self, id):
		self.base.debugmsg(5, "id:", id)
		if "colnames" in self.contentdata[id]["renamecolumns"]:
			for colname in list(self.contentdata[id]["renamecolumns"]["colnames"]):
				self.base.debugmsg(5, "id:", id, "	colname:", colname)
				collabel = "lbl_{}".format(colname)
				colinput = "inp_{}".format(colname)
				try:
					self.contentdata[id]["renamecolumns"][collabel].grid_forget()
				except Exception as e:
					self.base.debugmsg(9, "e:", e)
				try:
					self.contentdata[id]["renamecolumns"][colinput].grid_forget()
				except Exception as e:
					self.base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"][collabel]
				except Exception as e:
					self.base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"][colinput]
				except Exception as e:
					self.base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"][colname]
				except Exception as e:
					self.base.debugmsg(9, "e:", e)
				try:
					del self.contentdata[id]["renamecolumns"]["colnames"]
				except Exception as e:
					self.base.debugmsg(9, "e:", e)

	def cs_datatable_add_renamecol(self, id, colname):
		self.base.debugmsg(5, "id:", id, "	colname:", colname)
		datatype = self.base.rt_table_get_dt(id)

		if "renamecolumns" in self.contentdata[id] and "renamecols" in self.contentdata[id]["Frames"]:
			collabel = "lbl_{}".format(colname)
			colinput = "inp_{}".format(colname)
			colshow = "show_{}".format(colname)
			colopt = "opt_{}".format(colname)
			rownum = self.contentdata[id]["renamecolumns"]["rownum"]
			if colname not in self.contentdata[id]["renamecolumns"]["colnames"]:
				self.contentdata[id]["renamecolumns"]["rownum"] += 1
				colnum = 0
				self.contentdata[id]["renamecolumns"]["colnames"].append(colname)
				self.contentdata[id]["renamecolumns"][collabel] = ttk.Label(self.contentdata[id]["Frames"]["renamecols"], text=" {} ".format(colname))
				self.contentdata[id]["renamecolumns"][collabel].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				self.contentdata[id]["renamecolumns"][colname] = tk.StringVar()
				self.contentdata[id]["renamecolumns"][colinput] = ttk.Entry(self.contentdata[id]["Frames"]["renamecols"], textvariable=self.contentdata[id]["renamecolumns"][colname])
				self.contentdata[id]["renamecolumns"][colinput].grid(column=colnum, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[id]["renamecolumns"][colinput].bind('<Leave>', self.cs_datatable_update)
				self.contentdata[id]["renamecolumns"][colinput].bind('<FocusOut>', self.cs_datatable_update)
				self.contentdata[id]["renamecolumns"][colname].set(self.base.rt_table_get_colname(id, colname))

				colnum += 1
				self.contentdata[id]["renamecolumns"][f"{colname} Show"] = tk.IntVar()
				self.contentdata[id]["renamecolumns"][colshow] = ttk.Checkbutton(self.contentdata[id]["Frames"]["renamecols"], variable=self.contentdata[id]["renamecolumns"][f"{colname} Show"], command=self.cs_datatable_update)
				self.contentdata[id]["renamecolumns"][colshow].grid(column=colnum, row=rownum, sticky="nsew")
				self.contentdata[id]["renamecolumns"][f"{colname} Show"].set(self.base.report_item_get_bool_def1(id, self.base.rt_table_ini_colname(f"{colname} Show")))
				self.base.debugmsg(5, "colnum:", colnum, "	rownum:", rownum)

				if datatype in ["Plan", "Monitoring"]:
					if colname == "Script":
						colnum += 1
						optval = self.base.report_item_get_value(id, self.base.rt_table_ini_colname(f"{colname} Opt"))
						if optval is None:
							optval = "File"

						self.base.debugmsg(5, "colnum:", colnum, "	rownum:", rownum, "	optval:", optval)

						ScriptTypes = [None, "File", "Path"]
						self.contentdata[id]["renamecolumns"][f"{colname} Opt"] = tk.StringVar()
						self.contentdata[id]["renamecolumns"][colopt] = ttk.OptionMenu(self.contentdata[id]["Frames"]["renamecols"], self.contentdata[id]["renamecolumns"][f"{colname} Opt"], command=self.cs_datatable_update, *ScriptTypes)
						self.contentdata[id]["renamecolumns"][colopt].grid(column=colnum, row=rownum, sticky="nsew")
						self.contentdata[id]["renamecolumns"][f"{colname} Opt"].set(optval)

	#
	# Settings	-	Graph
	#

	def cs_graph(self, id):
		self.base.debugmsg(9, "id:", id)
		pid, idl, idr = self.base.rt_graph_LR_Ids(id)

		iST = self.base.rt_setting_get_starttime(pid)
		iET = self.base.rt_setting_get_endtime(pid)

		axisenl = self.base.rt_graph_get_axisen(idl)
		axisenr = self.base.rt_graph_get_axisen(idr)
		datatypel = self.base.rt_graph_get_dt(idl)
		datatyper = self.base.rt_graph_get_dt(idr)
		self.contentdata[pid]["LFrame"].columnconfigure(99, weight=1)
		rownum = 0

		# 		start time
		rownum += 1
		self.contentdata[pid]["lblST"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Start Time:")
		self.contentdata[pid]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[pid]["strST"] = tk.StringVar()
		fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
		self.contentdata[pid]["strST"].set(fST)
		self.contentdata[pid]["fST"] = fST

		self.contentdata[pid]["eST"] = ttk.Entry(self.contentdata[pid]["LFrame"], textvariable=self.contentdata[pid]["strST"])
		self.contentdata[pid]["eST"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[pid]["eST"].bind('<Leave>', self.cs_graph_update)
		self.contentdata[pid]["eST"].bind('<FocusOut>', self.cs_graph_update)

		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["RFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		# 		end time
		rownum += 1
		self.contentdata[pid]["lblET"] = ttk.Label(self.contentdata[pid]["LFrame"], text="End Time:")
		self.contentdata[pid]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[pid]["strET"] = tk.StringVar()
		fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
		self.contentdata[pid]["strET"].set(fET)
		self.contentdata[pid]["fET"] = fET

		self.contentdata[pid]["eET"] = ttk.Entry(self.contentdata[pid]["LFrame"], textvariable=self.contentdata[pid]["strET"])
		self.contentdata[pid]["eET"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[pid]["eET"].bind('<Leave>', self.cs_graph_update)
		self.contentdata[pid]["eET"].bind('<FocusOut>', self.cs_graph_update)

		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["RFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		# 		blank row
		rownum += 1
		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["LFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[pid]["lblBlank"] = ttk.Label(self.contentdata[pid]["RFrame"], text=" ")
		self.contentdata[pid]["lblBlank"].grid(column=0, row=rownum, sticky="nsew")

		# 		Y-Axis
		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Y-Axis:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblLeft"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Left")
		self.contentdata[id]["lblLeft"].grid(column=1, row=rownum, sticky="nsew")

		# self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[pid]["RFrame"], text="                        ", style='Report.TLabel')
		# self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblRight"] = ttk.Label(self.contentdata[pid]["RFrame"], text="Right")
		self.contentdata[id]["lblRight"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Enable:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[idl]["intAxsEn"] = tk.IntVar()
		self.contentdata[idl]["chkAxsEn"] = ttk.Checkbutton(self.contentdata[pid]["LFrame"], variable=self.contentdata[idl]["intAxsEn"], command=self.cs_graph_update)
		self.contentdata[idl]["intAxsEn"].set(axisenl)
		self.contentdata[idl]["chkAxsEn"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[idr]["intAxsEn"] = tk.IntVar()
		self.contentdata[idr]["chkAxsEn"] = ttk.Checkbutton(self.contentdata[pid]["RFrame"], variable=self.contentdata[idr]["intAxsEn"], command=self.cs_graph_update)
		self.contentdata[idr]["intAxsEn"].set(axisenr)
		self.contentdata[idr]["chkAxsEn"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblDT"] = ttk.Label(self.contentdata[pid]["LFrame"], text="Data Type:")
		self.contentdata[id]["lblDT"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[idl]["strDT"] = tk.StringVar()
		self.contentdata[idl]["omDT"] = ttk.OptionMenu(self.contentdata[pid]["LFrame"], self.contentdata[idl]["strDT"], command=self.cs_graph_switchdt, *self.DataTypes)
		self.contentdata[idl]["strDT"].set(datatypel)
		self.contentdata[idl]["omDT"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[idr]["strDT"] = tk.StringVar()
		self.contentdata[idr]["omDT"] = ttk.OptionMenu(self.contentdata[pid]["RFrame"], self.contentdata[idr]["strDT"], command=self.cs_graph_switchdt, *self.DataTypes)
		self.contentdata[idr]["strDT"].set(datatyper)
		self.contentdata[idr]["omDT"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["DTFrame"] = rownum
		self.cs_graph_switchdt(id)

	def cs_graph_update(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		id = self.sectionstree.focus()
		self.base.debugmsg(9, "id:", id)
		pid, idl, idr = self.base.rt_graph_LR_Ids(id)
		changes = 0

		# 		start time
		if "strST" in self.contentdata[pid] and "fST" in self.contentdata[pid]:
			st = self.contentdata[pid]["strST"].get()
			self.base.debugmsg(5, "st:", st)
			if st != self.contentdata[pid]["fST"]:
				ist = self.base.report_formateddatetimetosec(st)
				self.base.debugmsg(5, "ist:", ist)
				if ist > 0:
					ios = ist - self.base.rs_setting_get_starttime()
					self.base.debugmsg(5, "ios:", ios)
					changes += self.base.report_item_set_int(pid, "startoffset", ios)

			iST = self.base.rt_setting_get_starttime(pid)
			fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
			self.contentdata[id]["strST"].set(fST)
			self.contentdata[id]["fST"] = fST

		# 		end time
		if "strET" in self.contentdata[pid] and "fET" in self.contentdata[pid]:
			et = self.contentdata[pid]["strET"].get()
			self.base.debugmsg(5, "et:", et)
			if et != self.contentdata[pid]["fET"]:
				iet = self.base.report_formateddatetimetosec(et)
				self.base.debugmsg(5, "iet:", iet)
				if iet > 0:
					ios = self.base.rs_setting_get_endtime() - iet
					self.base.debugmsg(5, "ios:", ios)
					changes += self.base.report_item_set_int(pid, "endoffset", ios)

			iET = self.base.rt_setting_get_endtime(pid)
			fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
			self.contentdata[id]["strET"].set(fET)
			self.contentdata[id]["fET"] = fET

		# intIsNum
		if "intIsNum" in self.contentdata[idl]:
			value = self.contentdata[idl]["intIsNum"].get()
			changes += self.base.rt_table_set_isnumeric(idl, value)
		if "intIsNum" in self.contentdata[idr]:
			value = self.contentdata[idr]["intIsNum"].get()
			changes += self.base.rt_table_set_isnumeric(idr, value)

		# intShCnt
		if "intShCnt" in self.contentdata[idl]:
			value = self.contentdata[idl]["intShCnt"].get()
			changes += self.base.rt_table_set_showcount(idl, value)
		if "intShCnt" in self.contentdata[idr]:
			value = self.contentdata[idr]["intShCnt"].get()
			changes += self.base.rt_table_set_showcount(idr, value)

		if "MType" in self.contentdata[idl]:
			value = self.contentdata[idl]["MType"].get()
			changes += self.base.rt_table_set_mt(idl, value)
		if "MType" in self.contentdata[idr]:
			value = self.contentdata[idr]["MType"].get()
			changes += self.base.rt_table_set_mt(idr, value)

		if "PMetric" in self.contentdata[idl]:
			value = self.contentdata[idl]["PMetric"].get()
			changes += self.base.rt_table_set_pm(idl, value)
		if "PMetric" in self.contentdata[idr]:
			value = self.contentdata[idr]["PMetric"].get()
			changes += self.base.rt_table_set_pm(idr, value)

		if "SMetric" in self.contentdata[idl]:
			value = self.contentdata[idl]["SMetric"].get()
			changes += self.base.rt_table_set_sm(idl, value)
		if "SMetric" in self.contentdata[idr]:
			value = self.contentdata[idr]["SMetric"].get()
			changes += self.base.rt_table_set_sm(idr, value)

		RTypeChanges = 0
		if "RType" in self.contentdata[idl]:
			value = self.contentdata[idl]["RType"].get()
			changes += self.base.rt_table_set_rt(idl, value)
			RTypeChanges = changes
		if "RType" in self.contentdata[idr]:
			value = self.contentdata[idr]["RType"].get()
			changes += self.base.rt_table_set_rt(idr, value)
			RTypeChanges = changes

		if "FRType" in self.contentdata[idl]:
			value = self.contentdata[idl]["FRType"].get()
			changes += self.base.rt_table_set_fr(idl, value)
		if "FRType" in self.contentdata[idr]:
			value = self.contentdata[idr]["FRType"].get()
			changes += self.base.rt_table_set_fr(idr, value)

		if "intFR" in self.contentdata[idl]:
			value = self.contentdata[idl]["intFR"].get()
			changes += self.base.rt_table_set_enfr(idl, value)
		if "intFR" in self.contentdata[idr]:
			value = self.contentdata[idr]["intFR"].get()
			changes += self.base.rt_table_set_enfr(idr, value)

		if "intFA" in self.contentdata[idl]:
			value = self.contentdata[idl]["intFA"].get()
			changes += self.base.rt_table_set_enfa(idl, value)
		if "intFA" in self.contentdata[idr]:
			value = self.contentdata[idr]["intFA"].get()
			changes += self.base.rt_table_set_enfa(idr, value)

		if "FAType" in self.contentdata[idl]:
			value = self.contentdata[idl]["FAType"].get()
			changes += self.base.rt_table_set_fa(idl, value)
		if "FAType" in self.contentdata[idr]:
			value = self.contentdata[idr]["FAType"].get()
			changes += self.base.rt_table_set_fa(idr, value)

		if "FNType" in self.contentdata[idl]:
			value = self.contentdata[idl]["FNType"].get()
			changes += self.base.rt_table_set_fn(idl, value)
		if "FNType" in self.contentdata[idr]:
			value = self.contentdata[idr]["FNType"].get()
			changes += self.base.rt_table_set_fn(idr, value)

		if "FPattern" in self.contentdata[idl]:
			value = self.contentdata[idl]["FPattern"].get()
			changes += self.base.rt_table_set_fp(idl, value)
		if "FPattern" in self.contentdata[idr]:
			value = self.contentdata[idr]["FPattern"].get()
			changes += self.base.rt_table_set_fp(idr, value)

		if "GSeconds" in self.contentdata[idl]:
			value = float(self.contentdata[idl]["GSeconds"].get())
			changes += self.base.rt_graph_set_gseconds(idl, value)
		if "GSeconds" in self.contentdata[idr]:
			value = float(self.contentdata[idr]["GSeconds"].get())
			changes += self.base.rt_graph_set_gseconds(idr, value)

		if "GWType" in self.contentdata[idl]:
			value = self.contentdata[idl]["GWType"].get()
			changes += self.base.rt_graph_set_gw(idl, value)
		if "GWType" in self.contentdata[idr]:
			value = self.contentdata[idr]["GWType"].get()
			changes += self.base.rt_graph_set_gw(idr, value)

		if "strDT" in self.contentdata[idl]:
			datatype = self.contentdata[idl]["strDT"].get()
			changes += self.base.rt_table_set_dt(idl, datatype)
			if datatype == "Metric":
				self.cs_datatable_update_metrics(idl)
			if datatype != "SQL":
				time.sleep(0.1)
				self.base.rt_graph_generate_sql(idl)
		if "strDT" in self.contentdata[idr]:
			datatype = self.contentdata[idr]["strDT"].get()
			changes += self.base.rt_table_set_dt(idr, datatype)
			if datatype == "Metric":
				self.cs_datatable_update_metrics(idr)
			if datatype != "SQL":
				time.sleep(0.1)
				self.base.rt_graph_generate_sql(idr)

		# self.contentdata[idl]["intAxsEn"] = tk.IntVar()
		if "intAxsEn" in self.contentdata[idl]:
			value = self.contentdata[idl]["intAxsEn"].get()
			changes += self.base.rt_graph_set_axisen(idl, value)
		if "intAxsEn" in self.contentdata[idr]:
			value = self.contentdata[idr]["intAxsEn"].get()
			changes += self.base.rt_graph_set_axisen(idr, value)

		if "intSTot" in self.contentdata[idl]:
			value = self.contentdata[idl]["intSTot"].get()
			changes += self.base.report_item_set_int(idl, "ShowTotal", value)
		if "intSTot" in self.contentdata[idr]:
			value = self.contentdata[idr]["intSTot"].get()
			changes += self.base.report_item_set_int(idr, "ShowTotal", value)

		if "tSQL" in self.contentdata[idl]:
			data = self.contentdata[idl]["tSQL"].get('0.0', tk.END).strip()
			self.base.debugmsg(5, "data:", data)
			changes += self.base.rt_graph_set_sql(idl, data)
		else:
			time.sleep(0.1)
			self.base.rt_graph_generate_sql(idl)
			changes += 1

		if "tSQL" in self.contentdata[idr]:
			data = self.contentdata[idr]["tSQL"].get('0.0', tk.END).strip()
			self.base.debugmsg(5, "data:", data)
			changes += self.base.rt_graph_set_sql(idr, data)
		else:
			time.sleep(0.1)
			self.base.rt_graph_generate_sql(idr)
			changes += 1

		if changes > 0:
			self.base.debugmsg(5, "content_preview id:", id)
			# self.content_preview(id)
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

		if RTypeChanges > 0:
			self.cs_graph_switchdt(id)

	def cs_graph_switchdt(self, _event=None):
		self.base.debugmsg(5, "self:", self, "	_event:", _event)
		rownum = 0
		id = self.sectionstree.focus()
		self.base.debugmsg(5, "id:", id)

		changes = 0

		if _event is not None:
			name = self.base.report_item_get_name(_event)
			if name is not None:
				id = _event
				self.base.debugmsg(5, "id:", id)

		pid, idl, idr = self.base.rt_graph_LR_Ids(id)
		self.base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		# self.cs_datatable_update(id)
		datatypel = self.contentdata[idl]["strDT"].get()
		datatyper = self.contentdata[idr]["strDT"].get()
		self.base.debugmsg(5, "datatypel:", datatypel, "datatyper:", datatyper)
		if "Frames" not in self.contentdata[id]:
			self.contentdata[id]["Frames"] = {}
		if "Frames" not in self.contentdata[idl]:
			self.contentdata[idl]["Frames"] = {}
		if "Frames" not in self.contentdata[idr]:
			self.contentdata[idr]["Frames"] = {}
		# Forget
		for frame in self.contentdata[id]["Frames"].keys():
			if frame in self.contentdata[id]["Frames"]:
				self.contentdata[id]["Frames"][frame].grid_forget()
			self.contentdata[id]["Frames"] = {}
		for frame in self.contentdata[idl]["Frames"].keys():
			if frame in self.contentdata[id]["Frames"]:
				self.contentdata[idl]["Frames"][frame].grid_forget()
			self.contentdata[idl]["Frames"] = {}
		for frame in self.contentdata[idr]["Frames"].keys():
			if frame in self.contentdata[id]["Frames"]:
				self.contentdata[idr]["Frames"][frame].grid_forget()
			self.contentdata[idr]["Frames"] = {}

		# Construct
		if datatypel not in self.contentdata[id]["Frames"]:
			self.base.debugmsg(6, "datatypel:", datatypel)
			self.contentdata[idl]["Frames"][datatypel] = tk.Frame(self.contentdata[id]["LFrame"])
			# self.contentdata[id]["Frames"][datatypel].config(bg="SlateBlue3")
			# self.contentdata[id]["Frames"][datatypel].columnconfigure(0, weight=1)
			self.contentdata[idl]["Frames"][datatypel].columnconfigure(99, weight=1)

			# "Metric", "Result", "SQL"

			if datatypel == "Monitoring":
				rownum += 1
				self.contentdata[idl]["lblSTot"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Show Total:")
				self.contentdata[idl]["lblSTot"].grid(column=0, row=rownum, sticky="nsew")

				# self.contentdata[idl]["Frames"][datatypel].columnconfigure(1, weight=1)
				self.contentdata[idl]["Frames"][datatypel].columnconfigure(1, minsize=150)
				self.contentdata[idl]["intSTot"] = tk.IntVar()
				self.contentdata[idl]["chkSTot"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intSTot"], command=self.cs_graph_update)
				self.contentdata[idl]["chkSTot"].grid(column=1, row=rownum, sticky="nsew")

			if datatypel == "Plan":
				rownum += 1
				self.contentdata[idl]["lblSTot"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Show Total:")
				self.contentdata[idl]["lblSTot"].grid(column=0, row=rownum, sticky="nsew")

				# self.contentdata[idl]["Frames"][datatypel].columnconfigure(1, weight=1)
				self.contentdata[idl]["Frames"][datatypel].columnconfigure(1, minsize=150)
				self.contentdata[idl]["intSTot"] = tk.IntVar()
				self.contentdata[idl]["chkSTot"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intSTot"], command=self.cs_graph_update)
				self.contentdata[idl]["chkSTot"].grid(column=1, row=rownum, sticky="nsew")

			if datatypel == "Metric":
				showmetricagents = 0
				if "DBTable" in self.base.settings and "Metrics" in self.base.settings["DBTable"] and "DataSource" in self.base.settings["DBTable"]["Metrics"]:
					showmetricagents = self.base.settings["DBTable"]["Metrics"]["DataSource"]

				self.base.debugmsg(6, "datatypel:", datatypel)
				rownum += 1
				self.contentdata[idl]["lblIsNum"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Number Value:")
				self.contentdata[idl]["lblIsNum"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["intIsNum"] = tk.IntVar()
				self.contentdata[idl]["chkIsNum"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intIsNum"], command=self.cs_graph_update)
				self.contentdata[idl]["chkIsNum"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					# rownum += 1
					self.contentdata[idl]["lblEnabled"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Enabled")
					self.contentdata[idl]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblMT"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Metric Type:")
				self.contentdata[idl]["lblMT"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["MTypes"] = [None, "", "Loading..."]
				self.contentdata[idl]["MType"] = tk.StringVar()
				self.contentdata[idl]["omMT"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["MType"], command=self.cs_graph_update, *self.contentdata[idl]["MTypes"])
				self.contentdata[idl]["omMT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblPM"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Primrary Metric:")
				self.contentdata[idl]["lblPM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["PMetrics"] = [None, "", "Loading..."]
				self.contentdata[idl]["PMetric"] = tk.StringVar()
				self.contentdata[idl]["omPM"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["PMetric"], command=self.cs_graph_update, *self.contentdata[idl]["PMetrics"])
				self.contentdata[idl]["omPM"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblSM"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Secondary Metric:")
				self.contentdata[idl]["lblSM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["SMetrics"] = [None, "", "Loading..."]
				self.contentdata[idl]["SMetric"] = tk.StringVar()
				self.contentdata[idl]["omSM"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["SMetric"], command=self.cs_graph_update, *self.contentdata[idl]["SMetrics"])
				self.contentdata[idl]["omSM"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[idl]["lblFA"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Agent:")
					self.contentdata[idl]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

					self.contentdata[idl]["FATypes"] = [None, "", "Loading..."]
					self.contentdata[idl]["FAType"] = tk.StringVar()
					self.contentdata[idl]["omFA"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FAType"], command=self.cs_graph_update, *self.contentdata[idl]["FATypes"])
					self.contentdata[idl]["omFA"].grid(column=1, row=rownum, sticky="nsew")

					self.contentdata[idl]["intFA"] = tk.IntVar()
					self.contentdata[idl]["chkFA"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intFA"], command=self.cs_graph_update)
					self.contentdata[idl]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFN"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Type:")
				self.contentdata[idl]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idl]["FNType"] = tk.StringVar()
				self.contentdata[idl]["omFR"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idl]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFP"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Pattern:")
				self.contentdata[idl]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["FPattern"] = tk.StringVar()
				self.contentdata[idl]["inpFP"] = ttk.Entry(self.contentdata[idl]["Frames"][datatypel], textvariable=self.contentdata[idl]["FPattern"])
				self.contentdata[idl]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idl]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idl]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

				rownum += 1
				self.contentdata[idl]["lblGG"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Apply Granularity:")
				self.contentdata[idl]["lblGG"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["lblGS"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Seconds")
				self.contentdata[idl]["lblGS"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idl]["lblGW"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Show")
				self.contentdata[idl]["lblGW"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["GSeconds"] = tk.StringVar()
				self.contentdata[idl]["inpGS"] = ttk.Entry(self.contentdata[idl]["Frames"][datatypel], textvariable=self.contentdata[idl]["GSeconds"])
				self.contentdata[idl]["inpGS"].grid(column=1, row=rownum, sticky="nsew")
				self.contentdata[idl]["inpGS"].bind('<FocusOut>', self.cs_graph_update)

				GWTypes = ["Average", "Average", "Maximum", "Minimum"]
				self.contentdata[idl]["GWType"] = tk.StringVar()
				self.contentdata[idl]["omGW"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["GWType"], command=self.cs_graph_update, *GWTypes)
				self.contentdata[idl]["omGW"].grid(column=2, row=rownum, sticky="nsew")

			if datatypel == "Result":

				rownum += 1
				self.contentdata[idl]["lblEnabled"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Enabled")
				self.contentdata[idl]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblRT"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Result Type:")
				self.contentdata[idl]["lblRT"].grid(column=0, row=rownum, sticky="nsew")

				RType = self.base.rt_table_get_rt(idl)
				RTypes = [RType, "Response Time", "TPS", "Total TPS"]
				self.contentdata[idl]["RType"] = tk.StringVar()
				self.contentdata[idl]["omRT"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["RType"], command=self.cs_graph_update, *RTypes)
				self.contentdata[idl]["omRT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# result filtered by PASS, FAIL, None
				self.contentdata[idl]["lblFR"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Result:")
				self.contentdata[idl]["lblFR"].grid(column=0, row=rownum, sticky="nsew")

				FRTypes = [None, "None", "Pass", "Fail"]
				self.contentdata[idl]["FRType"] = tk.StringVar()
				self.contentdata[idl]["omFR"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FRType"], command=self.cs_graph_update, *FRTypes)
				self.contentdata[idl]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idl]["intFR"] = tk.IntVar()
				self.contentdata[idl]["chkFR"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intFR"], command=self.cs_graph_update)
				self.contentdata[idl]["chkFR"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFA"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Agent:")
				self.contentdata[idl]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[idl]["FAType"] = tk.StringVar()
				self.contentdata[idl]["omFA"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FAType"], command=self.cs_graph_update, *self.contentdata[idl]["FATypes"])
				self.contentdata[idl]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idl]["intFA"] = tk.IntVar()
				self.contentdata[idl]["chkFA"] = ttk.Checkbutton(self.contentdata[idl]["Frames"][datatypel], variable=self.contentdata[idl]["intFA"], command=self.cs_graph_update)
				self.contentdata[idl]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFN"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Type:")
				self.contentdata[idl]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idl]["FNType"] = tk.StringVar()
				self.contentdata[idl]["omFR"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idl]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["lblFP"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Filter Pattern:")
				self.contentdata[idl]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["FPattern"] = tk.StringVar()
				self.contentdata[idl]["inpFP"] = ttk.Entry(self.contentdata[idl]["Frames"][datatypel], textvariable=self.contentdata[idl]["FPattern"])
				self.contentdata[idl]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idl]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idl]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

				rownum += 1
				self.contentdata[idl]["lblGG"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Apply Granularity:")
				self.contentdata[idl]["lblGG"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idl]["lblGS"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Seconds")
				self.contentdata[idl]["lblGS"].grid(column=1, row=rownum, sticky="nsew")

				if RType is not None and "TPS" not in RType:
					self.contentdata[idl]["lblGW"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="Show")
					self.contentdata[idl]["lblGW"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["GSeconds"] = tk.StringVar()
				self.contentdata[idl]["inpGS"] = ttk.Entry(self.contentdata[idl]["Frames"][datatypel], textvariable=self.contentdata[idl]["GSeconds"])
				self.contentdata[idl]["inpGS"].grid(column=1, row=rownum, sticky="nsew")
				self.contentdata[idl]["inpGS"].bind('<FocusOut>', self.cs_graph_update)

				GWTypes = ["Average", "Average", "Maximum", "Minimum"]
				self.contentdata[idl]["GWType"] = tk.StringVar()
				if RType is not None and "TPS" not in RType:
					self.contentdata[idl]["omGW"] = ttk.OptionMenu(self.contentdata[idl]["Frames"][datatypel], self.contentdata[idl]["GWType"], command=self.cs_graph_update, *GWTypes)
					self.contentdata[idl]["omGW"].grid(column=2, row=rownum, sticky="nsew")

			if datatypel == "SQL":
				rownum += 1
				# sql = self.base.rt_table_get_sql(id)
				self.contentdata[idl]["lblSQL"] = ttk.Label(self.contentdata[idl]["Frames"][datatypel], text="SQL:")
				self.contentdata[idl]["lblSQL"].grid(column=0, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idl]["tSQL"] = tk.Text(self.contentdata[idl]["Frames"][datatypel])
				self.contentdata[idl]["tSQL"].grid(column=0, row=rownum, columnspan=100, sticky="nsew")
				# data = self.contentdata[id]["tSQL"].insert('0.0', sql)
				# <Leave> makes UI to jumpy
				# self.contentdata[idl]["tSQL"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idl]["tSQL"].bind('<FocusOut>', self.cs_graph_update)

		if datatyper not in self.contentdata[id]["Frames"]:
			self.base.debugmsg(6, "datatyper:", datatyper)
			self.contentdata[idr]["Frames"][datatyper] = tk.Frame(self.contentdata[id]["RFrame"])
			# self.contentdata[id]["Frames"][datatyper].config(bg="SlateBlue3")
			# self.contentdata[id]["Frames"][datatyper].columnconfigure(0, weight=1)
			self.contentdata[idr]["Frames"][datatyper].columnconfigure(99, weight=1)

			# "Metric", "Result", "SQL"

			if datatyper == "Monitoring":
				rownum += 1
				self.contentdata[idr]["lblSTot"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Show Total:")
				self.contentdata[idr]["lblSTot"].grid(column=0, row=rownum, sticky="nsew")

				# self.contentdata[idr]["Frames"][datatyper].columnconfigure(1, weight=1)
				self.contentdata[idr]["Frames"][datatyper].columnconfigure(1, minsize=150)
				self.contentdata[idr]["intSTot"] = tk.IntVar()
				self.contentdata[idr]["chkSTot"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intSTot"], command=self.cs_graph_update)
				self.contentdata[idr]["chkSTot"].grid(column=1, row=rownum, sticky="nsew")

			if datatyper == "Plan":
				rownum += 1
				self.contentdata[idr]["lblSTot"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Show Total:")
				self.contentdata[idr]["lblSTot"].grid(column=0, row=rownum, sticky="nsew")

				# self.contentdata[idr]["Frames"][datatyper].columnconfigure(1, weight=1)
				self.contentdata[idr]["Frames"][datatyper].columnconfigure(1, minsize=150)
				self.contentdata[idr]["intSTot"] = tk.IntVar()
				self.contentdata[idr]["chkSTot"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intSTot"], command=self.cs_graph_update)
				self.contentdata[idr]["chkSTot"].grid(column=1, row=rownum, sticky="nsew")

			if datatyper == "Metric":
				showmetricagents = 0
				if "DBTable" in self.base.settings and "Metrics" in self.base.settings["DBTable"] and "DataSource" in self.base.settings["DBTable"]["Metrics"]:
					showmetricagents = self.base.settings["DBTable"]["Metrics"]["DataSource"]

				self.base.debugmsg(6, "datatyper:", datatyper)
				rownum += 1
				self.contentdata[idr]["lblIsNum"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Number Value:")
				self.contentdata[idr]["lblIsNum"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["intIsNum"] = tk.IntVar()
				self.contentdata[idr]["chkIsNum"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intIsNum"], command=self.cs_graph_update)
				self.contentdata[idr]["chkIsNum"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					# rownum += 1
					self.contentdata[idr]["lblEnabled"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Enabled")
					self.contentdata[idr]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblMT"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Metric Type:")
				self.contentdata[idr]["lblMT"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["MTypes"] = [None, "", "Loading..."]
				self.contentdata[idr]["MType"] = tk.StringVar()
				self.contentdata[idr]["omMT"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["MType"], command=self.cs_graph_update, *self.contentdata[idr]["MTypes"])
				self.contentdata[idr]["omMT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblPM"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Primrary Metric:")
				self.contentdata[idr]["lblPM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["PMetrics"] = [None, "", "Loading..."]
				self.contentdata[idr]["PMetric"] = tk.StringVar()
				self.contentdata[idr]["omPM"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["PMetric"], command=self.cs_graph_update, *self.contentdata[idr]["PMetrics"])
				self.contentdata[idr]["omPM"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblSM"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Secondary Metric:")
				self.contentdata[idr]["lblSM"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["SMetrics"] = [None, "", "Loading..."]
				self.contentdata[idr]["SMetric"] = tk.StringVar()
				self.contentdata[idr]["omSM"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["SMetric"], command=self.cs_graph_update, *self.contentdata[idr]["SMetrics"])
				self.contentdata[idr]["omSM"].grid(column=1, row=rownum, sticky="nsew")

				if showmetricagents:
					rownum += 1
					self.contentdata[idr]["lblFA"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Agent:")
					self.contentdata[idr]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

					self.contentdata[idr]["FATypes"] = [None, "", "Loading..."]
					self.contentdata[idr]["FAType"] = tk.StringVar()
					self.contentdata[idr]["omFA"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FAType"], command=self.cs_graph_update, *self.contentdata[idr]["FATypes"])
					self.contentdata[idr]["omFA"].grid(column=1, row=rownum, sticky="nsew")

					self.contentdata[idr]["intFA"] = tk.IntVar()
					self.contentdata[idr]["chkFA"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intFA"], command=self.cs_graph_update)
					self.contentdata[idr]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFN"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Type:")
				self.contentdata[idr]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idr]["FNType"] = tk.StringVar()
				self.contentdata[idr]["omFR"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idr]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFP"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Pattern:")
				self.contentdata[idr]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["FPattern"] = tk.StringVar()
				self.contentdata[idr]["inpFP"] = ttk.Entry(self.contentdata[idr]["Frames"][datatyper], textvariable=self.contentdata[idr]["FPattern"])
				self.contentdata[idr]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idr]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idr]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

				rownum += 1
				self.contentdata[idr]["lblGG"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Apply Granularity:")
				self.contentdata[idr]["lblGG"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["lblGS"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Seconds")
				self.contentdata[idr]["lblGS"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idr]["lblGW"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Show")
				self.contentdata[idr]["lblGW"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["GSeconds"] = tk.StringVar()
				self.contentdata[idr]["inpGS"] = ttk.Entry(self.contentdata[idr]["Frames"][datatyper], textvariable=self.contentdata[idr]["GSeconds"])
				self.contentdata[idr]["inpGS"].grid(column=1, row=rownum, sticky="nsew")
				self.contentdata[idr]["inpGS"].bind('<FocusOut>', self.cs_graph_update)

				GWTypes = ["Average", "Average", "Maximum", "Minimum"]
				self.contentdata[idr]["GWType"] = tk.StringVar()
				self.contentdata[idr]["omGW"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["GWType"], command=self.cs_graph_update, *GWTypes)
				self.contentdata[idr]["omGW"].grid(column=2, row=rownum, sticky="nsew")

			if datatyper == "Result":

				rownum += 1
				self.contentdata[idr]["lblEnabled"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Enabled")
				self.contentdata[idr]["lblEnabled"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblRT"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Result Type:")
				self.contentdata[idr]["lblRT"].grid(column=0, row=rownum, sticky="nsew")

				RType = self.base.rt_table_get_rt(idr)
				RTypes = [RType, "Response Time", "TPS", "Total TPS"]
				self.contentdata[idr]["RType"] = tk.StringVar()
				self.contentdata[idr]["omRT"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["RType"], command=self.cs_graph_update, *RTypes)
				self.contentdata[idr]["omRT"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				# result filtered by PASS, FAIL, None
				self.contentdata[idr]["lblFR"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Result:")
				self.contentdata[idr]["lblFR"].grid(column=0, row=rownum, sticky="nsew")

				FRTypes = [None, "None", "Pass", "Fail"]
				self.contentdata[idr]["FRType"] = tk.StringVar()
				self.contentdata[idr]["omFR"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FRType"], command=self.cs_graph_update, *FRTypes)
				self.contentdata[idr]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idr]["intFR"] = tk.IntVar()
				self.contentdata[idr]["chkFR"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intFR"], command=self.cs_graph_update)
				self.contentdata[idr]["chkFR"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFA"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Agent:")
				self.contentdata[idr]["lblFA"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["FATypes"] = [None, "", "Loading..."]
				self.contentdata[idr]["FAType"] = tk.StringVar()
				self.contentdata[idr]["omFA"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FAType"], command=self.cs_graph_update, *self.contentdata[idr]["FATypes"])
				self.contentdata[idr]["omFA"].grid(column=1, row=rownum, sticky="nsew")

				self.contentdata[idr]["intFA"] = tk.IntVar()
				self.contentdata[idr]["chkFA"] = ttk.Checkbutton(self.contentdata[idr]["Frames"][datatyper], variable=self.contentdata[idr]["intFA"], command=self.cs_graph_update)
				self.contentdata[idr]["chkFA"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFN"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Type:")
				self.contentdata[idr]["lblFN"].grid(column=0, row=rownum, sticky="nsew")

				FNTypes = [None, "None", "Wildcard (Unix Glob)", "Not Wildcard (Unix Glob)"]
				self.contentdata[idr]["FNType"] = tk.StringVar()
				self.contentdata[idr]["omFR"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["FNType"], command=self.cs_graph_update, *FNTypes)
				self.contentdata[idr]["omFR"].grid(column=1, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["lblFP"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Filter Pattern:")
				self.contentdata[idr]["lblFP"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["FPattern"] = tk.StringVar()
				self.contentdata[idr]["inpFP"] = ttk.Entry(self.contentdata[idr]["Frames"][datatyper], textvariable=self.contentdata[idr]["FPattern"])
				self.contentdata[idr]["inpFP"].grid(column=1, row=rownum, sticky="nsew")
				# <Leave> makes UI to jumpy
				# self.contentdata[idr]["inpFP"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idr]["inpFP"].bind('<FocusOut>', self.cs_graph_update)

				rownum += 1
				self.contentdata[idr]["lblGG"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Apply Granularity:")
				self.contentdata[idr]["lblGG"].grid(column=0, row=rownum, sticky="nsew")

				self.contentdata[idr]["lblGS"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Seconds")
				self.contentdata[idr]["lblGS"].grid(column=1, row=rownum, sticky="nsew")

				if RType is not None and "TPS" not in RType:
					self.contentdata[idr]["lblGW"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="Show")
					self.contentdata[idr]["lblGW"].grid(column=2, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["GSeconds"] = tk.StringVar()
				self.contentdata[idr]["inpGS"] = ttk.Entry(self.contentdata[idr]["Frames"][datatyper], textvariable=self.contentdata[idr]["GSeconds"])
				self.contentdata[idr]["inpGS"].grid(column=1, row=rownum, sticky="nsew")
				self.contentdata[idr]["inpGS"].bind('<FocusOut>', self.cs_graph_update)

				GWTypes = ["Average", "Average", "Maximum", "Minimum"]
				self.contentdata[idr]["GWType"] = tk.StringVar()
				if RType is not None and "TPS" not in RType:
					self.contentdata[idr]["omGW"] = ttk.OptionMenu(self.contentdata[idr]["Frames"][datatyper], self.contentdata[idr]["GWType"], command=self.cs_graph_update, *GWTypes)
					self.contentdata[idr]["omGW"].grid(column=2, row=rownum, sticky="nsew")

			if datatyper == "SQL":
				rownum += 1
				# sql = self.base.rt_table_get_sql(id)
				self.contentdata[idr]["lblSQL"] = ttk.Label(self.contentdata[idr]["Frames"][datatyper], text="SQL:")
				self.contentdata[idr]["lblSQL"].grid(column=0, row=rownum, sticky="nsew")

				rownum += 1
				self.contentdata[idr]["tSQL"] = tk.Text(self.contentdata[idr]["Frames"][datatyper])
				self.contentdata[idr]["tSQL"].grid(column=0, row=rownum, columnspan=100, sticky="nsew")
				# data = self.contentdata[idr]["tSQL"].insert('0.0', sql)
				# <Leave> makes UI to jumpy
				# self.contentdata[idr]["tSQL"].bind('<Leave>', self.cs_graph_update)
				self.contentdata[idr]["tSQL"].bind('<FocusOut>', self.cs_graph_update)

		# Update
		if datatypel == "SQL":
			sql = self.base.rt_graph_get_sql(idl)
			self.contentdata[idl]["tSQL"].delete('0.0', tk.END)
			self.contentdata[idl]["tSQL"].insert('0.0', sql)

		if datatyper == "SQL":
			sql = self.base.rt_graph_get_sql(idr)
			self.contentdata[idr]["tSQL"].delete('0.0', tk.END)
			self.contentdata[idr]["tSQL"].insert('0.0', sql)

		if datatypel == "Result":
			self.cs_datatable_update_result(idl)
			self.contentdata[idl]["RType"].set(self.base.rt_table_get_rt(idl))
			self.contentdata[idl]["intFR"].set(self.base.rt_table_get_enfr(idl))
			self.contentdata[idl]["FRType"].set(self.base.rt_table_get_fr(idl))
			self.contentdata[idl]["intFA"].set(self.base.rt_table_get_enfa(idl))
			self.contentdata[idl]["FAType"].set(self.base.rt_table_get_fa(idl))
			self.contentdata[idl]["FNType"].set(self.base.rt_table_get_fn(idl))
			self.contentdata[idl]["FPattern"].set(self.base.rt_table_get_fp(idl))
			self.contentdata[idl]["GSeconds"].set(self.base.rt_graph_get_gseconds(idl))
			self.contentdata[idl]["GWType"].set(self.base.rt_graph_get_gw(idl))

		if datatyper == "Result":
			self.cs_datatable_update_result(idr)
			self.contentdata[idr]["RType"].set(self.base.rt_table_get_rt(idr))
			self.contentdata[idr]["intFR"].set(self.base.rt_table_get_enfr(idr))
			self.contentdata[idr]["FRType"].set(self.base.rt_table_get_fr(idr))
			self.contentdata[idr]["intFA"].set(self.base.rt_table_get_enfa(idr))
			self.contentdata[idr]["FAType"].set(self.base.rt_table_get_fa(idr))
			self.contentdata[idr]["FNType"].set(self.base.rt_table_get_fn(idr))
			self.contentdata[idr]["FPattern"].set(self.base.rt_table_get_fp(idr))

			self.contentdata[idr]["GSeconds"].set(self.base.rt_graph_get_gseconds(idr))
			self.contentdata[idr]["GWType"].set(self.base.rt_graph_get_gw(idr))

		if datatypel == "Metric":
			self.base.debugmsg(5, "Update Options")
			self.cs_datatable_update_metrics(idl)
			self.base.debugmsg(5, "Set Options")
			while "SMetric" not in self.contentdata[idl]:
				time.sleep(0.1)
			if "intIsNum" in self.contentdata[idl]:
				self.contentdata[idl]["intIsNum"].set(self.base.rt_table_get_isnumeric(idl))
			if "MType" in self.contentdata[idl]:
				self.contentdata[idl]["MType"].set(self.base.rt_table_get_mt(idl))
			if "PMetric" in self.contentdata[idl]:
				self.contentdata[idl]["PMetric"].set(self.base.rt_table_get_pm(idl))
			if "SMetric" in self.contentdata[idl]:
				self.contentdata[idl]["SMetric"].set(self.base.rt_table_get_sm(idl))
			if "intFA" in self.contentdata[idl]:
				self.contentdata[idl]["intFA"].set(self.base.rt_table_get_enfa(idl))
			if "FAType" in self.contentdata[idl]:
				self.contentdata[idl]["FAType"].set(self.base.rt_table_get_fa(idl))
			if "FNType" in self.contentdata[idl]:
				self.contentdata[idl]["FNType"].set(self.base.rt_table_get_fn(idl))
			if "FPattern" in self.contentdata[idl]:
				self.contentdata[idl]["FPattern"].set(self.base.rt_table_get_fp(idl))
			if "GSeconds" in self.contentdata[idl]:
				self.contentdata[idl]["GSeconds"].set(self.base.rt_graph_get_gseconds(idl))
			if "GWType" in self.contentdata[idl]:
				self.contentdata[idl]["GWType"].set(self.base.rt_graph_get_gw(idl))

		if datatyper == "Metric":
			self.base.debugmsg(5, "Update Options")
			self.cs_datatable_update_metrics(idr)
			self.base.debugmsg(5, "Set Options")
			while "SMetric" not in self.contentdata[idr]:
				time.sleep(0.1)
			if "intIsNum" in self.contentdata[idr]:
				self.contentdata[idr]["intIsNum"].set(self.base.rt_table_get_isnumeric(idr))
			if "MType" in self.contentdata[idr]:
				self.contentdata[idr]["MType"].set(self.base.rt_table_get_mt(idr))
			if "PMetric" in self.contentdata[idr]:
				self.contentdata[idr]["PMetric"].set(self.base.rt_table_get_pm(idr))
			if "SMetric" in self.contentdata[idr]:
				self.contentdata[idr]["SMetric"].set(self.base.rt_table_get_sm(idr))
			if "intFA" in self.contentdata[idr]:
				self.contentdata[idr]["intFA"].set(self.base.rt_table_get_enfa(idr))
			if "FAType" in self.contentdata[idr]:
				self.contentdata[idr]["FAType"].set(self.base.rt_table_get_fa(idr))
			if "FNType" in self.contentdata[idr]:
				self.contentdata[idr]["FNType"].set(self.base.rt_table_get_fn(idr))
			if "FPattern" in self.contentdata[idr]:
				self.contentdata[idr]["FPattern"].set(self.base.rt_table_get_fp(idr))
			if "GSeconds" in self.contentdata[idr]:
				self.contentdata[idr]["GSeconds"].set(self.base.rt_graph_get_gseconds(idr))
			if "GWType" in self.contentdata[idr]:
				self.contentdata[idr]["GWType"].set(self.base.rt_graph_get_gw(idr))

		if datatypel == "Plan":
			self.contentdata[idl]["intSTot"].set(self.base.report_item_get_int(idl, "ShowTotal"))
			changes += 1

		if datatyper == "Plan":
			self.contentdata[idr]["intSTot"].set(self.base.report_item_get_int(idr, "ShowTotal"))
			changes += 1

		if datatypel == "Monitoring":
			self.contentdata[idl]["intSTot"].set(self.base.report_item_get_int(idl, "ShowTotal"))
			changes += 1

		if datatyper == "Monitoring":
			self.contentdata[idr]["intSTot"].set(self.base.report_item_get_int(idr, "ShowTotal"))
			changes += 1

		# Show
		self.contentdata[idl]["Frames"][datatypel].grid(column=0, row=self.contentdata[id]["DTFrame"], columnspan=100, sticky="nsew")
		self.contentdata[idr]["Frames"][datatyper].grid(column=0, row=self.contentdata[id]["DTFrame"], columnspan=100, sticky="nsew")

		if changes > 0:
			self.cs_graph_update(_event)

	#
	# Settings	-	Error Details
	#

	def cs_errors(self, id):
		self.base.debugmsg(9, "id:", id)

		iST = self.base.rt_setting_get_starttime(id)
		self.base.debugmsg(5, "iST:", iST)
		iET = self.base.rt_setting_get_endtime(id)
		self.base.debugmsg(5, "iET:", iET)

		images = self.base.rt_errors_get_images(id)
		self.base.debugmsg(5, "images:", images)
		grouprn = self.base.rt_errors_get_group_rn(id)
		self.base.debugmsg(5, "grouprn:", grouprn)
		groupet = self.base.rt_errors_get_group_et(id)
		self.base.debugmsg(5, "groupet:", groupet)

		lbl_Result = self.base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = self.base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = self.base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = self.base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = self.base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = self.base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = self.base.rt_errors_get_label(id, "lbl_NoScreenshot")

		self.contentdata[id]["LFrame"].columnconfigure(99, weight=1)
		rownum = 0

		# 		start time
		rownum += 1
		self.contentdata[id]["lblST"] = ttk.Label(self.contentdata[id]["LFrame"], text="Start Time:")
		self.contentdata[id]["lblST"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strST"] = tk.StringVar()
		fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
		self.contentdata[id]["strST"].set(fST)
		self.contentdata[id]["fST"] = fST

		self.contentdata[id]["eST"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strST"])
		self.contentdata[id]["eST"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["eST"].bind('<FocusOut>', self.cs_errors_update)

		# 		end time
		rownum += 1
		self.contentdata[id]["lblET"] = ttk.Label(self.contentdata[id]["LFrame"], text="End Time:")
		self.contentdata[id]["lblET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["strET"] = tk.StringVar()
		fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
		self.contentdata[id]["strET"].set(fET)
		self.contentdata[id]["fET"] = fET

		self.contentdata[id]["eET"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["strET"])
		self.contentdata[id]["eET"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["eET"].bind('<FocusOut>', self.cs_errors_update)

		# 		Show Screenshots
		rownum += 1
		self.contentdata[id]["lblImages"] = ttk.Label(self.contentdata[id]["LFrame"], text="Show screenshots:")
		self.contentdata[id]["lblImages"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intImages"] = tk.IntVar()
		self.contentdata[id]["chkImages"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intImages"], command=self.cs_errors_update)
		self.contentdata[id]["intImages"].set(images)
		self.contentdata[id]["chkImages"].grid(column=1, row=rownum, sticky="nsew")

		# 		Group by result name
		rownum += 1
		self.contentdata[id]["lblGroupRN"] = ttk.Label(self.contentdata[id]["LFrame"], text="Group by result name:")
		self.contentdata[id]["lblGroupRN"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intGroupRN"] = tk.IntVar()
		self.contentdata[id]["chkGroupRN"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intGroupRN"], command=self.cs_errors_update)
		self.contentdata[id]["intGroupRN"].set(grouprn)
		self.contentdata[id]["chkGroupRN"].grid(column=1, row=rownum, sticky="nsew")

		# 		Group by error text
		rownum += 1
		self.contentdata[id]["lblGroupET"] = ttk.Label(self.contentdata[id]["LFrame"], text="Group by error text:")
		self.contentdata[id]["lblGroupET"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["intGroupET"] = tk.IntVar()
		self.contentdata[id]["chkGroupET"] = ttk.Checkbutton(self.contentdata[id]["LFrame"], variable=self.contentdata[id]["intGroupET"], command=self.cs_errors_update)
		self.contentdata[id]["intGroupET"].set(groupet)
		self.contentdata[id]["chkGroupET"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["LFrame"], text=" ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblRename"] = ttk.Label(self.contentdata[id]["LFrame"], text="Rename Labels")
		self.contentdata[id]["lblRename"].grid(column=0, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblLabelName"] = ttk.Label(self.contentdata[id]["LFrame"], text="Label Name")
		self.contentdata[id]["lblLabelName"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["lblDispName"] = ttk.Label(self.contentdata[id]["LFrame"], text="Display Name")
		self.contentdata[id]["lblDispName"].grid(column=1, row=rownum, sticky="nsew")

		rownum += 1
		self.contentdata[id]["lblResult"] = ttk.Label(self.contentdata[id]["LFrame"], text="Result Name")
		self.contentdata[id]["lblResult"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varResult"] = tk.StringVar()
		self.contentdata[id]["varResult"].set(lbl_Result)
		self.contentdata[id]["inpResult"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varResult"])
		self.contentdata[id]["inpResult"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpResult"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpResult"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblTest"] = ttk.Label(self.contentdata[id]["LFrame"], text="Test")
		self.contentdata[id]["lblTest"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varTest"] = tk.StringVar()
		self.contentdata[id]["varTest"].set(lbl_Test)
		self.contentdata[id]["inpTest"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varTest"])
		self.contentdata[id]["inpTest"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpTest"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpTest"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblScript"] = ttk.Label(self.contentdata[id]["LFrame"], text="Script")
		self.contentdata[id]["lblScript"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varScript"] = tk.StringVar()
		self.contentdata[id]["varScript"].set(lbl_Script)
		self.contentdata[id]["inpScript"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varScript"])
		self.contentdata[id]["inpScript"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpScript"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpScript"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblError"] = ttk.Label(self.contentdata[id]["LFrame"], text="Error")
		self.contentdata[id]["lblError"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varError"] = tk.StringVar()
		self.contentdata[id]["varError"].set(lbl_Error)
		self.contentdata[id]["inpError"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varError"])
		self.contentdata[id]["inpError"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpError"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpError"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblCount"] = ttk.Label(self.contentdata[id]["LFrame"], text="Count")
		self.contentdata[id]["lblCount"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varCount"] = tk.StringVar()
		self.contentdata[id]["varCount"].set(lbl_Count)
		self.contentdata[id]["inpCount"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varCount"])
		self.contentdata[id]["inpCount"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpCount"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpCount"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblScreenshot"] = ttk.Label(self.contentdata[id]["LFrame"], text="Screenshot")
		self.contentdata[id]["lblScreenshot"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varScreenshot"] = tk.StringVar()
		self.contentdata[id]["varScreenshot"].set(lbl_Screenshot)
		self.contentdata[id]["inpScreenshot"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varScreenshot"])
		self.contentdata[id]["inpScreenshot"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpScreenshot"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpScreenshot"].bind('<FocusOut>', self.cs_errors_update)

		rownum += 1
		self.contentdata[id]["lblNoScreenshot"] = ttk.Label(self.contentdata[id]["LFrame"], text="No Screenshot")
		self.contentdata[id]["lblNoScreenshot"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["varNoScreenshot"] = tk.StringVar()
		self.contentdata[id]["varNoScreenshot"].set(lbl_NoScreenshot)
		self.contentdata[id]["inpNoScreenshot"] = ttk.Entry(self.contentdata[id]["LFrame"], textvariable=self.contentdata[id]["varNoScreenshot"])
		self.contentdata[id]["inpNoScreenshot"].grid(column=1, row=rownum, sticky="nsew")
		# <Leave> makes UI to jumpy
		# self.contentdata[id]["inpNoScreenshot"].bind('<Leave>', self.cs_errors_update)
		self.contentdata[id]["inpNoScreenshot"].bind('<FocusOut>', self.cs_errors_update)

	def cs_errors_update(self, _event=None, *args):
		self.base.debugmsg(5, "_event:", _event, "	args:", args)
		changes = 0
		# if len(args) > 0:
		# 	self.base.debugmsg(8, "args[0]:", args[0])
		# 	changes += args[0]
		id = self.sectionstree.focus()
		if _event is not None:
			name = self.base.report_item_get_name(_event)
			if name is not None:
				id = _event
		self.base.debugmsg(9, "id:", id)

		# 		start time
		if "strST" in self.contentdata[id]:
			st = self.contentdata[id]["strST"].get()
			self.base.debugmsg(5, "st:", st)
			if st != self.contentdata[id]["fST"]:
				ist = self.base.report_formateddatetimetosec(st)
				self.base.debugmsg(5, "ist:", ist)
				if ist > 0:
					ios = ist - self.base.rs_setting_get_starttime()
					self.base.debugmsg(5, "ios:", ios)
					changes += self.base.report_item_set_int(id, "startoffset", ios)

			iST = self.base.rt_setting_get_starttime(id)
			fST = "{} {}".format(self.base.report_formatdate(iST), self.base.report_formattime(iST))
			self.contentdata[id]["strST"].set(fST)
			self.contentdata[id]["fST"] = fST

		# 		end time
		if "strET" in self.contentdata[id]:
			et = self.contentdata[id]["strET"].get()
			self.base.debugmsg(5, "et:", et)
			if et != self.contentdata[id]["fET"]:
				iet = self.base.report_formateddatetimetosec(et)
				self.base.debugmsg(5, "iet:", iet)
				if iet > 0:
					ios = self.base.rs_setting_get_endtime() - iet
					self.base.debugmsg(5, "ios:", ios)
					changes += self.base.report_item_set_int(id, "endoffset", ios)

			iET = self.base.rt_setting_get_endtime(id)
			fET = "{} {}".format(self.base.report_formatdate(iET), self.base.report_formattime(iET))
			self.contentdata[id]["strET"].set(fET)
			self.contentdata[id]["fET"] = fET

		if "intImages" in self.contentdata[id]:
			images = self.contentdata[id]["intImages"].get()
			changes += self.base.rt_errors_set_images(id, images)

		if "intGroupRN" in self.contentdata[id]:
			group = self.contentdata[id]["intGroupRN"].get()
			changes += self.base.rt_errors_set_group_rn(id, group)

		if "intGroupET" in self.contentdata[id]:
			group = self.contentdata[id]["intGroupET"].get()
			changes += self.base.rt_errors_set_group_et(id, group)

		if "varResult" in self.contentdata[id]:
			lbl_Result = self.contentdata[id]["varResult"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_Result", lbl_Result)

		if "varTest" in self.contentdata[id]:
			lbl_Test = self.contentdata[id]["varTest"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_Test", lbl_Test)

		if "varScript" in self.contentdata[id]:
			lbl_Script = self.contentdata[id]["varScript"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_Script", lbl_Script)

		if "varError" in self.contentdata[id]:
			lbl_Error = self.contentdata[id]["varError"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_Error", lbl_Error)

		if "varCount" in self.contentdata[id]:
			lbl_Count = self.contentdata[id]["varCount"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_Count", lbl_Count)

		if "varScreenshot" in self.contentdata[id]:
			lbl_Screenshot = self.contentdata[id]["varScreenshot"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_Screenshot", lbl_Screenshot)

		if "varNoScreenshot" in self.contentdata[id]:
			lbl_NoScreenshot = self.contentdata[id]["varNoScreenshot"].get()
			changes += self.base.rt_errors_set_label(id, "lbl_NoScreenshot", lbl_NoScreenshot)

		if changes > 0:
			self.base.debugmsg(5, "content_preview id:", id)
			# self.content_preview(id)
			cp = threading.Thread(target=lambda: self.content_preview(id))
			cp.start()

	def cs_update_start_and_end_times(self, id, fST, fET):
		children = self.base.report_get_order(id)

		for child in children:
			if child not in self.contentdata:
				break
			if "strST" in self.contentdata[child] and "strET" in self.contentdata[child]:
				self.base.debugmsg(5, "section id with strST and strET to update:", id)
				self.contentdata[child]["strST"].set(fST)
				self.contentdata[child]["strET"].set(fET)
			self.cs_update_start_and_end_times(child, fST, fET)

	#
	# Preview
	#

	def content_preview(self, id):
		self.base.debugmsg(9, "id:", id)

		if self.base.config['Reporter']['Results']:
			self.updateStatus("Preview Loading.....")
		else:
			sres = "Please select a result file"
			self.updateStatus(sres)
			return None
		try:
			self.cp_generate_preview(id)
		except Exception as e:
			self.base.debugmsg(5, "e:", e)

		# self.t_preview[id] = threading.Thread(target=lambda: self.cp_generate_preview(id))
		# self.t_preview[id].start()

		# curritem = self.contentpreview.grid_slaves(column=0, row=0)
		# self.base.debugmsg(5, "curritem:", curritem)
		# if len(curritem)>0:
		# 	curritem[0].grid_forget()
		curritems = self.contentpreview.grid_slaves()
		# count = len(curritems)
		for curritem in curritems:
			curritem.grid_forget()
		self.cp_display_preview(id, 0)
		self.contentcanvas.config(scrollregion=self.contentpreview.bbox("all"))
		# self.contentpreview.columnconfigure(0, weight=1)

		# self.contentpreview.columnconfigure(0, weight=1)
		self.updateStatus("Preview Loaded")

	def cp_regenerate_preview(self):
		# self.contentdata = {}
		for itm in self.contentdata.keys():
			# if "Preview" in self.contentdata[itm]:
			# 	del self.contentdata[itm]["Preview"]
			self.contentdata[itm]["Changed"] = 0

		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)
		if len(selected) > 0:
			self.content_preview(selected)
		else:
			self.content_preview("TOP")

	def cp_generate_preview(self, id):
		self.base.debugmsg(8, "id:", id)
		pid, idl, idr = self.base.rt_graph_LR_Ids(id)

		self.base.debugmsg(8, "pid:", pid, "	idl:", idl, "	idr:", idr)
		# if id not in self.contentdata:
		while id not in self.contentdata:
			time.sleep(0.1)
			self.contentdata[pid] = {}
		if "Changed" not in self.contentdata[pid]:
			self.contentdata[pid]["Changed"] = 0
		while idl not in self.contentdata:
			time.sleep(0.1)
			self.contentdata[idl] = {}
		if "Changed" not in self.contentdata[idl]:
			self.contentdata[idl]["Changed"] = 0
		while idr not in self.contentdata:
			time.sleep(0.1)
			self.contentdata[idr] = {}
		if "Changed" not in self.contentdata[idr]:
			self.contentdata[idr]["Changed"] = 0

		type = self.base.report_item_get_type(pid)
		self.base.debugmsg(8, "type:", type)
		changed = False

		self.base.debugmsg(9, "self.base.report_item_get_changed(pid):", self.base.report_item_get_changed(pid))
		self.base.debugmsg(9, "self.contentdata[pid]:", self.contentdata[pid])
		self.base.debugmsg(9, "self.contentdata[pid][Changed]:", self.contentdata[pid]["Changed"])
		if self.base.report_item_get_changed(pid) > self.contentdata[pid]["Changed"]:
			changed = True
		self.base.debugmsg(9, "changed:", changed)
		if type == 'graph':
			self.base.debugmsg(8, "type:", type)
			if self.base.report_item_get_changed(idl) > self.contentdata[idl]["Changed"]:
				changed = True
			if self.base.report_item_get_changed(idr) > self.contentdata[idr]["Changed"]:
				changed = True
		self.base.debugmsg(8, "changed:", changed)

		gen = False
		if "Preview" not in self.contentdata[pid]:
			gen = True
		# if "Changed" in self.contentdata[id] and self.base.report_item_get_changed(id) > self.contentdata[id]["Changed"]:
		elif changed:
			gen = True

			self.base.debugmsg(8, "report_item_get_changed pid:", self.base.report_item_get_changed(pid), "	contentdata Changed:", self.contentdata[pid]["Changed"])
			if type == 'graph':
				self.base.debugmsg(8, "report_item_get_changed idl:", self.base.report_item_get_changed(idl), "	contentdata Changed:", self.contentdata[idl]["Changed"])
				self.base.debugmsg(8, "report_item_get_changed idr:", self.base.report_item_get_changed(idr), "	contentdata Changed:", self.contentdata[idr]["Changed"])
		else:
			self.base.debugmsg(8, "report_item_get_changed pid:", self.base.report_item_get_changed(pid), "	contentdata Changed:", self.contentdata[pid]["Changed"])
			if type == 'graph':
				self.base.debugmsg(8, "report_item_get_changed idl:", self.base.report_item_get_changed(idl), "	contentdata Changed:", self.contentdata[idl]["Changed"])
				self.base.debugmsg(8, "report_item_get_changed idr:", self.base.report_item_get_changed(idr), "	contentdata Changed:", self.contentdata[idr]["Changed"])

		self.base.debugmsg(7, "gen:", gen)
		if gen:
			if "Preview" in self.contentdata[pid]:
				del self.contentdata[pid]["Preview"]
			while "Preview" not in self.contentdata[pid]:
				time.sleep(0.1)
				self.contentdata[pid]["Changed"] = self.base.report_item_get_changed(pid)
				if type == 'graph':
					self.contentdata[idl]["Changed"] = self.base.report_item_get_changed(idl)
					self.contentdata[idr]["Changed"] = self.base.report_item_get_changed(idr)
				self.contentdata[pid]["Preview"] = tk.Frame(self.contentpreview, padx=0, pady=0, bd=0)
			# self.contentdata[id]["Preview"].config(bg="gold")
			# self.contentdata[id]["Preview"].config(bg=self.style_reportbg_colour)
			if id == "TOP":
				try:
					self.cp_titlepage(id)
				except Exception:
					pass
			else:
				rownum = 0

				titlenum = self.base.report_sect_number(id)
				self.base.debugmsg(8, "titlenum:", titlenum)
				title = "{} {}".format(titlenum, self.base.report_item_get_name(id))
				level = self.base.report_sect_level(id)
				tstyle = 'Report.TLabel'
				if level == 1:

					self.contentdata[id]["lblpgbrk"] = tk.Label(self.contentdata[id]["Preview"], text="	--- page break --- ")
					self.contentdata[id]["lblpgbrk"].config(bg="#ddd")
					self.contentdata[id]["lblpgbrk"].config(fg="#bbb")
					self.contentdata[id]["lblpgbrk"].grid(column=0, row=rownum, columnspan=998, sticky="nsew")

					self.contentdata[id]["lblpgbrk"] = tk.Label(self.contentdata[id]["Preview"], text="	")
					self.contentdata[id]["lblpgbrk"].config(bg="#ddd")
					self.contentdata[id]["lblpgbrk"].grid(column=999, row=rownum, sticky="nsew")

					self.contentdata[id]["Preview"].columnconfigure(1, weight=1)
					# self.contentdata[id]["Preview"].columnconfigure(999, weight=1)

					rownum += 1

					tstyle = 'Report.H1.TLabel'
				if level == 2:
					tstyle = 'Report.H2.TLabel'
				if level == 3:
					tstyle = 'Report.H3.TLabel'
				if level == 4:
					tstyle = 'Report.H4.TLabel'
				if level == 5:
					tstyle = 'Report.H5.TLabel'
				if level == 6:
					tstyle = 'Report.H6.TLabel'

				self.contentdata[id]["lbltitle"] = ttk.Label(self.contentdata[id]["Preview"], text=title, style=tstyle)
				# self.contentdata[id]["lbltitle"] = ttk.Label(self.contentdata[id]["Preview"], text=title)
				# self.contentdata[id]["lbltitle"].config(background=self.style_reportbg_colour)
				self.contentdata[id]["lbltitle"].grid(column=0, row=rownum, columnspan=9, sticky="nsew")

				self.contentdata[id]["rownum"] = rownum + 1
				# type = self.base.report_item_get_type(id)
				self.base.debugmsg(8, "type:", type)
				if type == 'contents':
					self.cp_contents(id)
				if type == 'note':
					self.cp_note(id)
				if type == 'table':
					self.cp_table(id)
				if type == 'graph':
					self.cp_graph(id)
				if type == 'errors':
					self.cp_errors(id)

		children = self.base.report_get_order(id)
		for child in children:
			try:
				self.cp_generate_preview(child)
				# self.t_preview[child] = threading.Thread(target=lambda: self.cp_generate_preview(child))
				# self.t_preview[child].start()
			except Exception as e:
				self.base.debugmsg(5, "e:", e)

	def cp_display_preview(self, id, row):
		self.base.debugmsg(5, "id:", id)
		if id in self.t_preview:
			if self.t_preview[id].is_alive():
				self.t_preview[id].join()

		# wait for preview available
		while id not in self.contentdata:
			time.sleep(0.1)
		while "Preview" not in self.contentdata[id]:
			time.sleep(0.1)

		self.updateStatus("Preview Loading..... ({})".format(str(row)))

		self.contentdata[id]["Preview"].grid(column=0, row=row, sticky="nsew")
		nextrow = row + 1
		self.base.debugmsg(9, "nextrow:", nextrow)
		children = self.base.report_get_order(id)
		for child in children:
			nextrow = self.cp_display_preview(child, nextrow)
		return nextrow

	def cp_titlepage(self, id):
		self.base.debugmsg(9, "id:", id)

		self.contentdata[id]["Preview"].columnconfigure(0, weight=1)
		# self.contentdata[id]["Preview"].columnconfigure(1, weight=1)
		self.contentdata[id]["Preview"].columnconfigure(2, weight=1)
		# self.contentdata[id]["Preview"].columnconfigure(3, weight=1)
		self.contentdata[id]["Preview"].columnconfigure(4, weight=1)
		colcontent = 1
		colimg = 2

		# Title
		#  top: 1	centre: 11	bottom:	21
		rownum = 1

		title = "{}".format(self.base.rs_setting_get_title())
		self.contentdata[id]["lblTitle"] = ttk.Label(self.contentdata[id]["Preview"], text=title, style='Report.Title1.TLabel')
		self.contentdata[id]["lblTitle"].grid(column=colcontent, columnspan=3, row=rownum, sticky="nsew")

		# Logo
		#  top: 2	centre: 12	bottom:	22
		rownum = 12

		self.base.debugmsg(5, "showtlogo:", self.base.rs_setting_get_int("showtlogo"))
		if self.base.rs_setting_get_int("showtlogo"):
			while "strLIPath" not in self.contentdata[id]:
				time.sleep(0.1)
			self.base.debugmsg(5, "strLIPath:", self.contentdata[id]["strLIPath"])
			if self.contentdata[id]["strLIPath"] is not None and len(self.contentdata[id]["strLIPath"]) > 0:
				self.contentdata[id]["oimg"] = Image.open(self.contentdata[id]["strLIPath"])
				self.base.debugmsg(5, "oimg:", self.contentdata[id]["oimg"])

				self.contentdata[id]["ologo"] = ImageTk.PhotoImage(self.contentdata[id]["oimg"])
				self.base.debugmsg(5, "ologo:", self.contentdata[id]["ologo"])

				# display an image label
				# ologo = tk.PhotoImage(file=flogo)
				self.contentdata[id]["lblLogo"] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id]["ologo"])
				# , padding=5
				self.contentdata[id]["lblLogo"].grid(column=colimg, row=rownum, sticky="nsew")

		# Execution Date range
		#  top: 3	centre: 13	bottom:	23
		rownum = 23

		execdr = ""
		fSD = ""

		if self.base.rs_setting_get_int("showstarttime"):
			iST = self.base.rs_setting_get_starttime()
			fSD = "{}".format(self.base.report_formatdate(iST))
			fST = "{}".format(self.base.report_formattime(iST))

			execdr = "{} {}".format(fSD, fST)

		if self.base.rs_setting_get_int("showendtime"):
			iET = self.base.rs_setting_get_endtime()
			fED = "{}".format(self.base.report_formatdate(iET))
			fET = "{}".format(self.base.report_formattime(iET))

			if not self.base.rs_setting_get_int("showstarttime"):
				execdr = "{} {}".format(fED, fET)
			else:
				if fSD == fED:
					execdr = "{} - {}".format(execdr, fET)
				else:
					execdr = "{} - {} {}".format(execdr, fED, fET)

		self.contentdata[id]["lblTitle"] = ttk.Label(self.contentdata[id]["Preview"], text=execdr, style='Report.Title2.TLabel')
		self.contentdata[id]["lblTitle"].grid(column=colcontent, columnspan=3, row=rownum, sticky="nsew")

	def cp_contents(self, id):
		self.base.debugmsg(5, "id:", id)
		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ", style='Report.TLabel')
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		self.contentdata[id]["fmeTOC"] = tk.Frame(self.contentdata[id]["Preview"])
		# self.contentdata[id]["fmeGraph"].config(bg="green")
		self.contentdata[id]["fmeTOC"].grid(column=1, row=rownum, sticky="nsew")
		self.contentdata[id]["Preview"].columnconfigure(1, weight=1)

		mode = self.base.rt_contents_get_mode(id)
		level = self.base.rt_contents_get_level(id)

		self.base.debugmsg(5, "mode:", mode, "	level:", level)
		fmode = None
		if mode == "Table Of Contents":
			fmode = None
		if mode == "Table of Graphs":
			fmode = "graph"
		if mode == "Table Of Tables":
			fmode = "table"

		self.cp_contents_row("TOP", rownum, id, fmode, level)

	def cp_contents_row(self, id, rownum, fid, fmode, flevel):
		self.base.debugmsg(5, "id:", id, "	rownum:", rownum, "	fmode:", fmode, "	flevel:", flevel)
		display = True

		level = self.base.report_sect_level(id)
		if id == "TOP":
			display = False
			level = 0
		self.base.debugmsg(5, "level:", level)

		if display and fmode is not None:
			display = False
			type = self.base.report_item_get_type(id)
			if fmode == type:
				display = True

		if display and level > flevel:
			display = False

		nextrow = rownum
		if display:
			type = self.base.report_item_get_type(id)
			titlenum = self.base.report_sect_number(id)
			titlename = self.base.report_item_get_name(id)
			titlelevel = self.base.report_sect_level(id)
			self.base.debugmsg(6, "type:", type, "	titlenum:", titlenum, "	titlename:", titlename, "	titlelevel:", titlelevel)

			numarr = titlenum.split(".")
			self.base.debugmsg(5, "numarr:", numarr)
			pagenum = int(numarr[0]) + 1
			self.base.debugmsg(5, "pagenum:", pagenum)

			colnum = 1
			cellname = "{}_{}".format(id, colnum)
			self.contentdata[fid][cellname] = ttk.Label(self.contentdata[fid]["fmeTOC"], text=str(titlenum), style='Report.TLabel')
			self.contentdata[fid][cellname].grid(column=colnum, row=rownum, sticky="nsew")

			colnum += 1
			cellname = "{}_{}".format(id, colnum)
			self.contentdata[fid][cellname] = ttk.Label(self.contentdata[fid]["fmeTOC"], text=str(titlename), style='Report.TLabel')
			self.contentdata[fid][cellname].grid(column=colnum, row=rownum, sticky="nsew")

			colnum += 1
			self.contentdata[fid]["fmeTOC"].columnconfigure(colnum, weight=1)

			colnum += 1
			cellname = "{}_{}".format(id, colnum)
			self.contentdata[fid][cellname] = ttk.Label(self.contentdata[fid]["fmeTOC"], text=str(pagenum), style='Report.TLabel')
			self.contentdata[fid][cellname].grid(column=colnum, row=rownum, sticky="nsew")

			nextrow = rownum + 1

		self.base.debugmsg(9, "nextrow:", nextrow)
		if level < flevel:
			children = self.base.report_get_order(id)
			for child in children:
				nextrow = self.cp_contents_row(child, nextrow, fid, fmode, flevel)
		return nextrow

	def cp_note(self, id):
		self.base.debugmsg(9, "id:", id)
		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ", style='Report.TLabel')
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		notetxt = "{}".format(self.base.rt_note_get(id))
		self.contentdata[id]["lblNote"] = ttk.Label(self.contentdata[id]["Preview"], text=notetxt, style='Report.TLabel')
		self.contentdata[id]["lblNote"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[id]["Preview"].columnconfigure(1, weight=1)

	def cp_graph(self, id):
		pid, idl, idr = self.base.rt_graph_LR_Ids(id)
		self.base.debugmsg(5, "pid:", pid, "	idl:", idl, "	idr:", idr)

		axisenl = self.base.rt_graph_get_axisen(idl)
		axisenr = self.base.rt_graph_get_axisen(idr)

		datatypel = self.base.rt_graph_get_dt(idl)
		datatyper = self.base.rt_graph_get_dt(idr)

		tz = zoneinfo.ZoneInfo(self.base.rs_setting_get_timezone())

		if datatypel == "SQL":
			sqll = self.base.rt_graph_get_sql(idl)
		else:
			sqll = self.base.rt_graph_generate_sql(idl)
		self.base.debugmsg(9, "sqll:", sqll)

		if datatyper == "SQL":
			sqlr = self.base.rt_graph_get_sql(idr)
		else:
			sqlr = self.base.rt_graph_generate_sql(idr)
		self.base.debugmsg(9, "sqlr:", sqlr)

		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")
		# self.contentdata[id]["lblSpacer"].config(bg=self.style_reportbg_colour)

		self.contentdata[id]["Preview"].columnconfigure(1, weight=1)
		self.contentdata[id]["Preview"].rowconfigure(rownum, weight=1)

		self.contentdata[id]["fmeGraph"] = tk.Frame(self.contentdata[id]["Preview"])
		# self.contentdata[id]["fmeGraph"].config(bg="green")
		self.contentdata[id]["fmeGraph"].grid(column=1, row=rownum, sticky="nsew")

		self.contentdata[id]["fmeGraph"].columnconfigure(0, weight=1)
		self.contentdata[id]["fmeGraph"].rowconfigure(0, weight=1)
		self.contentdata[id]["fig_dpi"] = 72
		self.contentdata[id]["fig"] = Figure(dpi=self.contentdata[id]["fig_dpi"])

		self.contentdata[id]["axisL"] = self.contentdata[id]["fig"].add_subplot(1, 1, 1)
		self.base.debugmsg(8, "axisL:", self.contentdata[id]["axisL"])
		# self.contentdata[id]["axisL"].grid(True, 'major', 'both')
		self.contentdata[id]["axisL"].grid(True, 'major', 'x')
		# self.base.debugmsg(8, "axisL:", self.contentdata[id]["axisL"])
		self.contentdata[id]["axisR"] = self.contentdata[id]["axisL"].twinx()
		self.base.debugmsg(8, "axisR:", self.contentdata[id]["axisR"])
		# self.contentdata[id]["axisR"].grid(True, 'major', 'both')
		# self.base.debugmsg(8, "axisR:", self.contentdata[id]["axisR"])
		self.contentdata[id]["fig"].autofmt_xdate(bottom=0.2, rotation=30, ha='right')

		self.contentdata[id]["canvas"] = FigureCanvasTkAgg(self.contentdata[id]["fig"], self.contentdata[id]["fmeGraph"])
		self.contentdata[id]["canvas"].get_tk_widget().grid(column=0, row=0, sticky="nsew")
		# self.contentdata[id]["canvas"].get_tk_widget().config(bg="blue")

		self.base.debugmsg(8, "canvas:", self.contentdata[id]["canvas"])
		# self.base.debugmsg(8, "axis:", self.contentdata[id]["axis"])

		# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tick_params.html
		# self.contentdata[id]["axisL"].grid(True, 'major', 'x')
		# https://matplotlib.org/stable/api/_as_gen/matplotlib.axis.Axis.get_ticklabels.html

		# tckprms = self.contentdata[id]["axisL"].get_tick_params(which='major')
		# self.base.debugmsg(5, "tckprms:", tckprms)

		self.contentdata[id]["axisL"].tick_params(labelleft=False, length=0)
		self.contentdata[id]["axisR"].tick_params(labelright=False, length=0)

		try:
			self.contentdata[id]["canvas"].draw()
			self.contentdata[id]["fig"].set_tight_layout(True)
		except Exception as e:
			self.base.debugmsg(5, "canvas.draw() Exception:", e)

		dodraw = False
		self.contentdata[id]["graphdata"] = {}

		if (sqll is not None and len(sqll.strip()) > 0) or (sqlr is not None and len(sqlr.strip()) > 0):
			# Populate Left Y Axis Data
			if sqll is not None and len(sqll.strip()) > 0 and axisenl > 0:
				self.base.debugmsg(7, "sqll:", sqll)
				key = "{}_{}".format(id, self.base.report_item_get_changed(idl))
				self.base.debugmsg(7, "key:", key)
				self.base.dbqueue["Read"].append({"SQL": sqll, "KEY": key})
				while key not in self.base.dbqueue["ReadResult"]:
					time.sleep(0.1)
					# self.base.debugmsg(9, "Waiting for gdata for:", key)

				gdata = self.base.dbqueue["ReadResult"][key]

				if datatypel == "Plan":
					self.base.debugmsg(9, "gdata before:", gdata)
					gdata = self.base.graph_postprocess_data_plan(idl, gdata)
				if datatypel == "Monitoring":
					self.base.debugmsg(9, "gdata before:", gdata)
					gdata = self.base.graph_postprocess_data_monitoring(idl, gdata)

				self.base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					self.base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						self.base.debugmsg(9, "name:", name)
						if name not in self.contentdata[id]["graphdata"]:
							self.contentdata[id]["graphdata"][name] = {}

							colour = self.base.named_colour(name)
							self.base.debugmsg(8, "name:", name, "	colour:", colour)
							self.contentdata[id]["graphdata"][name]["Colour"] = colour
							self.contentdata[id]["graphdata"][name]["Axis"] = "axisL"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							self.contentdata[id]["graphdata"][name]["objTime"] = []
							self.contentdata[id]["graphdata"][name]["Values"] = []

						self.contentdata[id]["graphdata"][name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						self.contentdata[id]["graphdata"][name]["Values"].append(self.base.rt_graph_floatval(row["Value"]))
					else:
						break

			# attempt to Populate right Y Axis Data
			if sqlr is not None and len(sqlr.strip()) > 0 and axisenr > 0:
				self.base.debugmsg(7, "sqlr:", sqlr)
				key = "{}_{}".format(id, self.base.report_item_get_changed(idr))
				self.base.debugmsg(7, "key:", key)
				self.base.dbqueue["Read"].append({"SQL": sqlr, "KEY": key})
				while key not in self.base.dbqueue["ReadResult"]:
					time.sleep(0.1)
					# self.base.debugmsg(9, "Waiting for gdata for:", key)

				gdata = self.base.dbqueue["ReadResult"][key]

				if datatyper == "Plan":
					self.base.debugmsg(9, "gdata before:", gdata)
					gdata = self.base.graph_postprocess_data_plan(idr, gdata)
				if datatyper == "Monitoring":
					self.base.debugmsg(9, "gdata before:", gdata)
					gdata = self.base.graph_postprocess_data_monitoring(idr, gdata)

				self.base.debugmsg(9, "gdata:", gdata)

				for row in gdata:
					self.base.debugmsg(9, "row:", row)
					if 'Name' in row:
						name = row['Name']
						self.base.debugmsg(9, "name:", name)
						if name not in self.contentdata[id]["graphdata"]:
							self.contentdata[id]["graphdata"][name] = {}

							colour = self.base.named_colour(name)
							self.base.debugmsg(8, "name:", name, "	colour:", colour)
							self.contentdata[id]["graphdata"][name]["Colour"] = colour
							self.contentdata[id]["graphdata"][name]["Axis"] = "axisR"
							# self.contentdata[id]["graphdata"][name]["Time"] = []
							self.contentdata[id]["graphdata"][name]["objTime"] = []
							self.contentdata[id]["graphdata"][name]["Values"] = []

						self.contentdata[id]["graphdata"][name]["objTime"].append(datetime.fromtimestamp(row["Time"], tz))
						self.contentdata[id]["graphdata"][name]["Values"].append(self.base.rt_graph_floatval(row["Value"]))
					else:
						break

			self.base.debugmsg(8, "self.contentdata[id][graphdata]:", self.contentdata[id]["graphdata"])

			for name in self.contentdata[id]["graphdata"]:
				self.base.debugmsg(7, "name:", name)
				axis = "axisL"
				if "Axis" in self.contentdata[id]["graphdata"][name]:
					axis = self.contentdata[id]["graphdata"][name]["Axis"]

				if len(self.contentdata[id]["graphdata"][name]["Values"]) > 1 and len(self.contentdata[id]["graphdata"][name]["Values"]) == len(self.contentdata[id]["graphdata"][name]["objTime"]):
					try:
						self.contentdata[id][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name)
						# self.contentdata[id]["axis"][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name)
						dodraw = True
					except Exception as e:
						self.base.debugmsg(7, "axis.plot() Exception:", e)

				if len(self.contentdata[id]["graphdata"][name]["Values"]) == 1 and len(self.contentdata[id]["graphdata"][name]["Values"]) == len(self.contentdata[id]["graphdata"][name]["objTime"]):
					try:
						self.contentdata[id][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name, marker='o')
						# self.contentdata[id]["axis"][axis].plot(self.contentdata[id]["graphdata"][name]["objTime"], self.contentdata[id]["graphdata"][name]["Values"], self.contentdata[id]["graphdata"][name]["Colour"], label=name, marker='o')
						dodraw = True
					except Exception as e:
						self.base.debugmsg(7, "axis.plot() Exception:", e)

			if dodraw:

				# Left axis Limits
				if axisenl > 0:
					self.contentdata[id]["axisL"].grid(True, 'major', 'y')
					self.contentdata[id]["axisL"].tick_params(labelleft=True, length=5)

					SMetric = "Other"
					if datatypel == "Metric":
						SMetric = self.base.rt_table_get_sm(idl)
					self.base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						self.contentdata[id]["axisL"].set_ylim(0, 100)
					else:
						self.contentdata[id]["axisL"].set_ylim(0)

				# Right axis Limits
				if axisenr > 0:
					self.contentdata[id]["axisR"].grid(True, 'major', 'y')
					self.contentdata[id]["axisR"].tick_params(labelright=True, length=5)

					SMetric = "Other"
					if datatyper == "Metric":
						SMetric = self.base.rt_table_get_sm(idr)
					self.base.debugmsg(8, "SMetric:", SMetric)
					if SMetric in ["Load", "CPU", "MEM", "NET"]:
						self.contentdata[id]["axisR"].set_ylim(0, 100)
					else:
						self.contentdata[id]["axisR"].set_ylim(0)

				self.contentdata[id]["fig"].set_tight_layout(True)
				self.contentdata[id]["fig"].autofmt_xdate(bottom=0.2, rotation=30, ha='right')
				try:
					self.contentdata[id]["canvas"].draw()
				except Exception as e:
					self.base.debugmsg(5, "canvas.draw() Exception:", e)

	def cp_table(self, id):
		self.base.debugmsg(9, "id:", id)
		datatype = self.base.rt_table_get_dt(id)
		if datatype == "SQL":
			sql = self.base.rt_table_get_sql(id)
		else:
			sql = self.base.rt_table_generate_sql(id)
			self.base.debugmsg(5, "sql:", sql)
		colours = self.base.rt_table_get_colours(id)
		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")
		if sql is not None and len(sql.strip()) > 0:
			self.base.debugmsg(8, "sql:", sql)
			key = "{}_{}".format(id, self.base.report_item_get_changed(id))
			self.base.dbqueue["Read"].append({"SQL": sql, "KEY": key})
			while key not in self.base.dbqueue["ReadResult"]:
				time.sleep(0.1)

			tdata = self.base.dbqueue["ReadResult"][key]
			# table_postprocess_data_plan
			if datatype == "Plan":
				self.base.debugmsg(9, "tdata before:", tdata)
				tdata = self.base.table_postprocess_data_plan(id, tdata)
			if datatype == "Monitoring":
				self.base.debugmsg(9, "tdata before:", tdata)
				tdata = self.base.table_postprocess_data_monitoring(id, tdata)
			self.base.debugmsg(8, "tdata:", tdata)

			# self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text=notetxt)
			# self.contentdata[id]["lblSpacer"].grid(column=1, row=rownum, sticky="nsew")

			if len(tdata) > 0:
				cols = list(tdata[0].keys())
				self.base.debugmsg(7, "cols:", cols)

				if colours:
					cellname = "h_{}".format("colours")
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=" ", style='Report.THead.TLabel')
					self.contentdata[id][cellname].grid(column=1, row=rownum, sticky="nsew")

				colnum = 1 + colours
				for col in cols:
					if col not in ["Colour"]:
						show = self.base.report_item_get_bool_def1(id, self.base.rt_table_ini_colname(f"{col} Show"))
						if show:
							cellname = "h_{}".format(col)
							self.base.debugmsg(9, "cellname:", cellname)
							dispname = self.base.rt_table_get_colname(id, col)
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=f" {dispname.strip()} ", style='Report.THead.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")
							colnum += 1
				i = 0
				for row in tdata:
					i += 1
					rownum += 1
					colnum = 0
					if colours:
						colnum += 1
						cellname = "{}_{}".format(i, "colour")
						self.contentdata[id][cellname] = tk.Label(self.contentdata[id]["Preview"], text="  ")
						# self.contentdata[id][cellname] = tk.Button(self.contentdata[id]["Preview"], text=" ")
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						self.base.debugmsg(9, "row:", row)
						if "Colour" in row:
							label = row["Colour"]
						else:
							label = row[cols[0]]
						self.base.debugmsg(9, "label:", label)
						colour = self.base.named_colour(label)
						self.base.debugmsg(9, "colour:", colour)
						self.contentdata[id][cellname].config(bg=colour)
						# self.contentdata[id][cellname].config(background=colour, activebackground=colour)

						# self.contentdata[id][cellname].config(command= lambda a=id, b=cellname, c=label: self.cp_select_hcolour(a, b, c))
						self.contentdata[id][cellname].bind("<Button-1>", lambda a=id, b=cellname, c=label: self.cp_select_hcolour(a, b, c))

					for col in cols:
						if col not in ["Colour"]:
							show = self.base.report_item_get_bool_def1(id, self.base.rt_table_ini_colname(f"{col} Show"))
							if show:
								colnum += 1
								cellname = "{}_{}".format(i, col)
								self.base.debugmsg(9, "cellname:", cellname)
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=f" {str(row[col])} ", style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

	def cp_select_hcolour(self, id, cellname, label, *args):
		self.base.debugmsg(5, "args:", args)
		self.base.debugmsg(5, "id:", id, " cellname:", cellname, " label:", label)
		colour = self.base.named_colour(label)
		self.base.debugmsg(5, "colour:", colour)

		newcolour = tkac.askcolor(colour, title=f"Choose Colour for {label}")
		self.base.debugmsg(5, "newcolour:", newcolour)
		newcolourhx = newcolour[-1]
		self.base.debugmsg(5, "newcolourhx:", newcolourhx)
		if newcolourhx is not None:
			self.base.set_named_colour(label, newcolourhx)
			regen = threading.Thread(target=self.cp_regenerate_preview)
			regen.start()

	def cp_errors(self, id):
		self.base.debugmsg(5, "id:", id)
		showimages = self.base.rt_errors_get_images(id)
		self.base.debugmsg(5, "showimages:", showimages)
		grouprn = self.base.rt_errors_get_group_rn(id)
		self.base.debugmsg(5, "grouprn:", grouprn)
		groupet = self.base.rt_errors_get_group_et(id)
		self.base.debugmsg(5, "groupet:", groupet)

		lbl_Result = self.base.rt_errors_get_label(id, "lbl_Result")
		lbl_Test = self.base.rt_errors_get_label(id, "lbl_Test")
		lbl_Script = self.base.rt_errors_get_label(id, "lbl_Script")
		lbl_Error = self.base.rt_errors_get_label(id, "lbl_Error")
		lbl_Count = self.base.rt_errors_get_label(id, "lbl_Count")
		lbl_Screenshot = self.base.rt_errors_get_label(id, "lbl_Screenshot")
		lbl_NoScreenshot = self.base.rt_errors_get_label(id, "lbl_NoScreenshot")

		pctalike = 0.80
		self.base.debugmsg(5, "pctalike:", pctalike)

		self.base.rt_errors_get_data(id)
		if 'data' not in self.contentdata[id]:
			# edata = self.base.rt_errors_get_data(id)
			# self.contentdata[id]['data'] = edata
			self.contentdata[id]['data'] = {}

		self.base.debugmsg(5, "self.contentdata[", id, "]['data']:", self.contentdata[id]['data'])
		self.base.debugmsg(5, "self.base.reportdata[", id, "]:", self.base.reportdata[id])

		rownum = self.contentdata[id]["rownum"]
		self.contentdata[id]["lblSpacer"] = ttk.Label(self.contentdata[id]["Preview"], text="    ")
		self.contentdata[id]["lblSpacer"].grid(column=0, row=rownum, sticky="nsew")

		if grouprn or groupet:
			self.contentdata[id]["grpdata"] = {}
			self.contentdata[id]["grpdata"]["resultnames"] = {}
			self.contentdata[id]["grpdata"]["errortexts"] = {}

			keys = list(self.base.reportdata[id].keys())
			for key in keys:
				self.base.debugmsg(5, "key:", key)
				if key != "key":
					rdata = self.base.reportdata[id][key]

					if grouprn:
						result_name = rdata['result_name']
						matches = difflib.get_close_matches(result_name, list(self.contentdata[id]["grpdata"]["resultnames"].keys()), cutoff=pctalike)
						self.base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							result_name = matches[0]
							basekey = self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"][0]
							self.base.debugmsg(5, "basekey:", basekey)
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"].append(key)
						else:
							self.contentdata[id]["grpdata"]["resultnames"][result_name] = {}
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"] = []
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"].append(key)
							self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"] = {}

						if groupet and 'error' in rdata:
							errortext = rdata['error']
							# errortext_sub = errortext.split(r'\n')[0]
							errortext_sub = errortext.splitlines()[0]
							self.base.debugmsg(5, "errortext_sub:", errortext_sub)
							matcheset = difflib.get_close_matches(errortext_sub, list(self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"].keys()), cutoff=pctalike)
							self.base.debugmsg(5, "matcheset:", matcheset)
							if len(matcheset) > 0:
								errortext = matcheset[0]
								errortext_sub = errortext.splitlines()[0]
								self.base.debugmsg(5, "errortext:", errortext)
								baseid = self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"][0]
								self.base.debugmsg(5, "baseid:", baseid)
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)
							else:
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub] = {}
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"] = []
								self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext_sub]["keys"].append(key)

					if groupet and 'error' in rdata:
						errortext = rdata['error']
						errortext_sub = errortext.splitlines()[0]
						self.base.debugmsg(5, "errortext_sub:", errortext_sub)
						matches = difflib.get_close_matches(errortext_sub, list(self.contentdata[id]["grpdata"]["errortexts"].keys()), cutoff=pctalike)
						self.base.debugmsg(5, "matches:", matches)
						if len(matches) > 0:
							self.base.debugmsg(5, "errortext_sub:", errortext_sub)
							errortext = matches[0]
							self.base.debugmsg(5, "errortext:", errortext)
							baseid = self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"][0]
							self.base.debugmsg(5, "baseid:", baseid)
							self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"].append(key)
						else:
							self.base.debugmsg(5, "errortext_sub:", errortext_sub)
							self.contentdata[id]["grpdata"]["errortexts"][errortext_sub] = {}
							self.contentdata[id]["grpdata"]["errortexts"][errortext_sub]["keys"] = []
							self.contentdata[id]["grpdata"]["errortexts"][errortext_sub]["keys"].append(key)

			resultnames = self.contentdata[id]["grpdata"]["resultnames"]
			self.base.debugmsg(5, "resultnames:", resultnames)
			errortexts = self.contentdata[id]["grpdata"]["errortexts"]
			self.base.debugmsg(5, "errortexts:", errortexts)

		if grouprn:
			# self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"]
			for result_name in list(self.contentdata[id]["grpdata"]["resultnames"].keys()):
				basekey = self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"][0]
				self.base.debugmsg(5, "basekey:", basekey)
				rdata = self.base.reportdata[id][basekey]
				rownum += 1

				colnum = 0
				cellname = "{}_{}".format("result_name_lbl", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Result), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("result_name", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(result_name), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("test_name_lbl", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Test), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("test_name", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['test_name']), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("script_lbl", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Script), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("script", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['script']), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("count_lbl", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("countdisp", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				count = len(self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"])
				self.base.debugmsg(5, "count:", count)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				if groupet:
					# self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"]
					for errortext in list(self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"].keys()):
						basekey = self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"][0]
						self.base.debugmsg(5, "basekey:", basekey)
						rdata = self.base.reportdata[id][basekey]
						rownum += 1
						colnum = 0
						cellname = "{}_{}".format("error_lbl", basekey)
						self.base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("error", basekey)
						self.base.debugmsg(5, "cellname:", cellname)
						if 'error' in rdata:
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

						colnum += 5
						cellname = "{}_{}".format("ecount_lbl", basekey)
						self.base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Count), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("ecountdisp", basekey)
						self.base.debugmsg(5, "cellname:", cellname)
						count = len(self.contentdata[id]["grpdata"]["resultnames"][result_name]["errortexts"][errortext]["keys"])
						self.base.debugmsg(5, "count:", count)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(count), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						if showimages:
							rownum += 1
							colnum = 0
							cellname = "{}_{}".format("screenshot_lbl", basekey)
							self.base.debugmsg(5, "cellname:", cellname)
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

							colnum += 1
							cellname = "{}_{}".format("screenshot", basekey)
							cellimg = "{}_{}".format("image", basekey)
							self.base.debugmsg(5, "cellname:", cellname)
							if 'image_file' in rdata:
								self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)
							else:
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

				else:
					for keyi in self.contentdata[id]["grpdata"]["resultnames"][result_name]["keys"]:
						rdata = self.base.reportdata[id][keyi]

						rownum += 1
						colnum = 0
						cellname = "{}_{}".format("error_lbl", keyi)
						self.base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("error", keyi)
						self.base.debugmsg(5, "cellname:", cellname)
						if 'error' in rdata:
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

						if showimages:
							rownum += 1
							colnum = 0
							cellname = "{}_{}".format("screenshot_lbl", keyi)
							self.base.debugmsg(5, "cellname:", cellname)
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

							colnum += 1
							cellname = "{}_{}".format("screenshot", keyi)
							cellimg = "{}_{}".format("image", keyi)
							self.base.debugmsg(5, "cellname:", cellname)
							if 'image_file' in rdata:
								self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)
							else:
								self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
								self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

		if groupet and not grouprn:

			# baseid = self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"][0]
			for errortext in list(self.contentdata[id]["grpdata"]["errortexts"].keys()):
				basekey = self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"][0]
				self.base.debugmsg(5, "basekey:", basekey)
				rdata = self.base.reportdata[id][basekey]
				rownum += 1
				colnum = 0
				cellname = "{}_{}".format("error_lbl", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("error", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				if 'error' in rdata:
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

				colnum += 5
				cellname = "{}_{}".format("ecount_lbl", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				colnum += 1
				cellname = "{}_{}".format("ecountdisp", basekey)
				self.base.debugmsg(5, "cellname:", cellname)
				count = len(self.contentdata[id]["grpdata"]["errortexts"][errortext]["keys"])
				self.base.debugmsg(5, "count:", count)
				self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(count), style='Report.TBody.TLabel')
				self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

				if showimages:
					rownum += 1
					colnum = 0
					cellname = "{}_{}".format("screenshot_lbl", basekey)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("screenshot", basekey)
					cellimg = "{}_{}".format("image", basekey)
					self.base.debugmsg(5, "cellname:", cellname)
					if 'image_file' in rdata:
						self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)
					else:
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=7)

		if not grouprn and not groupet:
			i = 0
			keys = list(self.base.reportdata[id].keys())
			for key in keys:
				self.base.debugmsg(5, "key:", key)
				if key != "key":
					i += 1
					rownum += 1
					rdata = self.base.reportdata[id][key]

					colnum = 0
					cellname = "{}_{}".format("lbl_result_name", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Result), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("result_name", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['result_name']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("lbl_test_name", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Test), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("test_name", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['test_name']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("lbl_script", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Script), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("script", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['script']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					rownum += 1
					colnum = 0
					cellname = "{}_{}".format("lbl_error", key)
					self.base.debugmsg(5, "cellname:", cellname)
					self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Error), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

					colnum += 1
					cellname = "{}_{}".format("error", key)
					self.base.debugmsg(5, "cellname:", cellname)
					if 'error' in rdata:
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text=str(rdata['error']), style='Report.TBody.TLabel')
					self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

					if showimages:
						rownum += 1
						colnum = 0
						cellname = "{}_{}".format("lbl_image", key)
						self.base.debugmsg(5, "cellname:", cellname)
						self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}:".format(lbl_Screenshot), style='Report.TBody.TLabel')
						self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew")

						colnum += 1
						cellname = "{}_{}".format("image_file", key)
						cellimg = "{}_{}".format("image", key)
						self.base.debugmsg(5, "cellname:", cellname)
						if 'image_file' in rdata:
							self.contentdata[id][cellimg] = tk.PhotoImage(file=rdata['image_file'])
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], image=self.contentdata[id][cellimg], style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)
						else:
							self.contentdata[id][cellname] = ttk.Label(self.contentdata[id]["Preview"], text="{}".format(lbl_NoScreenshot), style='Report.TBody.TLabel')
							self.contentdata[id][cellname].grid(column=colnum, row=rownum, sticky="nsew", columnspan=5)

	#
	# Export content generation functions
	#

	def cg_export_xhtml(self):
		# self.base.debugmsg(5, "Not implimented yet.....")
		self.base.core.export_xhtml()

	def cg_export_pdf(self):
		self.base.debugmsg(5, "Not implimented yet.....")
		self.base.core.export_pdf()

	def cg_export_writer(self):
		self.base.debugmsg(5, "Not implimented yet.....")
		self.base.core.export_writer()

	def cg_export_word(self):
		# self.base.debugmsg(5, "Not implimented yet.....")
		self.base.core.export_word()

	def cg_export_calc(self):
		self.base.debugmsg(5, "Not implimented yet.....")
		self.base.core.export_calc()

	def cg_export_excel(self):
		self.base.debugmsg(5, "Not implimented yet.....")
		self.base.core.export_excel()

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	#
	# menu functions
	#
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def mnu_do_nothing(self, _event=None):
		self.base.debugmsg(5, "Not implimented yet.....")

	def mnu_results_Open(self, _event=None):
		self.base.debugmsg(9, "mnu_file_Open: _event:", _event, "	Type:", type(_event))

		# E721 do not compare types, use 'isinstance()'
		# if type(_event) is not type(""):
		if not isinstance(_event, str):
			# self.mnu_file_Close()	# ensure any previous scenario is closed and saved if required
			ResultsFile = str(
				tkf.askopenfilename(
					initialdir=self.base.config['Reporter']['ResultDir'],
					title="Select RFSwarm Results File",
					filetypes=(("RFSwarm Results", "*.db"), ("all files", "*.*"))
				)
			)
		else:
			ResultsFile = _event

		self.base.debugmsg(5, "ResultsFile:", ResultsFile)

		# ['Reporter']['Results']
		if len(ResultsFile) > 0:

			self.base.report = None
			self.contentdata = {}
			self.base.core.selectResults(ResultsFile)
			self.base.report_open()
			self.updateTitle()
			self.updateResults()
			self.base.debugmsg(5, "LoadSections")
			selected = self.sectionstree.focus()
			self.base.debugmsg(5, "selected:", selected)
			if len(selected) > 0:
				self.LoadSections(selected)
			else:
				self.LoadSections("TOP")
			self.base.debugmsg(5, "content_load")
			selected = self.sectionstree.focus()
			self.base.debugmsg(5, "selected:", selected)
			if len(selected) > 0:
				self.content_load(selected)
			else:
				self.content_load("TOP")

	def mnu_template_New(self, _event=None):
		self.base.debugmsg(5, "New Report Template")

		self.base.template_create()

		self.LoadSections("TOP")

		self.updateTemplate()

	def mnu_template_Open(self, _event=None):
		TemplateFile = str(
			tkf.askopenfilename(
				initialdir=self.base.config['Reporter']['TemplateDir'],
				title="Select RFSwarm Reporter Template",
				filetypes=(("RFSwarm Reporter Template", "*.template"), ("Yaml", "*.yml"), ("Yaml", "*.yaml"), ("JSON", "*.json"), ("all files", "*.*"))
			)
		)
		self.base.debugmsg(5, "TemplateFile:", TemplateFile)

		# ['Reporter']['Results']
		if len(TemplateFile) > 0:
			self.base.report = None
			self.contentdata = {}
			self.base.debugmsg(5, "template_open TemplateFile:", TemplateFile)
			self.base.template_open(TemplateFile)
			self.base.debugmsg(5, "report_save")
			self.base.report_save()
			self.base.debugmsg(5, "ConfigureStyle")
			self.ConfigureStyle()
			self.base.debugmsg(5, "LoadSections")
			selected = self.sectionstree.focus()
			self.base.debugmsg(5, "selected:", selected)
			self.LoadSections("TOP")
			self.base.debugmsg(5, "content_load")
			self.base.debugmsg(5, "selected:", selected)
			self.content_load("TOP")
			self.base.debugmsg(5, "updateTemplate")
			self.updateTemplate()
			# self.base.debugmsg(5, "cp_regenerate_preview")
			# self.cp_regenerate_preview()
			self.base.debugmsg(5, "done")

	def mnu_template_Save(self, _event=None):
		# self.base.debugmsg(5, "Not implimented yet.....")
		templatefile = self.base.whitespace_get_ini_value(self.base.config['Reporter']['Template'])
		self.base.debugmsg(5, "Filename:", templatefile)
		if len(templatefile) > 0:
			self.base.template_save(templatefile)
			self.updateTemplate()
		else:
			self.mnu_template_SaveAs()

	def mnu_template_SaveAs(self, _event=None):
		self.base.debugmsg(5, "Prompt for filename")
		templatefile = str(
			tkf.asksaveasfilename(
				initialdir=self.base.config['Reporter']['TemplateDir'],
				title="Save RFSwarm Reporter Template",
				filetypes=(("RFSwarm Reporter Template", "*.template"), ("Yaml", "*.yml"), ("Yaml", "*.yaml"), ("JSON", "*.json"), ("all files", "*.*")),
				defaultextension=".template"
			)
		)
		self.base.debugmsg(5, "templatefile", templatefile)
		self.base.template_save(templatefile)
		self.updateTemplate()

	def mnu_new_rpt_sect(self):
		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)
		name = tksd.askstring(title="New Section", prompt="Section Name:")
		# , bg=self.style_feild_colour	, background='green'
		if name is not None and len(name) > 0:
			if selected is None or len(selected) < 1:
				selected = "TOP"
			id = self.base.report_new_section(selected, name)
			self.LoadSection(selected, id)

	def mnu_rem_rpt_sect(self):
		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)
		if selected:
			self.base.debugmsg(5, "Removing:", self.base.whitespace_get_ini_value(self.base.report[selected]["Name"]))
			self.base.report_remove_section(selected)
			parent = self.base.report_item_parent(selected)
			self.LoadSections(parent)

	def mnu_rpt_sect_up(self):
		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)
		if selected:
			self.base.debugmsg(5, "Moving", self.base.whitespace_get_ini_value(self.base.report[selected]["Name"]), "up")
			self.base.report_move_section_up(selected)
			parent = self.base.report_item_parent(selected)
			self.LoadSections(parent)
			self.sectionstree.selection_set(selected)
			self.sectionstree.focus(selected)

	def mnu_rpt_sect_down(self):
		selected = self.sectionstree.focus()
		self.base.debugmsg(5, "selected:", selected)
		if selected:
			self.base.debugmsg(5, "Moving", self.base.whitespace_get_ini_value(self.base.report[selected]["Name"]), "down")
			self.base.report_move_section_down(selected)
			parent = self.base.report_item_parent(selected)
			self.LoadSections(parent)
			self.sectionstree.selection_set(selected)
			self.sectionstree.focus(selected)

	def mnu_content_settings(self):
		self.base.debugmsg(5, "Not implimented yet.....")
		# self.button0.config(state=tk.DISABLED)
		# self.cbbar.bprev.config(state=tk.NORMAL)
		# self.cbbar.bsett.config(state=tk.ACTIVE)
		# self.cbbar.bprev.config(relief=tk.RAISED)
		# self.cbbar.bsett.config(relief=tk.FLAT)

	def mnu_content_preview(self):
		self.base.debugmsg(5, "Not implimented yet.....")
		# self.cbbar.bprev.config(relief=tk.FLAT)
		# self.cbbar.bsett.config(relief=tk.RAISED)
		# self.cbbar.bprev.config(state=tk.ACTIVE)
		# self.cbbar.bsett.config(state=tk.NORMAL)

	# Export Functions
	def mnu_export_html(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		cghtml = threading.Thread(target=self.cg_export_xhtml)
		cghtml.start()

	def mnu_export_pdf(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		cgpdf = threading.Thread(target=self.cg_export_pdf)
		cgpdf.start()

	def mnu_export_writer(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		cgwriter = threading.Thread(target=self.cg_export_writer)
		cgwriter.start()

	def mnu_export_word(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		cgword = threading.Thread(target=self.cg_export_word)
		cgword.start()

	def mnu_export_calc(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		cgcalc = threading.Thread(target=self.cg_export_calc)
		cgcalc.start()

	def mnu_export_excel(self, _event=None):
		self.base.debugmsg(5, "_event:", _event)
		cgxcel = threading.Thread(target=self.cg_export_excel)
		cgxcel.start()
