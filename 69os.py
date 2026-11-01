import ast
import os
import subprocess
import hashlib
import secrets
import json
import re
import shutil
import tempfile
import textwrap
import sys
import time
import webbrowser
import urllib.request
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse

# 69ls - a tiny terminal OS. Everything is inside this one file.
# Run it with the Run button in VS Code, or:  python 69ls.py

os.system("")  # makes colors work in the Windows terminal

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"

GAMES = {
    "1": ("Slingshot Birds", "mouse - drag back and let go"),
    "2": ("Pipe Birds", "W/S angle, A/D power, SPACE fire"),
    "3": ("Free Kick", "mouse drag, A/D curve, W/S loft"),
}

BANNER = r"""
  ___  ___  _
 / _ \/ _ \| |  ___
| (_) \_, /| | / __|
 \__, |/_/ | | \__ \
   /_/     |_| |___/
"""


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return salt, pw_hash


def verify_password(stored_salt, stored_hash, password):
    _, pw_hash = hash_password(password, stored_salt)
    return pw_hash == stored_hash


def run_installation_and_auth():
    clear()
    print(GREEN + BANNER + RESET)
    print(CYAN + BOLD + "  69ls  -  First-Time Setup & Authentication System" + RESET)
    print("  " + "-" * 50)

    is_installed = os.path.exists(USERS_FILE) and os.path.exists(SETTINGS_FILE)

    if not is_installed:
        print(f"\n  {YELLOW}[SETUP WIZARD]{RESET} Welcome to 69ls! Let's set up your account.\n")
        
        countries = ["Australia", "United States", "United Kingdom", "Canada", "New Zealand", "Germany", "Japan", "Other"]
        print("  Select your country/region:")
        for idx, c in enumerate(countries, 1):
            print(f"    {GREEN}[{idx}]{RESET} {c}")
        
        country_choice = ask("  Enter choice number (default 1): ").strip()
        c_idx = int(country_choice) - 1 if country_choice.isdigit() and 0 <= int(country_choice) - 1 < len(countries) else 0
        selected_country = countries[c_idx]

        while True:
            username = ask("  Create Username: ").strip()
            if username:
                break
            print(f"  {RED}Username cannot be empty.{RESET}")

        while True:
            pwd1 = ask("  Create Password: ")
            pwd2 = ask("  Confirm Password: ")
            if pwd1 and pwd1 == pwd2:
                break
            print(f"  {RED}Passwords do not match or are empty. Try again.{RESET}")

        salt, pw_hash = hash_password(pwd1)
        user_data = {
            "username": username,
            "salt": salt,
            "hash": pw_hash,
            "country": selected_country
        }

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=4)

        settings_data = {
            "country": selected_country,
            "installed_at": datetime.now().isoformat()
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, indent=4)

        print(f"\n  {GREEN}Installation Complete!{RESET} Configuration saved securely.")
        time.sleep(1.5)

    print(f"\n  {BOLD}--- 69ls Login ---{RESET}")
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    attempts = 3
    while attempts > 0:
        entered_user = ask("  Username: ").strip()
        entered_pwd = ask("  Password: ")

        if entered_user == user_data["username"] and verify_password(user_data["salt"], user_data["hash"], entered_pwd):
            print(f"\n  {GREEN}Welcome back, {BOLD}{user_data['username']}{RESET}{GREEN}! Access granted.{RESET}\n")
            time.sleep(1.0)
            return user_data['username']
        else:
            attempts -= 1
            print(f"  {RED}Invalid credentials. {attempts} attempts remaining.{RESET}")

    print(f"\n  {RED}Too many failed login attempts. Shutting down.{RESET}")
    sys.exit(1)


def boot(username):
    clear()
    print(GREEN + BANNER + RESET)
    print(CYAN + BOLD + f"  69ls  -  terminal OS (Logged in as: {username})" + RESET)
    print(DIM + "  booting", end="", flush=True)
    for _ in range(5):
        time.sleep(0.25)
        print(".", end="", flush=True)
    print(RESET)
    print(f"\n  Type {YELLOW}games{RESET} for games, {YELLOW}sims{RESET} for simulators, {YELLOW}help{RESET} for commands.\n")


def show_help():
    print(f"""
  {BOLD}Commands{RESET}
    {YELLOW}games{RESET}   list your games
    {YELLOW}1 2 3{RESET}   launch a game from the list
    {YELLOW}<YouTube link>{RESET}   paste a link to watch it here
    {YELLOW}sims{RESET}    list the simulators (Windows, iOS 7)
    {YELLOW}install ffmpeg{RESET}   get sound for videos
    {YELLOW}clear{RESET}   clean the screen
    {YELLOW}time --melb{RESET}   time in a city (type {YELLOW}time{RESET} for the list)
    {YELLOW}about{RESET}   about 69ls
    {YELLOW}exit{RESET}    shut down
""")


SIMS = {
    "1": ("Windows Sim", "windows", "desktop + Start menu, Melbourne clock, web, YouTube, Shorts, TikTok"),
    "2": ("iOS 7 Sim", "ios", "phone with lock screen, Safari, YouTube, Shorts, TikTok inside it"),
}


def run_code(code, *args):
    """Run program text. Windows can't take huge code on the command line, so use a file."""
    name = "69ls_" + hashlib.md5(code.encode("utf-8")).hexdigest()[:12] + ".py"
    path = os.path.join(tempfile.gettempdir(), name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return subprocess.run([sys.executable, path, *args])


def show_sims():
    print(f"\n  {BOLD}Simulators{RESET}")
    print("  " + "-" * 44)
    for key, (name, _kind, hint) in SIMS.items():
        print(f"  {GREEN}[{key}]{RESET} {BOLD}{name}{RESET}")
        print(f"      {DIM}{hint}{RESET}")
    print("  " + "-" * 44)
    print(f"  Type {YELLOW}1{RESET} or {YELLOW}2{RESET} to start one.\n")


def launch_sim(kind):
    name = [v[0] for v in SIMS.values() if v[1] == kind][0]
    print(f"\n  {CYAN}Starting {name}...{RESET}  {DIM}(it runs right here in the terminal){RESET}")
    if not sys.stdin.isatty():
        print(f"  {RED}Open 69ls in a real terminal window to use the simulators.{RESET}\n")
        return
    print(f"  {DIM}Tip: make this terminal big (maximize the panel) for the best picture.{RESET}")
    time.sleep(1.2)
    try:
        run_terminal_sim(kind)
    except Exception as err:
        sys.stdout.write("\033[0m\033[?25h\033[2J\033[H")
        print(f"  {RED}Something went wrong: {err}{RESET}")
    print(f"\n  {GREEN}Back in 69ls.{RESET} Type {YELLOW}sims{RESET} to start another.\n")


def show_games():
    print(f"\n  {BOLD}Your games{RESET}")
    print("  " + "-" * 44)
    for key, (name, hint) in GAMES.items():
        print(f"  {GREEN}[{key}]{RESET} {BOLD}{name}{RESET}")
        print(f"      {DIM}{hint}{RESET}")
    print("  " + "-" * 44)
    print(f"  Type {YELLOW}1{RESET}, {YELLOW}2{RESET} or {YELLOW}3{RESET} to play.\n")


def launch(key):
    name = GAMES[key][0]
    print(f"\n  {CYAN}Launching {name}...{RESET}  {DIM}(close the game window to come back){RESET}\n")
    try:
        run_code(GAME_CODE[key])
    except Exception as err:
        print(f"  {RED}Something went wrong: {err}{RESET}")
    print(f"\n  {GREEN}Back in 69ls.{RESET} Type {YELLOW}games{RESET} to pick another.\n")


CITIES = {
    "melb": ("Melbourne", "Australia/Melbourne", 600, "au", "AEST", "AEDT"),
    "sydney": ("Sydney", "Australia/Sydney", 600, "au", "AEST", "AEDT"),
    "tokyo": ("Tokyo", "Asia/Tokyo", 540, "none", "JST", "JST"),
    "london": ("London", "Europe/London", 0, "eu", "GMT", "BST"),
    "paris": ("Paris", "Europe/Paris", 60, "eu", "CET", "CEST"),
    "ny": ("New York", "America/New_York", -300, "us", "EST", "EDT"),
    "la": ("Los Angeles", "America/Los_Angeles", -480, "us", "PST", "PDT"),
    "dubai": ("Dubai", "Asia/Dubai", 240, "none", "GST", "GST"),
    "delhi": ("Delhi", "Asia/Kolkata", 330, "none", "IST", "IST"),
}

ALIASES = {
    "melbourne": "melb", "newyork": "ny", "nyc": "ny",
    "losangeles": "la", "india": "delhi", "japan": "tokyo",
}


def nth_sunday(year, month, n):
    first = datetime(year, month, 1)
    first_sun = first + timedelta(days=(6 - first.weekday()) % 7)
    if n > 0:
        return first_sun + timedelta(days=7 * (n - 1))
    nxt = datetime(year + (month == 12), month % 12 + 1, 1)
    last_day = nxt - timedelta(days=1)
    return last_day - timedelta(days=(last_day.weekday() + 1) % 7)


def city_now(key):
    name, iana, std_min, rule, std_abbr, dst_abbr = CITIES[key]
    utc = datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        t = utc.astimezone(ZoneInfo(iana))
        return t, t.tzname()
    except Exception:
        pass

    naive_utc = utc.replace(tzinfo=None)
    std = naive_utc + timedelta(minutes=std_min)
    y = std.year
    dst = False
    if rule == "au":
        dst = std >= nth_sunday(y, 10, 1) + timedelta(hours=2) or \
              std < nth_sunday(y, 4, 1) + timedelta(hours=2)
    elif rule == "eu":
        dst = nth_sunday(y, 3, -1) + timedelta(hours=1) <= naive_utc < \
              nth_sunday(y, 10, -1) + timedelta(hours=1)
    elif rule == "us":
        dst = nth_sunday(y, 3, 2) + timedelta(hours=2) <= std < \
              nth_sunday(y, 11, 1) + timedelta(hours=1)
    if dst:
        return std + timedelta(hours=1), dst_abbr
    return std, std_abbr


def show_time(key):
    t, zone = city_now(key)
    clock = t.strftime("%I:%M:%S %p").lstrip("0")
    print(f"\n  {BOLD}{CITIES[key][0]}{RESET}")
    print(f"  {CYAN}{clock}{RESET} {zone}")
    print(f"  {DIM}{t.strftime('%A %d %B %Y')}{RESET}\n")


def show_all_times():
    print(f"\n  {BOLD}World clock{RESET}")
    print("  " + "-" * 44)
    for key in CITIES:
        t, zone = city_now(key)
        clock = t.strftime("%I:%M %p").lstrip("0")
        print(f"  {GREEN}{CITIES[key][0]:<13}{RESET} {CYAN}{clock:>8}{RESET} {zone:<5} {DIM}{t.strftime('%a %d %b')}{RESET}")
    print("  " + "-" * 44 + "\n")


def show_time_help():
    print(f"\n  {BOLD}Time commands{RESET}")
    for key, info in CITIES.items():
        print(f"    {YELLOW}time --{key:<7}{RESET} {info[0]}")
    print(f"    {YELLOW}time --all{RESET}     every city at once\n")


def handle_time(cmd):
    arg = cmd[4:].strip().lstrip("-").replace(" ", "").replace("-", "")
    if arg == "":
        show_time_help()
    elif arg == "all":
        show_all_times()
    else:
        key = ALIASES.get(arg, arg)
        if key in CITIES:
            show_time(key)
        else:
            print(f"  {RED}Don't know that city.{RESET} Type {YELLOW}time{RESET} to see the list.")


def is_video_link(text):
    pattern = r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/"
    return re.match(pattern, text.strip().strip("\"'"), re.I) is not None


def ensure_video_tools():
    try:
        import cv2, numpy, yt_dlp
        return True
    except ImportError:
        pass
    print(f"\n  {YELLOW}To play videos, 69ls needs 3 add-ons:{RESET} yt-dlp, opencv-python, numpy")
    answer = input("  Install them now? (y/n) ").strip().lower()
    if answer not in ("y", "yes"):
        print()
        return False
    result = subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp", "opencv-python", "numpy"])
    if result.returncode != 0:
        print(f"\n  {RED}Install failed.{RESET} Check your internet and try again.\n")
        return False
    import importlib
    importlib.invalidate_caches()
    try:
        import cv2, numpy, yt_dlp
        print(f"\n  {GREEN}Installed!{RESET}\n")
        return True
    except ImportError:
        print(f"\n  {YELLOW}Installed. Close 69ls, start it again, and paste the link again.{RESET}\n")
        return False


def get_stream(url, want_audio):
    import yt_dlp
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "best[height<=480]/bv*[height<=480]/best",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    stream = info.get("url")
    if not stream:
        for f in info.get("requested_formats") or []:
            if f.get("vcodec") not in (None, "none"):
                stream = f["url"]
                break
    audio = None
    if want_audio:
        has_both = info.get("acodec") not in (None, "none") and info.get("vcodec") not in (None, "none")
        if has_both:
            audio = stream
        else:
            try:
                a_opts = dict(opts, format="bestaudio/best")
                with yt_dlp.YoutubeDL(a_opts) as ydl:
                    audio = ydl.extract_info(url, download=False).get("url")
            except Exception:
                audio = None
    return info.get("title", "video"), stream, audio


def render_frame(cv2, frame, width, height):
    small = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    rgb = (small[:, :, ::-1] & 0xF8).tolist()
    rows = []
    for y in range(0, height, 2):
        parts = []
        last = None
        for top, bottom in zip(rgb[y], rgb[y + 1]):
            key = (top[0], top[1], top[2], bottom[0], bottom[1], bottom[2])
            if key != last:
                parts.append("\033[38;2;%d;%d;%d;48;2;%d;%d;%dm" % key)
                last = key
            parts.append("\u2580")
        rows.append("".join(parts) + "\033[0m")
    return "\n".join(rows)


def stop_key_pressed():
    if os.name == "nt":
        import msvcrt
        while msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
            elif ch.lower() in ("q", "h", "\x1b"):
                return True
        return False
    import select
    try:
        while select.select([sys.stdin], [], [], 0)[0]:
            data = os.read(sys.stdin.fileno(), 32)
            if not data:
                return False
            if any(c in data for c in b"qQhH\x1b"):
                return True
    except Exception:
        pass
    return False


def play_capture(cap, title, audio_url=None, region=None):
    import cv2
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    if fps < 1 or fps > 60:
        fps = 30
    vw = cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640
    vh = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 360
    term = shutil.get_terminal_size((100, 30))
    if region:
        rx, ry, cols, rows = region
    else:
        rx, ry, cols, rows = 1, 2, min(term.columns, 100), max(5, term.lines - 3)
    scale = min(cols / vw, rows * 2 / vh)
    width = max(2, int(vw * scale))
    height = max(2, int(vh * scale))
    height -= height % 2
    ox = rx + (cols - width) // 2
    oy = ry + (rows - height // 2) // 2

    audio = None
    if audio_url and shutil.which("ffplay"):
        audio = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_url],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    out = sys.stdout
    old_term = None
    if os.name != "nt":
        try:
            import termios
            import tty
            old_term = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
        except Exception:
            old_term = None
    if region:
        blank = "\033[0m\033[48;5;16m" + " " * cols + "\033[0m"
        out.write("\033[?25l" + "".join("\033[%d;%dH%s" % (ry + r, rx, blank) for r in range(rows)))
    else:
        header = (title[: max(10, term.columns - 16)] + "   [q] stop").ljust(term.columns - 1)
        out.write("\033[2J\033[?25l\033[1;1H" + header + "\033[0m")
    start = time.perf_counter()
    index = 0
    last_draw = 0.0
    try:
        while True:
            target = int((time.perf_counter() - start) * fps)
            if index > target:
                time.sleep(min(0.02, (index - target) / fps))
                continue
            ended = False
            while index < target - 1:
                if not cap.grab():
                    ended = True
                    break
                index += 1
            if ended:
                break
            ok, frame = cap.read()
            index += 1
            if not ok:
                break
            now = time.perf_counter()
            if now - last_draw >= 1 / 20:
                last_draw = now
                rows_text = render_frame(cv2, frame, width, height).split("\n")
                out.write("".join("\033[%d;%dH%s" % (oy + i, ox, line) for i, line in enumerate(rows_text)))
                out.flush()
            if stop_key_pressed():
                break
    except KeyboardInterrupt:
        pass
    finally:
        if old_term is not None:
            import termios
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term)
        cap.release()
        if audio:
            audio.terminate()
        if region:
            out.write("\033[0m")
        else:
            out.write("\033[0m\033[?25h\033[2J\033[H")
        out.flush()
    if not region:
        print(f"  {GREEN}Video finished.{RESET} Back in 69ls.\n")


