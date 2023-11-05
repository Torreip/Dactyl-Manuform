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
  ./dmenv/bin/python -m pip install numpy dataclasses-json scipy solidpython cadquery gitpython

clean:
  rm -rf ./things/*

run: clean act
  cd src && ./../dmenv/bin/python generate_configuration.py
  ./dmenv/bin/python src/dactyl_manuform.py

stl:
  #!/usr/bin/env sh
  for file in `ls things/*.scad`; do
    OpenSCAD-2023.10.27.ai16657-x86_64.AppImage -q $file -o $file.stl
  done

autom NAME: run stl
  cp src/generate_configuration.py things/
  cp src/run_config.* things/
  mv things aa_{{NAME}}
