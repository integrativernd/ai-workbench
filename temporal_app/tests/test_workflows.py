import uuid

import pytest
import json

from temporalio import activity
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from temporal_app.workflows import AIAgentWorkflow, AIAgentWorkflowInput

from django.test import TestCase
from ai_agents.models import AIAgent
from config.settings import SYSTEM_PROMPT



@activity.defn(name="get_tools")
async def get_tools_mocked(input: AIAgentWorkflowInput) -> str:
    return json.dumps([
        {
            'name': 'get_search_results',
            'input': {
                'query': 'bitcoin price',
            },
        },
    ])

@activity.defn(name="call_tool")
async def get_tool_call_mocked(input: AIAgentWorkflowInput) -> str:
    return "Tool called"


class TestTemporalWorkflows(TestCase):
    """
    Test the core temporal workflows
    """
    def setUp(self):
        self.ai_agent = AIAgent.objects.create(
            name='beta',
            token=uuid.uuid4(),
            description=SYSTEM_PROMPT,
        )
    
    def tearDown(self):
        AIAgent.objects.all().delete()
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        task_queue_name = str(uuid.uuid4())
        async with await WorkflowEnvironment.start_time_skipping() as env:
            # TODO: Implement test that calls the actual activity manager.
            # activity_manager = AIAgentActivityManager(env.client)
            async with Worker(
                env.client,
                task_queue=task_queue_name,
                workflows=[AIAgentWorkflow],
                activities=[
                    get_tools_mocked,
                    get_tool_call_mocked,
                    # activity_manager.get_tools,
                ],
            ):
                workflow_result = await env.client.execute_workflow(
                    AIAgentWorkflow.run,
                    AIAgentWorkflowInput(
                        self.ai_agent.token,
                        'Look up the price of bitcoin',
                        'username1235',
                        'example_channel_id',
                    ),
                    id=str(uuid.uuid4()),
                    task_queue=task_queue_name,
                )
                workflow_result_data = json.loads(workflow_result)
                assert workflow_result_data == [
                    {
                        'name': 'get_search_results',
                        'input': {
                            'query': 'bitcoin price',
                        },
                    },
                ]
