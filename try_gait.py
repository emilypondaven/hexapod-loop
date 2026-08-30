import sys
sys.path.append('/home/emily/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/Code/Server')

from control import Control

control = Control()

gait = sys.argv[1] if len(sys.argv) > 1 else '1'
cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 10

for _ in range(cycles):
    control.run_gait(['CMD_MOVE', gait, '0', '25', '5', '0'])
