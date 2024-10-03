from datetime import timedelta
from temporalio import workflow
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from temporal_app.activities import AIAgentActivityManager, AIAgentActivityInput
    from tools.search import get_search_data
    import json


TOOL_MAP = {
    "get_search_results": get_search_data,
}

@dataclass
class AIAgentWorkflowInput:
    ai_agent_token: str
    message_content: str
    message_author: str
    message_channel_id: str

@workflow.defn
class AIAgentWorkflow:
    
    @workflow.run
    async def run(self, input: AIAgentWorkflowInput) -> str:
        workflow_tools_result = await workflow.execute_activity(
            AIAgentActivityManager.get_tools,
            AIAgentActivityInput(
                input.ai_agent_token,
                input.message_content,
                input.message_author,
                input.message_channel_id,
            ),
            start_to_close_timeout=timedelta(seconds=120),
        )
        workflow_tools_data = json.loads(workflow_tools_result)

        return workflow_tools_result


        
# workflow_data = {
#     'tools': {},
# }

# tool_data = await workflow.execute_activity(
#     AIAgentActivityManager.get_tools,
#     AIAgentActivityInput(
#         input.ai_agent_token,
#         input.message_content,
#         input.message_author,
#         input.message_channel_id,
#     ),
#     start_to_close_timeout=timedelta(seconds=120),
# )

# tools = json.loads(tool_data)

# for tool in tools:
#     if tool['name'] in TOOL_MAP:
#         workflow_data['tools'][tool['name']] = {
#             'input': tool['input'],
#             'output': TOOL_MAP[tool['name']](tool['input']),
#             'channel_id': input.message_channel_id,
#         }

# return json.dumps(workflow_data)

# Use when we need to execute async
# return await workflow.execute_activity_method(
#     AIAgentActivityManager.perform_activity,
#     AIAgentActivityInput(
#         input.ai_agent_token,
#         input.message_content,
#         input.message_author,
#         input.message_channel_id,
#     ),
#     start_to_close_timeout=timedelta(seconds=120),
#     heartbeat_timeout=timedelta(seconds=120),
# )