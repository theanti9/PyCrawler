import curses

class Printer():

	def __init__(self, USE_COLORS):
		# Define our types
		self.success = 0;
		self.error = 1;
		self.other = 2;

		self.USE_COLORS = USE_COLORS

		# Initialize environment
		curses.setupterm()

		# Get the foreground color attribute for this environment
		self.fcap = curses.tigetstr('setaf')

		#Get the normal attribute
		self.COLOR_NORMAL = curses.tigetstr('sgr0')

		# Get + Save the color sequences
		self.COLOR_SUCCESS = curses.tparm(self.fcap, curses.COLOR_GREEN)
		self.COLOR_ERROR = curses.tparm(self.fcap, curses.COLOR_RED)
		self.COLOR_OTHER = curses.tparm(self.fcap, curses.COLOR_YELLOW)

	def p(self, text, type):
		if self.USE_COLORS:
			if type == self.success:
				print "%s[*] %s%s" % (self.COLOR_SUCCESS, text, self.COLOR_NORMAL)
			elif type == self.error:
				print "%s[!] %s%s" % (self.COLOR_ERROR, text, self.COLOR_NORMAL)
			elif type == self.other:
				print "%s[.] %s%s" % (self.COLOR_OTHER, text, self.COLOR_NORMAL)
		else:
			print text