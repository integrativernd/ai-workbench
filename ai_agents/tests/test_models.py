from django.test import TestCase
from ai_agents.models import AIAgent, AIAgentTask
from channels.models import Channel, Message

class AIAgentTaskTestCase(TestCase):
    def setUp(self):
        """Set up test data for all test methods."""
        self.ai_agent = AIAgent.objects.create()
        self.channel = Channel.objects.create()
        self.message = Message.objects.create(channel=self.channel)
        

    def create_task(self, parent_task=None, order=0):
        """Helper method to create a task."""
        return AIAgentTask.objects.create(
            ai_agent=self.ai_agent,
            message=self.message,
            channel=self.channel,
            parent_task=parent_task,
            order=order
        )

    def test_task_creation(self):
        """Test the initial state of a newly created task."""
        task = self.create_task()
        self.assertEqual(task.status, 'PENDING')
        self.assertIsNone(task.result)
        self.assertIsNone(task.parent_task)
        self.assertEqual(task.order, 0)

    def test_start_subtasks(self):
        """Test the start_subtasks method."""
        parent_task = self.create_task()
        subtask1 = self.create_task(parent_task=parent_task, order=1)
        subtask2 = self.create_task(parent_task=parent_task, order=2)

        parent_task.start_subtasks()

        for subtask in [subtask1, subtask2]:
            subtask.refresh_from_db()
            self.assertEqual(subtask.status, 'IN_PROGRESS')

    def test_task_relationships(self):
        """Test previous_task and next_task relationships."""
        parent_task = self.create_task()
        subtasks = [
            self.create_task(parent_task=parent_task, order=i)
            for i in range(1, 4)
        ]

        # Test previous_task
        self.assertIsNone(subtasks[0].previous_task)
        self.assertEqual(subtasks[1].previous_task, subtasks[0])
        self.assertEqual(subtasks[2].previous_task, subtasks[1])

        # Test next_task
        self.assertEqual(subtasks[0].next_task, subtasks[1])
        self.assertEqual(subtasks[1].next_task, subtasks[2])
        self.assertIsNone(subtasks[2].next_task)

if __name__ == '__main__':
    unittest.main()