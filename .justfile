set shell := ["bash", "-uc"]

bold    := '\033[1m'
normal  := '\033[0m'
green   := "\\e[32m"
yellow  := "\\e[33m"
blue    := "\\e[34m"
magenta := "\\e[35m"
grey    := "\\e[90m"

default:
  @just --list

act:
  source dmenv/bin/activate

setup01:
  virtualenv dmenv

setup02: act
  python -m pip install numpy dataclasses-json scipy solidpython cadquery gitpython

run: act
  python src/dactyl_manuform.py

stl:
  #!/usr/bin/env sh
  for file in `ls things/*.scad`; do
    @openscad $file -o $file.stl
  done
