import os
import time
import datetime

# global variables to be used across modules
# default values to be changed by simulation.py
sim_name = "sim"
sim_directory = "Logs/"
sim_trajectory_log = "Logs/test.log"
sim_log = "Logs/test.log"
sim_start_time = "" 
sim_end_time = ""

def setup():
    timestamp = time.time()
    time_string = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    sim_name = str(int(timestamp))
    sim_directory = "Logs/" + sim_name + "/"
    sim_trajectory_log = sim_directory + "trajectories.log"
    sim_log = sim_directory + "simulation.log"
    sim_start_time = time_string
    sim_end_time = time_string

    if not os.path.exists(sim_directory):
        os.makedirs(sim_directory)
    else:
        raise ValueError("Simulation directory already exists.")

    write_log()

def write_log():
    file = open(sim_log, "w")
    file.write("Name: " + sim_name)
    file.write("Directory: " + sim_directory)
    file.write("Log location: " + sim_log)
    file.write("Trajectory log: " + sim_trajectory_log)
    file.write("Start time: " + sim_start_time)
    file.write("End time: " + sim_end_time)
