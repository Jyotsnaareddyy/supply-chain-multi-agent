# Supply Chain Multi-Agent POC

Coordinated multi-agent planning system for responding to a
seven-day critical-supplier disruption, evaluated against a
reorder-rule baseline and a MILP-only baseline.

## Structure

```text
data/           generated datasets (fixed seed)
agents/         demand / inventory / supplier-risk / logistics agents
coordinator/    validation, conflict resolution, orchestration
optimization/   MILP model (PuLP / OR-Tools)
baselines/      reorder-rule policy
evaluation/     metrics, experiments, stability
dashboard/      Streamlit what-if UI
schemas/        shared recommendation schema
tests/
```

## Setup

```bash
python3 -m pip install -r requirements.txt
python3 data/generate_data.py
```

## Run

```bash
python3 evaluation/experiments.py   # scenario matrix (all 3 approaches)
python3 -m streamlit run dashboard/app.py   # what-if dashboard
```

## Tests

```bash
python3 -m pytest tests/ -q
```

## Deploy

```bash
./deploy.sh                    # Streamlit on :8501
pkill -f "streamlit run"       # stop it
```

For hosted deployment (Streamlit Community Cloud), point at
`dashboard/app.py` with `requirements.txt` and the `data/*.csv`
files committed. Docker is not available in this environment.

## Core research question

Can a coordinated multi-agent planning system respond to a seven-day
critical-supplier disruption with lower service loss and faster
recovery than conventional reorder rules, while remaining
constraint-feasible and requiring human approval?
