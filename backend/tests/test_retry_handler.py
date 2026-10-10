import pytest
from app.services.orchestrator.retry_handler import AsyncRetryHandler, RetryPolicy


@pytest.mark.asyncio
async def test_retry_successful_on_first_try():
    handler = AsyncRetryHandler(RetryPolicy(max_retries=3, base_delay_sec=0.01))
    attempts = 0

    async def successful_op():
        nonlocal attempts
        attempts += 1
        return "success"

    result = await handler.execute_with_retry("test_op", successful_op)
    assert result == "success"
    assert attempts == 1


@pytest.mark.asyncio
async def test_retry_eventual_success_after_failures():
    handler = AsyncRetryHandler(RetryPolicy(max_retries=3, base_delay_sec=0.01))
    attempts = 0

    async def flaky_op():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ConnectionError("Transient network drop")
        return "recovered_success"

    result = await handler.execute_with_retry("flaky_op", flaky_op)
    assert result == "recovered_success"
    assert attempts == 2


@pytest.mark.asyncio
async def test_retry_triggers_fallback_on_exhaustion():
    handler = AsyncRetryHandler(RetryPolicy(max_retries=2, base_delay_sec=0.01))
    attempts = 0
    fallback_called = False

    async def failing_op():
        nonlocal attempts
        attempts += 1
        raise ValueError("Permanent API error")

    async def fallback_op():
        nonlocal fallback_called
        fallback_called = True
        return "fallback_value"

    result = await handler.execute_with_retry(
        "failing_op",
        failing_op,
        fallback_func=fallback_op
    )
    assert result == "fallback_value"
    assert attempts == 2
    assert fallback_called is True
