import sys
import time


def loading_animation():
    animation_chars = r"/-\|"
    for i in range(20):
        sys.stdout.write(
            "\r"
            + "Waiting for a response from OpenAI "
            + animation_chars[i % len(animation_chars)]
        )
        sys.stdout.flush()
        time.sleep(0.1)
