# Noisy Qubits

How much noise can a quantum algorithm take before it stops working?

This project runs quantum algorithms (built with Qiskit) on a noisy simulator, tells you if they still pass, and tries to rescue the ones that fail. The website is only a welcome page so far.

## Folders

- `notebooks/` – Jupyter notebooks where we explain and experiment
- `src/noisy_qubits/` – the Python package the notebooks use
  - `algorithms/` – one file per algorithm
  - `noise/` – noise models and the slider
  - `mitigation/` – error handling
- `frontend/` – the website
- `tests/`

## Run it

You need [uv](https://docs.astral.sh/uv/) for the Python side and [Node.js](https://nodejs.org/) for the website.

### Notebooks and Python code

From the project root:

1. Install: `uv sync`
2. Open the notebooks: `uv run jupyter lab`
3. Run the tests: `uv run pytest`

### Website

1. Go to the website folder: `cd frontend`
2. Install (first time only): `npm install`
3. Start it: `npm run dev`
4. Open the address it prints, usually http://localhost:5173
5. Stop it with `Ctrl+C`
