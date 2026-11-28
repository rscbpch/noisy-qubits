# API contract (draft)

Status: **proposal from Member 2, waiting for Member 1.** The types are in
`frontend/src/api/types.ts`. The project description refers to Section 11.3 for
this contract, but the text is not in our copy.

## Endpoints

| Endpoint | Request | Response |
|---|---|---|
| `GET /api/algorithms` | none | `AlgorithmInfo[]` |
| `GET /api/devices` | none | `DeviceInfo[]` |
| `POST /api/run` | `RunRequest` | `RunResponse` |
| `POST /api/circuit/validate` | `ValidateRequest` | `ValidateResponse` |
| `POST /api/qasm` | `QasmRequest` | `QasmResponse` |

`/api/compare` (Member 3) is not defined here.

## `circuit.ops`

```json
{ "numQubits": 3, "ops": [
  { "name": "h",  "qubits": [0] },
  { "name": "cp", "qubits": [0, 1], "angle": 1.5708 },
  { "name": "measure", "qubits": [0], "clbit": 0 }
] }
```

- Ops are in execution order. The frontend chooses the columns.
- Names are lowercase Qiskit names. Controls come first and the target last.
- The circuit is the user-level one, never the transpiled one.

## Questions for Member 1

1. Are these endpoints and field names OK? JSON uses camelCase, so the API has
   to convert from Python's snake_case.
2. **Pass rule:** the description says PASS if `score >= 50% of ideal` (75% for
   Simon's). `AlgorithmResult.normalized` in `result.py` uses
   `(score - baseline) / (ideal - baseline)`. These give different answers.
   Which one is correct?
3. `docs/noise-contract.md` says every algorithm simulates through `run_counts`
   and exposes `score()`. Do Superposition and Deutsch-Jozsa still need that
   change? QFT and QPE will follow the contract.
4. A typed Deutsch-Jozsa oracle uses `mcx`, which is not in the gate list. Should
   the API decompose it before building `circuit.ops`?
5. Should one `/api/run` call take one device (as drafted) or up to three?
6. The sample UI has an "Add readout error" checkbox, sent as `readoutError`
   (true or false). `build_noise_model` needs an amount from 0 to 1. Which
   amount should the API use? (Member 5 may need to answer.)
7. What error shape should `/api/run` and `/api/qasm` return for invalid input?
