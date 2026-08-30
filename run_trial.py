import sys, time, json, csv, os
from datetime import datetime

LOG = "logs/trials.csv"

def next_trial_id():
    if not os.path.exists(LOG):
        return 1
    with open(LOG) as f:
        return sum(1 for _ in f)

def run_trial(control, config, batch, trial_id):
    # Set parameters:
    cycles = 0
    max_pitch = 0.0
    max_roll = 0.0
    start = time.time()
    
    ## Start writing
    try:
        while True:
            control.run_gait([
                'CMD_MOVE',
                str(config["gait"]),
                str(config["x"]),
                str(config["y"]),
                str(config["speed"]),
                str(config["angle"]),
            ], Z=config["step_height_Z"])
            
            ## Update values
            cycles += 1
            roll, pitch, yaw = control.imu.update_imu_state()
            max_pitch = max(max_pitch, abs(pitch))
            max_roll = max(max_roll, abs(roll))
    except KeyboardInterrupt:
        pass
    
    duration = round(time.time() - start, 2)
    control.relax(True)
    
    ## Querying for extra reward information
    print(f"\n{cycles} cycles, {duration}s")
    outcome = input("outcome [completed/drifted/tipped/leg_slipped/brownout/aborted]: ").strip()
    distance = input(f"distance cm [enter = {config['target_distance']}]: ").strip()
    distance = float(distance) if distance else config["target_distance"]
    notes = input("notes: ").strip()
    
    ## Organising into csv file
    row = {
        "trial_id": trial_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "batch": batch,
        "cfg_gait": config["gait"],
        "cfg_x": config["x"],
        "cfg_y": config["y"],
        "cfg_speed": config["speed"],
        "cfg_angle": config["angle"],
        "cfg_step_height_Z": config["step_height_Z"],
        "cfg_body_height": config["body_height"],
        "cfg_leg_order": config["leg_order"],
        "cfg_target_distance": config["target_distance"],
        "distance": distance,
        "cycles": cycles,
        "duration": duration,
        "outcome": outcome,
        "max_pitch": round(max_pitch, 1),
        "max_roll": round(max_roll, 1),
        "notes": notes,
    }
            
    os.makedirs("logs", exist_ok=True)
    write_header = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    
    print(f"logged trial {trial_id}, batch {batch}")
