import curses

class Printer():

	def __init__(self, COLOR_SUCCESS, COLOR_ERROR):
		# Define our types
		self.success = 0;
		self.error = 1;

		# Initialize environment
		curses.setupterm()

		# Get the foreground color attribute for this environment
		self.fcap = curses.tigetstr('setaf')

		#Get the normal attribute
		self.COLOR_NORMAL = curses.tigetstr('sgr0')

		# Initialize custom colors to the first two slots
		curses.initscr()
		curses.start_color()
		curses.init_color(0, COLOR_SUCCESS[0], COLOR_SUCCESS[1], COLOR_SUCCESS[2])
		curses.init_color(1, COLOR_ERROR[0], COLOR_ERROR[1], COLOR_ERROR[2])
		curses.endwin()

		# Get + Save the color sequences
		self.COLOR_SUCCESS = curses.tparm(self.fcap, 0)
		self.COLOR_ERROR = curses.tparm(self.fcap, 1)

	def p(self, text, type):
		if type == self.success:
			print "%s%s%s" % (self.COLOR_SUCCESS, text, self.COLOR_NORMAL)
		elif type == self.error:
			print "%s%s%s" % (self.COLOR_SUCCESS, text, self.COLOR_NORMAL)