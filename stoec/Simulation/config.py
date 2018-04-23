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
sim_xrange = (None, None)
sim_yrange = (None, None)
sim_pdf_location = "Logs/pdf.bmp"
sim_images_dir = "Logs/Images"

def setup(xrange = (None, None), yrange = (None, None)):
    global sim_name, sim_directory, sim_trajectory_log, sim_log, \
           sim_pdf_location, sim_start_time, sim_end_time, \
           sim_xrange, sim_yrange, sim_images_dir

    timestamp = time.time()
    time_string = datetime.datetime.fromtimestamp(timestamp) \
        .strftime('%Y-%m-%d %H:%M:%S')

    sim_name = str(int(timestamp))
    sim_directory = "Logs/" + sim_name + "/"
    sim_trajectory_log = sim_directory + "trajectories.log"
    sim_log = sim_directory + "simulation.log"
    sim_images_dir = sim_directory + "Images/"
    sim_start_time = time_string
    sim_end_time = time_string
    sim_xrange = xrange
    sim_yrange = yrange
    sim_pdf_location = sim_directory + "probability_map.bmp"

    if not os.path.exists(sim_directory):
        os.makedirs(sim_directory)
    else:
        raise ValueError("Simulation directory already exists.")

    if not os.path.exists(sim_images_dir):
        os.makedirs(sim_images_dir)
    else:
        raise ValueError("Simulation directory already exists.")

    write_log()

def get_pdf_location():
    global sim_pdf_location
    return sim_pdf_location

def get_image_dir():
    global sim_images_dir
    return sim_images_dir

def write_log():
    global sim_name, sim_directory, sim_trajectory_log, sim_log, \
           sim_start_time, sim_end_time, sim_xrange, sim_yrange

    print("write")
    timestamp = time.time()
    time_string = datetime.datetime.fromtimestamp(timestamp) \
        .strftime('%Y-%m-%d %H:%M:%S')
    sim_end_time = time_string

    file = open(sim_log, "w")
    file.write("Name: " + sim_name + "\n")
    file.write("Directory: " + sim_directory + "\n")
    file.write("Log location: " + sim_log + "\n")
    file.write("Trajectory log: " + sim_trajectory_log + "\n")
    file.write("X-Range: " + str(sim_xrange) + "\n")
    file.write("Y-Range: " + str(sim_yrange) + "\n")
    file.write("Start time: " + sim_start_time + "\n")
    file.write("End time: " + sim_end_time + "\n")
    file.close()

def write_trajectory(path):
    global sim_trajectory_log 

    to_str = lambda x: str(x[0]) + "," + str(x[1])

    file = open(sim_trajectory_log, "a")
    for point in path:
        file.write(to_str(point) + "\n")
    file.close()