def play_video(url):
    url = url.strip().strip("\"'")
    if not url.lower().startswith("http"):
        url = "https://" + url
    if not ensure_video_tools():
        return
    import cv2
    print(f"\n  {CYAN}Getting your video...{RESET}")
    want_audio = shutil.which("ffplay") is not None
    try:
        title, stream, audio = get_stream(url, want_audio)
    except Exception as err:
        print(f"\n  {RED}Couldn't load that video.{RESET}")
        print(f"  {DIM}{str(err)[:200]}{RESET}")
        print(f"  Tip: update the downloader with  {YELLOW}pip install -U yt-dlp{RESET}\n")
        return
    cap = cv2.VideoCapture(stream)
    if not stream or not cap.isOpened():
        print(f"\n  {RED}Couldn't open the video stream.{RESET}\n")
        return
    if not want_audio:
        print(f"  {DIM}(no sound: install ffmpeg to hear audio){RESET}")
        time.sleep(1.2)
    play_capture(cap, title, audio)


def install_ffmpeg():
    if shutil.which("ffplay"):
        print(f"\n  {GREEN}ffmpeg is already installed.{RESET} Videos will have sound.\n")
        return
    if not shutil.which("winget"):
        print(f"\n  {RED}winget wasn't found on this PC.{RESET}")
        print("  Download ffmpeg from gyan.dev/ffmpeg/builds and add its bin folder to PATH.\n")
        return
    print(f"\n  {CYAN}Installing ffmpeg with winget...{RESET}\n")
    result = subprocess.run(["winget", "install", "Gyan.FFmpeg",
                             "--accept-source-agreements", "--accept-package-agreements"])
    if result.returncode == 0:
        print(f"\n  {GREEN}Done!{RESET} Now close 69ls and VS Code, open them again, and sound will work.\n")
    else:
        print(f"\n  {RED}Install didn't finish.{RESET} Try running it in cmd:  winget install Gyan.FFmpeg\n")


ANSI_SPLIT = re.compile(r"(\x1b\[[0-9;?]*[A-Za-z])")
RS = "\033[0m"


def sty(fg=None, bg=None, bold=False, ul=False):
    s = ""
    if bold:
        s += "\033[1m"
    if ul:
        s += "\033[4m"
    if fg is not None:
        s += "\033[38;5;%dm" % fg
    if bg is not None:
        s += "\033[48;5;%dm" % bg
    return s


def term_size():
    size = shutil.get_terminal_size((100, 30))
    return size.columns, size.lines


