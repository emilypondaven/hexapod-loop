import csv, json, os
from collections import defaultdict

LOG = "logs/trials.csv"

def analyse():
    # Read trials.csv
    if not os.path.exists(LOG):
        print("no trials yet")
        return []

    batches = defaultdict(list)
    with open(LOG) as f:
        reader = csv.DictReader(f)
        for row in reader:
            batches[row["batch"]].append(row)
            
    summaries = []
    # Iterate through each batch
    for batch_id in sorted(batches.keys()):
        trials = batches[batch_id]
        
        # Load config for this batch
        config_path = f"batches/{batch_id}/config.json"
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
        else:
            print(f"warning: config from batch {batch_id} missing")
            continue
        
        # Count outcomes
        outcome_counts = defaultdict(int)
        for trial in trials:
            outcome_counts[trial["outcome"]] += 1
        
        # Stats on completed only
        completed_trials = [t for t in trials if t["outcome"] == "completed"]
        if completed_trials:
            distances = [float(t["distance"]) for t in completed_trials]
            cycles = [int(t["cycles"]) for t in completed_trials]
            durations = [float(t["duration"]) for t in completed_trials]
            max_rolls = [float(t["max_roll"]) for t in completed_trials]
        else:
            distances = cycles = durations = max_rolls = []
        
        summary = {
            "batch": batch_id,
            "config": config,
            "n_trials": len(trials),
            "n_completed": len(completed_trials),
            "outcomes": dict(outcome_counts),
            "mean_distance": round(sum(distances) / len(distances), 1) if distances else 0,
            "mean_cycles": round(sum(cycles) / len(cycles), 1) if cycles else 0,
            "mean_duration": round(sum(durations) / len(durations), 2) if durations else 0,
            "mean_max_roll": round(sum(max_rolls) / len(max_rolls), 1) if max_rolls else 0,
        }
        summaries.append(summary)

if __name__ == "__main__":
    summaries = analyse()
    for s in summaries:
        print(f"\n=== batch {s['batch']} ===")
        print(f"config: gait={s['config']['gait']}, speed={s['config']['speed']}, x={s['config']['x']}")
        print(f"trials: {s['n_trials']}")
        print(f"outcomes: {s['outcomes']}")
        print(f"mean distance {s['mean_distance']}cm, {s['mean_cycles']} cycles, {s['mean_duration']}s, roll {s['mean_max_roll']}°")
