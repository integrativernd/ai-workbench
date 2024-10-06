from datetime import timedelta
from temporalio import workflow
from dataclasses import dataclass
import json
with workflow.unsafe.imports_passed_through():
    from temporal_app.activities import (
        AIAgentActivityManager,
        AIAgentActivityInput,
        AIAgentToolInput
    )

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
        # workflow_tools_data = json.loads(workflow_tools_result)
        return workflow_tools_result

        # tool_results = []
        # for tool_instance in workflow_tools_data:
        #     tool_result = await workflow.execute_activity(
        #         AIAgentActivityManager.call_tool,
        #         AIAgentToolInput(
        #             tool_instance['name'],
        #             tool_instance['input'],
        #         ),
        #         start_to_close_timeout=timedelta(seconds=120),
        #     )
        #     tool_results.append(tool_result)

        # if len(tool_results) > 0:
        #     return ' '.join(tool_results)
        # else:
        #     return workflow_tools_result
            
            

# NOTES
        
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