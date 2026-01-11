## Phase 1 Complete: Contract Consolidation ✅
What was done:
### 1
Created interaction_schema.py - Consolidated:
### 2
hitl_schema.py → HitlRequestType, HitlResolutionStatus, HitlInputSchema, HitlRequest, HitlResolution
question_schema.py → QuestionType, Question, QuestionSetProvenance, QuestionSet, UserAnswers
Updated action_plan_schema.py - Added from plan_schema.py:
### 3
PlanProposalStep (renamed from PlanStep to avoid conflict)
PlanApproval, EstimatedCost, PlanProposal
Updated context_pack_schema.py - Added from evidence_schema.py:
### 4
EvidenceType, EvidenceSource, EvidenceItem
Updated flow_schema.py - Added from:
### 5
branch_schema.py → ConditionOp, ConditionScalar, ConditionValue, ConditionExpr
loop_schema.py → ConfidenceThreshold, NoMissingEvidence, StopConditionGroup, StopConditionExpr, LoopState
Added deprecation warnings to all 6 original files with backwards-compatible re-exports:
### 6
hitl_schema.py
question_schema.py
plan_schema.py (PlanStep aliased to PlanProposalStep)
evidence_schema.py
branch_schema.py
loop_schema.py
Contract file count:
Before: 21 files
After: 15 files (6 deprecated with re-exports)
Effective reduction: 6 files → 4 consolidated targets
### Test results: 195 passed ✅
The deprecated files still work via re-exports, so existing code continues to function while emitting deprecation warnings.
---
## Phase 2 Complete: Unused Module Removal ✅
What was done:
### Updated executor.py:

Removed imports for MCPBackend and RemoteToolBackend
Removed self._remote and self._mcp instantiation from __init__
Simplified execute() method to only support local backend mode
Other backend modes now return a clear error message
### Deleted files:

mcp_backend.py ❌
remote_backend.py ❌
### Backends directory now contains only:

__init__.py (empty)
local_backend.py ✅
### Test results: 195 passed ✅
