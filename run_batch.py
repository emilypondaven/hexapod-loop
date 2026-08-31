import sys, time, json, csv, os
from datetime import datetime
from run_trial import next_trial_id, run_trial

sys.path.append("/home/emily/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/Code/Server")
from control import Control

LOG = "logs/trials.csv"

with open("config.json") as f:
    config = json.load(f)
    
batch = config["batch"]
control = Control()

# Set all variables from config
control.body_height = config["body_height"]
n_trials = int(sys.argv[1]) if len(sys.argv) > 1 else 10

for i in range(n_trials):
    trial_id = next_trial_id()
    print(f"\n--- batch {batch}, trial {trial_id}  ({i + 1} of {n_trials}) ---")
    print("s = start, c = cancel batch")
    if input("> ").strip().lower() == "c":
        print("batch cancelled")
        break
    run_trial(control, config, batch, trial_id)

os.makedirs(f"batches/{batch}", exist_ok=True)
with open(f"batches/{batch}/config.json", "w") as f:
    json.dump(config, f, indent=2)
print(f"All {n_trials} completed. Saved to trials csv file.")
