import os
import curses
import time
import socket
import textwrap
from django.core.management.base import BaseCommand, CommandError

username = os.getlogin()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 7976))
client.setblocking(False)

def wrap_text(text, width):
    return [line for paragraph in text.split('\n') for line in textwrap.wrap(paragraph, width)]


def main(stdscr):
    stdscr.nodelay(True)
    sh, sw = stdscr.getmaxyx()

    curses.curs_set(1)  # Show cursor
    curses.use_default_colors()  # Use terminal's default colors
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    # Create windows
    chat_win = curses.newpad(1000, sw)  # Create a pad for scrollable content
    input_win = curses.newwin(3, sw, sh-3, 0)
    # Messages
    messages = []
    current_input = ""
    scroll_pos = 0
    max_scroll = 0
    last_update = time.time()
    # Flag to control auto-scrolling
    auto_scroll = True
    

    def add_message(msg):
        wrapped_msg = wrap_text(msg, sw - 2)  # Wrap the message
        messages.append(wrapped_msg)
        nonlocal max_scroll, scroll_pos
        max_scroll = max(0, sum(len(m) for m in messages) - (sh - 4))
        if auto_scroll:
            scroll_pos = max_scroll

    def update_screen():
        nonlocal scroll_pos
        chat_win.clear()
        input_win.clear()
        # Display chat history
        y = 0
        for msg in messages:
            for line in msg:
                chat_win.addstr(y, 1, line)
                y += 1
        # Ensure scroll position is within bounds
        scroll_pos = max(0, min(scroll_pos, max_scroll))
        # Display scrollable chat window
        chat_win.refresh(scroll_pos, 0, 0, 0, sh-4, sw-1)
        # Display input box
        input_win.box()
        input_win.addstr(1, 1, current_input[:sw-4])  # Limit input display to window width
        input_win.refresh()


    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                add_message(message)
                # Enable auto-scroll when new message arrives
                auto_scroll = True
        except BlockingIOError:
            pass  # No new message
        except Exception as e:
            add_message(f"Error: {str(e)}")
        # Update screen every 100ms
        current_time = time.time()
        if current_time - last_update > 0.2:
            update_screen()
            last_update = current_time
        key = stdscr.getch()
        if key == curses.ERR:
            time.sleep(0.01)  # Short sleep to prevent CPU hogging
            continue
        if key == ord('\n'):  # Enter key
            if current_input:
                if current_input == 'exit':
                    break
                add_message(f"You: {current_input}")
                client.send(f'{current_input}'.encode('utf-8'))
                current_input = ""
                # auto_scroll = True  # Enable auto-scroll when sending a message
        elif key == 27:  # ESC key
            break
        elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
            current_input = current_input[:-1]
        elif key == curses.KEY_UP:
            scroll_pos = max(0, scroll_pos - 1)
            auto_scroll = False  # Disable auto-scroll when manually scrolling
        elif key == curses.KEY_DOWN:
            scroll_pos = min(max_scroll, scroll_pos + 1)
            auto_scroll = True if scroll_pos == max_scroll else False
        elif key == curses.KEY_MOUSE:
            _, _, _, _, bstate = curses.getmouse()
            if bstate & curses.BUTTON4_PRESSED:  # Scroll up
                scroll_pos = max(0, scroll_pos - 3)
                auto_scroll = False
            elif bstate & (curses.BUTTON2_PRESSED | curses.BUTTON5_PRESSED):  # Scroll down
                scroll_pos = min(max_scroll, scroll_pos + 3)
                auto_scroll = True if scroll_pos == max_scroll else False
        elif 32 <= key <= 126:  # Printable ASCII characters
            current_input += chr(key)
    client.close()


class Command(BaseCommand):
    help = 'Basic AI Agent REPL'

    def handle(self, *args, **options):
        curses.wrapper(main)
