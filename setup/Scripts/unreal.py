import re
import unreal_engine as ue

def connect_mesg (mesg):
    ue.print_string(mesg)

def disconnect_mesg (mesg):
    ue.print_string(mesg)

def log_mesg (mesg):
    ue.print_string(mesg)

# predeclare commands variable
commands = {}

# try to match labels with params
def format_params(labels, defaults, params):
	final_params = {}
	for i in range(1, len(params)):
		if params[i][1] != "":
			if params[i][0] in labels:
				final_params[params[i][0]] = params[i][1]
			else:
				raise ValueError("Error: unknown key '" + params[i][0] + "'")

	i = 1 
	for j in range(len(labels)):
		key = labels[j]
		if key not in final_params:
			param = None
			while i < len(params) and params[i][1] != "":
				i += 1
			if i < len(params):
				param = params[i][0]
				i += 1
			elif key in defaults:
				param = defaults[key]
			else:
				raise ValueError("Error: not enough parameters supplied")
			final_params[key] = param

	return final_params

'''
Begin Available Commands
'''

def _list (params):
	return str([x for x in commands])

def _print(params):
	ue.print_string(params["mesg"])

'''
End Available Commands
'''

# dictionary of available commands
commands = {
	"list": [_list, [], {}],
	"print": [_print, ["mesg"], {}]
}

def send_command (mesg):
	# split mesg into comamand and parameters
	try:
		params = re.findall("(\"([^\"]*)\"|([^ =]+)[=]?\"([^\"]*)\"|([^ =]+)[=]?([^ ]*))", 
							mesg.replace("\n", ""))
		for i in range(len(params)):
			param = params[i]
			if param[-1] == "" and param[-2] == "":
				if param[-3] == "":
					params[i] = (param[1], "")
				else:
					params[i] = (param[2], param[3])
			elif param[-1] == "":
				params[i] = (param[-2], "")
			else:
				params[i] = (param[-2], param[-1])
	except:
		return "Error: couldn't properly regex command message"

	# make sure params is not zero length and first parameter is singleton
	if len(params) == 0 or params[0][1] != "":
		return "Error: improperly formatted command"
	elif params[0][0] not in commands:
		return "Error: command '" + params[0][0] + "' does not exist"

	# try to run the command with the parameters
	try:
		# format commands
		command = commands[params[0][0]]
		formatted_params = format_params(command[1], command[2], params)

		return command[0](formatted_params)
	except ValueError as e:
		return str(e)
	except Exception as e:
		print(e)
		return "Error: command could not be executed"
