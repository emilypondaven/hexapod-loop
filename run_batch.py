import sys, time, json, csv, os
from datetime import datetime
from run_trial import next_trial_id, run_trial
import copy

sys.path.append("/home/emily/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/Code/Server")
from control import Control

LOG = "logs/trials.csv"

with open("config.json") as f:
    config = json.load(f)
    
batch = config["batch"]
control = Control()

# Set all variables from config
control.body_height = config["body_height"]
for p in control.body_points:
    p[2] = control.body_height

home_body_points = copy.deepcopy(control.body_points)
home_body_height = control.body_height

n_trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3

completed = 0
for i in range(n_trials):
    trial_id = next_trial_id()
    print(f"\n--- batch {batch}, trial {trial_id}  ({i + 1} of {n_trials}) ---")
    print("s = start, c = cancel batch")
    if input("> ").strip().lower() == "c":
        print("batch cancelled")
        break
    
    control.body_points = copy.deepcopy(home_body_points)
    control.body_height = home_body_height
    control.transform_coordinates(control.body_points)
    control.set_leg_angles()
    time.sleep(0.5)
    run_trial(control, config, batch, trial_id)
    completed += 1

os.makedirs(f"batches/{batch}", exist_ok=True)
with open(f"batches/{batch}/config.json", "w") as f:
    json.dump(config, f, indent=2)
print(f"All {completed} completed. Saved to trials csv file.")
