from django.test import TestCase
from django.utils import timezone
from .models import Channel, Message

class ChannelModelTest(TestCase):
    def setUp(self):
        self.channel = Channel.objects.create(
            channel_name="Test Channel",
            channel_id="test123",
            channel_type="public"
        )

    def test_channel_creation(self):
        self.assertTrue(isinstance(self.channel, Channel))
        self.assertEqual(self.channel.__str__(), "Test Channel")

    def test_channel_fields(self):
        self.assertEqual(self.channel.channel_name, "Test Channel")
        self.assertEqual(self.channel.channel_id, "test123")
        self.assertEqual(self.channel.channel_type, "public")

    def test_channel_id_unique(self):
        with self.assertRaises(Exception):  # This will catch any exception raised
            Channel.objects.create(
                channel_name="Another Channel",
                channel_id="test123",  # Same as the first channel
                channel_type="private"
            )

class MessageModelTest(TestCase):
    def setUp(self):
        self.channel1 = Channel.objects.create(
            channel_name="Test Channel 1",
            channel_id="test123",
            channel_type="public"
        )
        self.channel2 = Channel.objects.create(
            channel_name="Test Channel 2",
            channel_id="test456",
            channel_type="private"
        )
        self.message1 = Message.objects.create(
            channel=self.channel1,
            content="This is a test message for channel 1",
            author="TestUser1"
        )
        self.message2 = Message.objects.create(
            channel=self.channel1,
            content="This is another test message for channel 1",
            author="TestUser2"
        )
        self.message3 = Message.objects.create(
            channel=self.channel2,
            content="This is a test message for channel 2",
            author="TestUser3"
        )

    def test_message_creation(self):
        self.assertTrue(isinstance(self.message1, Message))
        self.assertEqual(self.message1.__str__(), "TestUser1: This is a test message for channel 1...")

    def test_message_fields(self):
        self.assertEqual(self.message1.channel, self.channel1)
        self.assertEqual(self.message1.content, "This is a test message for channel 1")
        self.assertEqual(self.message1.author, "TestUser1")
        self.assertTrue(isinstance(self.message1.timestamp, timezone.datetime))

    def test_message_ordering(self):
        Message.objects.create(
            channel=self.channel1,
            content="This is an older message",
            author="TestUser",
            timestamp=timezone.now() - timezone.timedelta(days=1)
        )
        messages = Message.objects.all()
        self.assertEqual(messages[0], self.message3)  # The most recent message should be first

    def test_message_string_representation(self):
        long_content = "x" * 100
        message = Message.objects.create(
            channel=self.channel1,
            content=long_content,
            author="TestUser"
        )
        expected_str = f"TestUser: {'x' * 50}..."
        self.assertEqual(str(message), expected_str)

    def test_read_messages_by_channel(self):
        # Test reading messages from channel1
        channel1_messages = Message.objects.filter(channel=self.channel1)
        self.assertEqual(channel1_messages.count(), 2)
        self.assertIn(self.message1, channel1_messages)
        self.assertIn(self.message2, channel1_messages)
        self.assertNotIn(self.message3, channel1_messages)

        # Test reading messages from channel2
        channel2_messages = Message.objects.filter(channel=self.channel2)
        self.assertEqual(channel2_messages.count(), 1)
        self.assertIn(self.message3, channel2_messages)
        self.assertNotIn(self.message1, channel2_messages)
        self.assertNotIn(self.message2, channel2_messages)

    def test_read_messages_by_channel_ordering(self):
        # Create a new message in channel1 with an earlier timestamp
        earlier_message = Message.objects.create(
            channel=self.channel1,
            content="This is an earlier message",
            author="TestUser",
            timestamp=timezone.now() - timezone.timedelta(hours=1)
        )

        # Get messages from channel1, ordered by timestamp
        channel1_messages = Message.objects.filter(channel=self.channel1).order_by('-timestamp')

        # Check if the ordering is correct (most recent first)
        self.assertEqual(channel1_messages[0], self.message2)
        self.assertEqual(channel1_messages[1], self.message1)
        self.assertEqual(channel1_messages[2], earlier_message)

    def test_read_messages_by_non_existent_channel(self):
        non_existent_channel_id = "non_existent_id"
        messages = Message.objects.filter(channel__channel_id=non_existent_channel_id)
        self.assertEqual(messages.count(), 0)