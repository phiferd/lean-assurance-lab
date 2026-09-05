# Agent task navigation

This is an operational index, not research authority. Read `CONSTITUTION.md`,
then `docs/RESEARCH_STATUS.md`; its **Active** subsection selects the governing
plan. Consult older status entries only for the evidence or transition needed
by the task. Do not replace those sources with this page or a conversation.

## Load only the relevant branch

| Task | Additional starting points |
| --- | --- |
| Clone-safe CI and test execution | README “Prerequisites And Clone-Safe Checks”, `.github/workflows/unit-tests.yml`, `scripts/run-unit-tests` |
| Current publication-study work | `docs/research/DECLARATION_VALIDATION_PUBLICATION_STUDY_PLAN.md`, current gate artifact named by Active |
| Gate-9 synthesis protocol | `config/declaration-validation-publication-study-gate-9.json`, `scripts/validate-declaration-validation-publication-study-gate-9` |
| Gate-10 recorded result and next review | `results/research/publication-study-theorem-control-0001/result.json`, `scripts/validate-declaration-validation-publication-study-gate-10`, generated Gate-10 report; Gate 11 and Gate 12 remain separate |
| Authority, catalog, or declaration-validation evidence | `.agents/skills/declaration-validation-adjudication/SKILL.md`; follow its required evidence reads |
| Current-state artifact refresh | `scripts/build-artifact-graph`, `scripts/artifact-status`; affected generator and graph dependencies |
| Publication-study Gates 11–12 | `scripts/close-declaration-validation-publication-study`, canonical closure decision, content manifest and historical attestation; use `validate-historical` after the freeze |
| External-action preparation | `docs/INVESTIGATION_SOP.md`, exact investigation and action draft; publication still requires target-specific human authorization |

Use `rg` to find a section or artifact ID before opening large files. For JSON,
inspect keys and the relevant records first. Follow bindings when the task
requires evidence; summaries never substitute for those bytes.

## Delegation policy

The project owner authorized cheaper-agent delegation on 2026-09-04 in the
project-management conversation. Use Luna at low/medium reasoning for narrow
routine edits and Terra at medium reasoning for bounded implementation. The
lead handles research design, interpretation, consequential review and final
integration. Model names are operating preferences, not scientific authority;
verify available models when starting a new environment.

Start one worker by default. Add another only for independent work with useful
local work in parallel. Give workers minimal task-specific context and exact
file ownership; do not copy the whole conversation. Keep one writer for each
catalog, freeze, state document or shared output. Escalate substantive ambiguity
instead of repeatedly retrying or expanding scope. Use deterministic scripts
for generation, hashing, checker runs and report production.

A worker brief should state:

- objective and authorized gate;
- required governing documents and exact input paths;
- editable files and immutable predecessors;
- acceptance commands and evidence to return;
- stop condition and escalation trigger.

Return changed paths, checks and outcomes, unresolved issues, and a short
explanation. The lead reviews the diff and evidence rather than repeating all
successful work. Independent semantic review is reserved for consequential
claims and cannot establish authority by consensus.

## Context handoff

Prefer a fresh conversation at a verified gate boundary, after changes and
validation outcomes are durable. Reset sooner if unrelated work has accumulated
or important details are repeatedly lost; do not reset merely because a long
script is running. Before handoff, record the exact commit or uncommitted files,
last completed gate, next authorized action, checks and limitations in durable
state. Keep `docs/RESEARCH_STATUS.md` as the priority source.

A fresh conversation can start with: “Manage the currently authorized frontier
using `docs/AGENT_WORKFLOW.md`. Read governing state first; delegate routine work
to Luna and bounded implementation to Terra. Resume from the recorded gate.”

Add a new skill only after a repeated procedure demonstrates a need. Prefer
short navigation and existing validators over another overlapping rule set.

## Autonomous work and cost discipline

The owner requested maximum practical autonomy and script-first mechanical
work on 2026-09-04. Continue all authorized local steps through the durable stop
condition; do not spend model turns carrying command output between routine
phases. `scripts/refresh-current-state` performs the ordered assurance refresh
and final current-artifact check, stopping at the first failure and preserving
its logs. It launches no checker or campaign.

Use scripts for inventories, hashes, derivation, execution accounting, report
generation and validation. Use Luna for narrow edits, Terra for bounded
implementation, and the lead for research design, evidence interpretation and
integration. Use a separate Ultra review only for a concrete consequential
scientific ambiguity. Review and model agreement do not establish authority.

Run focused tests while engineering, then the required complete suite at the
gate boundary. Repeat broad checks only after relevant changes or unresolved
failures. Prefer a durable exact-input checkpoint to rerunning completed work.
Report progress at meaningful boundaries; unattended mechanical loops should
stop on changed inputs, depleted budgets, an exceptional result or an action
requiring human judgment.

An available campaign script does not authorize a research frontier. Normative
source approval and target-specific external submission remain explicit human
boundaries. Finish a concrete draft and its permissible preflight first, and
batch the remaining decisions for the owner.
