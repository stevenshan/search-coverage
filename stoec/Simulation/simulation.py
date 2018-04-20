import time

import airsim_simulation
import airsim_client
from stoec_utilities import Utilities

# run simulation with connecting to Airsim
HEADLESS = False

class Simulation:
    # call before beginning of loop finding new trajectories
    def __init__(self, utility, xrange, yrange):
        self.xmin, self.xmax = xrange
        self.ymin, self.ymax = yrange
        self.xrange = xrange
        self.yrange = yrange

        # generate utility map image
        self.utilities = Utilities()
        utilityRGB = self.utilities.getUtilityRGB(utility)
        self.utilities.displayImage(utilityRGB)

        if not HEADLESS:
            # connect to simulation (note: x100 scale for Airsim NED coordinates)
            self.simulation = airsim_simulation.AirsimSimulation() 
            sim_width = self.simulation.getOrthoWidth()

            sim_scale = (sim_width / ((self.xmax - self.xmin) * 100.0)), \
                        (sim_width / ((self.ymax - self.ymin) * 100.0))
            
            # display probability density
            self.simulation.displayPDF(utilityRGB)

            # initialize Airsim setup
            self.airsim = airsim_client.Multirotor(sim_scale)
            self.airsim.start()

    # call at beginning of loop finding new trajectories
    def wait(self):
        if not HEADLESS and self.airsim != None:
            while (self.airsim.getQueueLength() > 700):
                    time.sleep(0.2)

    def trajectory(self, trajectory):
        self.utilities.updateTrajectoryRGB(trajectory, self.xrange, self.yrange)
        if not HEADLESS:
            self.airsim.moveOnPath(trajectory, \
                ((self.xmax - self.xmin) / 2.0, (self.ymax - self.ymin) / 2.0))

    def displayPlot(self, fig):
        if not HEADLESS:
            self.simulation.displayPlot(fig)

    def updatePlot(self):
        if not HEADLESS:
            rgba = self.utilities.getTrajectoryRGB()
            self.simulation.displayPlot(rgba)
