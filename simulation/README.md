# AFAI Experiment integration contract

Status: interactive static frontend and design contracts. No simulation adapter or GPU worker is deployed by this commit. Existing Spark Q&A remains separate and unchanged. GitHub Pages cannot host these Python/GPU processes.

## Included

- ../experiment.html: motor example, founder-described RGB-D grasp case, telerobot/humanoid/exoskeleton concept catalogues, component search, session plans and JSON exports.
- adapters.json: capability registry for Isaac Sim, Isaac Lab, Omniverse, Cosmos and MuJoCo; all statuses are not_connected and tested_versions is empty.
- manifest.schema.json: draft manifest contract. A draft is deliberately not executable.

## Required backend boundaries

1. Identity: authenticated project membership, tier entitlements, tenant isolation and per-user compute quotas; the browser tier selector never grants access.
2. Artifact registry: immutable object storage, metadata database, checksums, versions, licences, access policy, citations and lineage. URDF/MJCF/USD conversion must validate physical semantics.
3. Orchestration: bounded agent plans and typed tools for research, assets, simulation, learning, evaluation and documentation. Supplier proposals and plugins carry evidence and compatibility checks.
4. Job service: validate draft and acceptance criteria; estimate resources/cost; schedule only after authorization. State machine: draft -> preflight -> queued -> running -> succeeded/failed/cancelled. Define idempotency, cancellation, retry policy, heartbeat and hard timeout.
5. Workers: isolated runtime per adapter/version with explicit CPU/GPU/RAM/VRAM requirements. Pin container digest, OS/architecture, drivers, CUDA where needed, solver, model and plugin versions. Never assume Spark/Jetson runs every workload.
6. Results: logs, time series, images/video, reports, policy checkpoints, seeds, versions and measured metrics. Mark generated, analytical, simulated and measured evidence separately.
7. Retrieval: permission-filtered indexing of results in the engineering knowledge repository; do not index private output into a public frontend.
8. Physical execution: separate authenticated robot/IoT gateway, independent controller checks and explicit project authorization; never treat a language-model plan as a motor command.

## Proposed API, not currently implemented

GET /simulation/capabilities -- tested adapter and worker versions
POST /simulation/projects/{id}/experiments -- authenticated draft creation
POST /simulation/experiments/{id}/preflight -- model, version, resource and authorization checks
POST /simulation/experiments/{id}/jobs -- authorized dispatch, idempotency key
GET /simulation/jobs/{id} -- state, progress, provenance and failure details
POST /simulation/jobs/{id}/cancel -- scoped cancellation
GET /simulation/jobs/{id}/artifacts -- authorized artifact references

Adapter interface: capabilities(), validate(manifest), estimate(manifest), run(approved_job), cancel(job_id), collect(job_id). The orchestrator must reject unknown or unavailable adapters, rather than return fabricated outputs.

## Verification gates before an adapter can be marked connected

- Install a supported runtime on the intended worker and record exact versions.
- Run one deterministic smoke scene and a task-level acceptance test; retain logs/artifacts.
- Check units, coordinate frames, inertias, joint limits, contacts and sensor calibration.
- Exercise failed preflight, cancellation, timeout, lost worker and insufficient quota.
- Test tenant isolation and prohibit shell commands supplied through natural-language prompts.
- Repeatability means measured tolerances, not an assumption of bitwise GPU determinism.

Cosmos data generation must not be presented as a physics validation result. Omniverse is an ecosystem for scene/application workflows, not a drop-in interchangeable dynamics solver. Cross-engine comparisons require matched tasks and documented modelling differences.

## Primary documentation

- https://docs.isaacsim.omniverse.nvidia.com/latest/index.html
- https://isaac-sim.github.io/IsaacLab/main/index.html
- https://docs.nvidia.com/omniverse/index.html
- https://docs.nvidia.com/cosmos/
- https://mujoco.readthedocs.io/en/stable/overview.html

Additional targets (Newton/PhysX profiles, ROS 2 bridges and further simulators) use the same contract after their own compatibility and acceptance tests.