class Canvas:
    def __init__(self, w, h, style=""):
        self.w, self.h = w, h
        self.ox = self.oy = 0
        self.cells = [[(" ", style)] * w for _ in range(h)]

    def put(self, x, y, text, style=""):
        if 0 <= y < self.h:
            row = self.cells[y]
            for i, ch in enumerate(text):
                if 0 <= x + i < self.w:
                    row[x + i] = (ch, style)

    def put_ansi(self, x, y, text, base=""):
        style, col = base, x
        for tok in ANSI_SPLIT.split(text):
            if not tok:
                continue
            if tok.startswith("\x1b["):
                style = base if tok == RS else style + tok
            else:
                self.put(col, y, tok, style)
                col += len(tok)

    def fill(self, x, y, w, h, style="", ch=" "):
        for yy in range(max(0, y), min(self.h, y + h)):
            row = self.cells[yy]
            for xx in range(max(0, x), min(self.w, x + w)):
                row[xx] = (ch, style)

    def center(self, y, text, style="", x=0, w=None):
        w = self.w if w is None else w
        self.put(x + max(0, (w - len(text)) // 2), y, text, style)

    def lines(self):
        out = []
        for row in self.cells:
            parts, last = [], None
            for ch, st in row:
                if st != last:
                    parts.append(RS + st)
                    last = st
                parts.append(ch)
            out.append("".join(parts) + RS)
        return out


class View:
    def __init__(self, cv, x, y, w, h):
        self.cv, self.x, self.y, self.w, self.h = cv, x, y, w, h

    def put(self, x, y, text, style=""):
        if not (0 <= y < self.h):
            return
        if x < 0:
            text, x = text[-x:], 0
        text = text[: max(0, self.w - x)]
        if text:
            self.cv.put(self.x + x, self.y + y, text, style)

    def put_ansi(self, x, y, text, base=""):
        style, col = base, x
        for tok in ANSI_SPLIT.split(text):
            if not tok:
                continue
            if tok.startswith("\x1b["):
                style = base if tok == RS else style + tok
            else:
                self.put(col, y, tok, style)
                col += len(tok)

    def fill(self, x, y, w, h, style="", ch=" "):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 > x0 and y1 > y0:
            self.cv.fill(self.x + x0, self.y + y0, x1 - x0, y1 - y0, style, ch)

    def center(self, y, text, style="", x=0, w=None):
        w = self.w if w is None else w
        self.put(x + max(0, (w - len(text)) // 2), y, text, style)


def show(cv):
    out = ["\033[?25l"]
    for i, line in enumerate(cv.lines()):
        out.append("\033[%d;1H%s" % (i + 1, line))
    out.append("\033[1;1H")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def _key_name(ch):
    if ch in ("\r", "\n"):
        return "enter"
    if ch == "\x1b":
        return "esc"
    if ch in ("\x08", "\x7f"):
        return "backspace"
    if ch == "\t":
        return "tab"
    if ch == "\x03":
        raise KeyboardInterrupt
    return ch


def _enable_console_mouse():
    if os.name != "nt":
        return
    try:
        import ctypes
        from ctypes import wintypes
        h = ctypes.windll.kernel32.GetStdHandle(-10)
        mode = wintypes.DWORD()
        ctypes.windll.kernel32.GetConsoleMode(h, ctypes.byref(mode))
        ctypes.windll.kernel32.SetConsoleMode(h, mode.value | 0x0080 | 0x0001 | 0x0010)
    except Exception:
        pass


_MOUSE_DOWN_AT = None


def get_key(timeout=None):
    global _MOUSE_DOWN_AT
    _enable_console_mouse()
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
        class KEY_EVENT_RECORD(ctypes.Structure):
            _fields_ = [("bKeyDown", wintypes.BOOL), ("wRepeatCount", wintypes.WORD),
                        ("wVirtualKeyCode", wintypes.WORD), ("wVirtualScanCode", wintypes.WORD),
                        ("uChar", wintypes.WCHAR), ("dwControlKeyState", wintypes.DWORD)]
        class MOUSE_EVENT_RECORD(ctypes.Structure):
            _fields_ = [("dwMousePosition", COORD), ("dwButtonState", wintypes.DWORD),
                        ("dwControlKeyState", wintypes.DWORD), ("dwEventFlags", wintypes.DWORD)]
        class INPUT_RECORD_Event(ctypes.Union):
            _fields_ = [("KeyEvent", KEY_EVENT_RECORD), ("MouseEvent", MOUSE_EVENT_RECORD)]
        class INPUT_RECORD(ctypes.Structure):
            _fields_ = [("EventType", wintypes.WORD), ("Event", INPUT_RECORD_Event)]

        h = ctypes.windll.kernel32.GetStdHandle(-10)
        end = None if timeout is None else time.time() + timeout
        while True:
            if end is not None and time.time() >= end:
                return None
            record = INPUT_RECORD()
            num_read = wintypes.DWORD()
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):
                    code = msvcrt.getwch()
                    return {"H": "up", "P": "down", "K": "left", "M": "right", "I": "pgup",
                            "Q": "pgdn", "G": "home", "O": "end"}.get(code, "")
                return _key_name(ch)
            
            events_count = wintypes.DWORD()
            ctypes.windll.kernel32.GetNumberOfConsoleInputEvents(h, ctypes.byref(events_count))
            if events_count.value > 0:
                if ctypes.windll.kernel32.ReadConsoleInputW(h, ctypes.byref(record), 1, ctypes.byref(num_read)):
                    if record.EventType == 0x0002:
                        me = record.Event.MouseEvent
                        if me.dwEventFlags == 0x0004:
                            wheel = ctypes.c_short((me.dwButtonState >> 16) & 0xFFFF).value
                            return "wheel_up" if wheel > 0 else "wheel_down"
                        point = (me.dwMousePosition.X, me.dwMousePosition.Y)
                        if me.dwEventFlags == 0 and (me.dwButtonState & 0x0001):
                            _MOUSE_DOWN_AT = point
                            return ("click", point[0], point[1])
                        if me.dwEventFlags == 0 and not me.dwButtonState and _MOUSE_DOWN_AT is not None:
                            start = _MOUSE_DOWN_AT
                            _MOUSE_DOWN_AT = None
                            dy = point[1] - start[1]
                            if abs(dy) >= 2:
                                return "wheel_down" if dy < 0 else "wheel_up"
            time.sleep(0.02)

    import select
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ready, _, _ = select.select([fd], [], [], timeout)
        if not ready:
            return None
        data = os.read(fd, 1).decode("utf-8", "ignore")
        if data == "\x1b":
            deadline = time.monotonic() + 0.06
            while len(data) < 64:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                more, _, _ = select.select([fd], [], [], remaining)
                if not more:
                    break
                chunk = os.read(fd, 63 - len(data)).decode("utf-8", "ignore")
                if not chunk:
                    break
                data += chunk
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    if not data:
        return None

    mouse = re.search(r"\x1b\[<(\d+);(\d+);(\d+)([Mm])", data)
    if mouse:
        button, x, y = map(int, mouse.groups()[:3])
        ending = mouse.group(4)
        if button & 64:
            return "wheel_up" if (button & 1) == 0 else "wheel_down"
        point = (max(0, x - 1), max(0, y - 1))
        if ending == "M" and not (button & 32) and (button & 3) == 0:
            _MOUSE_DOWN_AT = point
            return ("click", point[0], point[1])
        if ending == "M" and (button & 32) and _MOUSE_DOWN_AT is not None:
            return None
        if ending == "m" and _MOUSE_DOWN_AT is not None:
            start = _MOUSE_DOWN_AT
            _MOUSE_DOWN_AT = None
            dy = point[1] - start[1]
            if abs(dy) >= 2:
                return "wheel_down" if dy < 0 else "wheel_up"
        return None

    if data.startswith("\x1b") and len(data) > 1:
        table = {"[A": "up", "[B": "down", "[C": "right", "[D": "left", "[5~": "pgup",
                 "[6~": "pgdn", "[H": "home", "[F": "end", "OA": "up", "OB": "down",
                 "OC": "right", "OD": "left"}
        return table.get(data[1:], "")
    return _key_name(data[0])


def ask(prompt):
    _w, h = term_size()
    sys.stdout.write("\033[%d;1H\033[0m\033[K\033[?25h%s" % (h, prompt))
    sys.stdout.flush()
    try:
        text = input()
    except (EOFError, KeyboardInterrupt):
        text = ""
    sys.stdout.write("\033[?25l")
    return text.strip()


def pause_key(message="Press any key to go back"):
    w, h = term_size()
    sys.stdout.write("\033[%d;1H\033[0m\033[K  %s" % (h, message))
    sys.stdout.flush()
    get_key(None)


def safe_eval(expr):
    import operator
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
           ast.Mod: operator.mod, ast.Pow: operator.pow}

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 100:
                raise ValueError("too big")
            return ops[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            v = ev(n.operand)
            return v if isinstance(n.op, ast.UAdd) else -v
        raise ValueError("bad")

    expr = expr.replace("x", "*").replace("X", "*").replace("\u00d7", "*").replace("\u00f7", "/").replace("^", "**")
    try:
        v = ev(ast.parse(expr.strip(), mode="eval"))
    except ZeroDivisionError:
        return "Error"
    except Exception:
        return "Error"
    if isinstance(v, float):
        v = float("%.10g" % v)
        if v != v or v in (float("inf"), float("-inf")):
            return "Error"
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
    return str(v)


def melb_clock():
    t, zone = city_now("melb")
    return (t.strftime("%I:%M:%S %p").lstrip("0"), t.strftime("%I:%M %p").lstrip("0"),
            t.strftime("%d/%m/%Y"), zone, t)


class _PageParser(HTMLParser):
    BLOCK = {"p", "div", "section", "article", "header", "footer", "nav", "ul", "ol", "table", "tr",
             "br", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "form", "hr",
             "main", "aside", "dl", "dt", "dd", "figure", "figcaption", "td", "th"}
    SKIP = {"script", "style", "noscript", "svg", "template"}

    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.blocks, self.cur, self.kind = [], [], "p"
        self.skip, self.title, self.in_title = 0, "", False
        self.links, self.link_ids, self.stack = [], {}, []

    def flush(self):
        text = " ".join("".join(self.cur).split())
        if text:
            self.blocks.append((self.kind, text))
        self.cur, self.kind = [], "p"

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
            return
        if tag in self.SKIP:
            self.skip += 1
            return
        if tag in ("h1", "h2", "h3"):
            self.flush()
            self.kind = "h"
        elif tag == "li":
            self.flush()
            self.kind = "li"
        elif tag in self.BLOCK:
            self.flush()
        if tag == "a":
            num = None
            href = (a.get("href") or "").strip()
            if href and not self.skip:
                full = urljoin(self.base, href)
                if full.lower().startswith(("http://", "https://")):
                    if "duckduckgo.com/l/" in full:
                        real = parse_qs(urlparse(full).query).get("uddg")
                        if real:
                            full = real[0]
                    if full not in self.link_ids:
                        self.links.append(full)
                        self.link_ids[full] = len(self.links)
                    num = self.link_ids[full]
            self.stack.append(num)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag == "a":
            if self.stack:
                num = self.stack.pop()
                if num and not self.skip:
                    self.cur.append("[%d]" % num)
        elif tag in self.BLOCK:
            self.flush()

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.skip:
            self.cur.append(data)


def to_web_url(text):
    text = text.strip()
    if re.match(r"^https?://", text, re.I):
        return text
    if " " not in text and "." in text:
        return "https://" + text
    return "https://html.duckduckgo.com/html/?q=" + quote_plus(text)


def load_page(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-AU,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read(2500000)
        final = resp.geturl()
        enc = resp.headers.get_content_charset() or "utf-8"
        ctype = resp.headers.get_content_type()
    if "html" not in ctype and not ctype.startswith("text"):
        return {"title": final, "url": final, "links": [],
                "blocks": [("p", "This isn't a web page (%s), so it can't be shown here." % ctype)]}
    try:
        text = raw.decode(enc, errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    parser = _PageParser(final)
    parser.feed(text)
    parser.flush()
    title = " ".join(parser.title.split()) or final
    return {"title": title, "url": final, "blocks": parser.blocks, "links": parser.links}


def welcome_page():
    sites = [("Wikipedia", "https://www.wikipedia.org"), ("DuckDuckGo", "https://duckduckgo.com/html/"),
             ("BBC News", "https://www.bbc.com/news"), ("Hacker News", "https://news.ycombinator.com"),
             ("Reddit (old)", "https://old.reddit.com")]
    blocks = [("h", "Welcome to the 69ls web browser"),
              ("p", "Press g to type a web address or search words."),
              ("p", "Press f to follow a link by its number, like [3]. Press b to go back."),
              ("p", "YouTube and TikTok video links play right here in the terminal."),
              ("h", "Quick links")]
    links = []
    for name, url in sites:
        links.append(url)
        blocks.append(("li", "%s[%d]" % (name, len(links))))
    return {"title": "Start page", "url": "about:start", "blocks": blocks, "links": links}


def page_lines(page, width):
    out = []
    for kind, text in page["blocks"]:
        if kind == "h":
            out.append(("p", ""))
            out += [("h", ln) for ln in textwrap.wrap(text.upper(), width) or [""]]
            out.append(("p", ""))
        elif kind == "li":
            wrapped = textwrap.wrap(text, max(10, width - 2)) or [""]
            out += [("p", ("\u2022 " if i == 0 else "  ") + ln) for i, ln in enumerate(wrapped)]
        else:
            out += [("p", ln) for ln in (textwrap.wrap(text, width) or [""])]
            out.append(("p", ""))
    return out


class App:
    title = "App"
    bg, fg = 234, 252
    side = []

    def style(self, **kw):
        return sty(kw.get("fg", self.fg), kw.get("bg", self.bg), kw.get("bold", False), kw.get("ul", False))

    def draw(self, v, sim):
        pass

    def key(self, k, sim):
        return k in ("q", "esc")

    def click(self, x, y, sim):
        return False


def hint_row(v, text, bg=236):
    v.fill(0, v.h - 1, v.w, 1, sty(246, bg))
    v.put(1, v.h - 1, text[: v.w - 2], sty(246, bg))


class BrowserApp(App):
    title = "Web Browser"
    bg, fg = 234, 252
    side = ["g  type an address or search", "Enter / Click  open in browser", "1-9  jump to that link",
            "b  back      r  reload", "Up/Down/PgUp/PgDn  scroll", "q or Esc  close"]

    def __init__(self, start=None):
        self.page = welcome_page()
        self.hist = []
        self.scroll = 0
        self.msg = ""
        self.start = start
        self.cache_w, self.cache = None, []

    def lines(self, width):
        key = (width, id(self.page))
        if self.cache_w != key:
            self.cache = page_lines(self.page, width)
            self.cache_w = key
        return self.cache

    def open_external(self, target):
        """Open the URL directly in the graphical web browser."""
        url = to_web_url(target)
        try:
            opened = webbrowser.open(url, new=2)
            if not opened:
                if os.name == "nt":
                    os.startfile(url)
                    opened = True
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    opened = True
                else:
                    opener = shutil.which("xdg-open")
                    if opener:
                        subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        opened = True
            self.msg = "Opened in graphical browser!" if opened else "Could not open browser."
        except Exception as err:
            self.msg = "Browser error: " + str(err)[:40]

    def go(self, target, sim):
        url = to_web_url(target)
        if is_video_link(url) or re.search(r"tiktok\.com/.*/video/|vm\.tiktok\.com|vt\.tiktok\.com", url):
            self.msg = sim.play(url)
            return
        
        # Launch externally in graphical browser
        self.open_external(url)

    def draw(self, v, sim):
        if self.start:
            target, self.start = self.start, None
            self.go(target, sim)
        v.fill(0, 0, v.w, 1, sty(255, 238))
        v.put(1, 0, ("\u25cf " + self.page["url"])[: v.w - 2], sty(255, 238))
        body_h = v.h - 2
        lines = self.lines(max(10, v.w - 2))
        self.scroll = max(0, min(self.scroll, max(0, len(lines) - body_h)))
        for i, (kind, text) in enumerate(lines[self.scroll:self.scroll + body_h]):
            if kind == "h":
                v.put(1, 1 + i, text, sty(220, self.bg, bold=True))
            else:
                v.put_ansi(1, 1 + i, re.sub(r"\[(\d+)\]", "\033[1;36m[\\1]" + RS, text), self.style())
        if len(lines) > body_h:
            pos = int(self.scroll / max(1, len(lines) - body_h) * (body_h - 1))
            v.put(v.w - 1, 1 + pos, "\u2590", sty(244, self.bg))
        hint_row(v, self.msg or "g go  f link  Enter/Click launch graphical browser  q quit")

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if k == "up":
            self.scroll -= 1
        elif k in ("down", "wheel_down"):
            self.scroll += 1
        elif k == "wheel_up":
            self.scroll -= 1
        elif k in ("pgdn", " "):
            self.scroll += 8
        elif k == "pgup":
            self.scroll -= 8
        elif k == "home":
            self.scroll = 0
        elif k == "end":
            self.scroll = 10 ** 6
        elif k == "g":
            text = ask("Go to (web address or search words): ")
            if text:
                self.go(text, sim)
            sim.clear()
        elif k == "enter":
            self.open_external(self.page["url"])
        elif k == "b":
            if self.hist:
                self.page, self.scroll, self.msg = self.hist.pop(), 0, ""
        elif k == "r":
            if self.page["url"] != "about:start":
                self.go(self.page["url"], sim)
        elif k == "f" or (len(k) == 1 and k.isdigit()):
            pre = k if k.isdigit() else ""
            text = ask("Link number%s: " % (" (so far %s)" % pre if pre else ""))
            num = (pre + text).strip()
            sim.clear()
            if num.isdigit() and 1 <= int(num) <= len(self.page["links"]):
                self.go(self.page["links"][int(num) - 1], sim)
            elif num:
                self.msg = "No link number " + num
        return False

    def click(self, x, y, sim):
        width = phone_geometry()["sw"] if sim.kind == "ios" else max(10, term_size()[0] - 3)
        lines = self.lines(max(10, width - 2))
        line_index = self.scroll + max(0, y - 1)
        if 0 <= line_index < len(lines):
            text = lines[line_index][1]
            match = re.search(r"\[(\d+)\]", text)
            if match:
                number = int(match.group(1))
                if 1 <= number <= len(self.page["links"]):
                    self.go(self.page["links"][number - 1], sim)
                    return False
        self.open_external(self.page["url"])
        return False


def yt_search(query, count=12):
    import yt_dlp
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info("ytsearch%d:%s" % (count, query), download=False)
    out = []
    for e in info.get("entries") or []:
        if e and e.get("id"):
            out.append({"id": e["id"], "title": e.get("title") or "(no title)",
                        "who": e.get("channel") or e.get("uploader") or "",
                        "dur": e.get("duration")})
    return out


def dur_text(sec):
    if not sec:
        return "  ?  "
    sec = int(sec)
    return "%d:%02d" % (sec // 60, sec % 60) if sec < 3600 else "%d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)


class YouTubeApp(App):
    title = "YouTube"
    bg, fg = 234, 252
    side = ["s  search YouTube", "p  paste a video link", "Up/Down + Enter  pick a video",
            "1-9  play that result", "While playing: q or Esc stops", "q or Esc  close"]

    def __init__(self):
        self.results, self.sel, self.msg = [], 0, ""

    def draw(self, v, sim):
        v.fill(0, 0, v.w, 1, sty(255, 160, bold=True))
        v.put(1, 0, "\u25b6 YouTube", sty(255, 160, bold=True))
        if not self.results:
            v.put(1, 2, "s  search videos", sty(255, self.bg, bold=True))
            v.put(1, 3, "p  paste a link", sty(255, self.bg, bold=True))
            v.put(1, 5, "Videos play right here,", sty(246, self.bg))
            v.put(1, 6, "inside this screen.", sty(246, self.bg))
        else:
            per = max(1, (v.h - 2) // 2)
            top = max(0, min(self.sel - per // 2, len(self.results) - per))
            for i, r in enumerate(self.results[top: top + per]):
                idx = top + i
                y = 1 + i * 2
                on = idx == self.sel
                st = sty(16, 255, bold=True) if on else sty(252, self.bg)
                v.fill(0, y, v.w, 2, st)
                v.put(1, y, ("%d. %s" % (idx + 1, r["title"]))[: v.w - 2], st)
                v.put(3, y + 1, ("%s  %s" % (dur_text(r["dur"]), r["who"]))[: v.w - 4], sty(240 if on else 245, 255 if on else self.bg))
        hint_row(v, self.msg or "s search p link Enter play q quit")

    def search(self, sim):
        text = ask("Search YouTube: ")
        sim.clear()
        if not text:
            return
        if is_video_link(text):
            self.msg = sim.play(text)
            return
        if not ensure_video_tools():
            sim.clear()
            self.msg = "Add-ons needed"
            return
        sim.clear()
        self.msg = "Searching..."
        sim.redraw()
        try:
            self.results = yt_search(text)
            self.sel = 0
            self.msg = "" if self.results else "Nothing found"
        except Exception as err:
            self.msg = "Search failed: " + str(err)[:50]

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if k == "s":
            self.search(sim)
        elif k == "p":
            text = ask("Paste a YouTube link: ")
            sim.clear()
            if text:
                self.msg = sim.play(text)
        elif self.results and k == "up":
            self.sel = max(0, self.sel - 1)
        elif self.results and k == "down":
            self.sel = min(len(self.results) - 1, self.sel + 1)
        elif self.results and k == "enter":
            self.msg = sim.play("https://www.youtube.com/watch?v=" + self.results[self.sel]["id"])
        elif self.results and len(k) == 1 and k.isdigit() and 1 <= int(k) <= len(self.results):
            self.sel = int(k) - 1
            self.msg = sim.play("https://www.youtube.com/watch?v=" + self.results[self.sel]["id"])
        return False

    def click(self, x, y, sim):
        if not self.results:
            if y in (2, 3):
                self.search(sim) if y == 2 else self.key("p", sim)
            return False
        height = phone_geometry()["sh"] - 1 if sim.kind == "ios" else max(8, term_size()[1] - 3)
        per = max(1, (height - 2) // 2)
        top = max(0, min(self.sel - per // 2, len(self.results) - per))
        if y >= 1:
            idx = top + (y - 1) // 2
            if 0 <= idx < len(self.results):
                self.sel = idx
                self.msg = sim.play("https://www.youtube.com/watch?v=" + self.results[idx]["id"])
        return False


class ShortsApp(App):
    title = "YouTube Shorts"
    bg, fg = 16, 252
    side = ["t  pick a topic", "Enter  play this Short", "n / p  next / previous Short",
            "While playing: q or Esc stops", "q or Esc  close"]

    def __init__(self):
        self.items, self.idx, self.msg, self.topic = [], 0, "", ""

    def load(self, sim, topic):
        if not ensure_video_tools():
            sim.clear()
            self.msg = "Add-ons needed"
            return
        sim.clear()
        self.msg = "Finding Shorts..."
        sim.redraw()
        try:
            found = yt_search(topic + " shorts", 25)
            self.items = [r for r in found if (r["dur"] or 0) <= 70] or found
            self.idx, self.topic = 0, topic
            self.msg = "" if self.items else "Nothing found"
        except Exception as err:
            self.msg = "Search failed: " + str(err)[:50]

    def draw(self, v, sim):
        v.fill(0, 0, v.w, 1, sty(255, 197, bold=True))
        v.put(1, 0, "\u25b6 Shorts", sty(255, 197, bold=True))
        if not self.items:
            v.put(1, 2, "t  pick a topic", sty(255, self.bg, bold=True))
            v.put(1, 4, "Short videos play inside", sty(246, self.bg))
            v.put(1, 5, "this screen, one after another.", sty(246, self.bg))
        else:
            r = self.items[self.idx]
            v.center(2, "Short %d of %d" % (self.idx + 1, len(self.items)), sty(246, self.bg))
            for i, ln in enumerate(textwrap.wrap(r["title"], max(10, v.w - 4))[:4]):
                v.put(2, 4 + i, ln, sty(255, self.bg, bold=True))
            v.put(2, 9, (r["who"] or "")[: v.w - 4], sty(246, self.bg))
            v.center(11, "[ Enter = play ]", sty(16, 255, bold=True))
            v.center(13, "n = next    p = previous", sty(246, self.bg))
        hint_row(v, self.msg or "t topic Enter play n next q quit", 233)

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if k == "t":
            text = ask("Shorts topic (Enter = funny): ")
            self.load(sim, text or "funny")
        elif self.items and k in ("n", "right", "down", "wheel_down"):
            self.idx = (self.idx + 1) % len(self.items)
        elif self.items and k in ("p", "left", "up", "wheel_up"):
            self.idx = (self.idx - 1) % len(self.items)
        elif self.items and k == "enter":
            self.msg = sim.play("https://www.youtube.com/watch?v=" + self.items[self.idx]["id"])
            self.idx = (self.idx + 1) % len(self.items)
        return False

    def click(self, x, y, sim):
        height = phone_geometry()["sh"] - 1 if sim.kind == "ios" else max(8, term_size()[1] - 3)
        width = phone_geometry()["sw"] if sim.kind == "ios" else max(12, term_size()[0] - 3)
        if not self.items or (y >= height - 2 and x < width // 3):
            text = ask("Shorts topic (Enter = funny): ")
            self.load(sim, text or "funny")
        elif y >= height - 2 and x < (2 * width) // 3:
            self.idx = (self.idx - 1) % len(self.items)
        elif y >= height - 2:
            self.idx = (self.idx + 1) % len(self.items)
        else:
            self.msg = sim.play("https://www.youtube.com/watch?v=" + self.items[self.idx]["id"])
        return False


class TikTokApp(App):
    title = "TikTok"
    bg, fg = 16, 252
    side = ["a / p  add a TikTok video link", "Up/Down or mouse wheel  scroll feed",
            "Enter  open selected video in browser", "c  local comments   o  open TikTok",
            "q or Esc  close"]

    def __init__(self):
        self.path = os.path.join(os.path.expanduser("~"), ".69ls_tiktok_feed.json")
        self.posts = []
        self.sel = 0
        self.mode = "feed"
        self.comment_scroll = 0
        self.msg = ""
        self.load()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, list):
                for item in raw:
                    if not isinstance(item, dict):
                        continue
                    url = str(item.get("url", ""))
                    if not re.match(r"^https?://([a-z0-9-]+\.)?tiktok\.com/", url, re.I):
                        continue
                    comments = item.get("comments", [])
                    if not isinstance(comments, list):
                        comments = []
                    clean_comments = []
                    for comment in comments:
                        if isinstance(comment, str) and comment.strip():
                            clean_comments.append(comment[:500])
                    self.posts.append({"url": url, "title": str(item.get("title") or "TikTok video")[:100],
                                       "comments": clean_comments})
        except (OSError, ValueError, TypeError):
            self.posts = []

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.posts, f, ensure_ascii=False, indent=2)
        except OSError as err:
            self.msg = "Couldn't save feed: " + str(err)[:35]

    def selected(self):
        if not self.posts:
            return None
        self.sel = max(0, min(self.sel, len(self.posts) - 1))
        return self.posts[self.sel]

    def add_video(self, sim):
        text = ask("Paste a TikTok video URL: ")
        sim.clear()
        if not text:
            return
        url = text.strip().strip('"\'')
        if not url.lower().startswith(("http://", "https://")):
            url = "https://" + url
        if not re.match(r"^https?://([a-z0-9-]+\.)?tiktok\.com/", url, re.I):
            self.msg = "That doesn't look like a TikTok URL"
            return
        if any(p["url"] == url for p in self.posts):
            self.sel = next(i for i, p in enumerate(self.posts) if p["url"] == url)
            self.msg = "Already in your feed"
            return
        path = urlparse(url).path
        match = re.search(r"/@([^/]+)/video/(\d+)", path)
        title = ("@" + match.group(1) + "'s video") if match else "TikTok video"
        self.posts.insert(0, {"url": url, "title": title, "comments": []})
        self.sel = 0
        self.save()
        self.msg = "Added to your local feed"

    def add_comment(self, sim):
        post = self.selected()
        if not post:
            self.msg = "Add a video first"
            return
        text = ask("Write a local comment: ")
        sim.clear()
        if text:
            post["comments"].append(text[:500])
            self.save()
            self.msg = "Saved locally — not posted to TikTok"
        self.mode = "comments"
        self.comment_scroll = 10 ** 6

    def open_real_tiktok(self):
        post = self.selected()
        url = post["url"] if post else "https://www.tiktok.com/"
        try:
            opened = webbrowser.open(url, new=2)
            if not opened:
                if os.name == "nt":
                    os.startfile(url)
                    opened = True
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", url], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    opened = True
                else:
                    opener = shutil.which("xdg-open")
                    if opener:
                        subprocess.Popen([opener, url], stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                        opened = True
            self.msg = ("Opened video in your browser" if opened else "No browser URL handler found")
        except Exception as err:
            self.msg = "Couldn't open browser: " + str(err)[:40]

    def draw(self, v, sim):
        if self.mode == "comments":
            post = self.selected()
            v.fill(0, 0, v.w, 1, sty(51, 16, bold=True))
            v.put(1, 0, "\u266a TikTok / Comments", sty(51, 16, bold=True))
            if post:
                v.put(1, 2, post["title"][:v.w - 2], sty(255, self.bg, bold=True))
                v.put(1, 3, "LOCAL COMMENTS — only saved on this device", sty(220, self.bg))
                comments = post["comments"]
                body_h = max(1, v.h - 6)
                self.comment_scroll = max(0, min(self.comment_scroll, max(0, len(comments) - body_h)))
                if not comments:
                    v.put(2, 5, "No local comments yet.", sty(246, self.bg))
                    v.put(2, 6, "Press a to write the first one.", sty(246, self.bg))
                else:
                    shown = comments[self.comment_scroll:self.comment_scroll + body_h]
                    for i, comment in enumerate(shown):
                        wrapped = textwrap.wrap(comment, max(10, v.w - 5)) or [""]
                        y = 5 + sum(len(textwrap.wrap(c, max(10, v.w - 5)) or [""]) for c in comments[self.comment_scroll:self.comment_scroll + i])
                        for j, line in enumerate(wrapped):
                            if y + j < v.h - 1:
                                v.put(2, y + j, "%d. %s" % (self.comment_scroll + i + 1, line) if j == 0 else "   " + line,
                                      sty(252, self.bg))
            hint_row(v, "a add comment  Up/Down scroll  b back", 233)
            return

        v.fill(0, 0, v.w, 1, sty(51, 16, bold=True))
        v.put(1, 0, "\u266a TikTok — For You", sty(51, 16, bold=True))
        v.put(1, 1, "Saved video feed  |  a add link  Enter open video", sty(245, self.bg))
        if not self.posts:
            v.center(5, "Your feed is empty", sty(255, self.bg, bold=True))
            v.center(7, "Press a or p to add a TikTok video URL", sty(246, self.bg))
            v.center(9, "Press o to open TikTok in your browser", sty(246, self.bg))
        else:
            per = max(1, (v.h - 5) // 4)
            top = max(0, min(self.sel - per // 2, len(self.posts) - per))
            for i, post in enumerate(self.posts[top:top + per]):
                idx = top + i
                y = 3 + i * 4
                on = idx == self.sel
                st = sty(16, 255, bold=True) if on else sty(252, self.bg)
                v.fill(0, y, v.w, 3, st if on else sty(252, self.bg))
                v.put(1, y, ("%s %d. %s" % ("▶" if on else "•", idx + 1, post["title"]))[:v.w - 2], st)
                short = post["url"].replace("https://", "").replace("http://", "")
                v.put(3, y + 1, short[:v.w - 5], sty(245 if on else 244, 255 if on else self.bg))
                action = "Enter = open in browser    c = comments (%d)" % len(post["comments"])
                v.put(3, y + 2, action[:v.w - 5], sty(16 if on else 220, 255 if on else self.bg))
        hint_row(v, self.msg or "Up/Down scroll  Enter open video  c comments  a add  o browser", 233)

    def key(self, k, sim):
        if self.mode == "comments":
            if k in ("q", "esc", "b", "left"):
                self.mode = "feed"
                self.msg = ""
            elif k in ("a", "c"):
                self.add_comment(sim)
            elif k in ("up", "wheel_up"):
                self.comment_scroll = max(0, self.comment_scroll - 1)
            elif k in ("down", "wheel_down"):
                self.comment_scroll += 1
            elif k == "pgup":
                self.comment_scroll = max(0, self.comment_scroll - 8)
            elif k == "pgdn":
                self.comment_scroll += 8
            return False

        if k in ("q", "esc"):
            return True
        if k in ("a", "p"):
            self.add_video(sim)
        elif k in ("up", "k", "wheel_up") and self.posts:
            self.sel = max(0, self.sel - 1)
            self.msg = ""
        elif k in ("down", "j", "wheel_down") and self.posts:
            self.sel = min(len(self.posts) - 1, self.sel + 1)
            self.msg = ""
        elif k == "pgup" and self.posts:
            self.sel = max(0, self.sel - 5)
        elif k == "pgdn" and self.posts:
            self.sel = min(len(self.posts) - 1, self.sel + 5)
        elif k in ("enter", "v") and self.selected():
            self.open_real_tiktok()
        elif k == "c" and self.selected():
            self.mode = "comments"
            self.comment_scroll = max(0, len(self.selected()["comments"]) - 1)
        elif k == "o":
            self.open_real_tiktok()
        elif k == "d" and self.selected():
            post = self.selected()
            if confirm(sim, "Remove this saved video from your 69ls feed? (y/n) "):
                self.posts.remove(post)
                self.sel = min(self.sel, max(0, len(self.posts) - 1))
                self.save()
            self.msg = ""
        return False

    def click(self, x, y, sim):
        width = phone_geometry()["sw"] if sim.kind == "ios" else max(12, term_size()[0] - 3)
        height = phone_geometry()["sh"] - 1 if sim.kind == "ios" else max(8, term_size()[1] - 3)
        if self.mode == "comments":
            if y >= height - 2 and x < width // 2:
                self.add_comment(sim)
            elif y >= height - 2:
                self.mode = "feed"
            else:
                self.comment_scroll = max(0, self.comment_scroll + (1 if y > height // 2 else -1))
            return False
        if not self.posts:
            if y >= 1:
                self.add_video(sim)
            return False
        per = max(1, (height - 5) // 4)
        top = max(0, min(self.sel - per // 2, len(self.posts) - per))
        if y >= 3:
            idx = top + (y - 3) // 4
            if 0 <= idx < len(self.posts):
                self.sel = idx
                row_y = 3 + (idx - top) * 4
                if y >= row_y + 2 and x >= width // 2:
                    self.mode = "comments"
                    self.comment_scroll = max(0, len(self.posts[idx]["comments"]) - 1)
                else:
                    self.open_real_tiktok()
        elif y == 1:
            self.add_video(sim)
        return False


class CalcApp(App):
    title = "Calculator"
    bg, fg = 16, 255
    side = ["Type numbers and + - x / ( )", "Enter or =  work it out", "Backspace  delete", "c  clear", "q or Esc  close"]

    def __init__(self):
        self.buf, self.result = "", ""

    def draw(self, v, sim):
        v.put(v.w - 1 - len(self.buf[-(v.w - 2):]), 1, self.buf[-(v.w - 2):], sty(246, self.bg))
        shown = self.result or self.buf or "0"
        big = shown[-(v.w - 2):]
        v.put(v.w - 1 - len(big), 3, big, sty(255, self.bg, bold=True))
        rows = [["c", "(", ")", "/"], ["7", "8", "9", "x"], ["4", "5", "6", "-"], ["1", "2", "3", "+"], ["0", ".", "<", "="]]
        kh = max(1, min(2, (v.h - 6) // 5))
        kw = max(3, v.w // 4)
        for r, row in enumerate(rows):
            for c, key in enumerate(row):
                st = sty(16, 208, bold=True) if key in "/x-+=" else (sty(16, 250, bold=True) if key in "c()" else sty(255, 238, bold=True))
                x, y = c * kw, 5 + r * kh
                v.fill(x, y, kw - 1, kh, st)
                v.put(x + (kw - 1) // 2, y + kh // 2, key, st)
        hint_row(v, "digits  Enter =  c clear  q quit", 233)

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if self.result and len(k) == 1 and k in "0123456789.(":
            self.buf, self.result = "", ""
        elif self.result and len(k) == 1 and k in "+-*/x":
            self.buf, self.result = self.result, ""
        if len(k) == 1 and k in "0123456789.+-*/x()%^":
            self.buf += k
        elif k in ("enter", "="):
            if self.buf:
                self.result = safe_eval(self.buf)
        elif k == "backspace":
            self.buf, self.result = self.buf[:-1], ""
        elif k in ("c", "C"):
            self.buf, self.result = "", ""
        return False

    def click(self, x, y, sim):
        rows = [["c", "(", ")", "/"], ["7", "8", "9", "x"], ["4", "5", "6", "-"],
                ["1", "2", "3", "+"], ["0", ".", "<", "="]]
        height = phone_geometry()["sh"] - 1 if sim.kind == "ios" else max(8, term_size()[1] - 3)
        width = phone_geometry()["sw"] if sim.kind == "ios" else max(12, term_size()[0] - 3)
        kh = max(1, min(2, (height - 6) // 5))
        kw = max(3, width // 4)
        if y >= 5:
            r = (y - 5) // kh
            c = x // kw
            if 0 <= r < len(rows) and 0 <= c < 4:
                key = rows[r][c]
                if key == "<":
                    self.buf, self.result = self.buf[:-1], ""
                else:
                    self.key(key, sim)
        return False


class ClockApp(App):
    title = "World Clock"
    bg, fg = 16, 255
    side = ["Live world clock", "Melbourne is first", "q or Esc  close"]

    def draw(self, v, sim):
        v.center(0, "World Clock", sty(255, self.bg, bold=True))
        order = ["melb", "tokyo", "london", "paris", "ny", "la", "dubai", "delhi", "sydney"]
        for i, key in enumerate(order[: max(1, (v.h - 2) // 2)]):
            t, zone = city_now(key)
            y = 1 + i * 2
            hot = key == "melb"
            v.put(1, y, CITIES[key][0] + (" (home)" if hot else ""), sty(208 if hot else 255, self.bg, bold=hot))
            v.put(1, y + 1, t.strftime("%A"), sty(244, self.bg))
            clock = t.strftime("%I:%M %p").lstrip("0") + " " + zone
            v.put(v.w - 1 - len(clock), y, clock, sty(208 if hot else 255, self.bg, bold=True))
        hint_row(v, "q close", 233)


class NotesApp(App):
    title = "Notes"
    bg, fg = 229, 94
    side = ["a or Enter  add a line", "d  delete the last line", "q or Esc  close", "(saved automatically)"]

    def __init__(self):
        self.path = os.path.join(os.path.expanduser("~"), "69ls_notes.txt")
        try:
            with open(self.path, encoding="utf-8") as f:
                self.lines = f.read().splitlines()
        except OSError:
            self.lines = []

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.lines))
        except OSError:
            pass

    def draw(self, v, sim):
        v.fill(0, 0, v.w, v.h, sty(94, 229))
        v.put(1, 0, "Notes", sty(94, 229, bold=True))
        shown = []
        for ln in self.lines:
            shown += textwrap.wrap(ln, max(10, v.w - 3)) or [""]
        shown = shown[-(v.h - 3):]
        if not shown:
            v.put(1, 2, "(empty - press a to write)", sty(137, 229))
        for i, ln in enumerate(shown):
            v.put(1, 2 + i, ln, sty(94, 229))
        hint_row(v, "a add line  d delete  q close", 187)

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if k in ("a", "enter"):
            text = ask("New line: ")
            sim.clear()
            if text:
                self.lines.append(text)
                self.save()
        elif k == "d" and self.lines:
            self.lines.pop()
            self.save()
        return False

    def click(self, x, y, sim):
        if y >= max(3, 18):
            text = ask("New line: ")
            sim.clear()
            if text:
                self.lines.append(text)
                self.save()
        elif y >= 2 and self.lines:
            self.lines.pop()
            self.save()
        return False


class GamesApp(App):
    title = "Games"
    bg, fg = 235, 252
    side = ["1-3  play a game", "q or Esc  close"]

    def draw(self, v, sim):
        v.put(1, 1, "Pick a game:", sty(255, self.bg, bold=True))
        for i, (key, (name, hint)) in enumerate(GAMES.items()):
            v.put(1, 3 + i * 3, "%s  %s" % (key, name), sty(114, self.bg, bold=True))
            v.put(4, 4 + i * 3, hint[: v.w - 6], sty(245, self.bg))
        hint_row(v, "1-3 play  q close", 233)

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if k in GAMES:
            sys.stdout.write(RS + "\033[2J\033[H\033[?25h")
            launch(k)
            sim.pause()
            sim.clear()
        return False

    def click(self, x, y, sim):
        if y >= 2:
            idx = max(0, min(len(GAMES) - 1, (y - 3) // 3))
            key = list(GAMES)[idx]
            if key in GAMES:
                sys.stdout.write(RS + "\033[2J\033[H\033[?25h")
                launch(key)
                sim.pause()
                sim.clear()
        return False


class AlertApp(App):
    title = "Alert"
    bg, fg = 234, 252

    def __init__(self, title, message):
        self.t, self.m = title, message

    def draw(self, v, sim):
        v.fill(0, 0, v.w, v.h, sty(250, 236))
        bw = min(v.w - 4, 30)
        lines = textwrap.wrap(self.m, bw - 4)
        bh = len(lines) + 5
        y0 = max(1, (v.h - bh) // 2)
        x0 = (v.w - bw) // 2
        v.fill(x0, y0, bw, bh, sty(16, 253))
        v.center(y0 + 1, self.t, sty(16, 253, bold=True), x0, bw)
        for i, ln in enumerate(lines):
            v.center(y0 + 2 + i, ln, sty(16, 253), x0, bw)
        v.center(y0 + bh - 2, "[ OK ]", sty(27, 253, bold=True), x0, bw)

    def key(self, k, sim):
        return True

    def click(self, x, y, sim):
        return True


class SettingsApp(App):
    title = "Settings"
    bg, fg = 254, 16
    side = ["Up/Down  choose a row", "Left/Right or Enter  change it", "q or Esc  close"]

    def __init__(self):
        self.sel = 0

    def rows(self, sim):
        return [("Airplane Mode", "ON" if sim.air else "OFF"), ("Wi-Fi", "ON" if sim.wifi else "OFF"),
                ("Wallpaper", "%d / %d" % (sim.wi + 1, len(WALLS))), ("Software Version", "7.1"),
                ("Time Zone", "Melbourne"), ("Carrier", "Telstra")]

    def draw(self, v, sim):
        v.put(1, 0, "Settings", sty(16, self.bg, bold=True))
        for i, (name, val) in enumerate(self.rows(sim)):
            on = i == self.sel
            st = sty(255, 27) if on else sty(16, 255)
            v.fill(0, 2 + i * 2, v.w, 1, st)
            v.put(1, 2 + i * 2, name, st)
            v.put(v.w - 1 - len(val), 2 + i * 2, val, st if on else sty(244, 255))
        hint_row(v, "Up/Down  Left/Right  q close", 250)

    def key(self, k, sim):
        if k in ("q", "esc"):
            return True
        if k == "up":
            self.sel = max(0, self.sel - 1)
        elif k == "down":
            self.sel = min(5, self.sel + 1)
        elif k in ("left", "right", "enter", " "):
            step = -1 if k == "left" else 1
            if self.sel == 0:
                sim.air = not sim.air
            elif self.sel == 1:
                sim.wifi = not sim.wifi
            elif self.sel == 2:
                sim.wi = (sim.wi + step) % len(WALLS)
        return False

    def click(self, x, y, sim):
        idx = (y - 2) // 2
        if 0 <= idx < 6:
            self.sel = idx
            if idx in (0, 1):
                self.key("enter", sim)
            elif idx == 2:
                self.key("right", sim)
        return False


WALLS = [[53, 89, 125, 168, 174, 215], [17, 18, 24, 30, 31, 37], [27, 33, 39, 45, 51, 87],
         [130, 166, 208, 214, 220, 226], [22, 28, 34, 40, 46, 83]]

BIG = {"0": ["#####", "#   #", "#   #", "#   #", "#####"], "1": ["  #  ", " ##  ", "  #  ", "  #  ", "#####"],
       "2": ["#####", "    #", "#####", "#    ", "#####"], "3": ["#####", "    #", " ####", "    #", "#####"],
       "4": ["#   #", "#   #", "#####", "    #", "    #"], "5": ["#####", "#    ", "#####", "    #", "#####"],
       "6": ["#####", "#    ", "#####", "#   #", "#####"], "7": ["#####", "    #", "   # ", "  #  ", "  #  "],
       "8": ["#####", "#   #", "#####", "#   #", "#####"], "9": ["#####", "#   #", "#####", "    #", "#####"],
       ":": ["  ", "##", "  ", "##", "  "]}


class Sim:
    def __init__(self, kind):
        self.kind = kind
        self.wi, self.wifi, self.air = 0, True, False
        self.redraw = lambda: None

    def clear(self):
        sys.stdout.write(RS + "\033[2J")
        sys.stdout.flush()

    def pause(self):
        pause_key()

    def video_region(self):
        w, h = term_size()
        if self.kind == "windows":
            return (2, 2, max(10, w - 3), max(4, h - 4))
        g = phone_geometry()
        return (g["px"] + 3, g["py"] + 5, g["sw"], g["sh"] - 1)

    def play(self, url):
        url = url.strip().strip("\"'")
        if not url.lower().startswith("http"):
            url = "https://" + url
        if self.air:
            return "Airplane Mode is on"
        if not ensure_video_tools():
            self.clear()
            return "Video add-ons not installed"
        self.clear()
        self.redraw()
        x, y, cols, rows = self.video_region()
        sys.stdout.write("\033[%d;%dH%s%s%s" % (y + rows // 2, x + 1, sty(255, 16), "Getting your video...", RS))
        sys.stdout.flush()
        import cv2
        try:
            title, stream, audio = get_stream(url, shutil.which("ffplay") is not None)
        except Exception as err:
            self.clear()
            return "Couldn't load: " + str(err)[:40]
        cap = cv2.VideoCapture(stream)
        if not stream or not cap.isOpened():
            self.clear()
            return "Couldn't open that video"
        play_capture(cap, title, audio, region=(x, y, cols, rows))
        self.clear()
        return "Video finished"


def confirm(sim, prompt):
    ok = ask(prompt).lower().startswith("y")
    sim.clear()
    return ok


def make_app(app_id):
    return {"web": BrowserApp, "safari": BrowserApp, "yt": YouTubeApp, "shorts": ShortsApp, "tt": TikTokApp,
            "note": NotesApp, "notes": NotesApp, "calc": CalcApp, "clock": ClockApp, "games": GamesApp,
            "settings": SettingsApp}[app_id]()


WIN_ICONS = [("Web Browser", "web", 25, "@", "Web"), ("YouTube", "yt", 160, "\u25b6", "YouTube"),
             ("YT Shorts", "shorts", 197, "S", "Shorts"), ("TikTok", "tt", 16, "\u266a", "TikTok"),
             ("Notepad", "note", 39, "\u2261", "Notepad"), ("Calculator", "calc", 60, "=", "Calc"),
             ("Clock", "clock", 98, "O", "Clock"), ("Games", "games", 34, "G", "Games")]


def win_taskbar(cv, y, menu_open=False):
    cv.fill(0, y, cv.w, 1, sty(252, 236))
    cv.put(0, y, " \u2590\u2588\u258c Start ", sty(255, 27 if menu_open else 25, bold=True))
    t, _short, d, zone, _ = melb_clock()
    right = " Melbourne  %s %s   %s " % (t, zone, d)
    x = 13
    for item in WIN_ICONS[:6]:
        label = " %s " % item[4]
        if x + len(label) < cv.w - len(right) - 1:
            cv.put(x, y, label, sty(250, 238))
            x += len(label) + 1
    cv.put(max(x, cv.w - len(right)), y, right, sty(123, 236, bold=True))


def host_windows(sim, app):
    while True:
        def render():
            w, h = term_size()
            cv = Canvas(w - 1, h, sty(app.fg, app.bg))
            cv.fill(0, 0, cv.w, 1, sty(255, 25, bold=True))
            cv.put(1, 0, "\u25a3 " + app.title, sty(255, 25, bold=True))
            right = " \u2500  \u25a1  \u2715 "
            cv.put(cv.w - len(right), 0, right, sty(255, 25, bold=True))
            win_taskbar(cv, h - 1)
            view = View(cv, 1, 1, cv.w - 2, max(3, h - 3))
            app.draw(view, sim)
            show(cv)
        sim.redraw = render
        render()
        res = get_key(1.0)
        if res is None:
            continue
        if isinstance(res, tuple) and res[0] == "click":
            _typ, cx, cy = res
            w, h = term_size()
            if cy == 0 and cx >= (w - 1) - 6:
                return
            if 1 <= cy < h - 1:
                view_x, view_y = cx - 1, cy - 1
                if app.click(view_x, view_y, sim):
                    return
            continue
        k = res
        if app.key(k, sim):
            return


def draw_desktop(sim, sel, menu, msel):
    w, h = term_size()
    cv = Canvas(w - 1, h, sty(255, 18))
    cv.fill(0, 0, cv.w, h - 1, sty(255, 18))
    if cv.w > 60 and h > 12:
        cx, cy = cv.w * 2 // 3, (h - 1) // 2
        for dx, dy, col in ((0, 0, 39), (1, 0, 45), (0, 1, 33), (1, 1, 27)):
            cv.fill(cx - 8 + dx * 8, cy - 2 + dy * 3, 7, 2, sty(255, col))
    th = 2 if h >= 24 else 1
    per = max(1, (h - 2) // (th + 2))
    for i, (name, _id, color, glyph, _short) in enumerate(WIN_ICONS):
        col, row = divmod(i, per)
        x, y = 3 + col * 15, 1 + row * (th + 2)
        on = i == sel and not menu
        cv.fill(x, y, 8, th, sty(255, color, bold=True))
        cv.put(x + 3, y + th // 2, glyph, sty(255, color, bold=True))
        if on:
            for r in range(th):
                cv.put(x - 1, y + r, "\u258c", sty(255, 18))
                cv.put(x + 8, y + r, "\u2590", sty(255, 18))
        cv.center(y + th, name, sty(16, 255, bold=True) if on else sty(255, 18), x - 2, 12)
    if menu:
        n = len(WIN_ICONS) + 1
        mh = n + 3
        cv.fill(0, h - 1 - mh, 26, mh, sty(255, 236))
        cv.put(2, h - mh, "Apps", sty(250, 236, bold=True))
        for i in range(n):
            name = WIN_ICONS[i][0] if i < len(WIN_ICONS) else "Shut down"
            st = sty(255, 25, bold=True) if i == msel else sty(252, 236)
            cv.fill(1, h - mh + 1 + i, 24, 1, st)
            cv.put(3, h - mh + 1 + i, "%s%s" % ("" if i >= len(WIN_ICONS) else "%d  " % (i + 1), name), st)
    win_taskbar(cv, h - 1, menu)
    show(cv)


def run_windows_sim():
    sim = Sim("windows")
    sim.clear()
    sel, menu, msel = 0, False, 0

    def opener(idx):
        host_windows(sim, make_app(WIN_ICONS[idx][1]))
        sim.clear()

    while True:
        w, h = term_size()
        sim.redraw = lambda: draw_desktop(sim, sel, menu, msel)
        draw_desktop(sim, sel, menu, msel)
        res = get_key(1.0)
        if res is None:
            continue
        if isinstance(res, tuple) and res[0] == "click":
            _typ, cx, cy = res
            if cy == h - 1 and cx < 12:
                menu = not menu
                continue
            th = 2 if h >= 24 else 1
            per = max(1, (h - 2) // (th + 2))
            clicked_icon = None
            for i, (name, _id, color, glyph, _short) in enumerate(WIN_ICONS):
                col, row = divmod(i, per)
                x, y = 3 + col * 15, 1 + row * (th + 2)
                if x <= cx < x + 8 and y <= cy <= y + th:
                    clicked_icon = i
                    break
            if clicked_icon is not None:
                sel = clicked_icon
                opener(sel)
                continue
            if menu:
                n = len(WIN_ICONS) + 1
                mh = n + 3
                menu_y0 = h - 1 - mh
                if 0 <= cx < 26 and menu_y0 + 1 <= cy <= menu_y0 + n:
                    idx = cy - (menu_y0 + 1)
                    menu = False
                    if idx == len(WIN_ICONS):
                        if confirm(sim, "Shut down? (y/n) "):
                            return
                    elif 0 <= idx < len(WIN_ICONS):
                        opener(idx)
                    continue
                else:
                    menu = False
            continue

        k = res
        th = 2 if h >= 24 else 1
        per = max(1, (h - 2) // (th + 2))
        n = len(WIN_ICONS)
        if menu:
            if k == "up":
                msel = (msel - 1) % (n + 1)
            elif k == "down":
                msel = (msel + 1) % (n + 1)
            elif k == "enter":
                menu = False
                if msel == n:
                    if confirm(sim, "Shut down? (y/n) "):
                        return
                else:
                    opener(msel)
            elif k in ("esc", "tab", "s"):
                menu = False
            continue
        if k == "up" and sel % per:
            sel -= 1
        elif k == "down" and sel % per < per - 1 and sel + 1 < n:
            sel += 1
        elif k == "left" and sel - per >= 0:
            sel -= per
        elif k == "right" and sel + per < n:
            sel += per
        elif k == "enter":
            opener(sel)
        elif k in ("s", "tab"):
            menu, msel = True, 0
        elif len(k) == 1 and k.isdigit() and 1 <= int(k) <= n:
            opener(int(k) - 1)
        elif k in ("q", "esc"):
            if confirm(sim, "Shut down? (y/n) "):
                return


def phone_geometry():
    w, h = term_size()
    sw = 36
    sh = max(8, min(24, h - 6))
    pw, ph = sw + 4, sh + 6
    side = (w - 1) >= pw + 34
    px = max(0, ((w - 1 - pw) // 2) - (14 if side else 0))
    py = max(0, (h - ph) // 2)
    return {"w": w, "h": h, "sw": sw, "sh": sh, "pw": pw, "ph": ph, "px": px, "py": py,
            "side": side, "ok": (w - 1) >= pw and h >= 15}


def draw_shell(cv, g):
    px, py, pw, ph = g["px"], g["py"], g["pw"], g["ph"]
    edge = sty(245, 237)
    cv.fill(px, py, pw, ph, sty(250, 237))
    cv.put(px, py, "\u256d" + "\u2500" * (pw - 2) + "\u256e", edge)
    for y in range(1, ph - 1):
        cv.put(px, py + y, "\u2502", edge)
        cv.put(px + pw - 1, py + y, "\u2502", edge)
    cv.put(px, py + ph - 1, "\u2570" + "\u2500" * (pw - 2) + "\u256f", edge)
    cv.put(px + pw // 2 - 4, py + 1, "\u25ac" * 8, sty(240, 237))
    cv.put(px + pw // 2 - 8, py + 1, "\u2022", sty(60, 237))
    cv.put(px + pw // 2 - 1, py + ph - 2, "\u25ef", sty(252, 237))
    return View(cv, px + 2, py + 3, g["sw"], g["sh"])


def wall_color(wi, row, rows):
    stops = WALLS[wi]
    return stops[min(len(stops) - 1, row * len(stops) // max(1, rows))]


def paint_wall(scr, wi):
    for r in range(scr.h):
        scr.fill(0, r, scr.w, 1, sty(255, wall_color(wi, r, scr.h)))


def status_bar(scr, sim, bg, fg=255):
    scr.fill(0, 0, scr.w, 1, sty(fg, bg))
    left = " Telstra " + ("\u2708" if sim.air else ("\u2248" if sim.wifi else " "))
    scr.put(0, 0, left, sty(fg, bg, bold=True))
    scr.center(0, melb_clock()[1], sty(fg, bg, bold=True))
    right = "100% \u25ae\u25ae\u25ae "
    scr.put(scr.w - len(right), 0, right, sty(fg, bg, bold=True))


HOME_APPS = [("Messages", "msg", 34, "\u2709"), ("Calendar", "cal", 255, ""), ("Photos", "photos", 213, "\u273f"),
             ("Camera", "cam", 243, "\u25c9"), ("Weather", "weather", 33, "\u2600"), ("Clock", "clock", 255, ""),
             ("Maps", "maps", 71, "M"), ("Notes", "notes", 221, "\u2261"), ("YouTube", "yt", 160, "\u25b6"),
             ("YT Shorts", "shorts", 197, "S"), ("TikTok", "tt", 16, "\u266a"), ("Calc", "calc", 240, "="),
             ("Settings", "settings", 246, "*"), ("App Store", "store", 27, "A")]
DOCK_APPS = [("Phone", "phone", 34, "T"), ("Mail", "mail", 33, "@"), ("Safari", "safari", 255, "\u25ce"),
             ("Music", "music", 202, "\u266b")]
ALL_IOS = HOME_APPS + DOCK_APPS


def draw_tile(scr, x, y, th, app, sim, on):
    name, app_id, color, glyph = app
    fg = 16 if color in (255, 221, 213) else 255
    if app_id == "cal":
        t = melb_clock()[4]
        if th == 2:
            scr.fill(x, y, 7, 1, sty(255, 196, bold=True))
            scr.center(y, t.strftime("%a").upper(), sty(255, 196, bold=True), x, 7)
            scr.fill(x, y + 1, 7, 1, sty(16, 255, bold=True))
            scr.center(y + 1, str(t.day), sty(16, 255, bold=True), x, 7)
        else:
            scr.fill(x, y, 7, 1, sty(16, 255, bold=True))
            scr.center(y, str(t.day), sty(16, 255, bold=True), x, 7)
    elif app_id == "clock":
        scr.fill(x, y, 7, th, sty(16, 255, bold=True))
        scr.center(y + th // 2, melb_clock()[1].replace(" PM", "").replace(" AM", ""), sty(16, 255, bold=True), x, 7)
    else:
        st = sty(51 if app_id == "tt" else (27 if app_id == "safari" else fg), color, bold=True)
        scr.fill(x, y, 7, th, st)
        scr.center(y + th // 2, glyph, st, x, 7)
    if on:
        for r in range(th):
            scr.put(x - 1, y + r, "\u258c", sty(255, 255))
            scr.put(x + 7, y + r, "\u2590", sty(255, 255))


def draw_home(scr, sim, sel):
    paint_wall(scr, sim.wi)
    status_bar(scr, sim, wall_color(sim.wi, 0, scr.h))
    sh, sw = scr.h, scr.w
    if sh < 16:
        rows = sh - 2
        top = max(0, min(sel - rows // 2, len(ALL_IOS) - rows))
        for i, (name, _id, color, glyph) in enumerate(ALL_IOS[top: top + rows]):
            on = top + i == sel
            bg = wall_color(sim.wi, i + 1, sh)
            scr.fill(0, 1 + i, sw, 1, sty(16, 255, bold=True) if on else sty(255, bg))
            scr.put(1, 1 + i, " %s " % (glyph or name[0]), sty(255 if color != 255 else 16, color, bold=True))
            scr.put(6, 1 + i, name, sty(16, 255, bold=True) if on else sty(255, bg, bold=True))
        return
    th = 2 if sh >= 22 else 1
    cell_h, cw = th + 2, sw // 4
    for i, app in enumerate(HOME_APPS):
        r, c = divmod(i, 4)
        x, y = c * cw + (cw - 7) // 2, 2 + r * cell_h
        draw_tile(scr, x, y, th, app, sim, i == sel)
        bg = wall_color(sim.wi, y + th, sh)
        st = sty(16, 255, bold=True) if i == sel else sty(255, bg)
        scr.center(y + th, app[0][:cw], st, c * cw, cw)
    dock_h = th + 1
    for r in range(sh - dock_h, sh):
        scr.fill(0, r, sw, 1, sty(255, 60))
    scr.center(sh - dock_h - 1, "\u25cf \u25cb", sty(255, wall_color(sim.wi, sh - dock_h - 1, sh)))
    for i, app in enumerate(DOCK_APPS):
        x = i * cw + (cw - 7) // 2
        draw_tile(scr, x, sh - dock_h, th, app, sim, 14 + i == sel)


def home_move(sel, k):
    n = len(HOME_APPS)
    if sel < n:
        r, c = divmod(sel, 4)
        if k == "left":
            return max(0, sel - 1)
        if k == "right":
            return min(n - 1, sel + 1)
        if k == "up":
            return sel - 4 if sel >= 4 else sel
        if k == "down":
            return sel + 4 if sel + 4 < n else n + min(c, 3)
    else:
        d = sel - n
        if k == "left":
            return n + max(0, d - 1)
        if k == "right":
            return n + min(3, d + 1)
        if k == "up":
            for r in (3, 2, 1, 0):
                if r * 4 + d < n:
                    return r * 4 + d
    return sel


def phone_once(sim, draw, side=None):
    g = phone_geometry()
    cv = Canvas(g["w"] - 1, g["h"], sty(252, 16))
    if not g["ok"]:
        cv.put(1, 1, "Make this window bigger to see the phone", sty(255, 16))
        cv.put(1, 2, "(it needs about 45 columns and 15 rows).", sty(255, 16))
        show(cv)
        return
    scr = draw_shell(cv, g)
    draw(scr)
    if g["side"] and side:
        x = g["px"] + g["pw"] + 3
        cv.put(x, g["py"] + 2, "iOS 7 simulator", sty(255, 16, bold=True))
        cv.put(x, g["py"] + 3, "Melbourne time, " + melb_clock()[3], sty(123, 16))
        for i, line in enumerate(side):
            cv.put(x, g["py"] + 5 + i, line, sty(245, 16))
    sys.stdout.write("\033[?25l")
    show(cv)


def phone_run(sim, draw, on_key, side=None):
    while True:
        sim.redraw = lambda: phone_once(sim, draw, side)
        phone_once(sim, draw, side)
        res = get_key(1.0)
        if res is None:
            continue
        g = phone_geometry()
        if isinstance(res, tuple) and res[0] == "click":
            _typ, cx, cy = res
            vx = cx - (g["px"] + 2)
            vy = cy - (g["py"] + 3)
            if cy == g["py"] + g["ph"] - 2 and abs(cx - (g["px"] + g["pw"] // 2)) <= 1:
                return ("home", None)
            r = on_key(("click", vx, vy))
            if r is not None:
                return r
            continue
        k = res
        r = on_key(k)
        if r is not None:
            return r


def draw_lock(scr, sim, knob):
    paint_wall(scr, sim.wi)
    status_bar(scr, sim, wall_color(sim.wi, 0, scr.h))
    _t, short, _d, zone, dt = melb_clock()
    hhmm = short.replace(" PM", "").replace(" AM", "")
    if scr.h >= 16:
        width = sum(len(BIG[c][0]) + 1 for c in hhmm) - 1
        x0 = (scr.w - width) // 2
        for r in range(5):
            x = x0
            for c in hhmm:
                for i, ch in enumerate(BIG[c][r]):
                    if ch == "#":
                        scr.put(x + i, 3 + r, " ", sty(255, 255))
                x += len(BIG[c][r]) + 1
        ytxt = 9
    else:
        scr.center(3, hhmm, sty(255, wall_color(sim.wi, 3, scr.h), bold=True))
        ytxt = 5
    bg = lambda r: wall_color(sim.wi, r, scr.h)
    scr.center(ytxt, dt.strftime("%A %d %B"), sty(255, bg(ytxt), bold=True))
    scr.center(ytxt + 1, "Melbourne \u00b7 " + zone, sty(255, bg(ytxt + 1)))
    bw = scr.w - 6
    by = scr.h - 3
    scr.fill(3, by, bw, 1, sty(250, 238))
    scr.center(by, "slide to unlock >>", sty(250, 238), 3, bw)
    kx = 3 + int(knob * (bw - 5))
    scr.fill(kx, by, 5, 1, sty(16, 253, bold=True))
    scr.center(by, "( \u25b6 )", sty(16, 253, bold=True), kx, 5)


def lock_screen(sim):
    side = ["Click or press Enter / Right", "to slide to unlock.", "", "q  turn the phone off"]
    knob = 0.0

    def draw(scr):
        draw_lock(scr, sim, knob)

    def on_key(arg):
        nonlocal knob
        if isinstance(arg, tuple) and arg[0] == "click":
            _typ, vx, vy = arg
            geometry = phone_geometry()
            by = geometry["sh"] - 3
            bw = geometry["sw"] - 6
            if vy == by and 3 <= vx <= 3 + bw:
                for step in range(0, 11):
                    knob = step / 10
                    phone_once(sim, draw, side)
                    time.sleep(0.03)
                return "unlocked"
            return None
        k = arg
        if k in ("enter", "right", " "):
            for step in range(0, 11):
                knob = step / 10
                phone_once(sim, draw, side)
                time.sleep(0.03)
            return "unlocked"
        if k in ("q", "esc"):
            return "quit"
        return None

    return phone_run(sim, draw, on_key, side)


def open_ios_app(sim, app_id):
    messages = {"cal": ("Calendar", "Today is " + melb_clock()[4].strftime("%A %d %B") + " (Melbourne time)."),
                "weather": ("Weather", "Sunny in the sim. Weather isn't connected."),
                "phone": ("Phone", "Calls aren't part of the sim.")}
    if app_id in ("clock", "calc", "notes", "settings", "safari", "yt", "shorts", "tt"):
        app = make_app(app_id)
    else:
        title, text = messages.get(app_id, (dict((a[1], a[0]) for a in ALL_IOS).get(app_id, "App"),
                                            "This app isn't part of the sim. Try YouTube, Shorts, TikTok, Safari, Calculator, Notes, Clock or Settings."))
        app = AlertApp(title, text)
    light = app.bg in (254, 229, 255)

    def draw(scr):
        scr.fill(0, 0, scr.w, scr.h, sty(app.fg, app.bg))
        status_bar(scr, sim, app.bg, 16 if light else 255)
        app.draw(View(scr, 0, 1, scr.w, scr.h - 1), sim)

    def on_key(arg):
        if isinstance(arg, tuple) and arg[0] == "click":
            _typ, vx, vy = arg
            g = phone_geometry()
            if vy >= g["sh"]:
                return True
            app_y = vy - 1
            if app_y >= 0:
                if app.click(vx, app_y, sim):
                    return True
            return None
        return True if app.key(arg, sim) else None

    phone_run(sim, draw, on_key, (app.side or []) + ["", "Esc or q  =  Home button"])


def run_ios_sim():
    sim = Sim("ios")
    sim.clear()
    if lock_screen(sim) == "quit" and confirm(sim, "Turn the phone off? (y/n) "):
        return
    sel = 0
    side = ["Click apps to open", "Arrow keys  move", "Enter  open an app", "l  lock the phone", "q  turn the phone off"]

    def draw(scr):
        draw_home(scr, sim, sel)

    def on_key(arg):
        nonlocal sel
        sh = phone_geometry()["sh"]
        if isinstance(arg, tuple) and arg[0] == "click":
            _typ, vx, vy = arg
            if sh < 16:
                if 1 <= vy < sh - 1:
                    idx = vy - 1
                    if 0 <= idx < len(ALL_IOS):
                        sel = idx
                        return ("open", ALL_IOS[sel][1])
                return None
            th = 2 if sh >= 22 else 1
            cell_h, cw = th + 2, 36 // 4
            for i, app in enumerate(HOME_APPS):
                r, c = divmod(i, 4)
                y = 2 + r * cell_h
                if c * cw <= vx < (c + 1) * cw and y <= vy <= y + th:
                    sel = i
                    return ("open", ALL_IOS[sel][1])
            dock_h = th + 1
            dock_y = sh - dock_h
            if dock_y <= vy < sh:
                for i, app in enumerate(DOCK_APPS):
                    if i * cw <= vx < (i + 1) * cw and dock_y <= vy < dock_y + th:
                        sel = 14 + i
                        return ("open", ALL_IOS[sel][1])
            return None

        k = arg
        if k in ("up", "down", "left", "right", "wheel_up", "wheel_down"):
            direction = {"wheel_up": "up", "wheel_down": "down"}.get(k, k)
            if sh < 16:
                sel = max(0, min(len(ALL_IOS) - 1, sel + (1 if direction in ("down", "right") else -1)))
            else:
                sel = home_move(sel, direction)
            return None
        if k == "enter":
            return ("open", ALL_IOS[sel][1])
        if k == "l":
            return ("lock", None)
        if k in ("q", "esc"):
            return ("quit", None)
        return None

    while True:
        res = phone_run(sim, draw, on_key, side)
        if res == ("home", None):
            continue
        action, arg = res if isinstance(res, tuple) else (None, None)
        if action == "open":
            open_ios_app(sim, arg)
            sim.clear()
        elif action == "lock":
            if lock_screen(sim) == "quit" and confirm(sim, "Turn the phone off? (y/n) "):
                return
        elif action == "quit":
            if confirm(sim, "Turn the phone off? (y/n) "):
                return


def run_terminal_sim(kind):
    if not sys.stdin.isatty():
        print("  Open 69ls in a real terminal window to use the simulators.")
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    mouse_on = "\033[?1002h\033[?1006h"
    mouse_off = "\033[?1002l\033[?1006l"
    sys.stdout.write(mouse_on + "\033[?25l\033[2J")
    sys.stdout.flush()
    try:
        run_windows_sim() if kind == "windows" else run_ios_sim()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(mouse_off + RS + "\033[?25h\033[2J\033[H")
        sys.stdout.flush()


def main():
    username = run_installation_and_auth()
    boot(username)
    mode = "games"
    while True:
        try:
            raw = input(f"{GREEN}69ls{RESET}{DIM}>{RESET} ").strip()
            cmd = raw.lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd == "":
            continue
        elif is_video_link(raw):
            play_video(raw)
        elif cmd.startswith(("yt ", "play ")):
            play_video(raw.split(None, 1)[1])
        elif cmd in ("yt", "play"):
            print(f"  Paste a YouTube link, or type {YELLOW}yt <link>{RESET}")
        elif cmd in ("install ffmpeg", "winget install gyan.ffmpeg", "winget install ffmpeg"):
            install_ffmpeg()
        elif cmd in ("sims", "sim", "simulators"):
            show_sims()
            mode = "sims"
        elif cmd in ("games", "ls", "list"):
            show_games()
            mode = "games"
        elif cmd in ("windows", "win", "sim windows", "sim win"):
            launch_sim("windows")
        elif cmd in ("ios", "ios7", "sim ios", "sim ios7"):
            launch_sim("ios")
        elif mode == "sims" and cmd in SIMS:
            launch_sim(SIMS[cmd][1])
        elif cmd in GAMES:
            launch(cmd)
        elif cmd in ("help", "?"):
            show_help()
        elif cmd in ("clear", "cls"):
            clear()
        elif cmd == "time" or cmd.startswith("time "):
            handle_time(cmd)
        elif cmd == "about":
            print(f"\n  69ls - a tiny terminal OS for your games. Made with Python {sys.version.split()[0]}.\n")
        elif cmd in ("exit", "quit", "shutdown"):
            break
        else:
            print(f"  {RED}Unknown command:{RESET} {cmd}   {DIM}(type help){RESET}")

    print(f"\n  {DIM}Shutting down 69ls... bye!{RESET}\n")


GAME_CODE = {}

GAME_CODE['1'] = 'import tkinter as tk\nimport math\n\nW, H, GROUND = 900, 500, 450\nANCHOR = (150, 340)\nR = 15\nPR = 18\nMAX_PULL = 90\n\n\nclass Game:\n    def __init__(self, root):\n        root.title("Slingshot Birds")\n        self.c = tk.Canvas(root, width=W, height=H, bg="#87ceeb", highlightthickness=0)\n        self.c.pack()\n        self.c.bind("<ButtonPress-1>", self.press)\n        self.c.bind("<B1-Motion>", self.motion)\n        self.c.bind("<ButtonRelease-1>", self.release)\n        self.reset()\n        self.loop()\n\n    def reset(self):\n        self.birds = 5\n        self.score = 0\n        self.state = "aim"\n        self.drag = False\n        self.still = 0\n        self.bx, self.by = ANCHOR\n        self.vx = self.vy = 0\n        self.blocks = [\n            [620, GROUND - 100, 645, GROUND],\n            [700, GROUND - 100, 725, GROUND],\n            [610, GROUND - 120, 735, GROUND - 100],\n            [790, GROUND - 80, 815, GROUND],\n            [850, GROUND - 80, 875, GROUND],\n            [780, GROUND - 100, 885, GROUND - 80],\n        ]\n        self.pigs = [\n            [672, GROUND - PR],\n            [672, GROUND - 120 - PR],\n            [832, GROUND - PR],\n        ]\n\n    def press(self, e):\n        if self.state in ("win", "lose"):\n            self.reset()\n            return\n        if self.state == "aim" and math.hypot(e.x - self.bx, e.y - self.by) < 35:\n            self.drag = True\n\n    def motion(self, e):\n        if not self.drag:\n            return\n        dx, dy = e.x - ANCHOR[0], e.y - ANCHOR[1]\n        d = math.hypot(dx, dy)\n        if d > MAX_PULL:\n            dx, dy = dx / d * MAX_PULL, dy / d * MAX_PULL\n        self.bx, self.by = ANCHOR[0] + dx, ANCHOR[1] + dy\n\n    def release(self, e):\n        if not self.drag:\n            return\n        self.drag = False\n        self.vx = (ANCHOR[0] - self.bx) * 0.22\n        self.vy = (ANCHOR[1] - self.by) * 0.22\n        self.state = "fly"\n        self.still = 0\n\n    def supported(self, x1, x2, bottom, me):\n        if bottom >= GROUND - 1:\n            return True\n        for b in self.blocks:\n            if b is me:\n                continue\n            if abs(b[1] - bottom) < 3 and b[0] < x2 and b[2] > x1:\n                return True\n        return False\n\n    def next_bird(self):\n        self.birds -= 1\n        if not self.pigs:\n            self.state = "win"\n        elif self.birds <= 0:\n            self.state = "lose"\n        else:\n            self.state = "aim"\n            self.bx, self.by = ANCHOR\n            self.vx = self.vy = 0\n\n    def update(self):\n        for b in self.blocks:\n            if not self.supported(b[0], b[2], b[3], b):\n                b[1] += 4\n                b[3] += 4\n        for p in self.pigs:\n            if not self.supported(p[0] - PR, p[0] + PR, p[1] + PR, None):\n                p[1] += 4\n\n        if self.state != "fly":\n            return\n\n        self.vy += 0.4\n        self.bx += self.vx\n        self.by += self.vy\n\n        if self.by + R > GROUND:\n            self.by = GROUND - R\n            self.vy = -self.vy * 0.4\n            self.vx *= 0.8\n\n        for p in self.pigs[:]:\n            if math.hypot(self.bx - p[0], self.by - p[1]) < R + PR:\n                self.pigs.remove(p)\n                self.score += 500\n\n        for b in self.blocks[:]:\n            cx = max(b[0], min(self.bx, b[2]))\n            cy = max(b[1], min(self.by, b[3]))\n            if math.hypot(self.bx - cx, self.by - cy) < R:\n                self.blocks.remove(b)\n                self.score += 100\n                self.vx *= 0.6\n                self.vy *= 0.6\n\n        if math.hypot(self.vx, self.vy) < 1.0 and self.by >= GROUND - R - 1:\n            self.still += 1\n        if self.still > 30 or self.bx > W + 60 or self.bx < -60:\n            self.next_bird()\n\n    def draw_pig(self, x, y):\n        c = self.c\n        c.create_oval(x - PR, y - PR, x + PR, y + PR, fill="#5cb85c", outline="#2d7a2d", width=2)\n        for ex in (-6, 6):\n            c.create_oval(x + ex - 4, y - 8, x + ex + 4, y, fill="white")\n            c.create_oval(x + ex - 1, y - 6, x + ex + 1, y - 2, fill="black")\n        c.create_oval(x - 6, y + 2, x + 6, y + 11, fill="#8bd48b", outline="#2d7a2d")\n\n    def draw(self):\n        c = self.c\n        c.delete("all")\n        c.create_rectangle(0, GROUND, W, H, fill="#6b8e23", outline="")\n        ax, ay = ANCHOR\n        c.create_line(ax, ay + 10, ax, GROUND, width=10, fill="#5a3b1a")\n        c.create_line(ax - 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        c.create_line(ax + 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        if self.state in ("aim",):\n            c.create_line(ax - 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n            c.create_line(ax + 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n        for b in self.blocks:\n            c.create_rectangle(*b, fill="#c68642", outline="#7a4a14", width=2)\n        for p in self.pigs:\n            self.draw_pig(p[0], p[1])\n        if self.state in ("aim", "fly"):\n            x, y = self.bx, self.by\n            c.create_oval(x - R, y - R, x + R, y + R, fill="#e03131", outline="#8b1a1a", width=2)\n            c.create_oval(x + 1, y - 8, x + 9, y, fill="white")\n            c.create_oval(x + 4, y - 6, x + 7, y - 2, fill="black")\n            c.create_polygon(x + 10, y - 1, x + 20, y + 3, x + 10, y + 7, fill="#f2b705")\n        if self.drag:\n            vx = (ax - self.bx) * 0.22\n            vy = (ay - self.by) * 0.22\n            x, y = self.bx, self.by\n            for i in range(25):\n                vy += 0.4\n                x += vx\n                y += vy\n                if i % 2 == 0:\n                    c.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white", outline="")\n        c.create_text(15, 15, anchor="nw", font=("Arial", 16, "bold"),\n                      text=f"Score: {self.score}    Birds left: {max(self.birds, 0)}")\n        if self.state == "win":\n            c.create_text(W // 2, 180, font=("Arial", 40, "bold"), fill="gold", text="YOU WIN!")\n            c.create_text(W // 2, 230, font=("Arial", 16), text="Click to play again")\n        elif self.state == "lose":\n            c.create_text(W // 2, 180, font=("Arial", 40, "bold"), fill="darkred", text="OUT OF BIRDS")\n            c.create_text(W // 2, 230, font=("Arial", 16), text="Click to try again")\n\n    def loop(self):\n        self.update()\n        self.draw()\n        self.c.after(16, self.loop)\n\n\nroot = tk.Tk()\nGame(root)\nroot.mainloop()\n'

GAME_CODE['2'] = 'import tkinter as tk\nimport math\n\nW, H, GROUND = 900, 500, 450\nANCHOR = (110, 360)\nR = 15\nPR = 18\nPIPE_W = 60\nCAP_W = 72\nCAP_H = 22\n\nLEVELS = [\n    {\n        "bottom": [(430, 140), (700, 200)],\n        "top": [],\n        "pigs": [(565, GROUND - PR), (830, GROUND - PR)],\n    },\n    {\n        "bottom": [(400, 180), (650, 230)],\n        "top": [(400, 100), (650, 60)],\n        "pigs": [(525, GROUND - PR), (680, GROUND - 230 - PR), (820, GROUND - PR)],\n    },\n    {\n        "bottom": [(350, 120), (520, 200), (690, 260)],\n        "top": [(520, 90), (690, 120)],\n        "pigs": [(440, GROUND - PR), (605, GROUND - PR),\n                 (720, GROUND - 260 - PR), (830, GROUND - PR)],\n    },\n]\n\n\nclass Game:\n    def __init__(self, root):\n        root.title("Pipe Birds")\n        self.c = tk.Canvas(root, width=W, height=H, bg="#87ceeb", highlightthickness=0)\n        self.c.pack()\n        self.keys = set()\n        root.bind("<KeyPress>", self.key_down)\n        root.bind("<KeyRelease>", self.key_up)\n        self.c.bind("<Button-1>", lambda e: self.confirm())\n        self.level = 0\n        self.load_level()\n        self.loop()\n\n    def load_level(self):\n        lv = LEVELS[self.level]\n        self.pipes = []\n        for x, h in lv["bottom"]:\n            body = (x, GROUND - h, x + PIPE_W, GROUND)\n            cap = (x - (CAP_W - PIPE_W) / 2, GROUND - h, x + (CAP_W + PIPE_W) / 2, GROUND - h + CAP_H)\n            self.pipes.append((body, cap))\n        for x, h in lv["top"]:\n            body = (x, 0, x + PIPE_W, h)\n            cap = (x - (CAP_W - PIPE_W) / 2, h - CAP_H, x + (CAP_W + PIPE_W) / 2, h)\n            self.pipes.append((body, cap))\n        self.pigs = [list(p) for p in lv["pigs"]]\n        self.birds = 5\n        self.angle = 45\n        self.power = 60\n        self.state = "aim"\n        self.msg = ""\n        self.msg_timer = 0\n        self.still = 0\n        self.vx = self.vy = 0\n        self.bx, self.by = ANCHOR\n\n    def key_down(self, e):\n        k = e.keysym.lower()\n        self.keys.add(k)\n        if k == "space":\n            self.confirm()\n\n    def key_up(self, e):\n        self.keys.discard(e.keysym.lower())\n\n    def confirm(self):\n        if self.state == "aim":\n            speed = self.power * 0.2\n            a = math.radians(self.angle)\n            self.vx = math.cos(a) * speed\n            self.vy = -math.sin(a) * speed\n            self.state = "fly"\n            self.still = 0\n        elif self.state == "win":\n            self.level += 1\n            if self.level >= len(LEVELS):\n                self.state = "done"\n            else:\n                self.load_level()\n        elif self.state == "lose":\n            self.load_level()\n        elif self.state == "done":\n            self.level = 0\n            self.load_level()\n\n    def next_bird(self, message=""):\n        self.birds -= 1\n        if message:\n            self.msg, self.msg_timer = message, 50\n        if not self.pigs:\n            self.state = "win"\n        elif self.birds <= 0:\n            self.state = "lose"\n        else:\n            self.state = "aim"\n            self.bx, self.by = ANCHOR\n            self.vx = self.vy = 0\n\n    def hits_rect(self, r):\n        cx = max(r[0], min(self.bx, r[2]))\n        cy = max(r[1], min(self.by, r[3]))\n        return math.hypot(self.bx - cx, self.by - cy) < R\n\n    def update(self):\n        if self.msg_timer > 0:\n            self.msg_timer -= 1\n        if self.state == "aim":\n            if "w" in self.keys:\n                self.angle = min(85, self.angle + 0.8)\n            if "s" in self.keys:\n                self.angle = max(5, self.angle - 0.8)\n            if "d" in self.keys:\n                self.power = min(100, self.power + 0.8)\n            if "a" in self.keys:\n                self.power = max(20, self.power - 0.8)\n            a = math.radians(self.angle)\n            pull = self.power * 0.6\n            self.bx = ANCHOR[0] - math.cos(a) * pull\n            self.by = ANCHOR[1] + math.sin(a) * pull\n            return\n        if self.state != "fly":\n            return\n        self.vy += 0.4\n        self.bx += self.vx\n        self.by += self.vy\n        if self.by + R > GROUND:\n            self.by = GROUND - R\n            self.vy = -self.vy * 0.4\n            self.vx *= 0.8\n        for body, cap in self.pipes:\n            if self.hits_rect(body) or self.hits_rect(cap):\n                self.next_bird("Crashed into a pipe!")\n                return\n        for p in self.pigs[:]:\n            if math.hypot(self.bx - p[0], self.by - p[1]) < R + PR:\n                self.pigs.remove(p)\n        if not self.pigs:\n            self.next_bird("All pigs popped!")\n            return\n        if math.hypot(self.vx, self.vy) < 1.0 and self.by >= GROUND - R - 1:\n            self.still += 1\n        if self.still > 30 or self.bx > W + 60 or self.bx < -60 or self.by < -400:\n            self.next_bird()\n\n    def draw(self):\n        c = self.c\n        c.delete("all")\n        c.create_rectangle(0, GROUND, W, H, fill="#6b8e23", outline="")\n        for body, cap in self.pipes:\n            c.create_rectangle(*body, fill="#2ecc40", outline="#17731f", width=3)\n            c.create_rectangle(body[0] + 8, body[1], body[0] + 16, body[3], fill="#7dea88", outline="")\n            c.create_rectangle(*cap, fill="#27b839", outline="#17731f", width=3)\n        ax, ay = ANCHOR\n        c.create_line(ax, ay + 10, ax, GROUND, width=10, fill="#5a3b1a")\n        c.create_line(ax - 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        c.create_line(ax + 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        if self.state == "aim":\n            c.create_line(ax - 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n            c.create_line(ax + 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n        for p in self.pigs:\n            c.create_oval(p[0] - PR, p[1] - PR, p[0] + PR, p[1] + PR, fill="#5cb85c", outline="#2d7a2d", width=2)\n        if self.state in ("aim", "fly"):\n            c.create_oval(self.bx - R, self.by - R, self.bx + R, self.by + R, fill="#e03131", outline="#8b1a1a", width=2)\n        c.create_text(15, 12, anchor="nw", font=("Arial", 16, "bold"),\n                      text=f"Level {self.level + 1}/{len(LEVELS)}    Birds: {max(self.birds, 0)}    Pigs: {len(self.pigs)}")\n\n    def loop(self):\n        self.update()\n        self.draw()\n        self.c.after(16, self.loop)\n\n\nroot = tk.Tk()\nGame(root)\nroot.mainloop()\n'

GAME_CODE['3'] = 'import tkinter as tk\nimport math\nimport random\n\nW, H = 900, 560\nHORIZON = 215\nF = 700\nCAMY, CAMZ = 1.2, -5.0\nGOAL_Z = 20.0\nGOAL_HW = 3.66\nGOAL_H = 2.44\nWALL_Z = 9.15\nBALL_R = 0.11\nG = 9.8\nDT = 1 / 60\nSHOTS = 5\n\n\nclass Game:\n    def __init__(self, root):\n        root.title("Free Kick")\n        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0)\n        self.c.pack()\n        self.keys = set()\n        self.loft = 0.30\n        self.curve = 0.0\n        self.frame = 0\n        self.new_game()\n        self.loop()\n\n    def new_game(self):\n        self.attempt = 0\n        self.goals = 0\n        self.new_attempt()\n\n    def new_attempt(self):\n        self.state = "aim"\n        self.bx0 = 0.0\n        self.camx = self.bx0\n        self.bx, self.by, self.bz = self.bx0, 0.0, 0.0\n        self.vx = self.vy = self.vz = 0.0\n        self.msg = ""\n        self.drag = False\n\n    def update(self):\n        pass\n\n    def draw(self):\n        self.c.delete("all")\n        self.c.create_rectangle(0, 0, W, HORIZON, fill="#6ec1ff", outline="")\n        self.c.create_rectangle(0, HORIZON, W, H, fill="#2e8b3d", outline="")\n        self.c.create_text(W // 2, 30, text=f"Goals: {self.goals}", fill="white", font=("Arial", 16, "bold"))\n\n    def loop(self):\n        self.update()\n        self.draw()\n        self.c.after(16, self.loop)\n\n\nroot = tk.Tk()\nGame(root)\nroot.mainloop()\n'


if __name__ == "__main__":
    main()