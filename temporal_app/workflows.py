from datetime import timedelta
from temporalio import workflow
from concurrent.futures import ThreadPoolExecutor

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal_app.activities import say_hello, review_message_history

@workflow.defn
class SayHello:
    @workflow.run
    async def run(self, name: str) -> str:
        activity = workflow.start_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=120),
            heartbeat_timeout=timedelta(seconds=120),
        )
        return "Done"

@workflow.defn
class ReviewMessageHistory:
    @workflow.run
    async def run(self, name: str) -> str:
        return workflow.execute_activity(
            review_message_history, name, start_to_close_timeout=timedelta(seconds=5)
        )