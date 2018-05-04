# Search Coverage

Biorobotics Lab work. Working on demonstrating trajectory planning with goal of optimizing ergodicity, or the coverage of areas proportional to a probability density function. Simulation is done using Unreal Engine 4 with the Microsoft AirSim plugin. The trajectory planning communicates with the simulation over a socket connection, meaning that although this is mainly implemented in Python, it is possible to get it to work with other languages.

Here is a video of the simulation:

[![Simulation](https://img.youtube.com/vi/ij7dZU_yoRI/0.jpg)](https://www.youtube.com/watch?v=ij7dZU_yoRI)

## Installation

Most of the work on this project has been done in Windows 10 because it has better Unreal Engine support (there is no Epic Games Launcher for Linux so you can't download environments from Unreal Marketplace on Linux) and AirSim was originally designed for Windows. However, all of the code should be able to work on Ubuntu with a little effort and Unreal Marketplace environments can be downloaded from a Windows machine and copied to Linux. **Note:** In order to have access to the Unreal Engine source code, you need to register your Github account with Epic Games.

### Windows 10

1. Follow the instructions to build Unreal Engine, Airsim, and Unreal Engine Python. Unreal Engine has to be built from source instead of downloaded using the Epic Games Launcher in order to get the right click context menu with the project build tool. 
2. Make sure Python is in the system environment path and include the path to your Python installation in `UnrealEnginePython/Source/UnrealEnginePython/UnrealEnginePython.Build.cs`.

### Ubuntu 16.04

These instructions may be out of date since I haven't tried using this on Ubuntu in a while.

1. Clone this repository somewhere
   ```bash
   git clone https://github.com/stevenshan/search-coverage.git
   ```
2. Clone Unreal Engine source from [https://github.com/EpicGames/UnrealEngine](https://github.com/EpicGames/UnrealEngine) to another location it doesn't matter where. **Note:** You will only have access to this if you are register with Epic Games (check prereq).
   ```bash
   # go to the folder where you clone GitHub projects
   git clone -b 4.17 git@github.com:EpicGames/UnrealEngine.git
   cd UnrealEngine
   # the Unreal build was broken a few times so we will get the commit that works
   git checkout af96417313a908b20621a443175ba91683c238c8
   ```
3. Run the file `setup_unreal_install.sh` from this repository (in the `setup` folder) with the path to the Unreal Engine repository. This will replace several setup files in Unreal Engine so that `clang-3.5` is installed, which is necessary for the Python interface that is used.
4. Build Unreal Engine. Go to the Unreal Engine folder:
   ```bash
   ./Setup.sh
   ./GenerateProjectFiles.sh
   make
   ```
5. Clone AirSim and build it:
   ```bash
   # go to the folder where you clone GitHub projects
   git clone https://github.com/Microsoft/AirSim.git
   cd AirSim
   ./setup.sh
   ./build.sh
   ```
6. Clone and build UnrealEnginePython Plugin. Make an empty C++ project in Unreal Editor. Go to the project folder and make a new folder called `Plugins`.
   ```bash
   sudo apt-get install python3.6-dev
   git clone https://github.com/20tab/UnrealEnginePython
   ```
   Open the project in Unreal Editor and it should say modules are missing and offer to rebuild, click rebuild.

### Possible Problems

1. **Pop-up from Unreal Engine saying plugin is for different engine version**: The correct UE4 version should be 4.17. If this is correct, then press `no` to ignore the warning.
2. **Pop-up from Unreal Engine at around 73% load saying plugin could not be loaded because module was not found**: This means the plugins were not built. If the error is about AirSim, you can try copying the `Plugins/AirSim` folder from the Blocks environment or `Unreal/Plugins/Airsim` folder of Airsim. On Linux, you can also try modifying the `*.uproject` file to remove the modules entry with the key `AdditionalDependencies`. If the error is about UnrealEnginePython, follow the steps to rebuild the plugin. The plugin cannot be built from a non-empty project folder for some reason.
3. **UnrealEnginePython Plugin fails to build**: I have only gotten it to build when in a completely empty C++ Unreal project so make sure the project is empty. Also the Python dev version needs to be installed.
   ```bash
   sudo apt-get install python3.6-dev
   ```
   Note sure if this works for anything other than Python 3.6

## How to Setup Simulation

1. Follow the instructions in Airsim's docs to setup a new environment. The environment in the documentation is a Mountain Landscape environment from the Unreal Marketplace.
2. In the `Plugins` folder in the project directory, copy and paste the Unreal Engine Python plugin that was built in the Installation instructions.
3. At this point, the project should at least play in the default fly-around gamemode in Unreal Editor. On Windows, the project is run by opening the Visual Studio solution in the project directory and beginning debugging. This will open Unreal Editor in a new window.
4. Copy the contents of the `search-coverage/setup/Scripts` directory from this repository into `Content/Scripts` directory in the project directory.
5. Make a new folder in the `Contents` folder in the project directory called whatever you want and copy the Unreal Blueprints in `search-coverage/setup/STOEC` into it.
6. This should complete the installation. To run it, open the project in Unreal Editor by debugging the Visual Studio solution and click the play button to run the level in the current viewport. Then, separately run `search-coverage/stoec/main.py`, which should start the simulation and begin displaying trajectories in the game in Unreal Editor.

## Code Layout

### Backend Simulation

This is mostly contained in the directory `search-coverage/stoec` and is the part that is responsible for calculating the planned trajectory for the quadcopter.

- The folder `Simulation` contains the code that communicates between instructions from the backend like trajectories and plots to display to the Unreal simulation. The file `simulation.py` contains the interface used to do so. The file `airsim_client.py` contains the code that communicates with Airsim to control the path of the quadcopter. To fix the problem of the quadcopter's path glitching when there are no new coordinates to travel to, a queue is used so that new paths can be calculated asynchronously so that there are always new instructions. There is also a script called `image_unmask.py` that was used to make it easier to generate images containing the probability density functions. This is used by taking a screenshot of the top-down view of the simulation and drawing using the color (44, 2, 122) over it to mark the areas of interest. The script then takes the image and extracts the areas with this color.

### UnrealEngine Python Scripts

There are several Python scripts that are run by Unreal Engine during the simulation that are used control the downward camera view, the trace of the quadcopter's path, and displaying all of the mini-windows in the simulation

- `Pixel_Image.py` contains class definitions used for image manipulations by the other scripts
- `trace.py` contains everything that is used to interact with objects in the simulation world. This includes tracking the quadcopter and tracing it's path, and moving the camera that shows the downward view from the quadcopter.
- `main.py` contains the server socket that listens for commands from the backend such as drawing a plot or getting the orthographic width of the camera. New commands can also be added in this file. This file is long because there was some caching going on with Unreal Engine Python so only changes in this file had any effect.
- `ue_site.py` only exists as a placeholder because Unreal Engine Python requires it

### UnrealEngine Blueprints

These are Blueprints for Unreal Engine to enable the functionality of the Python scripts.

- `Texture` blueprints are used as an output target for the cameras in the simulation
- `Material` blueprints are linked to `Texture`s to allow them to be displayed in the `Widget` (user interface) 
- `MaterialInstance` blueprints are similar to `Material` blueprints but their texture can be changed by the Python script. These are used to display the plots.
- `Widget` blueprint is the user interface that holds the images that display the plots and trace of the path
- several `Actor` blueprints are used to manipulate cameras like the top-down view of the scene and the downward camera from the quadcopter. The `stoec_actor.uasset` blueprint has the Python component that runs `trace.py`
- `stoec.uasset` is a gamemode blueprint that extends the Airsim gamemode and has the Python component running `main.py`
