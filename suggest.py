# Per LLM API key, extract:
## trace: model's chain-of-thought tokens
## reasoning: the justification written down
## answer: the update config
import json, os
import urllib.request
import urllib.error
from datetime import datetime
from analyse import analyse
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

CONFIG = "config.json"
PROMPT = "prompt.md"
BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

TUNABLE = (
    "gait", "speed", "x", "y", "angle", "step_height_Z", "body_height"
)

SCHEMA = {
    "type": "object",
    "properties": {
        "param": {"type": "string", "enum": list(TUNABLE)},
        "value": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["param", "value", "reasoning"],
    "additionalProperties": False,
}

def format_config(config):
    return " ".join(f"{p}={config[p]}" for p in TUNABLE if p in config)

def format_history(summaries):
    lines = []
    for s in summaries:
        lines.append(
            f"Batch {s['batch']}\n"
            f"  config:    {format_config(s['config'])}\n"
            f"  completed: {s['n_completed']}/{s['n_trials']}\n"
            f"  outcomes:  {s['outcomes']}\n"
            f"  means:     {s['mean_distance']}cm, {s['mean_cycles']} cycles, "
            f"{s['mean_duration']}s, roll {s['mean_max_roll']}deg"
        )
    return "\n\n".join(lines)

def format_past_suggestions(summaries):
    lines = []
    for s in summaries:
        path = f"batches/{s['batch']}/suggestion.json"
        if not os.path.exists(path):
            continue
        with open(path) as f:
            past = json.load(f)
        lines.append(
            f"  for batch {past['batch']}: {past['param']} -> {past['value']} "
            f"because {past['reasoning']}"
        )
 
    if not lines:
        return ""
    return "Changes you proposed previously:\n" + "\n".join(lines) + "\n\n"

def build_prompt(summaries, config):
    with open(PROMPT) as f:
        instructions = f.read().strip()
 
    return (
        f"{instructions}\n\n"
        f"---\n\n"
        f"{format_history(summaries)}\n\n"
        f"{format_past_suggestions(summaries)}"
        f"Current config: {format_config(config)}\n\n"
        f"Suggest one change for the next batch."
    )
    
def ask_model(user_prompt):
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise SystemExit("GROQ_API_KEY not set")
    
    client = OpenAI(api_key=key, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_prompt}],
        max_completion_tokens=2048,
        temperature=0.6,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "gait_suggestion",
                "strict": True,
                "schema": SCHEMA,
            },
        },
        extra_body={
            "include_reasoning": True,
            "reasoning_effort": "high",
        },
    )
 
    message = response.choices[0].message
    trace = (message.model_extra or {}).get("reasoning")
    return json.loads(message.content), trace

def apply_suggestion(config, param, value):
    updated = dict(config)
    updated[param] = value
    updated["batch"] = str(int(config["batch"]) + 1)
    return updated



def main():
    summaries = analyse()
    if not summaries:
        print("no trials yet")
        return
 
    with open(CONFIG) as f:
        config = json.load(f)
    
    prompt = build_prompt(summaries, config)
    print(f"asking {MODEL} about {len(summaries)} batches...")
    
    answer, trace = ask_model(prompt)
    param, value, reasoning = answer["param"], answer["value"], answer["reasoning"]
    
    updated = apply_suggestion(config, param, value)
    batch = updated["batch"]
    
    with open(CONFIG, "w") as f:
        json.dump(updated, f, indent=2)
 
    record = {
        "batch": batch,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "model": MODEL,
        "param": param,
        "value": value,
        "previous_value": config.get(param),
        "reasoning": reasoning,
        "trace": trace,
        "prompt": prompt,
    }
    
    # Make new batch folder
    path = f"batches/{batch}/suggestion.json"
    os.makedirs(f"batches/{batch}", exist_ok=True)
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
 
    print(f"\n{param}: {config.get(param)} -> {value}")
    print(f"stated:  {reasoning}")
    if trace:
        print(f"trace:   {len(trace.split())} words, saved to {path}")
    else:
        print("trace:   none returned")
    print(f"\nconfig.json now batch {batch}. run: sudo python run_batch.py 10")
 
 
if __name__ == "__main__":
    main()