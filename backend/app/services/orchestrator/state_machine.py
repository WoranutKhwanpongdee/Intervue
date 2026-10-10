import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger("intervue.orchestrator.state_machine")


class InterviewState(str, Enum):
    INITIALIZING = "INITIALIZING"
    RESUME_ANALYSIS = "RESUME_ANALYSIS"
    TOPIC_SELECTION = "TOPIC_SELECTION"
    QUESTION_GENERATION = "QUESTION_GENERATION"
    AWAITING_ANSWER = "AWAITING_ANSWER"
    EVALUATING_ANSWER = "EVALUATING_ANSWER"
    DECIDING_NEXT_ACTION = "DECIDING_NEXT_ACTION"
    DEEP_DIVE_PROBE = "DEEP_DIVE_PROBE"
    COMPILING_REPORT = "COMPILING_REPORT"
    COMPLETED = "COMPLETED"
    RECOVERING = "RECOVERING"
    FAILED = "FAILED"


class TransitionTrigger(str, Enum):
    ANALYZE_PROFILE = "ANALYZE_PROFILE"
    SELECT_TOPIC = "SELECT_TOPIC"
    GENERATE_QUESTION = "GENERATE_QUESTION"
    AWAIT_INPUT = "AWAIT_INPUT"
    SUBMIT_ANSWER = "SUBMIT_ANSWER"
    EVALUATE_ANSWER = "EVALUATE_ANSWER"
    DECIDE_NEXT = "DECIDE_NEXT"
    TRIGGER_FOLLOWUP = "TRIGGER_FOLLOWUP"
    ADVANCE_TOPIC = "ADVANCE_TOPIC"
    COMPILE_REPORT = "COMPILE_REPORT"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"
    RECOVER = "RECOVER"
    RESUME = "RESUME"


class NextActionDecision(str, Enum):
    FOLLOWUP_PROBE = "FOLLOWUP_PROBE"
    NEXT_TOPIC = "NEXT_TOPIC"
    COMPLETE = "COMPLETE"


class StateTransitionLog(BaseModel):
    from_state: InterviewState
    to_state: InterviewState
    trigger: TransitionTrigger
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowContext(BaseModel):
    session_id: Optional[str] = None
    role_title: str = ""
    experience_level: str = "Senior"
    interview_type: str = "Full-Loop"
    difficulty: str = "Medium"
    num_questions: int = 5
    
    # Progress tracking
    current_round_stage: Optional[str] = None
    current_persona: Optional[str] = None
    active_topic: Optional[str] = None
    covered_topics: List[str] = Field(default_factory=list)
    
    # Execution & Recovery
    retry_count: int = 0
    last_error: Optional[str] = None
    last_checkpoint_state: InterviewState = InterviewState.INITIALIZING
    transition_history: List[StateTransitionLog] = Field(default_factory=list)
    
    # Candidate profile cache
    extracted_skills: List[str] = Field(default_factory=list)
    extracted_projects: List[str] = Field(default_factory=list)


# Valid state transitions graph
VALID_TRANSITIONS: Dict[InterviewState, Set[InterviewState]] = {
    InterviewState.INITIALIZING: {
        InterviewState.INITIALIZING,
        InterviewState.RESUME_ANALYSIS,
        InterviewState.TOPIC_SELECTION,
        InterviewState.FAILED,
    },
    InterviewState.RESUME_ANALYSIS: {
        InterviewState.RESUME_ANALYSIS,
        InterviewState.TOPIC_SELECTION,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.TOPIC_SELECTION: {
        InterviewState.TOPIC_SELECTION,
        InterviewState.QUESTION_GENERATION,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.QUESTION_GENERATION: {
        InterviewState.QUESTION_GENERATION,
        InterviewState.AWAITING_ANSWER,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.AWAITING_ANSWER: {
        InterviewState.AWAITING_ANSWER,  # Re-entry / Resume
        InterviewState.EVALUATING_ANSWER,
        InterviewState.COMPILING_REPORT,  # Early finish
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.EVALUATING_ANSWER: {
        InterviewState.EVALUATING_ANSWER,
        InterviewState.DECIDING_NEXT_ACTION,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.DECIDING_NEXT_ACTION: {
        InterviewState.DECIDING_NEXT_ACTION,
        InterviewState.DEEP_DIVE_PROBE,
        InterviewState.TOPIC_SELECTION,
        InterviewState.QUESTION_GENERATION,
        InterviewState.COMPILING_REPORT,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.DEEP_DIVE_PROBE: {
        InterviewState.DEEP_DIVE_PROBE,
        InterviewState.AWAITING_ANSWER,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.COMPILING_REPORT: {
        InterviewState.COMPILING_REPORT,
        InterviewState.COMPLETED,
        InterviewState.RECOVERING,
        InterviewState.FAILED,
    },
    InterviewState.RECOVERING: {
        InterviewState.RECOVERING,
        InterviewState.INITIALIZING,
        InterviewState.TOPIC_SELECTION,
        InterviewState.QUESTION_GENERATION,
        InterviewState.AWAITING_ANSWER,
        InterviewState.EVALUATING_ANSWER,
        InterviewState.DECIDING_NEXT_ACTION,
        InterviewState.COMPILING_REPORT,
        InterviewState.FAILED,
    },
    InterviewState.FAILED: {
        InterviewState.FAILED,
        InterviewState.RECOVERING,
        InterviewState.INITIALIZING,
    },
    InterviewState.COMPLETED: {
        InterviewState.COMPLETED,
    },
}


class StateMachineError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class InterviewStateMachine:
    """
    Finite State Machine orchestrating the lifecycle of an adaptive interview session.
    Guarantees state safety, invariant enforcement, and transition auditing.
    """

    def __init__(
        self,
        initial_state: InterviewState = InterviewState.INITIALIZING,
        context: Optional[WorkflowContext] = None
    ):
        self.current_state = initial_state
        self.context = context or WorkflowContext()

    def can_transition_to(self, target_state: InterviewState) -> bool:
        """Check if transition from current state to target state is allowed."""
        allowed = VALID_TRANSITIONS.get(self.current_state, set())
        return target_state in allowed

    def transition_to(
        self,
        target_state: InterviewState,
        trigger: TransitionTrigger,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InterviewState:
        """
        Execute state transition with guard checks and history logging.
        """
        if not self.can_transition_to(target_state):
            err_msg = (
                f"Illegal state transition from [{self.current_state.value}] to [{target_state.value}] "
                f"via trigger [{trigger.value}]."
            )
            logger.error(err_msg)
            raise StateMachineError(err_msg)

        old_state = self.current_state
        self.current_state = target_state

        log_entry = StateTransitionLog(
            from_state=old_state,
            to_state=target_state,
            trigger=trigger,
            details=details,
            metadata=metadata or {}
        )
        self.context.transition_history.append(log_entry)

        # Update stable checkpoint state
        if target_state in {
            InterviewState.AWAITING_ANSWER,
            InterviewState.TOPIC_SELECTION,
            InterviewState.COMPLETED
        }:
            self.context.last_checkpoint_state = target_state

        logger.info(
            f"State Transition: [{old_state.value}] ➔ [{target_state.value}] (Trigger: {trigger.value})"
        )
        return self.current_state
