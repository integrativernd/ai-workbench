import os
import socket
import threading
import time
import signal
import json
from django.core.management.base import BaseCommand, CommandError
from llm.interpreter import get_response_mode_for_message, ResponseMode
from llm.anthropic_integration import get_basic_message
from config.settings import SYSTEM_PROMPT

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 7976

clients = []
running = True
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SOCKET_HOST, SOCKET_PORT))
server.listen()

def signal_handler(signum, frame):
    global running
    print("Shutting down...")
    running = False
    for client in clients:
        client.close()
    server.close()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_message_history():
    with open('ai_agents/management/commands/message_history.json', 'r') as f:
        existing_messages = json.loads(f.read())
    return existing_messages


def save_message_history(messages):
    with open('ai_agents/management/commands/message_history.json', 'w') as f:
        f.write(json.dumps(messages, indent=4))


def handle_client(client):
    messages = get_message_history()

    global running
    while running:
        try:
            if not running:
                break
            message_text = client.recv(1024).decode('utf-8')            
            if message_text:
                print(message_text)
                message = {
                    "role": "user",
                    "content": message_text
                }
                messages.append(message)
                response_mode = get_response_mode_for_message(message_text)
                if response_mode == ResponseMode.SIMPLE_ANSWER:
                    response_message = get_basic_message(
                        """
                        Applying critical thinking, logic, reason, ethics, and common sense
                        when analyzing the user's request can help determine the best course of action.
                        Provide a clear, concise, and accurate answer to the user's question or request.
                        If for any reason you are unable to provide an answer, please let the user know.
                        """,
                        messages,
                    )
                    response_text = response_message.content[0].text
                    client.send(response_text.encode('utf-8'))
                    assistant_message = {
                        "role": "assistant",
                        "content": response_text
                    }
                    messages.append(assistant_message)
                elif response_mode == ResponseMode.SIMPLE_QUESTION:
                    response_message = get_basic_message(
                        """
                        Applying critical thinking, logic, reason, ethics, and common sense
                        when analyzing the user's request can help determine the best course of action.
                        List the questions that need to be asked to clarify the user's request
                        and gather enough information to provide an accurate answer or solution.
                        """,
                        messages,
                    )
                    response_text = response_message.content[0].text
                    client.send(response_text.encode('utf-8'))
                    assistant_message = {
                        "role": "assistant",
                        "content": response_text
                    }
                    messages.append(assistant_message)
                elif response_mode == ResponseMode.TOOL_CALL:
                    assistant_message = {
                        "role": "assistant",
                        "content": "tool_call"
                    }
                    messages.append(assistant_message)
                    client.send("TOOL_CALL".encode('utf-8'))
                else:
                    client.send("ERROR".encode('utf-8'))
                
                # messages.append(message)
                # # save_message_history(messages)
                # assistant_message = {
                #     "role": "assistant",
                #     "content": str(response_type.type)
                # }
                # messages.append(assistant_message)
                # save_message_history(messages)
                # client.send(assistant_message['content'].encode('utf-8'))

                # response_type = get_response_type_for_message(SYSTEM_PROMPT, messages)
                # if response_type.type == ResponseType.MESSAGE:
                #     response = get_basic_message(SYSTEM_PROMPT, messages)
                #     response_text = response.content[0].text
                #     messages.append({ "role": "assistant", "content": response_text })
                #     save_message_history(messages)
                #     client.send(f'ace> {response_text}'.encode('utf-8'))
                # elif response_type.type == ResponseType.TOOL:
                #     client.send(f'ace> {response_type.type}'.encode('utf-8'))
                # else:
                #     client.send(f'{response_type.type}'.encode('utf-8'))
        except:
            break
    clients.remove(client)
    client.close()

def broadcast_queue(client):
    global running
    while running:
        time.sleep(10)
        if not running:
            break
        print('Heartbeat')

class Command(BaseCommand):
    help = 'Basic AI Agent REPL'

    def handle(self, *args, **options):
        print("Server is listening...")
        threads = []
        try:
            while running:
                try:
                    # Set a timeout for server.accept()
                    server.settimeout(1.0)
                    client, address = server.accept()
                    clients.append(client)
                    # Start a separate thread for handling each client
                    thread = threading.Thread(target=handle_client, args=(client,))
                    thread.start()
                    threads.append(thread)
                    # Start a separate thread for broadcasting messages
                    thread2 = threading.Thread(target=broadcast_queue, args=(client,))
                    thread2.start()
                    threads.append(thread2)
                except socket.timeout:
                    continue
                except socket.error:
                    break
        finally:
            server.close()
            print("Server shut down. Waiting for all threads to finish...")
            for thread in threads:
                # Wait for each thread with a timeout
                thread.join(timeout=5.0)
            print("All threads finished. Exiting.")