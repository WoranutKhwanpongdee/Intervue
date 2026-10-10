import asyncio
import logging
import random
from typing import Callable, TypeVar, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("intervue.orchestrator.retry")

T = TypeVar("T")


class RetryPolicy(BaseModel):
    max_retries: int = 3
    base_delay_sec: float = 0.5
    max_delay_sec: float = 5.0
    backoff_multiplier: float = 2.0
    jitter: bool = True


class AsyncRetryHandler:
    """
    Handles robust execution of asynchronous operations with backoff, jitter,
    and fallback recovery options.
    """

    def __init__(self, policy: Optional[RetryPolicy] = None):
        self.policy = policy or RetryPolicy()

    async def execute_with_retry(
        self,
        operation_name: str,
        coro_func: Callable[[], Any],
        fallback_func: Optional[Callable[[], Any]] = None,
        custom_policy: Optional[RetryPolicy] = None
    ) -> Any:
        policy = custom_policy or self.policy
        attempts = 0
        current_delay = policy.base_delay_sec

        while attempts < policy.max_retries:
            attempts += 1
            try:
                logger.debug(f"Executing [{operation_name}] (Attempt {attempts}/{policy.max_retries})...")
                return await coro_func()
            except Exception as e:
                logger.warning(
                    f"Attempt {attempts} for [{operation_name}] failed with error: {str(e)}"
                )

                if attempts >= policy.max_retries:
                    if fallback_func:
                        logger.warning(
                            f"Max retries ({policy.max_retries}) reached for [{operation_name}]. Invoking fallback strategy..."
                        )
                        try:
                            return await fallback_func()
                        except Exception as fb_err:
                            logger.error(f"Fallback strategy for [{operation_name}] also failed: {fb_err}", exc_info=True)
                            raise fb_err
                    raise e

                # Calculate backoff delay with jitter
                delay = current_delay
                if policy.jitter:
                    delay += random.uniform(0, current_delay * 0.5)
                delay = min(delay, policy.max_delay_sec)

                logger.info(f"Retrying [{operation_name}] in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
                current_delay *= policy.backoff_multiplier
