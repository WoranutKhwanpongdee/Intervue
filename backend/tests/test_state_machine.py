import pytest
from app.services.orchestrator.state_machine import (
    InterviewStateMachine,
    InterviewState,
    TransitionTrigger,
    StateMachineError,
    WorkflowContext,
)


def test_initial_state():
    sm = InterviewStateMachine()
    assert sm.current_state == InterviewState.INITIALIZING
    assert sm.can_transition_to(InterviewState.RESUME_ANALYSIS)
    assert sm.can_transition_to(InterviewState.TOPIC_SELECTION)
    assert not sm.can_transition_to(InterviewState.COMPLETED)


def test_valid_forward_transitions():
    sm = InterviewStateMachine()

    # Step 1: Resume Analysis
    sm.transition_to(
        InterviewState.RESUME_ANALYSIS,
        trigger=TransitionTrigger.ANALYZE_PROFILE,
        details="Parsing resume text."
    )
    assert sm.current_state == InterviewState.RESUME_ANALYSIS

    # Step 2: Topic Selection
    sm.transition_to(
        InterviewState.TOPIC_SELECTION,
        trigger=TransitionTrigger.SELECT_TOPIC,
        details="Selecting topic."
    )
    assert sm.current_state == InterviewState.TOPIC_SELECTION

    # Step 3: Question Generation
    sm.transition_to(
        InterviewState.QUESTION_GENERATION,
        trigger=TransitionTrigger.GENERATE_QUESTION
    )
    assert sm.current_state == InterviewState.QUESTION_GENERATION

    # Step 4: Awaiting Answer
    sm.transition_to(
        InterviewState.AWAITING_ANSWER,
        trigger=TransitionTrigger.AWAIT_INPUT
    )
    assert sm.current_state == InterviewState.AWAITING_ANSWER
    assert sm.context.last_checkpoint_state == InterviewState.AWAITING_ANSWER

    # Step 5: Evaluating Answer
    sm.transition_to(
        InterviewState.EVALUATING_ANSWER,
        trigger=TransitionTrigger.SUBMIT_ANSWER
    )
    assert sm.current_state == InterviewState.EVALUATING_ANSWER

    # Step 6: Deciding Next Action
    sm.transition_to(
        InterviewState.DECIDING_NEXT_ACTION,
        trigger=TransitionTrigger.DECIDE_NEXT
    )
    assert sm.current_state == InterviewState.DECIDING_NEXT_ACTION

    # Step 7: Compiling Report
    sm.transition_to(
        InterviewState.COMPILING_REPORT,
        trigger=TransitionTrigger.COMPILE_REPORT
    )
    assert sm.current_state == InterviewState.COMPILING_REPORT

    # Step 8: Completed
    sm.transition_to(
        InterviewState.COMPLETED,
        trigger=TransitionTrigger.COMPLETE
    )
    assert sm.current_state == InterviewState.COMPLETED
    assert len(sm.context.transition_history) == 8


def test_followup_branch_transition():
    sm = InterviewStateMachine(initial_state=InterviewState.DECIDING_NEXT_ACTION)
    
    # Transition to DEEP_DIVE_PROBE
    sm.transition_to(
        InterviewState.DEEP_DIVE_PROBE,
        trigger=TransitionTrigger.TRIGGER_FOLLOWUP,
        details="Bluff detected on Kafka terminology."
    )
    assert sm.current_state == InterviewState.DEEP_DIVE_PROBE

    # Transition to AWAITING_ANSWER
    sm.transition_to(
        InterviewState.AWAITING_ANSWER,
        trigger=TransitionTrigger.AWAIT_INPUT
    )
    assert sm.current_state == InterviewState.AWAITING_ANSWER


def test_invalid_transition_raises_error():
    sm = InterviewStateMachine(initial_state=InterviewState.INITIALIZING)

    with pytest.raises(StateMachineError):
        sm.transition_to(
            InterviewState.COMPLETED,
            trigger=TransitionTrigger.COMPLETE
        )


def test_recovery_transitions():
    sm = InterviewStateMachine(initial_state=InterviewState.FAILED)
    
    sm.transition_to(
        InterviewState.RECOVERING,
        trigger=TransitionTrigger.RECOVER
    )
    assert sm.current_state == InterviewState.RECOVERING

    sm.transition_to(
        InterviewState.AWAITING_ANSWER,
        trigger=TransitionTrigger.RESUME
    )
    assert sm.current_state == InterviewState.AWAITING_ANSWER
