import subprocess
import sys


def run_applescript(script):
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip()


def open_kakaotalk():
    script = 'tell application "KakaoTalk" to activate'
    out, err = run_applescript(script)
    if err:
        print(f"Error: {err}")
    else:
        print("KakaoTalk opened.")


def get_kakaotalk_info():
    script = '''
    tell application "System Events"
        tell process "KakaoTalk"
            get name of every window
        end tell
    end tell
    '''
    out, err = run_applescript(script)
    if err:
        print(f"Error: {err}")
    else:
        print(f"KakaoTalk windows: {out}")


def send_message(friend_name, message):
    # Search for friend and send message via UI automation
    script = f'''
    tell application "KakaoTalk" to activate
    delay 1
    tell application "System Events"
        tell process "KakaoTalk"
            -- Try to find the chat window with friend_name
            keystroke "f" using command down
            delay 0.5
            keystroke "{friend_name}"
            delay 1
            keystroke return
            delay 1
            keystroke "{message}"
            delay 0.5
            keystroke return
        end tell
    end tell
    '''
    out, err = run_applescript(script)
    if err:
        print(f"Error sending message: {err}")
    else:
        print(f"Message sent to {friend_name}: {message}")


def list_windows():
    script = '''
    tell application "System Events"
        tell process "KakaoTalk"
            set windowList to {}
            repeat with w in every window
                set end of windowList to name of w
            end repeat
            return windowList
        end tell
    end tell
    '''
    out, err = run_applescript(script)
    print(f"Windows: {out}")
    if err:
        print(f"Errors: {err}")


if __name__ == "__main__":
    print("1. Opening KakaoTalk...")
    open_kakaotalk()

    import time
    time.sleep(2)

    print("\n2. Getting window info...")
    list_windows()
