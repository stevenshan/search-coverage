#!/bin/bash

# Script to change setup of UnrealEngine source so that clang-3.5 is used
# https://answerse.unrealengine.com/questions/357404/linux-specify-clang-version.html

trap "exit 1" TERM
export TOP_PID=$$

# first argument should be path to cloned Unreal Engine source
if [ -z "$1" ]; then
	echo "Need path to Unreal Engine source"
	exit
fi

# make sure the directory exists
check_dir () {
	if [ ! -d "$1" ]; then
		echo "Invalid path given: ${1}"
		kill -s TERM $TOP_PID
	fi
}

target="${1%/}/Engine/"

check_dir $target

targetone="${target}Build/BatchFiles/Linux/"
targettwo="${target}Source/Programs/UnrealBuildTool/Linux"
check_dir $targetone
check_dir $targettwo

# move modified setup files to Unreal folder

# replace all instances of clang-3.* to clang-3.5
mv setup/UnrealEngine/Setup.sh $targetone

# change CLANG_TO_USE=`which clang` to CLANG_TO_USE=`clang-3.5`
mv setup/UnrealEngine/BuildThirdParty.sh $targetone

# force use of clang-3.5
mv setup/UnrealEngine/LinuxToolChain.cs $targettwo
