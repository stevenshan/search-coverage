import unreal_engine as ue

from PythonClient.AirSimClient import *
import re
import sys
import time

# remember Airsim uses reversed z-axis so -100 is 100 units up
DEFAULT_SPEED = 15
DEFAULT_TIMEOUT = 60

# predeclare commands variable
commands = {}

# global parameters
global_parameters = {
	"logging": True,
	"started": False,
	"client": None
}

'''
Begin Available Commands
'''

def _help (params):
	return str([x for x in commands])

def _print (params):
	ue.print_string(params["mesg"])

def _toggle_log (params):
	if params["value"] == "on":
		global_parameters["logging"] = True
	elif params["value"] == "off":
		global_parameters["logging"] = False 
	return "Logging is " + ("on" if global_parameters["logging"] else "off")

def _status (params):
	return "Started" if global_parameters["started"] else "Not Started"

def _init (params):
	global_parameters["client"] = MultirotorClient()
	global_parameters["started"] = False

def _getPosition (params):
	# get position vector
	pos_vector = global_parameters["client"].getPosition()

	# return each component of position
	return "{0:.3f}".format(pos_vector.x_val) + "," + \
		   "{0:.3f}".format(pos_vector.y_val) + "," + \
		   "{0:.3f}".format(pos_vector.z_val)

def _start (params):
	try:
		global_parameters["client"].reset()
	except msgpackrpc.error.TransportError:
		return "Error: Not connected"

	global_parameters["client"].confirmConnection()
	global_parameters["client"].enableApiControl(True)
	global_parameters["client"].armDisarm(True)

	global_parameters["client"].takeoff()

	position = global_parameters["client"].getPosition()

	global_parameters["started"] = True

	z = params["z"]

	# move up/down to z position
	return global_parameters["client"]. \
				moveToPosition(position.x_val, position.y_val, z, \
                       		   DEFAULT_SPEED, DEFAULT_TIMEOUT, \
                       		   DrivetrainType.MaxDegreeOfFreedom, \
                       		   YawMode(False,0), -1, 0)

# flies quadcopter in 2d plane at specified height (default 100)
# takes vectors as list of coordinates (x, y)
def _moveOnPath (params):
	if not global_parameters["started"]: return "Error: Not started"

	# construct list of vector objects for position
	path = []
	for vector in vectors:
		path.append(Vector3r(vector[0] - params["offset"][0],  \
							 vector[1] - params["offset"][1], params["z"]))

	return global_parameters["client"]. \
				moveOnPath(path, params["speed"], params["timeout"], \
						   DrivetrainType.MaxDegreeOfFreedom, \
						   YawMode(False, 0), -1, 0)

'''
End Available Commands
'''

# dictionary of available commands
commands = {
	"help": [_help, [], {}],
	"print": [_print, ["mesg"], {}],
	"log": [_toggle_log, ["value"], {"value": ""}],
	"status": [_status, [], {}],
	"init": [_init, [], {}],
	"start": [_start, ["z"], {"z": -100}],
	"getPosition": [_getPosition, [], {}],
	"moveOnPath": [_moveOnPath, ["vectors", "offset", "speed", "z", "timeout"], \
				   {"z": -100, "offset": (0, 0), \
				   	"speed": DEFAULT_SPEED, "timeout": DEFAULT_TIMEOUT}]
}

def connect_mesg (mesg):
    ue.print_string(mesg)

def disconnect_mesg (mesg):
    ue.print_string(mesg)

def log_mesg (mesg):
	if global_parameters["logging"]:
	    ue.print_string(mesg)

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
		ue.print_string(e)
		return "Error: fsdfsdfcommand could not be executed"
