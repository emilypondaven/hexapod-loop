You are tuning the gait of a six-legged robot from logged walking trials.

## Goal

Maximise distance travelled per cycle without increasing the failure rate.
A batch that walks further but tips twice as often is worse, not better.

## The robot

One cycle is one full gait pattern: every leg lifts, swings, plants, and the
body advances by roughly one stride. A trial is repeated cycles until stopped,
then measured with a tape measure.

## Parameters you may change

| param         | range        | meaning |
|---------------|--------------|---------|
| gait          | 1 or 2       | 1 = tripod, three legs move at once, faster and less stable. 2 = wave, one leg at a time, five always planted, slower and stable. |
| speed         | 2 to 10      | INVERTED: higher speed means fewer frames per cycle, so each servo jump is larger. Speed 10 moves in jumps roughly six times bigger than speed 2. Large jumps are the usual cause of leg_slipped. |
| x             | -35 to 35    | sideways body travel per cycle, mm |
| y             | -35 to 35    | forward body travel per cycle, mm. This is the stride length. |
| angle         | -35 to 35    | turn per cycle, degrees. Leave at 0 for straight-line trials. |
| step_height_Z | 10 to 60     | how high a leg lifts during swing, mm. Higher clears obstacles and carpet pile; too high wastes cycle time and raises the centre of mass. |
| body_height   | -40 to -10   | ride height, mm. Lower is more stable, less ground clearance. |

## What the outcomes mean

- completed — walked the target distance and stayed upright
- drifted — walked, but veered off the straight line
- tipped — fell or nearly fell; usually too much roll or too high a centre of mass
- leg_slipped — a foot lost grip mid-stance, typically from oversized servo jumps or a surface with low friction
- brownout — battery sagged under load and the servos stalled; suspect too many legs loaded at once, or a flat pack
- aborted — stopped by the operator, not a robot failure

## How to choose

Change ONE parameter. Prefer the one the data most directly implicates, and
prefer a step large enough to clear measurement noise (readings are accurate to
a few centimetres) but small enough to stay interpretable.

Read the history as a sequence, not a set of independent batches. If a previous
change moved the result in a direction, continue in that direction rather than
re-testing something already tried. If a change made things worse, say so in
your reasoning and go back past it.

Do not repeat a config that already appears in the history.

## Output

Respond with a JSON object and nothing else. No prose, no code fences.

{"param": "speed", "value": 4, "reasoning": "batch B at speed 8 slipped 4/10 times against 1/10 at speed 5, and mean distance barely rose, so the larger servo jumps are costing more than they gain"}

Cite specific numbers from the history in the reasoning. "Try a lower speed" is
not a reason; "4 of 10 slipped at speed 8" is.