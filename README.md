# Search Coverage

Biorobotics Lab work. Working on demonstrating trajectory planning with goal of optimizing ergodicity, or the coverage of areas proportional to a probability density function. Visualization is done using Unreal Engine 4 with the Microsoft AirSim plugin. The trajectory planning communicates with the simulation using a Python interface.

## Installation

At the moment, this has only been tested on Ubuntu 16.04. It is likely to work on Ubuntu 14 but this has not been tested.

### Ubuntu 16.04

#### Prerequisites

Register an account with Epic Games in order to get access to Unreal Engine Github repo with source code.

#### Installing

1. Clone this repository somewhere
   ```bash
   git clone https://github.com/stevenshan/search-coverage.git
   ```
2. Clone Unreal Engine source from [https://github.com/EpicGames/UnrealEngine](https://github.com/EpicGames/UnrealEngine) to another location it doesn't matter where. **Note:** You will only have access to this if you are register with Epic Games (check prereq)
   ```bash
   # go to the folder where you clone GitHub projects
   git clone -b 4.17 git@github.com:EpicGames/UnrealEngine.git
   cd UnrealEngine
   # the Unreal build was broken a few times so we will get the commit that works
   git checkout af96417313a908b20621a443175ba91683c238c8
   ```
3. Run the file `setup.sh` from this repository with the path to the Unreal Engine repository. This will replace several setup files in Unreal Engine so that `clang-3.5` is installed, which is necessary for the Python interface that is used.
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
   git clone https://github.com/20tab/UnrealEnginePython
   ```
   Open the project in Unreal Editor and it should say modules are missing and offer to rebuild, click rebuild.

## Known Problems

1. **Pop-up from Unreal Engine saying plugin is for different engine version**: The correct UE4 version should be 4.17. If this is correct, then press `no` to ignore the warning.
2. **Pop-up from Unreal Engine at around 73% load saying plugin could not be loaded because module was not found**: This means the plugins were not built. If the error is about AirSim, you can try copying the `Plugins/AirSim` folder from the Blocks environment or `Unreal/Plugins/Airsim` folder of Airsim. On Linux, you can also try modifying the `*.uproject` file to remove the modules entry with the key `AdditionalDependencies`. If the error is about UnrealEnginePython, follow the steps to rebuild the plugin. The plugin cannot be built from a non-empty project folder for some reason.
