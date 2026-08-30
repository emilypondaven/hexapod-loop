import sys
sys.path.append('/home/emily/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/Code/Server')

from control import Control

control = Control()
control.relax(True)
