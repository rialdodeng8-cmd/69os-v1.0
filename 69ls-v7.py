import os
import subprocess
import hashlib
import re
import shutil
import tempfile
import sys
import time
import platform
import getpass
import socket
import ast
import operator
import math
import runpy
import traceback
import shlex
from pathlib import Path
from datetime import datetime, timedelta, timezone

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

GAMES = {
    "1": ("Slingshot Birds", "mouse - drag back and let go"),
    "2": ("Pipe Birds", "W/S angle, A/D power, SPACE fire"),
    "3": ("Free Kick", "mouse drag, A/D curve, W/S loft"),
    "4": ("Kart Racer", "WASD / arrow keys to drive, SPACE to restart"),
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


def boot():
    clear()
    print(GREEN + BANNER + RESET)
    print(CYAN + BOLD + "  69ls  -  terminal OS" + RESET)
    print(DIM + "  booting", end="", flush=True)
    for _ in range(5):
        time.sleep(0.25)
        print(".", end="", flush=True)
    print(RESET)
    print(f"\n  Type {YELLOW}games{RESET} for games, {YELLOW}sims{RESET} for simulators, {YELLOW}help{RESET} for commands.\n")


def show_help():
    print(f"""
  {BOLD}69ls command centre{RESET}
  {DIM}Type any command below. 'help' and 'cmds' show this list.{RESET}

  {CYAN}SYSTEM{RESET}
    {YELLOW}69fetch{RESET} / fetch       colourful system information
    {YELLOW}about{RESET}                 about 69ls
    {YELLOW}date{RESET}                  show today's date and time
    {YELLOW}time{RESET}                  world clock (time --all for every city)
    {YELLOW}disk{RESET}                  show free and used disk space
    {YELLOW}mem{RESET}                   show memory info (if available)
    {YELLOW}uptime{RESET}                how long 69ls has been running
    {YELLOW}python{RESET}                write Python code inside 69ls
    {YELLOW}run "name.py"{RESET}         run a saved 69ls Python program
    {YELLOW}programs{RESET}              list saved 69ls Python programs
    {YELLOW}whoami{RESET}                show your Windows/Linux username

  {CYAN}FILES & TERMINAL{RESET}
    {YELLOW}pwd{RESET}                   show the current folder
    {YELLOW}files{RESET}                 list files in the current folder
    {YELLOW}clear{RESET} / cls           clear the screen
    {YELLOW}echo <text>{RESET}            print text
    {YELLOW}calc <expression>{RESET}     safe calculator (example: calc (12+4)*3)
    {YELLOW}mkdir <name>{RESET}          create a folder
    {YELLOW}touch <name>{RESET}          create an empty file
    {YELLOW}open <path or URL>{RESET}    open a file, folder or website
    {YELLOW}history{RESET}               show commands used this session

  {CYAN}GAMES & SIMULATORS{RESET}
    {YELLOW}games{RESET}                 list games; type {YELLOW}1{RESET}, {YELLOW}2{RESET}, {YELLOW}3{RESET} or {YELLOW}4{RESET} to launch
    {YELLOW}sims{RESET}                  list Windows Sim and iOS 7 Sim
    {YELLOW}windows{RESET} / {YELLOW}ios{RESET}        launch a simulator directly

  {CYAN}MEDIA{RESET}
    {YELLOW}yt <YouTube link>{RESET}     play a YouTube video in the terminal
    {YELLOW}<YouTube link>{RESET}        paste a link directly
    {YELLOW}install ffmpeg{RESET}        install video audio support (Windows)

  {YELLOW}exit{RESET} / quit            shut down 69ls
""")


SIMS = {
    "1": ("Windows Sim", "windows", "desktop, Start menu, Melbourne clock, web, YouTube, Shorts, TikTok"),
    "2": ("iOS 7 Sim", "ios", "lock screen, home screen, Safari, YouTube, Shorts, TikTok + more"),
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
    print(f"\n  {CYAN}Starting {name}...{RESET}  {DIM}(close the sim window to come back){RESET}")
    print(f"  {DIM}Websites open in their own browser windows (Edge or Chrome).{RESET}\n")
    try:
        run_code(SIM_CODE, kind)
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(f"  {RED}Something went wrong: {err}{RESET}")
    print(f"\n  {GREEN}Back in 69ls.{RESET} Type {YELLOW}sims{RESET} to start another.\n")


def show_games():
    print(f"\n  {BOLD}Your games{RESET}")
    print("  " + "-" * 44)
    for key, (name, hint) in GAMES.items():
        print(f"  {GREEN}[{key}]{RESET} {BOLD}{name}{RESET}")
        print(f"      {DIM}{hint}{RESET}")
    print("  " + "-" * 44)
    print(f"  Type {YELLOW}1{RESET}, {YELLOW}2{RESET}, {YELLOW}3{RESET} or {YELLOW}4{RESET} to play.\n")


def launch(key):
    name = GAMES[key][0]
    print(f"\n  {CYAN}Launching {name}...{RESET}  {DIM}(close the game window to come back){RESET}\n")
    try:
        run_code(GAME_CODE[key])
    except Exception as err:
        print(f"  {RED}Something went wrong: {err}{RESET}")
    print(f"\n  {GREEN}Back in 69ls.{RESET} Type {YELLOW}games{RESET} to pick another.\n")


# name: (display, IANA zone, standard offset in minutes, DST rule, std abbr, dst abbr)
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
    """n = 1 for the first Sunday, 2 for the second, -1 for the last."""
    first = datetime(year, month, 1)
    first_sun = first + timedelta(days=(6 - first.weekday()) % 7)
    if n > 0:
        return first_sun + timedelta(days=7 * (n - 1))
    nxt = datetime(year + (month == 12), month % 12 + 1, 1)
    last_day = nxt - timedelta(days=1)
    return last_day - timedelta(days=(last_day.weekday() + 1) % 7)


def city_now(key):
    """Current time in a city, with daylight saving. Returns (datetime, abbr)."""
    name, iana, std_min, rule, std_abbr, dst_abbr = CITIES[key]
    utc = datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        t = utc.astimezone(ZoneInfo(iana))
        return t, t.tzname()
    except Exception:
        pass  # Windows without tzdata: work it out by hand

    naive_utc = utc.replace(tzinfo=None)
    std = naive_utc + timedelta(minutes=std_min)
    y = std.year
    dst = False
    if rule == "au":      # first Sun Oct 2:00 -> first Sun Apr 3:00
        dst = std >= nth_sunday(y, 10, 1) + timedelta(hours=2) or \
              std < nth_sunday(y, 4, 1) + timedelta(hours=2)
    elif rule == "eu":    # last Sun Mar 01:00 UTC -> last Sun Oct 01:00 UTC
        dst = nth_sunday(y, 3, -1) + timedelta(hours=1) <= naive_utc < \
              nth_sunday(y, 10, -1) + timedelta(hours=1)
    elif rule == "us":    # 2nd Sun Mar 2:00 -> 1st Sun Nov 2:00
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


# ---------------------------------------------------------------
# YouTube player (plays video in the terminal using colored blocks)
# ---------------------------------------------------------------
def is_video_link(text):
    pattern = r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/"
    return re.match(pattern, text.strip().strip("\"'"), re.I) is not None


def ensure_video_tools():
    try:
        import cv2, numpy, yt_dlp  # noqa: F401
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
        import cv2, numpy, yt_dlp  # noqa: F401
        print(f"\n  {GREEN}Installed!{RESET}\n")
        return True
    except ImportError:
        print(f"\n  {YELLOW}Installed. Close 69ls, start it again, and paste the link again.{RESET}\n")
        return False


def get_stream(url, want_audio):
    """Ask yt-dlp for a direct video stream (and audio stream if wanted)."""
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
    """Turn one video frame into text: each character shows 2 pixels."""
    small = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    rgb = (small[:, :, ::-1] & 0xF8).tolist()       # fewer colors = less text to draw
    rows = []
    for y in range(0, height, 2):
        parts = []
        last = None
        for top, bottom in zip(rgb[y], rgb[y + 1]):
            key = (top[0], top[1], top[2], bottom[0], bottom[1], bottom[2])
            if key != last:                          # only change colors when needed
                parts.append("\033[38;2;%d;%d;%d;48;2;%d;%d;%dm" % key)
                last = key
            parts.append("\u2580")
        rows.append("".join(parts) + "\033[0m")
    return "\n".join(rows)


def stop_key_pressed():
    if os.name == "nt":
        import msvcrt
        while msvcrt.kbhit():
            if msvcrt.getwch().lower() == "q":
                return True
    return False


def play_capture(cap, title, audio_url=None):
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
    cols = min(term.columns, 100)
    rows = max(5, term.lines - 3)
    scale = min(cols / vw, rows * 2 / vh)
    width = max(2, int(vw * scale))
    height = max(2, int(vh * scale))
    height -= height % 2

    audio = None
    if audio_url and shutil.which("ffplay"):
        audio = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_url],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    header = (title[: max(10, term.columns - 16)] + "   [q] stop").ljust(term.columns - 1)
    out = sys.stdout
    out.write("\033[2J\033[?25l")
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
            while index < target - 1:          # catch up if we're running late
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
            if now - last_draw >= 1 / 20:           # draw at most 20 times a second
                last_draw = now
                out.write("\033[H" + header + "\033[0m\n" + render_frame(cv2, frame, width, height))
                out.flush()
            if stop_key_pressed():
                break
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\033[0m\033[?25h\033[2J\033[H")
        out.flush()
        cap.release()
        if audio:
            audio.terminate()
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



# ---------------------------------------------------------------
# 69ls extras: system fetch, handy terminal commands and calculator
# ---------------------------------------------------------------
SESSION_STARTED = time.monotonic()
COMMAND_HISTORY = []

FETCH_ART = r"""
   __   ___  _      _
  / /  / _ \| |    / /
 / /  / /_\ \ |   / /
/ /___|  _  | |__/ /
\_____/|_| |_|____/
"""


def format_bytes(amount):
    amount = float(amount)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.1f} {unit}"
        amount /= 1024


def show_fetch():
    clear()
    print(CYAN + FETCH_ART + RESET)
    print(f"  {BOLD}{CYAN}69fetch{RESET} {DIM}- system information{RESET}\n")
    try:
        disk = shutil.disk_usage(os.path.abspath(os.sep))
        disk_line = f"{format_bytes(disk.free)} free / {format_bytes(disk.total)} total"
    except OSError:
        disk_line = "unavailable"
    try:
        terminal = shutil.get_terminal_size()
        terminal_line = f"{terminal.columns} x {terminal.lines}"
    except OSError:
        terminal_line = "unknown"
    try:
        import psutil
        vm = psutil.virtual_memory()
        memory_line = f"{format_bytes(vm.used)} used / {format_bytes(vm.total)} total ({vm.percent:.0f}%)"
    except ImportError:
        memory_line = "install psutil for live RAM stats"
    except Exception:
        memory_line = "unavailable"
    details = [
        ("OS", f"{platform.system()} {platform.release()}"),
        ("Device", platform.node() or "unknown"),
        ("User", getpass.getuser()),
        ("Shell", os.environ.get("SHELL") or os.environ.get("COMSPEC") or "Python terminal"),
        ("Architecture", platform.machine() or "unknown"),
        ("Python", platform.python_version()),
        ("Disk", disk_line),
        ("Memory", memory_line),
        ("Terminal", terminal_line),
        ("69ls uptime", format_uptime(time.monotonic() - SESSION_STARTED)),
    ]
    for label, value in details:
        print(f"  {GREEN}{label:<14}{RESET} {value}")
    print(f"\n  {DIM}69ls is a Python terminal environment. Type 'cmds' to see commands.{RESET}\n")


def format_uptime(seconds):
    seconds = max(0, int(seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_calculate(expression):
    """Evaluate arithmetic only; never execute Python code."""
    tree = ast.parse(expression, mode="eval")
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large")
            result = _ALLOWED_BINOPS[type(node.op)](left, right)
            if isinstance(result, complex) or (isinstance(result, float) and not math.isfinite(result)):
                raise ValueError("Result is outside the supported range")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[type(node.op)](visit(node.operand))
        raise ValueError("Use numbers and + - * / // % ** with parentheses")
    return visit(tree)




# Programs written in 69ls live in this app's own program folder.
PROGRAMS_DIR = Path.home() / ".69ls" / "programs"


def python_filename_from_line(line):
    """Accept the final editor line: save as "hello".py."""
    match = re.fullmatch(
        r'\s*save\s+as\s+(?:"([^"]+)"|\'([^\']+)\')(\.py)?\s*',
        line,
        re.IGNORECASE,
    )
    if not match:
        return None
    name = (match.group(1) or match.group(2) or "").strip()
    if match.group(3):
        name += ".py"
    if not name.lower().endswith(".py"):
        name += ".py"
    if Path(name).name != name or name in ("", ".", ".."):
        return None
    return name


def run_saved_program(filename):
    """Run a saved 69ls program in the 69ls terminal."""
    name = Path(filename).name
    if name != filename or not name.lower().endswith(".py"):
        print(f'  {RED}Use a program name like run "hello.py".{RESET}\n')
        return

    path = PROGRAMS_DIR / name
    if not path.is_file():
        print(f"  {RED}No saved 69ls program named {name}.{RESET}")
        print(f"  Type {YELLOW}python{RESET} to create one.\n")
        return

    print(f"\n  {CYAN}69ls Python — running {name}{RESET}\n")
    old_cwd = Path.cwd()
    old_argv = sys.argv[:]
    old_sys_path = sys.path[:]
    try:
        os.chdir(PROGRAMS_DIR)
        sys.path.insert(0, str(PROGRAMS_DIR))
        sys.argv = [str(path)]
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as err:
        if err.code not in (None, 0):
            print(f"\n  {YELLOW}Program exited with code {err.code}.{RESET}")
    except KeyboardInterrupt:
        print(f"\n  {YELLOW}Program stopped.{RESET}")
    except Exception:
        traceback.print_exc()
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv
        sys.path[:] = old_sys_path

    print(f"\n  {GREEN}Back in 69ls.{RESET}\n")


def python_code_mode():
    """Read Python lines until the final save-as marker, save, then run."""
    PROGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n  {BOLD}69ls Python editor{RESET}")
    print("  Write or paste your Python code below.")
    print(f'  Finish with {YELLOW}save as "hello".py{RESET} on its own line.')
    print("  Your program will be saved and run inside this 69ls session.")
    print(f"  Type {YELLOW}.cancel{RESET} on its own line to cancel.\n")

    lines = []
    while True:
        try:
            line = input(f"{CYAN}PY{RESET}{DIM}>{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\n  Code entry cancelled.\n")
            return

        if line.strip().lower() == ".cancel":
            print("\n  Code entry cancelled.\n")
            return

        filename = python_filename_from_line(line)
        if filename:
            if not any(item.strip() for item in lines):
                print(f"  {RED}No Python code entered. Nothing saved.{RESET}\n")
                return
            source = "\n".join(lines).rstrip() + "\n"
            path = PROGRAMS_DIR / filename
            try:
                path.write_text(source, encoding="utf-8")
            except OSError as err:
                print(f"  {RED}Couldn't save the program: {err}{RESET}\n")
                return
            print(f"\n  {GREEN}Saved in 69ls:{RESET} {filename}\n")
            run_saved_program(filename)
            return

        if line.strip().lower().startswith("save as"):
            print(f'  {RED}Use this final-line format:{RESET} save as "hello".py')
            continue

        lines.append(line)


def show_saved_programs():
    PROGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    programs = sorted(PROGRAMS_DIR.glob("*.py"), key=lambda p: p.name.lower())
    print(f"\n  {BOLD}69ls Python programs{RESET}")
    if not programs:
        print("  No programs saved yet. Type python to create one.")
    else:
        for program in programs:
            print(f"  {GREEN}{program.name}{RESET}")
    print()


def handle_extra_command(raw, cmd):
    parts = raw.split(maxsplit=1)
    name = cmd.split(maxsplit=1)[0]
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("69fetch", "fetch", "neofetch", "sysinfo"):
        show_fetch()
    elif cmd in ("cmds", "commands", "help", "?"):
        show_help()
    elif cmd == "date":
        print(f"  {CYAN}{datetime.now().astimezone().strftime('%A %d %B %Y - %I:%M:%S %p %Z')}{RESET}\n")
    elif cmd == "uptime":
        print(f"  69ls has been running for {CYAN}{format_uptime(time.monotonic() - SESSION_STARTED)}{RESET}.\n")
    elif cmd == "pwd":
        print(f"  {os.getcwd()}\n")
    elif cmd in ("files", "dir"):
        try:
            entries = sorted(os.scandir(os.getcwd()), key=lambda e: (not e.is_dir(), e.name.lower()))
            if not entries:
                print("  This folder is empty.\n")
            else:
                for entry in entries:
                    marker = "/" if entry.is_dir() else ""
                    colour = CYAN if entry.is_dir() else RESET
                    print(f"  {colour}{entry.name}{marker}{RESET}")
                print()
        except OSError as err:
            print(f"  {RED}{err}{RESET}\n")
    elif cmd == "whoami":
        print(f"  {getpass.getuser()}\n")
    elif cmd == "python":
        python_code_mode()
    elif cmd == "programs":
        show_saved_programs()
    elif cmd == "run" or cmd.startswith("run "):
        match = re.fullmatch(r'run\s+(?:"([^"]+)"|\'([^\']+)\')', raw, re.IGNORECASE)
        filename = (match.group(1) or match.group(2)) if match else None
        if filename:
            run_saved_program(filename)
        else:
            print(f'  Usage: {YELLOW}run "hello.py"{RESET}\n')
    elif cmd == "disk":
        try:
            d = shutil.disk_usage(os.getcwd())
            used = d.total - d.free
            print(f"  Used: {format_bytes(used)}  |  Free: {format_bytes(d.free)}  |  Total: {format_bytes(d.total)}\n")
        except OSError as err:
            print(f"  {RED}{err}{RESET}\n")
    elif cmd == "mem":
        try:
            import psutil
            m = psutil.virtual_memory()
            print(f"  RAM: {format_bytes(m.used)} used / {format_bytes(m.total)} total ({m.percent:.1f}%)\n")
        except ImportError:
            print(f"  Install optional RAM support with: {YELLOW}pip install psutil{RESET}\n")
        except Exception as err:
            print(f"  {RED}{err}{RESET}\n")
    elif name == "echo":
        print(f"  {arg}\n")
    elif name == "calc":
        if not arg:
            print(f"  Usage: {YELLOW}calc (12 + 4) * 3{RESET}\n")
        else:
            try:
                print(f"  {CYAN}{safe_calculate(arg)}{RESET}\n")
            except Exception as err:
                print(f"  {RED}Calculator: {err}{RESET}\n")
    elif name == "mkdir":
        if not arg:
            print(f"  Usage: {YELLOW}mkdir folder-name{RESET}\n")
        else:
            try:
                os.makedirs(arg, exist_ok=True)
                print(f"  {GREEN}Created folder:{RESET} {os.path.abspath(arg)}\n")
            except OSError as err:
                print(f"  {RED}{err}{RESET}\n")
    elif name == "touch":
        if not arg:
            print(f"  Usage: {YELLOW}touch file-name.txt{RESET}\n")
        else:
            try:
                Path(arg).touch(exist_ok=True)
                print(f"  {GREEN}Created file:{RESET} {os.path.abspath(arg)}\n")
            except OSError as err:
                print(f"  {RED}{err}{RESET}\n")
    elif name == "open":
        if not arg:
            print(f"  Usage: {YELLOW}open path-or-URL{RESET}\n")
        else:
            try:
                if re.match(r"^https?://", arg, re.I):
                    import webbrowser
                    webbrowser.open(arg)
                else:
                    target = os.path.abspath(os.path.expanduser(arg.strip('"')))
                    if not os.path.exists(target):
                        print(f"  {RED}Path not found:{RESET} {target}\n")
                    elif os.name == "nt":
                        os.startfile(target)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", target])
                    else:
                        subprocess.Popen(["xdg-open", target])
                    print(f"  {GREEN}Opened.{RESET}\n")
            except Exception as err:
                print(f"  {RED}Couldn't open it: {err}{RESET}\n")
    elif cmd == "history":
        if not COMMAND_HISTORY:
            print("  No commands yet.\n")
        else:
            print(f"  {BOLD}Session history{RESET}")
            for i, item in enumerate(COMMAND_HISTORY[-30:], 1):
                print(f"  {DIM}{i:>2}.{RESET} {item}")
            print()
    else:
        return False
    return True


def main():
    boot()
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
        COMMAND_HISTORY.append(raw)
        if is_video_link(raw):
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
        elif handle_extra_command(raw, cmd):
            pass
        elif cmd == "about":
            print(f"\n  69ls - a tiny terminal OS for your games. Made with Python {sys.version.split()[0]}.\n")
        elif cmd in ("exit", "quit", "shutdown"):
            break
        else:
            print(f"  {RED}Unknown command:{RESET} {cmd}   {DIM}(type help){RESET}")

    print(f"\n  {DIM}Shutting down 69ls... bye!{RESET}\n")


# ---------------------------------------------------------------
# The games (stored as text and run in their own window)
# ---------------------------------------------------------------
GAME_CODE = {}

GAME_CODE['1'] = 'import tkinter as tk\nimport math\n\nW, H, GROUND = 900, 500, 450\nANCHOR = (150, 340)\nR = 15          # bird radius\nPR = 18         # pig radius\nMAX_PULL = 90\n\n\nclass Game:\n    def __init__(self, root):\n        root.title("Slingshot Birds")\n        self.c = tk.Canvas(root, width=W, height=H, bg="#87ceeb", highlightthickness=0)\n        self.c.pack()\n        self.c.bind("<ButtonPress-1>", self.press)\n        self.c.bind("<B1-Motion>", self.motion)\n        self.c.bind("<ButtonRelease-1>", self.release)\n        self.reset()\n        self.loop()\n\n    def reset(self):\n        self.birds = 5\n        self.score = 0\n        self.state = "aim"          # aim, fly, win, lose\n        self.drag = False\n        self.still = 0\n        self.bx, self.by = ANCHOR\n        self.vx = self.vy = 0\n        # blocks: [x1, y1, x2, y2]\n        self.blocks = [\n            [620, GROUND - 100, 645, GROUND],\n            [700, GROUND - 100, 725, GROUND],\n            [610, GROUND - 120, 735, GROUND - 100],\n            [790, GROUND - 80, 815, GROUND],\n            [850, GROUND - 80, 875, GROUND],\n            [780, GROUND - 100, 885, GROUND - 80],\n        ]\n        # pigs: [x, y] (y is centre)\n        self.pigs = [\n            [672, GROUND - PR],\n            [672, GROUND - 120 - PR],\n            [832, GROUND - PR],\n        ]\n\n    # ---------- mouse ----------\n    def press(self, e):\n        if self.state in ("win", "lose"):\n            self.reset()\n            return\n        if self.state == "aim" and math.hypot(e.x - self.bx, e.y - self.by) < 35:\n            self.drag = True\n\n    def motion(self, e):\n        if not self.drag:\n            return\n        dx, dy = e.x - ANCHOR[0], e.y - ANCHOR[1]\n        d = math.hypot(dx, dy)\n        if d > MAX_PULL:\n            dx, dy = dx / d * MAX_PULL, dy / d * MAX_PULL\n        self.bx, self.by = ANCHOR[0] + dx, ANCHOR[1] + dy\n\n    def release(self, e):\n        if not self.drag:\n            return\n        self.drag = False\n        self.vx = (ANCHOR[0] - self.bx) * 0.22\n        self.vy = (ANCHOR[1] - self.by) * 0.22\n        self.state = "fly"\n        self.still = 0\n\n    # ---------- physics ----------\n    def supported(self, x1, x2, bottom, me):\n        if bottom >= GROUND - 1:\n            return True\n        for b in self.blocks:\n            if b is me:\n                continue\n            if abs(b[1] - bottom) < 3 and b[0] < x2 and b[2] > x1:\n                return True\n        return False\n\n    def next_bird(self):\n        self.birds -= 1\n        if not self.pigs:\n            self.state = "win"\n        elif self.birds <= 0:\n            self.state = "lose"\n        else:\n            self.state = "aim"\n            self.bx, self.by = ANCHOR\n            self.vx = self.vy = 0\n\n    def update(self):\n        # things fall if nothing is under them\n        for b in self.blocks:\n            if not self.supported(b[0], b[2], b[3], b):\n                b[1] += 4\n                b[3] += 4\n        for p in self.pigs:\n            if not self.supported(p[0] - PR, p[0] + PR, p[1] + PR, None):\n                p[1] += 4\n\n        if self.state != "fly":\n            return\n\n        self.vy += 0.4\n        self.bx += self.vx\n        self.by += self.vy\n\n        if self.by + R > GROUND:\n            self.by = GROUND - R\n            self.vy = -self.vy * 0.4\n            self.vx *= 0.8\n\n        for p in self.pigs[:]:\n            if math.hypot(self.bx - p[0], self.by - p[1]) < R + PR:\n                self.pigs.remove(p)\n                self.score += 500\n\n        for b in self.blocks[:]:\n            cx = max(b[0], min(self.bx, b[2]))\n            cy = max(b[1], min(self.by, b[3]))\n            if math.hypot(self.bx - cx, self.by - cy) < R:\n                self.blocks.remove(b)\n                self.score += 100\n                self.vx *= 0.6\n                self.vy *= 0.6\n\n        if math.hypot(self.vx, self.vy) < 1.0 and self.by >= GROUND - R - 1:\n            self.still += 1\n        if self.still > 30 or self.bx > W + 60 or self.bx < -60:\n            self.next_bird()\n\n    # ---------- drawing ----------\n    def draw_pig(self, x, y):\n        c = self.c\n        c.create_oval(x - PR, y - PR, x + PR, y + PR, fill="#5cb85c", outline="#2d7a2d", width=2)\n        for ex in (-6, 6):\n            c.create_oval(x + ex - 4, y - 8, x + ex + 4, y, fill="white")\n            c.create_oval(x + ex - 1, y - 6, x + ex + 1, y - 2, fill="black")\n        c.create_oval(x - 6, y + 2, x + 6, y + 11, fill="#8bd48b", outline="#2d7a2d")\n\n    def draw(self):\n        c = self.c\n        c.delete("all")\n        c.create_rectangle(0, GROUND, W, H, fill="#6b8e23", outline="")\n        # slingshot\n        ax, ay = ANCHOR\n        c.create_line(ax, ay + 10, ax, GROUND, width=10, fill="#5a3b1a")\n        c.create_line(ax - 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        c.create_line(ax + 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        if self.state in ("aim",):\n            c.create_line(ax - 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n            c.create_line(ax + 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n        # blocks and pigs\n        for b in self.blocks:\n            c.create_rectangle(*b, fill="#c68642", outline="#7a4a14", width=2)\n        for p in self.pigs:\n            self.draw_pig(p[0], p[1])\n        # bird\n        if self.state in ("aim", "fly"):\n            x, y = self.bx, self.by\n            c.create_oval(x - R, y - R, x + R, y + R, fill="#e03131", outline="#8b1a1a", width=2)\n            c.create_oval(x + 1, y - 8, x + 9, y, fill="white")\n            c.create_oval(x + 4, y - 6, x + 7, y - 2, fill="black")\n            c.create_polygon(x + 10, y - 1, x + 20, y + 3, x + 10, y + 7, fill="#f2b705")\n        # trajectory dots while aiming\n        if self.drag:\n            vx = (ax - self.bx) * 0.22\n            vy = (ay - self.by) * 0.22\n            x, y = self.bx, self.by\n            for i in range(25):\n                vy += 0.4\n                x += vx\n                y += vy\n                if i % 2 == 0:\n                    c.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white", outline="")\n        # HUD\n        c.create_text(15, 15, anchor="nw", font=("Arial", 16, "bold"),\n                      text=f"Score: {self.score}    Birds left: {max(self.birds, 0)}")\n        if self.state == "win":\n            c.create_text(W // 2, 180, font=("Arial", 40, "bold"), fill="gold", text="YOU WIN!")\n            c.create_text(W // 2, 230, font=("Arial", 16), text="Click to play again")\n        elif self.state == "lose":\n            c.create_text(W // 2, 180, font=("Arial", 40, "bold"), fill="darkred", text="OUT OF BIRDS")\n            c.create_text(W // 2, 230, font=("Arial", 16), text="Click to try again")\n        elif self.state == "aim" and self.birds == 5 and self.score == 0:\n            c.create_text(W // 2, 70, font=("Arial", 14),\n                          text="Drag the bird back, then let go to fire!")\n\n    def loop(self):\n        self.update()\n        self.draw()\n        self.c.after(16, self.loop)\n\n\nroot = tk.Tk()\nGame(root)\nroot.mainloop()\n'

GAME_CODE['2'] = 'import tkinter as tk\nimport math\n\nW, H, GROUND = 900, 500, 450\nANCHOR = (110, 360)\nR = 15           # bird radius\nPR = 18          # pig radius\nPIPE_W = 60\nCAP_W = 72\nCAP_H = 22\n\n# Each level: bottom pipes (x, height), top pipes (x, height), pigs (x, y)\nLEVELS = [\n    {\n        "bottom": [(430, 140), (700, 200)],\n        "top": [],\n        "pigs": [(565, GROUND - PR), (830, GROUND - PR)],\n    },\n    {\n        "bottom": [(400, 180), (650, 230)],\n        "top": [(400, 100), (650, 60)],\n        "pigs": [(525, GROUND - PR), (680, GROUND - 230 - PR), (820, GROUND - PR)],\n    },\n    {\n        "bottom": [(350, 120), (520, 200), (690, 260)],\n        "top": [(520, 90), (690, 120)],\n        "pigs": [(440, GROUND - PR), (605, GROUND - PR),\n                 (720, GROUND - 260 - PR), (830, GROUND - PR)],\n    },\n]\n\n\nclass Game:\n    def __init__(self, root):\n        root.title("Pipe Birds  -  W/S angle, A/D power, SPACE fire")\n        self.c = tk.Canvas(root, width=W, height=H, bg="#87ceeb", highlightthickness=0)\n        self.c.pack()\n        self.keys = set()\n        root.bind("<KeyPress>", self.key_down)\n        root.bind("<KeyRelease>", self.key_up)\n        self.c.bind("<Button-1>", lambda e: self.confirm())\n        self.level = 0\n        self.load_level()\n        self.loop()\n\n    # ---------- setup ----------\n    def load_level(self):\n        lv = LEVELS[self.level]\n        self.pipes = []   # list of (body_rect, cap_rect)\n        for x, h in lv["bottom"]:\n            body = (x, GROUND - h, x + PIPE_W, GROUND)\n            cap = (x - (CAP_W - PIPE_W) / 2, GROUND - h, x + (CAP_W + PIPE_W) / 2, GROUND - h + CAP_H)\n            self.pipes.append((body, cap))\n        for x, h in lv["top"]:\n            body = (x, 0, x + PIPE_W, h)\n            cap = (x - (CAP_W - PIPE_W) / 2, h - CAP_H, x + (CAP_W + PIPE_W) / 2, h)\n            self.pipes.append((body, cap))\n        self.pigs = [list(p) for p in lv["pigs"]]\n        self.birds = 5\n        self.angle = 45\n        self.power = 60\n        self.state = "aim"      # aim, fly, win, lose, done\n        self.msg = ""\n        self.msg_timer = 0\n        self.still = 0\n        self.vx = self.vy = 0\n        self.bx, self.by = ANCHOR\n\n    # ---------- input ----------\n    def key_down(self, e):\n        k = e.keysym.lower()\n        self.keys.add(k)\n        if k == "space":\n            self.confirm()\n\n    def key_up(self, e):\n        self.keys.discard(e.keysym.lower())\n\n    def confirm(self):\n        if self.state == "aim":\n            speed = self.power * 0.2\n            a = math.radians(self.angle)\n            self.vx = math.cos(a) * speed\n            self.vy = -math.sin(a) * speed\n            self.state = "fly"\n            self.still = 0\n        elif self.state == "win":\n            self.level += 1\n            if self.level >= len(LEVELS):\n                self.state = "done"\n            else:\n                self.load_level()\n        elif self.state == "lose":\n            self.load_level()\n        elif self.state == "done":\n            self.level = 0\n            self.load_level()\n\n    # ---------- game logic ----------\n    def next_bird(self, message=""):\n        self.birds -= 1\n        if message:\n            self.msg, self.msg_timer = message, 50\n        if not self.pigs:\n            self.state = "win"\n        elif self.birds <= 0:\n            self.state = "lose"\n        else:\n            self.state = "aim"\n            self.bx, self.by = ANCHOR\n            self.vx = self.vy = 0\n\n    def hits_rect(self, r):\n        cx = max(r[0], min(self.bx, r[2]))\n        cy = max(r[1], min(self.by, r[3]))\n        return math.hypot(self.bx - cx, self.by - cy) < R\n\n    def update(self):\n        if self.msg_timer > 0:\n            self.msg_timer -= 1\n\n        if self.state == "aim":\n            if "w" in self.keys:\n                self.angle = min(85, self.angle + 0.8)\n            if "s" in self.keys:\n                self.angle = max(5, self.angle - 0.8)\n            if "d" in self.keys:\n                self.power = min(100, self.power + 0.8)\n            if "a" in self.keys:\n                self.power = max(20, self.power - 0.8)\n            a = math.radians(self.angle)\n            pull = self.power * 0.6\n            self.bx = ANCHOR[0] - math.cos(a) * pull\n            self.by = ANCHOR[1] + math.sin(a) * pull\n            return\n\n        if self.state != "fly":\n            return\n\n        self.vy += 0.4\n        self.bx += self.vx\n        self.by += self.vy\n\n        if self.by + R > GROUND:\n            self.by = GROUND - R\n            self.vy = -self.vy * 0.4\n            self.vx *= 0.8\n\n        # pipes: hit one and the bird is lost\n        for body, cap in self.pipes:\n            if self.hits_rect(body) or self.hits_rect(cap):\n                self.next_bird("Crashed into a pipe!")\n                return\n\n        for p in self.pigs[:]:\n            if math.hypot(self.bx - p[0], self.by - p[1]) < R + PR:\n                self.pigs.remove(p)\n\n        if not self.pigs:\n            self.next_bird("All pigs popped!")\n            return\n\n        if math.hypot(self.vx, self.vy) < 1.0 and self.by >= GROUND - R - 1:\n            self.still += 1\n        if self.still > 30 or self.bx > W + 60 or self.bx < -60 or self.by < -400:\n            self.next_bird()\n\n    # ---------- drawing ----------\n    def draw_pig(self, x, y):\n        c = self.c\n        c.create_oval(x - PR, y - PR, x + PR, y + PR, fill="#5cb85c", outline="#2d7a2d", width=2)\n        for ex in (-6, 6):\n            c.create_oval(x + ex - 4, y - 8, x + ex + 4, y, fill="white")\n            c.create_oval(x + ex - 1, y - 6, x + ex + 1, y - 2, fill="black")\n        c.create_oval(x - 6, y + 2, x + 6, y + 11, fill="#8bd48b", outline="#2d7a2d")\n\n    def draw_bird(self, x, y):\n        c = self.c\n        c.create_oval(x - R, y - R, x + R, y + R, fill="#e03131", outline="#8b1a1a", width=2)\n        c.create_oval(x + 1, y - 8, x + 9, y, fill="white")\n        c.create_oval(x + 4, y - 6, x + 7, y - 2, fill="black")\n        c.create_polygon(x + 10, y - 1, x + 20, y + 3, x + 10, y + 7, fill="#f2b705")\n\n    def draw(self):\n        c = self.c\n        c.delete("all")\n        c.create_rectangle(0, GROUND, W, H, fill="#6b8e23", outline="")\n\n        # pipes\n        for body, cap in self.pipes:\n            c.create_rectangle(*body, fill="#2ecc40", outline="#17731f", width=3)\n            c.create_rectangle(body[0] + 8, body[1], body[0] + 16, body[3], fill="#7dea88", outline="")\n            c.create_rectangle(*cap, fill="#27b839", outline="#17731f", width=3)\n\n        # slingshot\n        ax, ay = ANCHOR\n        c.create_line(ax, ay + 10, ax, GROUND, width=10, fill="#5a3b1a")\n        c.create_line(ax - 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        c.create_line(ax + 14, ay - 15, ax, ay + 10, width=8, fill="#5a3b1a")\n        if self.state == "aim":\n            c.create_line(ax - 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n            c.create_line(ax + 14, ay - 12, self.bx, self.by, width=4, fill="#3b2410")\n\n        for p in self.pigs:\n            self.draw_pig(p[0], p[1])\n\n        if self.state in ("aim", "fly"):\n            self.draw_bird(self.bx, self.by)\n\n        # trajectory preview\n        if self.state == "aim":\n            speed = self.power * 0.2\n            a = math.radians(self.angle)\n            vx, vy = math.cos(a) * speed, -math.sin(a) * speed\n            x, y = self.bx, self.by\n            for i in range(40):\n                vy += 0.4\n                x += vx\n                y += vy\n                if y > GROUND:\n                    break\n                if i % 2 == 0:\n                    c.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white", outline="")\n\n        # HUD\n        c.create_text(15, 12, anchor="nw", font=("Arial", 16, "bold"),\n                      text=f"Level {self.level + 1}/{len(LEVELS)}    Birds: {max(self.birds, 0)}    Pigs: {len(self.pigs)}")\n        if self.state == "aim":\n            c.create_text(15, 40, anchor="nw", font=("Arial", 12),\n                          text=f"Angle {int(self.angle)}\\u00b0   Power {int(self.power)}")\n            c.create_rectangle(15, 62, 135, 74, outline="black")\n            c.create_rectangle(15, 62, 15 + 1.2 * self.power, 74, fill="#e03131", outline="")\n            c.create_text(W // 2, H - 22, font=("Arial", 12), fill="white",\n                          text="W/S = angle    A/D = power    SPACE = fire    (avoid the pipes!)")\n\n        if self.msg_timer > 0 and self.msg:\n            c.create_text(W // 2, 110, font=("Arial", 22, "bold"), fill="white", text=self.msg)\n\n        if self.state == "win":\n            c.create_text(W // 2, 170, font=("Arial", 40, "bold"), fill="gold", text="LEVEL CLEARED!")\n            c.create_text(W // 2, 220, font=("Arial", 16), text="Press SPACE for the next level")\n        elif self.state == "lose":\n            c.create_text(W // 2, 170, font=("Arial", 40, "bold"), fill="darkred", text="OUT OF BIRDS")\n            c.create_text(W // 2, 220, font=("Arial", 16), text="Press SPACE to try again")\n        elif self.state == "done":\n            c.create_text(W // 2, 170, font=("Arial", 40, "bold"), fill="gold", text="YOU BEAT THE GAME!")\n            c.create_text(W // 2, 220, font=("Arial", 16), text="Press SPACE to play again")\n\n    def loop(self):\n        self.update()\n        self.draw()\n        self.c.after(16, self.loop)\n\n\nroot = tk.Tk()\nGame(root)\nroot.mainloop()\n'

GAME_CODE['3'] = 'import tkinter as tk\nimport math\nimport random\n\nW, H = 900, 560\nHORIZON = 215\nF = 700                 # camera "zoom"\nCAMY, CAMZ = 1.2, -5.0  # camera height and distance behind the ball\nGOAL_Z = 20.0           # distance to the goal (metres)\nGOAL_HW = 3.66          # half goal width\nGOAL_H = 2.44           # goal height\nWALL_Z = 9.15           # distance to the defensive wall\nBALL_R = 0.11\nG = 9.8\nDT = 1 / 60\nSHOTS = 5\n\n\ndef clamp(v, lo, hi):\n    return max(lo, min(hi, v))\n\n\nclass Game:\n    def __init__(self, root):\n        root.title("Free Kick")\n        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0)\n        self.c.pack()\n        self.keys = set()\n        self.loft = 0.30\n        self.curve = 0.0\n        self.frame = 0\n        self.tag = "dyn"\n        self.crowd = [(random.randint(0, W), random.randint(135, HORIZON - 4),\n                       random.choice(["#c0392b", "#f1c40f", "#ecf0f1", "#2980b9", "#8e44ad", "#e67e22"]))\n                      for _ in range(260)]\n        root.bind("<KeyPress>", self.key_down)\n        root.bind("<KeyRelease>", self.key_up)\n        self.c.bind("<ButtonPress-1>", self.press)\n        self.c.bind("<B1-Motion>", self.motion)\n        self.c.bind("<ButtonRelease-1>", self.release)\n        self.new_game()\n        self.loop()\n\n    # ------------------------------------------------------------ setup\n    def new_game(self):\n        self.attempt = 0\n        self.goals = 0\n        self.new_attempt()\n\n    def new_attempt(self):\n        self.state = "aim"          # aim, fly, result, over\n        self.bx0 = random.choice([-9, -7, -5, -3, 3, 5, 7, 9]) + random.uniform(-0.8, 0.8)\n        self.camx = self.bx0\n        self.bx, self.by, self.bz = self.bx0, 0.0, 0.0\n        self.vx = self.vy = self.vz = 0.0\n        self.wall_x = self.bx0 * (1 - WALL_Z / GOAL_Z)\n        self.kx = 0.0\n        self.kx0 = 0.0\n        self.ktarget = None\n        self.kdelay = 0\n        self.kprog = 0.0\n        self.kdir = 0\n        self.msg = ""\n        self.timer = 0\n        self.scored = False\n        self.drag = False\n        self.press_pt = (0, 0)\n        self.cur_pt = (0, 0)\n        self.spin = 0.0\n        self.still = 0\n        self.redraw_bg()\n\n    # ------------------------------------------------------------ helpers\n    def proj(self, x, y, z):\n        d = z - CAMZ\n        s = F / d\n        return W / 2 + (x - self.camx) * s, HORIZON - (y - CAMY) * s, s\n\n    def line(self, *a, **k):\n        return self.c.create_line(*a, tags=self.tag, **k)\n\n    def oval(self, *a, **k):\n        return self.c.create_oval(*a, tags=self.tag, **k)\n\n    def rect(self, *a, **k):\n        return self.c.create_rectangle(*a, tags=self.tag, **k)\n\n    def poly(self, *a, **k):\n        return self.c.create_polygon(*a, tags=self.tag, **k)\n\n    def text(self, *a, **k):\n        return self.c.create_text(*a, tags=self.tag, **k)\n\n    # ------------------------------------------------------------ static scenery\n    def redraw_bg(self):\n        c = self.c\n        c.delete("bg")\n        self.tag = "bg"\n        self.rect(0, 0, W, HORIZON, fill="#6ec1ff", outline="")\n        self.rect(0, 120, W, HORIZON, fill="#3a3f55", outline="")\n        for x, y, col in self.crowd:\n            self.rect(x, y, x + 4, y + 4, fill=col, outline="")\n        self.rect(0, HORIZON, W, H, fill="#2e8b3d", outline="")\n        i = 0\n        z = -4.5\n        while z < 120:\n            z2 = z + 5\n            y1 = HORIZON + CAMY * F / (z - CAMZ)\n            y2 = HORIZON + CAMY * F / (z2 - CAMZ)\n            if i % 2 == 0 and y2 < H:\n                self.rect(0, y2, W, min(y1, H + 5), fill="#37a049", outline="")\n            z = z2\n            i += 1\n        self.draw_goal()\n        c.tag_lower("bg")\n        self.tag = "dyn"\n\n    def draw_goal(self):\n        zb = GOAL_Z + 2.2\n        p = [self.proj(-GOAL_HW, 0, zb), self.proj(GOAL_HW, 0, zb),\n             self.proj(GOAL_HW, GOAL_H, zb), self.proj(-GOAL_HW, GOAL_H, zb)]\n        self.poly(*[v for q in p for v in q[:2]], fill="#dfe5df", outline="#8d998d")\n        for i in range(1, 12):\n            x = -GOAL_HW + i * (2 * GOAL_HW / 12)\n            a, b = self.proj(x, 0, zb), self.proj(x, GOAL_H, zb)\n            self.line(a[0], a[1], b[0], b[1], fill="#9aa59a")\n        for j in range(1, 6):\n            y = GOAL_H * j / 6\n            a, b = self.proj(-GOAL_HW, y, zb), self.proj(GOAL_HW, y, zb)\n            self.line(a[0], a[1], b[0], b[1], fill="#9aa59a")\n        for sx in (-GOAL_HW, GOAL_HW):\n            ft = self.proj(sx, GOAL_H, GOAL_Z)\n            bt = self.proj(sx, GOAL_H, zb)\n            fb = self.proj(sx, 0, GOAL_Z)\n            bb = self.proj(sx, 0, zb)\n            self.line(ft[0], ft[1], bt[0], bt[1], fill="#8d998d")\n            self.line(fb[0], fb[1], bb[0], bb[1], fill="#8d998d")\n        for sx in (-GOAL_HW, GOAL_HW):\n            a, b = self.proj(sx, 0, GOAL_Z), self.proj(sx, GOAL_H, GOAL_Z)\n            self.line(a[0], a[1], b[0], b[1], fill="white", width=5, capstyle="round")\n        a, b = self.proj(-GOAL_HW, GOAL_H, GOAL_Z), self.proj(GOAL_HW, GOAL_H, GOAL_Z)\n        self.line(a[0], a[1], b[0], b[1], fill="white", width=5, capstyle="round")\n\n    # ------------------------------------------------------------ input\n    def key_down(self, e):\n        k = e.keysym.lower()\n        self.keys.add(k)\n        if k in ("space", "return") and self.state == "over":\n            self.new_game()\n\n    def key_up(self, e):\n        self.keys.discard(e.keysym.lower())\n\n    def press(self, e):\n        if self.state == "over":\n            self.new_game()\n            return\n        if self.state == "aim":\n            self.drag = True\n            self.press_pt = (e.x, e.y)\n            self.cur_pt = (e.x, e.y)\n\n    def motion(self, e):\n        if self.drag:\n            self.cur_pt = (e.x, e.y)\n\n    def release(self, e):\n        if not self.drag:\n            return\n        self.drag = False\n        power, yaw = self.pull()\n        if power < 0.12:\n            return\n        self.launch(power, yaw)\n\n    def pull(self):\n        dx = self.cur_pt[0] - self.press_pt[0]\n        dy = self.cur_pt[1] - self.press_pt[1]\n        power = clamp(dy, 0, 140) / 140\n        yaw = -clamp(dx, -140, 140) / 140 * 0.6\n        return power, yaw\n\n    # ------------------------------------------------------------ physics\n    def velocities(self, power, yaw):\n        speed = 14 + 16 * power\n        vh = speed * math.cos(self.loft)\n        vy = speed * math.sin(self.loft)\n        return vh * math.sin(yaw), vy, vh * math.cos(yaw)\n\n    def simulate(self, power, yaw, steps=170):\n        vx, vy, vz = self.velocities(power, yaw)\n        x, y, z = self.bx, self.by, self.bz\n        pts = []\n        for _ in range(steps):\n            vx += self.curve * 10 * DT\n            vy -= G * DT\n            x += vx * DT\n            y += vy * DT\n            z += vz * DT\n            if y < 0 or z > GOAL_Z + 2:\n                break\n            pts.append((x, y, z))\n        return pts\n\n    def launch(self, power, yaw):\n        self.vx, self.vy, self.vz = self.velocities(power, yaw)\n        self.state = "fly"\n        self.still = 0\n        # keeper reads the shot, but not perfectly\n        pts = self.simulate(power, yaw)\n        target = None\n        for (x, y, z) in pts:\n            if z >= GOAL_Z - 0.3:\n                if abs(x) < GOAL_HW + 1.5:\n                    err = 0.9 + 0.12 * self.attempt\n                    target = clamp(x + random.uniform(-err, err), -3.2, 3.2)\n                break\n        self.kx0 = self.kx\n        self.ktarget = target\n        self.kdelay = 10\n        if target is not None:\n            self.kdir = 1 if target > self.kx else -1\n\n    def ball_step(self):\n        self.vx += self.curve * 10 * DT if self.state == "fly" else 0\n        self.vy -= G * DT\n        self.bx += self.vx * DT\n        self.by += self.vy * DT\n        self.bz = max(-4.5, self.bz + self.vz * DT)\n        self.spin += math.hypot(self.vx, self.vz) * 0.08\n        if self.by < 0:\n            self.by = 0.0\n            self.vy = -self.vy * 0.55\n            if abs(self.vy) < 1.2:\n                self.vy = 0.0\n        if self.by == 0.0 and self.vy == 0.0:\n            self.vx *= 0.985\n            self.vz *= 0.985\n\n    def finish(self, msg, scored=False):\n        self.state = "result"\n        self.msg = msg\n        self.timer = 110\n        self.scored = scored\n        if scored:\n            self.goals += 1\n\n    def update_keeper(self):\n        if self.state == "aim":\n            self.kx = 1.4 * math.sin(self.frame * 0.025)\n            return\n        if self.ktarget is None:\n            return\n        if self.kdelay > 0:\n            self.kdelay -= 1\n            return\n        step = 6.5 * DT\n        diff = self.ktarget - self.kx\n        if abs(diff) <= step:\n            self.kx = self.ktarget\n        else:\n            self.kx += step * (1 if diff > 0 else -1)\n        total = max(abs(self.ktarget - self.kx0), 0.01)\n        self.kprog = min(1.0, abs(self.kx - self.kx0) / total)\n\n    def update(self):\n        self.frame += 1\n        k = self.keys\n        if self.state == "aim":\n            if "w" in k:\n                self.loft = min(0.7, self.loft + 0.004)\n            if "s" in k:\n                self.loft = max(0.1, self.loft - 0.004)\n            if "d" in k:\n                self.curve = min(1.0, self.curve + 0.025)\n            if "a" in k:\n                self.curve = max(-1.0, self.curve - 0.025)\n            if "q" in k:\n                self.curve = 0.0\n        self.update_keeper()\n\n        if self.state == "fly":\n            px, py, pz = self.bx, self.by, self.bz\n            self.ball_step()\n\n            # the wall\n            if pz < WALL_Z <= self.bz:\n                f = (WALL_Z - pz) / (self.bz - pz)\n                xi = px + (self.bx - px) * f\n                yi = py + (self.by - py) * f\n                if abs(xi - self.wall_x) < 1.0 + BALL_R + 0.05 and yi < 1.85:\n                    self.bz = WALL_Z - 0.2\n                    self.vz = -self.vz * 0.3\n                    self.vx *= 0.5\n                    self.vy = abs(self.vy) * 0.3\n                    self.finish("BLOCKED BY THE WALL!")\n                    return\n\n            # the goal line\n            if pz < GOAL_Z <= self.bz:\n                f = (GOAL_Z - pz) / (self.bz - pz)\n                xi = px + (self.bx - px) * f\n                yi = py + (self.by - py) * f\n                inside = abs(xi) <= GOAL_HW - 0.06 and yi <= GOAL_H - 0.06\n                post = abs(xi) <= GOAL_HW + 0.14 and yi <= GOAL_H + 0.14\n                if inside:\n                    if abs(xi - self.kx) < 0.95 and yi < 2.15:\n                        self.vz = -self.vz * 0.25\n                        self.vx += random.uniform(-2, 2)\n                        self.vy = abs(self.vy) * 0.3\n                        self.bz = GOAL_Z - 0.3\n                        self.finish("SAVED BY THE KEEPER!")\n                    else:\n                        self.finish("GOAL!!!", scored=True)\n                elif post:\n                    self.vz = -self.vz * 0.5\n                    self.bz = GOAL_Z - 0.2\n                    self.finish("HIT THE POST!")\n                else:\n                    self.finish("OFF TARGET!")\n                return\n\n            if self.bz > GOAL_Z + 6 or abs(self.bx) > 45:\n                self.finish("OFF TARGET!")\n                return\n            if self.by == 0.0 and math.hypot(self.vx, self.vz) < 1.0:\n                self.still += 1\n                if self.still > 30:\n                    self.finish("SHORT!")\n\n        elif self.state == "result":\n            self.ball_step()\n            if self.scored and self.bz > GOAL_Z + 2.0:\n                self.bz = GOAL_Z + 2.0\n                self.vz = -self.vz * 0.1\n                self.vx *= 0.3\n            self.timer -= 1\n            if self.timer <= 0:\n                self.attempt += 1\n                if self.attempt >= SHOTS:\n                    self.state = "over"\n                else:\n                    self.new_attempt()\n\n    # ------------------------------------------------------------ drawing\n    def person(self, x, z, h, shirt, tilt=0.0, keeper=False):\n        fx, fy, s = self.proj(x, 0, z)\n        hx = fx + math.sin(tilt) * h * s\n        hy = fy - math.cos(tilt) * h * s\n        self.line(fx, fy, hx, hy, width=max(3, 0.42 * s), fill=shirt, capstyle="round")\n        mx, my = fx + (hx - fx) * 0.4, fy + (hy - fy) * 0.4\n        self.line(fx, fy, mx, my, width=max(3, 0.36 * s), fill="#1d1d1d", capstyle="round")\n        ux, uy = math.sin(tilt), -math.cos(tilt)\n        head_x, head_y = hx + ux * 0.16 * s, hy + uy * 0.16 * s\n        self.oval(head_x - 0.14 * s, head_y - 0.14 * s, head_x + 0.14 * s, head_y + 0.14 * s,\n                  fill="#f1c27d", outline="")\n        if keeper:\n            shx, shy = fx + (hx - fx) * 0.85, fy + (hy - fy) * 0.85\n            dx, dy = math.cos(tilt), math.sin(tilt)\n            for sg in (-1, 1):\n                ex = shx + sg * dx * 0.85 * s + ux * 0.35 * s\n                ey = shy + sg * dy * 0.85 * s + uy * 0.35 * s\n                self.line(shx, shy, ex, ey, width=max(2, 0.18 * s), fill=shirt, capstyle="round")\n                self.oval(ex - 0.12 * s, ey - 0.12 * s, ex + 0.12 * s, ey + 0.12 * s,\n                          fill="white", outline="#999")\n\n    def draw(self):\n        self.c.delete("dyn")\n        self.tag = "dyn"\n\n        # keeper\n        tilt = 0.0\n        if self.ktarget is not None and abs(self.ktarget - self.kx0) > 0.6:\n            tilt = self.kdir * self.kprog * 1.2\n        self.person(self.kx, GOAL_Z, 1.85, "#f5a623", tilt, keeper=True)\n\n        # wall\n        for off in (-0.75, -0.25, 0.25, 0.75):\n            self.person(self.wall_x + off, WALL_Z, 1.8, "#d62828")\n\n        # ball\n        sx, sy, s = self.proj(self.bx, self.by, self.bz)\n        shx, shy, _ = self.proj(self.bx, 0, self.bz)\n        r = BALL_R * s\n        self.oval(shx - r * 1.1, shy - r * 0.35, shx + r * 1.1, shy + r * 0.35, fill="#1e6b2a", outline="")\n        self.oval(sx - r, sy - r, sx + r, sy + r, fill="white", outline="#333", width=2)\n        px = sx + math.cos(self.spin) * r * 0.45\n        py = sy + math.sin(self.spin) * r * 0.45\n        self.oval(px - r * 0.3, py - r * 0.3, px + r * 0.3, py + r * 0.3, fill="#222", outline="")\n\n        # aiming\n        if self.state == "aim" and self.drag:\n            power, yaw = self.pull()\n            self.line(self.press_pt[0], self.press_pt[1], self.cur_pt[0], self.cur_pt[1],\n                      fill="white", width=3, dash=(6, 4))\n            pts = self.simulate(power, yaw)\n            for i, (x, y, z) in enumerate(pts):\n                if i % 3 == 0:\n                    ax, ay, a_s = self.proj(x, y, z)\n                    rr = max(2, 0.07 * a_s)\n                    self.oval(ax - rr, ay - rr, ax + rr, ay + rr, fill="#ffeb3b", outline="")\n            self.rect(W - 40, H - 150, W - 20, H - 30, outline="white", width=2)\n            self.rect(W - 38, H - 32 - 116 * power, W - 22, H - 32, fill="#e03131", outline="")\n            self.text(W - 30, H - 160, text="POWER", fill="white", font=("Arial", 10, "bold"))\n\n        # HUD\n        self.rect(0, 0, W, 38, fill="#111", outline="")\n        shot = min(self.attempt + 1, SHOTS)\n        self.text(15, 19, anchor="w", fill="white", font=("Arial", 16, "bold"),\n                  text=f"Goals: {self.goals}     Shot {shot} / {SHOTS}")\n        self.text(W - 15, 19, anchor="e", fill="#ddd", font=("Arial", 12),\n                  text=f"Loft {int(math.degrees(self.loft))}\\u00b0")\n\n        # curve gauge\n        gx, gy = 15, H - 35\n        self.text(gx, gy - 16, anchor="w", fill="white", font=("Arial", 10, "bold"), text="CURVE  (A / D)")\n        self.rect(gx, gy, gx + 160, gy + 12, fill="#222", outline="white")\n        self.line(gx + 80, gy - 2, gx + 80, gy + 14, fill="white")\n        mx = gx + 80 + self.curve * 78\n        self.rect(mx - 4, gy - 3, mx + 4, gy + 15, fill="#ffeb3b", outline="")\n\n        if self.state == "aim" and not self.drag:\n            self.text(W // 2, H - 22, fill="white", font=("Arial", 12, "bold"),\n                      text="Click and drag DOWN to pull back (left/right aims)   |   W/S loft   A/D curve   Q reset curve")\n\n        if self.state == "result" and self.msg:\n            col = "gold" if self.scored else "white"\n            self.text(W // 2 + 2, 112, text=self.msg, fill="black", font=("Arial", 36, "bold"))\n            self.text(W // 2, 110, text=self.msg, fill=col, font=("Arial", 36, "bold"))\n\n        if self.state == "over":\n            self.rect(W // 2 - 260, 150, W // 2 + 260, 340, fill="#111", outline="white", width=3)\n            self.text(W // 2, 200, text="FULL TIME!", fill="gold", font=("Arial", 36, "bold"))\n            self.text(W // 2, 255, text=f"You scored {self.goals} out of {SHOTS}",\n                      fill="white", font=("Arial", 20))\n            self.text(W // 2, 305, text="Click or press SPACE to play again",\n                      fill="#ccc", font=("Arial", 14))\n\n    def loop(self):\n        self.update()\n        self.draw()\n        self.c.after(16, self.loop)\n\n\nroot = tk.Tk()\nGame(root)\nroot.mainloop()\n'

# ---------------------------------------------------------------
# The simulators (a tiny local web server + Windows / iOS 7 pages)
# ---------------------------------------------------------------
SIM_CODE = 'import os\nimport secrets\nimport shutil\nimport subprocess\nimport sys\nimport threading\nimport time\nimport urllib.parse\nimport webbrowser\nfrom http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\n\nPAGES = {}   # filled in below: "windows" and "ios"\nCOMMON_JS = r\'\'\'const TOKEN="__TOKEN__";\nconst TZ="Australia/Melbourne";\nconst CITIES=[["Melbourne","Australia/Melbourne"],["Tokyo","Asia/Tokyo"],["London","Europe/London"],["New York","America/New_York"],["Los Angeles","America/Los_Angeles"],["Dubai","Asia/Dubai"]];\nfunction fmt(tz,o){return new Intl.DateTimeFormat("en-AU",Object.assign({timeZone:tz},o)).format(new Date()).toUpperCase().replace(/\\s/g," ");}\nfunction melb(){\n  const d=new Date();\n  const f=function(o){return new Intl.DateTimeFormat("en-AU",Object.assign({timeZone:TZ},o));};\n  let zone="AEST";\n  try{const p=f({timeZoneName:"short"}).formatToParts(d).find(function(x){return x.type==="timeZoneName";}); if(p)zone=p.value;}catch(e){}\n  return {\n    time:fmt(TZ,{hour:"numeric",minute:"2-digit",hour12:true}),\n    timeS:fmt(TZ,{hour:"numeric",minute:"2-digit",second:"2-digit",hour12:true}),\n    date:fmt(TZ,{day:"2-digit",month:"2-digit",year:"numeric"}),\n    long:f({weekday:"long",day:"numeric",month:"long"}).format(d),\n    weekday:f({weekday:"long"}).format(d),\n    day:f({day:"numeric"}).format(d),\n    hms:new Intl.DateTimeFormat("en-GB",{timeZone:TZ,hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false}).format(d).split(":").map(Number),\n    zone:zone\n  };\n}\nfunction openSite(url,o){\n  o=o||{};\n  const q=new URLSearchParams({token:TOKEN,url:url,w:Math.round(o.w||1000),h:Math.round(o.h||680),x:Math.round(o.x||0),y:Math.round(o.y||0),mobile:o.mobile?1:0});\n  fetch("/open?"+q).catch(function(){});\n}\nfunction toUrl(t){\n  t=(t||"").trim(); if(!t)return null;\n  if(/^https?:\\/\\//i.test(t))return t;\n  if(/^[^\\s]+\\.[a-z]{2,}(\\/\\S*)?$/i.test(t))return "https://"+t;\n  return "https://www.google.com/search?q="+encodeURIComponent(t);\n}\nfunction ping(){fetch("/ping?token="+TOKEN).catch(function(){});}\nping(); setInterval(ping,2000);\nfunction store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){return null;}}\nfunction Calc(onChange){\n  let cur="0",prev=null,op=null,fresh=true;\n  const fm=function(n){return String(parseFloat(n.toPrecision(10)));};\n  function compute(){\n    const b=parseFloat(cur); let r=prev;\n    if(op==="+")r=prev+b; else if(op==="-")r=prev-b; else if(op==="\\u00d7")r=prev*b; else if(op==="\\u00f7")r=(b===0?NaN:prev/b);\n    if(isFinite(r)){cur=fm(r);prev=r;}else{cur="Error";prev=null;}\n  }\n  function press(k){\n    if(cur==="Error"&&k!=="C"&&k!=="AC")return;\n    if(/^\\d$/.test(k)){ if(fresh||cur==="0"){cur=k;fresh=false;} else if(cur.replace(/[-.]/g,"").length<9)cur+=k; }\n    else if(k==="."){ if(fresh){cur="0.";fresh=false;} else if(cur.indexOf(".")<0)cur+="."; }\n    else if(k==="C"||k==="AC"){cur="0";prev=null;op=null;fresh=true;}\n    else if(k==="\\u00b1"){ cur=cur.charAt(0)==="-"?cur.slice(1):(cur==="0"?cur:"-"+cur); }\n    else if(k==="%"){ cur=fm(parseFloat(cur)/100); fresh=true; }\n    else if("+-\\u00d7\\u00f7".indexOf(k)>=0){ if(op&&!fresh)compute(); prev=parseFloat(cur); op=k; fresh=true; }\n    else if(k==="="){ if(op){compute();op=null;} fresh=true; }\n    onChange(cur,op);\n  }\n  return {press:press};\n}\n\'\'\'\nPAGES["windows"] = r\'\'\'<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>Windows Sim</title>\n<style>\n*{box-sizing:border-box;user-select:none}\nhtml,body{margin:0;height:100%;overflow:hidden;font-family:"Segoe UI",system-ui,sans-serif;color:#fff;font-size:14px}\n#desk{position:absolute;inset:0 0 48px 0;overflow:hidden;\n background:radial-gradient(900px 600px at 72% 28%,rgba(120,190,255,.85),transparent 60%),radial-gradient(700px 500px at 30% 85%,rgba(150,80,255,.55),transparent 65%),linear-gradient(135deg,#0a2a7a,#1456d8 45%,#0b1c5e)}\n#desk:before{content:"";position:absolute;left:50%;top:48%;width:420px;height:420px;margin:-210px;border-radius:50%;background:conic-gradient(from 20deg,#3aa0ff,#7c5cff,#e86aff,#3aa0ff);filter:blur(60px);opacity:.55}\n#icons{position:absolute;left:8px;top:8px;bottom:8px;display:grid;grid-auto-flow:column;grid-template-rows:repeat(auto-fill,98px);grid-auto-columns:92px;align-content:start}\n.di{width:88px;height:94px;display:flex;flex-direction:column;align-items:center;padding-top:6px;border:1px solid transparent;border-radius:4px;text-align:center;font-size:12px;text-shadow:0 1px 3px #000}\n.di:hover{background:rgba(255,255,255,.14)} .di.sel{background:rgba(255,255,255,.25);border-color:rgba(255,255,255,.4)}\n.tile{border-radius:22%;display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 2px 6px rgba(0,0,0,.35);margin-bottom:4px;line-height:1}\n.tri{display:block;border-left:.46em solid #fff;border-top:.3em solid transparent;border-bottom:.3em solid transparent;margin-left:.1em}\n.tk{color:#fff;text-shadow:-2px -1px 0 #25f4ee,2px 1px 0 #fe2c55;font-weight:700}\n#task{position:absolute;left:0;right:0;bottom:0;height:48px;background:rgba(28,28,34,.88);backdrop-filter:blur(18px);border-top:1px solid rgba(255,255,255,.1);display:flex;align-items:center;justify-content:space-between;z-index:9000}\n#tl{flex:1;display:flex;justify-content:center;align-items:center;gap:4px;padding-left:210px}\n.tb2{width:42px;height:40px;border-radius:6px;display:flex;align-items:center;justify-content:center;position:relative}\n.tb2:hover{background:rgba(255,255,255,.12)} .tb2.run:after{content:"";position:absolute;bottom:2px;left:14px;right:14px;height:3px;border-radius:2px;background:#76b9ff}\n.tb2.act{background:rgba(255,255,255,.16)}\n#startbtn{display:grid;grid-template-columns:11px 11px;gap:2px}\n#startbtn i{width:11px;height:11px;background:#4cc2ff;display:block}\n#tray{display:flex;align-items:center;gap:12px;padding-right:8px;font-size:12px}\n#clk{text-align:right;line-height:1.15;padding:3px 8px;border-radius:6px;min-width:128px}\n#clk:hover{background:rgba(255,255,255,.12)} #clk small{display:block;font-size:10px;color:#9fd0ff}\n.win{position:absolute;background:#2b2b31;border:1px solid rgba(255,255,255,.18);border-radius:8px;box-shadow:0 12px 40px rgba(0,0,0,.55);display:flex;flex-direction:column;overflow:hidden;min-width:260px;min-height:160px}\n.win.max{left:0!important;top:0!important;width:100%!important;height:100%!important;border-radius:0}\n.win.min{display:none}\n.tbar{height:34px;background:#202026;display:flex;align-items:center;padding-left:10px;gap:8px;flex:none;cursor:default}\n.tbar .tt{flex:1;font-size:12px}\n.tbar .ti{font-size:14px}\n.tc{display:flex;height:100%} .tc b{width:46px;display:flex;align-items:center;justify-content:center;font-weight:400;font-size:13px}\n.tc b:hover{background:rgba(255,255,255,.12)} .tc b.cl:hover{background:#e81123}\n.wb{flex:1;overflow:auto;background:#fff;color:#111;position:relative}\n.wb.dark{background:#1f1f24;color:#fff}\ntextarea.np{width:100%;height:100%;border:0;outline:0;resize:none;padding:10px;font:14px Consolas,monospace;user-select:text}\n.bar{display:flex;gap:6px;padding:8px;background:#f1f3f4;border-bottom:1px solid #ddd}\n.bar button{border:0;background:transparent;font-size:16px;width:30px;border-radius:50%} .bar button:hover{background:#ddd}\n.bar input{flex:1;border:1px solid #ccc;border-radius:16px;padding:6px 14px;font-size:13px;outline:0;user-select:text}\n.bar input:focus{border-color:#1a73e8}\n.sites{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:30px 24px}\n.site{background:#f4f6fa;border-radius:10px;padding:18px 8px;text-align:center;font-size:13px;color:#222}\n.site:hover{background:#e3ebfa} .site span{display:block;font-size:26px;margin-bottom:6px}\n.hint{text-align:center;color:#777;font-size:12px;padding:0 20px}\n.calc{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;padding:2px;height:100%;background:#1f1f24}\n.calc .disp{grid-column:1/5;text-align:right;font-size:38px;padding:14px 12px;font-weight:300;align-self:end;overflow:hidden}\n.calc button{border:0;background:#3a3a42;color:#fff;font-size:18px;border-radius:4px} .calc button:hover{background:#4a4a54}\n.calc button.o{background:#3b7ddd} .calc button.e{background:#4cc2ff;color:#000}\n.clist{padding:12px 18px} .crow{display:flex;justify-content:space-between;align-items:baseline;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.12)}\n.crow b{font-size:26px;font-weight:300} .crow.m b{color:#4cc2ff}\n.pcrow{padding:14px 18px;border-bottom:1px solid #eee}\n#start{position:absolute;left:50%;bottom:56px;width:520px;margin-left:-260px;height:560px;background:rgba(36,36,44,.94);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.14);border-radius:10px;z-index:9500;display:none;flex-direction:column;box-shadow:0 12px 40px rgba(0,0,0,.5)}\n#start.open{display:flex}\n#start h4{margin:22px 28px 10px;font-weight:600;font-size:13px}\n#sgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:0 20px}\n.sa{display:flex;flex-direction:column;align-items:center;padding:12px 4px;border-radius:6px;font-size:12px}\n.sa:hover{background:rgba(255,255,255,.1)}\n#sfoot{margin-top:auto;height:62px;background:rgba(0,0,0,.25);display:flex;align-items:center;justify-content:space-between;padding:0 24px;border-radius:0 0 10px 10px}\n#pw{position:relative}\n#pwm{display:none;position:absolute;right:0;bottom:44px;background:#2d2d35;border:1px solid rgba(255,255,255,.15);border-radius:8px;width:150px;overflow:hidden}\n#pwm.open{display:block} #pwm div{padding:10px 14px;font-size:13px} #pwm div:hover{background:rgba(255,255,255,.12)}\n.round{width:36px;height:36px;border-radius:50%;background:#4a6df0;display:flex;align-items:center;justify-content:center}\n#fly{position:absolute;right:8px;bottom:56px;width:330px;background:rgba(36,36,44,.95);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.14);border-radius:10px;z-index:9500;display:none;padding:18px 22px;box-shadow:0 12px 40px rgba(0,0,0,.5)}\n#fly.open{display:block}\n#fly .big{font-size:42px;font-weight:300} #fly .lbl{color:#9fd0ff;margin-bottom:12px}\n#toast{position:absolute;right:14px;bottom:60px;background:rgba(36,36,44,.95);border:1px solid rgba(255,255,255,.18);border-radius:8px;padding:12px 18px;z-index:9800;display:none}\n#off{position:absolute;inset:0;background:#000;z-index:99999;display:none;align-items:center;justify-content:center;font-size:22px}\n</style></head><body>\n<div id="desk"><div id="icons"></div><div id="winlayer"></div></div>\n<div id="start"><h4>Pinned</h4><div id="sgrid"></div>\n <div id="sfoot"><div style="display:flex;align-items:center;gap:10px"><div class="round">&#128100;</div>You</div>\n <div id="pw"><div id="pwm"><div id="shut">&#9211; Shut down</div><div id="rest">&#8635; Restart</div></div><div class="round" id="pwb" style="background:#444">&#9211;</div></div></div></div>\n<div id="fly"><div class="big" id="fbig"></div><div class="lbl" id="flbl"></div><div id="fcities"></div></div>\n<div id="toast"></div>\n<div id="task"><div id="tl"></div>\n <div id="tray"><span>&#8963;</span><span>&#128246;</span><span>&#128266;</span><div id="clk"><div id="ct"></div><div id="cd"></div><small id="cz"></small></div></div></div>\n<div id="off">Shutting down&hellip;</div>\n<script>\n/*COMMON*/\nconst APPS=[\n {id:"web",name:"Web Browser",bg:"linear-gradient(135deg,#0ea5e9,#2563eb)",glyph:"&#127760;",type:"win"},\n {id:"yt",name:"YouTube",bg:"#ff0000",glyph:"<i class=\'tri\'></i>",type:"site",url:"https://www.youtube.com/"},\n {id:"shorts",name:"YT Shorts",bg:"linear-gradient(135deg,#ff0050,#ff5a3c)",glyph:"<b style=\'font-style:italic\'>S</b>",type:"site",url:"https://www.youtube.com/shorts"},\n {id:"tt",name:"TikTok",bg:"#000",glyph:"<span class=\'tk\'>&#9834;</span>",type:"site",url:"https://www.tiktok.com/"},\n {id:"note",name:"Notepad",bg:"linear-gradient(135deg,#7dd3fc,#38bdf8)",glyph:"&#128221;",type:"win"},\n {id:"calc",name:"Calculator",bg:"linear-gradient(135deg,#64748b,#1e293b)",glyph:"&#129518;",type:"win"},\n {id:"clock",name:"Clock",bg:"linear-gradient(135deg,#8b5cf6,#6d28d9)",glyph:"&#128338;",type:"win"},\n {id:"pc",name:"This PC",bg:"linear-gradient(135deg,#60a5fa,#3b82f6)",glyph:"&#128187;",type:"win"},\n {id:"bin",name:"Recycle Bin",bg:"linear-gradient(135deg,#94a3b8,#64748b)",glyph:"&#128465;",type:"win"}\n];\nconst PINNED=["web","yt","shorts","tt","note","calc"];\nconst $=function(s){return document.querySelector(s);};\nfunction app(id){return APPS.find(function(a){return a.id===id;});}\nfunction tile(a,s){return "<div class=\'tile\' style=\'width:"+s+"px;height:"+s+"px;background:"+a.bg+";font-size:"+Math.round(s*0.55)+"px\'>"+a.glyph+"</div>";}\nfunction toast(t){const e=$("#toast");e.textContent=t;e.style.display="block";clearTimeout(toast.t);toast.t=setTimeout(function(){e.style.display="none";},2600);}\n\n/* desktop icons */\nAPPS.forEach(function(a){\n  const d=document.createElement("div");d.className="di";d.innerHTML=tile(a,48)+"<span>"+a.name+"</span>";\n  d.onclick=function(e){e.stopPropagation();document.querySelectorAll(".di").forEach(function(x){x.classList.remove("sel");});d.classList.add("sel");};\n  d.ondblclick=function(){launch(a.id);};\n  $("#icons").appendChild(d);\n});\n$("#desk").addEventListener("mousedown",function(){document.querySelectorAll(".di").forEach(function(x){x.classList.remove("sel");});closePops();});\n\n/* start menu */\nAPPS.slice(0,8).forEach(function(a){\n  const d=document.createElement("div");d.className="sa";d.innerHTML=tile(a,40)+"<span>"+a.name+"</span>";\n  d.onclick=function(){closePops();launch(a.id);};$("#sgrid").appendChild(d);\n});\nfunction closePops(){$("#start").classList.remove("open");$("#fly").classList.remove("open");$("#pwm").classList.remove("open");}\n$("#pwb").onclick=function(e){e.stopPropagation();$("#pwm").classList.toggle("open");};\nfunction powerOff(){$("#off").style.display="flex";fetch("/quit?token="+TOKEN).catch(function(){});setTimeout(function(){window.close();},900);}\n$("#shut").onclick=powerOff; $("#rest").onclick=function(){location.reload();};\n\n/* taskbar */\nconst wins={}; let zc=10, nwin=0, nsite=0;\nfunction renderTask(){\n  const t=$("#tl");t.innerHTML="";\n  const sb=document.createElement("div");sb.className="tb2";sb.innerHTML="<div id=\'startbtn\'><i></i><i></i><i></i><i></i></div>";\n  sb.onclick=function(e){e.stopPropagation();const o=$("#start").classList.contains("open");closePops();if(!o)$("#start").classList.add("open");};\n  t.appendChild(sb);\n  const ids=PINNED.slice();Object.keys(wins).forEach(function(k){if(ids.indexOf(k)<0)ids.push(k);});\n  ids.forEach(function(id){\n    const a=app(id);const b=document.createElement("div");b.className="tb2"+(wins[id]?" run":"")+(wins[id]&&wins[id].active?" act":"");\n    b.innerHTML=tile(a,26);b.title=a.name;b.onclick=function(){closePops();if(wins[id]&&a.type==="win"){toggleWin(id);}else{launch(id);}};\n    t.appendChild(b);\n  });\n}\nfunction launch(id){\n  const a=app(id);\n  if(a.type==="site"){\n    toast("Opening "+a.name+" in a new window\\u2026");\n    openSite(a.url,{w:1000,h:680,x:window.screenX+90+nsite*34,y:window.screenY+50+nsite*34});nsite=(nsite+1)%6;return;\n  }\n  openWin(id);\n}\n\n/* window manager */\nfunction focusWin(id){Object.keys(wins).forEach(function(k){wins[k].active=false;});const w=wins[id];w.active=true;w.el.style.zIndex=++zc;w.el.classList.remove("min");renderTask();}\nfunction toggleWin(id){const w=wins[id];if(w.active&&!w.el.classList.contains("min")){w.el.classList.add("min");w.active=false;renderTask();}else focusWin(id);}\nfunction openWin(id){\n  if(wins[id]){focusWin(id);return;}\n  const a=app(id);const sz={web:[760,520],note:[520,380],calc:[300,440],clock:[360,400],pc:[480,300],bin:[420,260]}[id]||[480,360];\n  const el=document.createElement("div");el.className="win";\n  el.style.cssText="width:"+sz[0]+"px;height:"+sz[1]+"px;left:"+(70+nwin*30)+"px;top:"+(36+nwin*30)+"px";nwin=(nwin+1)%7;\n  el.innerHTML="<div class=\'tbar\'><span class=\'ti\'>"+(a.glyph.indexOf("<")<0?a.glyph:"")+"</span><span class=\'tt\'>"+a.name+"</span><div class=\'tc\'><b class=\'mn\'>&#8211;</b><b class=\'mx\'>&#9723;</b><b class=\'cl\'>&#10005;</b></div></div><div class=\'wb\'></div>";\n  $("#winlayer").appendChild(el);\n  const body=el.querySelector(".wb");BUILD[id](body);\n  wins[id]={el:el,active:false};\n  const tb=el.querySelector(".tbar");\n  tb.addEventListener("mousedown",function(e){\n    focusWin(id);if(e.target.closest(".tc")||el.classList.contains("max"))return;\n    const ox=e.clientX-el.offsetLeft,oy=e.clientY-el.offsetTop;\n    function mv(ev){el.style.left=(ev.clientX-ox)+"px";el.style.top=Math.max(0,ev.clientY-oy)+"px";}\n    function up(){document.removeEventListener("mousemove",mv);document.removeEventListener("mouseup",up);}\n    document.addEventListener("mousemove",mv);document.addEventListener("mouseup",up);\n  });\n  tb.addEventListener("dblclick",function(e){if(!e.target.closest(".tc"))el.classList.toggle("max");});\n  el.addEventListener("mousedown",function(){if(!wins[id].active)focusWin(id);});\n  el.querySelector(".mn").onclick=function(){el.classList.add("min");wins[id].active=false;renderTask();};\n  el.querySelector(".mx").onclick=function(){el.classList.toggle("max");};\n  el.querySelector(".cl").onclick=function(){el.remove();delete wins[id];renderTask();};\n  focusWin(id);\n}\nconst BUILD={\n web:function(b){\n  b.innerHTML="<div class=\'bar\'><button>&#8592;</button><button>&#8594;</button><button>&#8635;</button><input placeholder=\'Search or type a web address\'><button class=\'go\'>&#10148;</button></div>"+\n  "<div class=\'sites\'></div><div class=\'hint\'>Pages open in a real browser window, so YouTube, TikTok and every website work for real.</div>";\n  const inp=b.querySelector("input");\n  function go(v){const u=toUrl(v);if(!u)return;toast("Opening "+u.replace(/^https?:\\/\\//,"").slice(0,40)+"\\u2026");openSite(u,{w:1000,h:680,x:window.screenX+100+nsite*34,y:window.screenY+60+nsite*34});nsite=(nsite+1)%6;}\n  inp.addEventListener("keydown",function(e){if(e.key==="Enter")go(inp.value);});\n  b.querySelector(".go").onclick=function(){go(inp.value);};\n  [["&#128269;","Google","https://www.google.com"],["&#128214;","Wikipedia","https://www.wikipedia.org"],["&#9654;&#65039;","YouTube","https://www.youtube.com"],["&#128172;","Reddit","https://www.reddit.com"],["&#128240;","BBC News","https://www.bbc.com/news"],["&#128049;","GitHub","https://github.com"]].forEach(function(s){\n    const d=document.createElement("div");d.className="site";d.innerHTML="<span>"+s[0]+"</span>"+s[1];d.onclick=function(){go(s[2]);};b.querySelector(".sites").appendChild(d);});\n },\n note:function(b){const t=document.createElement("textarea");t.className="np";t.placeholder="Type here\\u2026";t.value=store("w_note")||"";t.oninput=function(){store("w_note",t.value);};b.appendChild(t);},\n calc:function(b){\n  b.className="wb dark";const g=document.createElement("div");g.className="calc";g.innerHTML="<div class=\'disp\'>0</div>";\n  const c=Calc(function(v){g.querySelector(".disp").textContent=v;});\n  ["AC","\\u00b1","%","\\u00f7","7","8","9","\\u00d7","4","5","6","-","1","2","3","+","0",".","="].forEach(function(k){\n    const bt=document.createElement("button");bt.textContent=k;if("\\u00f7\\u00d7-+".indexOf(k)>=0)bt.className="o";if(k==="=")bt.className="e";if(k==="0")bt.style.gridColumn="1/3";\n    bt.onclick=function(){c.press(k);};g.appendChild(bt);});\n  b.appendChild(g);\n },\n clock:function(b){\n  b.className="wb dark";const l=document.createElement("div");l.className="clist";b.appendChild(l);\n  function up(){l.innerHTML=CITIES.map(function(c,i){return "<div class=\'crow"+(i===0?" m":"")+"\'><span>"+c[0]+(i===0?" (home)":"")+"<br><small style=\'color:#9aa\'>"+fmt(c[1],{weekday:"short",day:"numeric",month:"short"})+"</small></span><b>"+fmt(c[1],{hour:"numeric",minute:"2-digit",hour12:true})+"</b></div>";}).join("");}\n  up();b._t=setInterval(function(){if(!document.body.contains(b)){clearInterval(b._t);return;}up();},1000);\n },\n pc:function(b){b.innerHTML="<div class=\'pcrow\'>&#128190; Local Disk (C:) &mdash; 312 GB free of 476 GB</div><div class=\'pcrow\'>&#128193; Documents</div><div class=\'pcrow\'>&#128193; Downloads</div><div class=\'pcrow\'>&#127918; 69ls Games</div>";},\n bin:function(b){b.innerHTML="<div class=\'hint\' style=\'padding-top:80px\'>The Recycle Bin is empty.</div>";}\n};\n\n/* clocks */\nfunction tick(){\n  const m=melb();$("#ct").textContent=m.timeS;$("#cd").textContent=m.date;$("#cz").textContent="Melbourne \\u00b7 "+m.zone;\n  if($("#fly").classList.contains("open")){\n    $("#fbig").textContent=m.timeS;$("#flbl").textContent=m.long+" \\u2014 Melbourne ("+m.zone+")";\n    $("#fcities").innerHTML=CITIES.slice(1).map(function(c){return "<div class=\'crow\' style=\'padding:8px 0\'><span>"+c[0]+"</span><span>"+fmt(c[1],{hour:"numeric",minute:"2-digit",hour12:true})+"</span></div>";}).join("");\n  }\n}\n$("#clk").onclick=function(e){e.stopPropagation();const o=$("#fly").classList.contains("open");closePops();if(!o){$("#fly").classList.add("open");}tick();};\ndocument.addEventListener("mousedown",function(e){if(!e.target.closest("#start,#fly,#task"))closePops();});\nsetInterval(tick,1000);tick();renderTask();\nsetTimeout(function(){toast("Welcome! Double-click an icon, or use the Start menu.");},600);\n</script></body></html>\n\'\'\'\nPAGES["ios"] = r\'\'\'<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>iOS 7 Sim</title>\n<style>\n*{box-sizing:border-box;user-select:none;-webkit-tap-highlight-color:transparent}\nhtml,body{margin:0;height:100%;overflow:hidden;background:radial-gradient(circle at 50% 40%,#3a3f4b,#14161b);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}\n#phone{position:absolute;left:50%;top:50%;width:400px;height:780px;margin:-390px 0 0 -200px;transform-origin:50% 50%;\n background:linear-gradient(145deg,#2a2b2f,#0b0b0d);border-radius:58px;box-shadow:0 0 0 3px #6b6e75,0 0 0 6px #17181b,0 30px 80px rgba(0,0,0,.7)}\n#spk{position:absolute;left:150px;top:44px;width:100px;height:10px;border-radius:5px;background:#050506;box-shadow:inset 0 1px 2px #333}\n#cam{position:absolute;left:112px;top:42px;width:14px;height:14px;border-radius:50%;background:radial-gradient(#2c3a6a,#05060a)}\n#hb{position:absolute;left:174px;top:706px;width:52px;height:52px;border-radius:50%;border:2px solid #3a3b40;background:#0c0c0e;display:flex;align-items:center;justify-content:center}\n#hb:active{background:#1b1b1f} #hb i{width:18px;height:18px;border:2px solid #777;border-radius:5px;display:block}\n#pwr{position:absolute;right:-8px;top:110px;width:6px;height:60px;background:#17181b;border-radius:0 4px 4px 0}\n#pwr:hover{background:#44474d}\n#screen{position:absolute;left:30px;top:88px;width:340px;height:604px;background:#000;overflow:hidden;border-radius:2px}\n.layer{position:absolute;inset:0}\n#wall{background-size:cover;transition:background .4s}\n#wall:after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 20% 25%,rgba(255,255,255,.22) 0 40px,transparent 41px),radial-gradient(circle at 80% 15%,rgba(255,255,255,.15) 0 60px,transparent 61px),radial-gradient(circle at 70% 70%,rgba(255,255,255,.12) 0 90px,transparent 91px),radial-gradient(circle at 25% 80%,rgba(255,255,255,.14) 0 50px,transparent 51px)}\n#status{position:absolute;left:0;right:0;top:0;height:20px;display:flex;align-items:center;justify-content:space-between;padding:0 6px;color:#fff;font-size:12px;font-weight:600;z-index:85}\n#status.dark{color:#000} #status .c{position:absolute;left:0;right:0;text-align:center;pointer-events:none}\n.sig{letter-spacing:-1px;font-size:9px;margin-right:4px}\n#home{padding-top:30px}\n#grid{display:grid;grid-template-columns:repeat(4,1fr);row-gap:12px;padding:0 4px}\n.ic{display:flex;flex-direction:column;align-items:center;font-size:11px;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6);cursor:default}\n.ic:active .sq{filter:brightness(.7)}\n.sq{width:60px;height:60px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:32px;margin-bottom:4px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.15);position:relative;overflow:hidden;color:#fff;line-height:1}\n.tri{display:block;border-left:.44em solid #fff;border-top:.28em solid transparent;border-bottom:.28em solid transparent;margin-left:.08em}\n.tk{color:#fff;text-shadow:-2px -1px 0 #25f4ee,2px 1px 0 #fe2c55;font-weight:700}\n.calic{background:#fff;color:#111;flex-direction:column;font-size:30px;font-weight:300} .calic small{font-size:9px;font-weight:600;color:#fff;background:#f33;width:100%;text-align:center;padding:2px 0;position:absolute;top:0}\n.calic b{margin-top:13px;font-weight:200}\n.clkic{background:#fff} .face{width:50px;height:50px;border-radius:50%;background:#fff;border:2px solid #222;position:relative}\n.face i{position:absolute;left:50%;bottom:50%;width:2px;background:#111;transform-origin:50% 100%;border-radius:1px}\n#dots{position:absolute;left:0;right:0;bottom:104px;text-align:center;color:rgba(255,255,255,.8);font-size:10px;letter-spacing:5px}\n#dock{position:absolute;left:0;right:0;bottom:0;height:92px;background:rgba(255,255,255,.22);backdrop-filter:blur(12px);display:flex;justify-content:space-around;align-items:center;padding:0 4px}\n#dock .ic{flex:1}\n#applayer{display:none;background:#fff;z-index:40;flex-direction:column}\n#applayer.open{display:flex;animation:pop .25s ease-out}\n@keyframes pop{from{transform:scale(.3);opacity:0}to{transform:scale(1);opacity:1}}\n.nav{flex:none;height:64px;padding-top:20px;background:rgba(247,247,247,.95);border-bottom:1px solid #b2b2b2;text-align:center;font-weight:600;font-size:17px;line-height:44px;color:#000}\n.appbody{flex:1;overflow:auto;position:relative}\n#lock{z-index:80;color:#fff;transition:transform .45s cubic-bezier(.3,.7,.3,1)}\n#lock.off{transform:translateY(-105%)}\n#lk{position:absolute;left:0;right:0;top:60px;text-align:center}\n#lk .t{font-size:78px;font-weight:100;letter-spacing:-2px;line-height:1}\n#lk .d{font-size:18px;margin-top:6px;font-weight:300} #lk .z{font-size:12px;opacity:.85;margin-top:6px}\n#slider{position:absolute;left:30px;right:30px;bottom:36px;height:56px;border-radius:28px;background:rgba(0,0,0,.25);overflow:hidden}\n#slider .txt{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding-left:46px;font-size:22px;font-weight:300;\n background:linear-gradient(90deg,rgba(255,255,255,.35) 30%,#fff 50%,rgba(255,255,255,.35) 70%);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shim 2.2s linear infinite}\n@keyframes shim{from{background-position:200% 0}to{background-position:-200% 0}}\n#knob{position:absolute;left:3px;top:3px;width:50px;height:50px;border-radius:25px;background:linear-gradient(#f4f4f4,#bdbdbd);display:flex;align-items:center;justify-content:center;color:#555;font-size:22px;touch-action:none;cursor:grab}\n#dim{background:#000;opacity:0;pointer-events:none;z-index:95}\n#alertbg{display:none;background:rgba(0,0,0,.4);z-index:90;align-items:center;justify-content:center}\n#alertbg.open{display:flex}\n#alert{width:250px;background:rgba(245,245,245,.96);border-radius:12px;text-align:center;color:#000}\n#alert h3{margin:0;padding:18px 16px 4px;font-size:17px} #alert p{margin:0;padding:0 16px 16px;font-size:13px}\n#alert div{border-top:1px solid #b8b8b8;padding:12px;color:#007aff;font-size:17px;font-weight:600}\n.tog{width:51px;height:31px;border-radius:16px;background:#ddd;position:relative;transition:.2s;flex:none} .tog:after{content:"";position:absolute;left:2px;top:2px;width:27px;height:27px;border-radius:50%;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.3);transition:.2s}\n.tog.on{background:#4cd964} .tog.on:after{left:22px}\n.srow{background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 14px;height:44px;border-bottom:1px solid #ddd;font-size:17px;color:#000}\n.sec{font-size:13px;color:#6d6d72;padding:22px 14px 6px;text-transform:uppercase}\n.swatches{display:flex;gap:8px;padding:10px 14px;background:#fff}\n.sw{width:44px;height:64px;border-radius:6px;border:2px solid transparent} .sw.sel{border-color:#007aff}\n.cities{background:#000;color:#fff;height:100%;padding:0 12px}\n.crow{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #333}\n.crow b{font-size:38px;font-weight:200} .crow small{color:#999;display:block;font-size:12px} .crow span{font-size:20px}\n.crow.m b{color:#ff9500}\n.cdisp{color:#fff;font-size:64px;font-weight:200;text-align:right;padding:0 16px 8px;height:130px;display:flex;align-items:flex-end;justify-content:flex-end;overflow:hidden}\n.ckeys{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#222;flex:1}\n.ckeys button{border:0;background:#333;color:#fff;font-size:26px;font-weight:300} .ckeys button:active{background:#777}\n.ckeys .f{background:#a5a5a5;color:#000} .ckeys .o{background:#ff9500} .ckeys .o.on{background:#fff;color:#ff9500}\n.notepad{width:100%;height:100%;border:0;outline:0;resize:none;padding:10px 14px;font:19px "Marker Felt","Comic Sans MS",cursive;background:repeating-linear-gradient(#fffbd5 0,#fffbd5 29px,#e3d9a0 30px);line-height:30px;user-select:text;color:#222}\n.saf{padding:10px}\n.saf input{width:100%;padding:8px 12px;border-radius:8px;border:0;background:#e5e5ea;font-size:16px;outline:0;user-select:text}\n.stiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:26px 10px}\n.stile{text-align:center;font-size:11px;color:#333} .stile div{width:56px;height:56px;border-radius:12px;background:#f2f2f7;margin:0 auto 4px;display:flex;align-items:center;justify-content:center;font-size:28px}\n.splash{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:#fff;padding:30px}\n.splash p{font-size:14px;opacity:.85}\n.spin{width:30px;height:30px;border:3px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:rot 1s linear infinite;margin-top:14px} @keyframes rot{to{transform:rotate(360deg)}}\n</style></head><body>\n<div id="phone">\n <div id="cam"></div><div id="spk"></div><div id="pwr" title="Lock / wake"></div>\n <div id="screen">\n  <div class="layer" id="wall"></div>\n  <div class="layer" id="home"><div id="grid"></div><div id="dots">&#9679; &#9675;</div><div id="dock"></div></div>\n  <div class="layer" id="applayer"><div class="nav" id="nav"></div><div class="appbody" id="appbody"></div></div>\n  <div id="status"><span><span class="sig">&#9679;&#9679;&#9679;&#9679;&#9675;</span>Telstra &#8776;</span><span class="c" id="stime"></span><span>100% &#9646;&#9646;&#9646;</span></div>\n  <div class="layer" id="lock"><div class="layer" id="wall2"></div>\n   <div id="lk"><div class="t" id="lt"></div><div class="d" id="ld"></div><div class="z" id="lz"></div></div>\n   <div id="slider"><div class="txt">slide to unlock</div><div id="knob">&#10095;</div></div></div>\n  <div class="layer" id="alertbg"><div id="alert"><h3 id="at"></h3><p id="am"></p><div id="ok">OK</div></div></div>\n  <div class="layer" id="dim"></div>\n </div>\n <div id="hb"><i></i></div>\n</div>\n<script>\n/*COMMON*/\nconst $=function(s){return document.querySelector(s);};\nfunction fit(){const k=Math.min(innerWidth/410,innerHeight/790);$("#phone").style.transform="scale("+k+")";}\nfit();addEventListener("resize",fit);\nconst WALLS=["linear-gradient(160deg,#2b1d63 0%,#7b3fa0 40%,#e86a92 75%,#f9b36a 100%)","linear-gradient(180deg,#0f2027,#203a43,#2c5364)","linear-gradient(160deg,#00c6ff,#0072ff)","linear-gradient(160deg,#f7971e,#ffd200)","linear-gradient(160deg,#11998e,#38ef7d)"];\nlet wallIdx=parseInt(store("i_wall")||"0",10)||0;\nfunction setWall(i){wallIdx=i;store("i_wall",String(i));$("#wall").style.background=WALLS[i];$("#wall2").style.background=WALLS[i];}\nsetWall(wallIdx);\nfunction tri(){return "<i class=\'tri\'></i>";}\nconst HOME=[\n ["Messages","msg","linear-gradient(#6ff07a,#1bb831)","&#128172;"],["Calendar","cal"],["Photos","photos","linear-gradient(#fff,#e8e8e8)","&#127804;"],["Camera","cam","linear-gradient(#aaa,#555)","&#128247;"],\n ["Weather","weather","linear-gradient(#4aa8ff,#1d6fe0)","&#9925;"],["Clock","clock"],["Maps","maps","linear-gradient(#7fe08a,#3aa0ff)","&#128506;"],["Notes","notes","linear-gradient(#fff6a8,#ffd952)","&#128210;"],\n ["YouTube","yt","#e52d27",tri()],["YT Shorts","shorts","linear-gradient(135deg,#ff0050,#ff5a3c)","<b style=\'font-style:italic\'>S</b>"],["TikTok","tt","#010101","<span class=\'tk\'>&#9834;</span>"],["Calculator","calc","linear-gradient(#666,#222)","&#129518;"],\n ["Settings","settings","linear-gradient(#c5cbd3,#7d848c)","&#9881;"],["App Store","store","linear-gradient(#5ac8fa,#1d62f0)","&#9400;"]\n];\nconst DOCK=[["Phone","phone","linear-gradient(#6ff07a,#1bb831)","&#128222;"],["Mail","mail","linear-gradient(#5ac8fa,#1d62f0)","&#9993;"],["Safari","safari","linear-gradient(#fff,#d6e9ff)","&#129517;"],["Music","music","linear-gradient(#ff9a5c,#ff3b30)","&#127925;"]];\nfunction icon(d){\n  let inner;\n  if(d[1]==="cal")inner="<div class=\'sq calic\'><small id=\'calw\'></small><b id=\'cald\'></b></div>";\n  else if(d[1]==="clock")inner="<div class=\'sq clkic\'><div class=\'face\'><i id=\'hh\' style=\'height:13px\'></i><i id=\'mh\' style=\'height:19px\'></i><i id=\'sh\' style=\'height:21px;width:1px;background:#f33\'></i></div></div>";\n  else inner="<div class=\'sq\' style=\'background:"+d[2]+"\'>"+d[3]+"</div>";\n  const e=document.createElement("div");e.className="ic";e.innerHTML=inner+"<span>"+d[0]+"</span>";\n  e.onclick=function(){openApp(d[1],d[0]);};return e;\n}\nHOME.forEach(function(d){$("#grid").appendChild(icon(d));});\nDOCK.forEach(function(d){const e=icon(d);e.querySelector("span").remove();$("#dock").appendChild(e);});\n\n/* alerts */\nfunction alertBox(t,m){$("#at").textContent=t;$("#am").textContent=m;$("#alertbg").classList.add("open");}\n$("#ok").onclick=function(){$("#alertbg").classList.remove("open");};\n\n/* mobile web overlay window */\nfunction openMobile(url){\n  const r=$("#screen").getBoundingClientRect();\n  openSite(url,{mobile:true,w:r.width+(outerWidth-innerWidth),h:r.height+(outerHeight-innerHeight),x:window.screenX+r.left,y:window.screenY+r.top});\n}\nconst SITES={yt:["YouTube","https://m.youtube.com/","#e52d27"],shorts:["YouTube Shorts","https://m.youtube.com/shorts","#d4003d"],tt:["TikTok","https://www.tiktok.com/","#010101"]};\n\n/* apps */\nlet current=null;\nfunction showApp(title,dark,body,navColor){\n  $("#nav").textContent=title;$("#nav").style.display=navColor===false?"none":"block";\n  $("#appbody").innerHTML="";$("#appbody").appendChild(body);\n  $("#applayer").style.background=dark?"#000":"#fff";$("#nav").style.background=dark?"#111":"rgba(247,247,247,.95)";$("#nav").style.color=dark?"#fff":"#000";\n  $("#status").className=dark?"":"dark";\n  $("#applayer").classList.remove("open");void $("#applayer").offsetWidth;$("#applayer").classList.add("open");\n}\nfunction closeApp(){current=null;$("#applayer").classList.remove("open");$("#status").className="";}\nfunction openApp(id,name){\n  if(SITES[id]){\n    const s=SITES[id];current=id;\n    const b=document.createElement("div");b.style.cssText="position:absolute;inset:0;background:"+s[2];\n    b.innerHTML="<div class=\'splash\'><div style=\'font-size:20px;font-weight:600\'>"+s[0]+"</div><div class=\'spin\'></div><p style=\'margin-top:20px\'>Opened in its own window on top of the phone.<br>Close that window, or press Home, to come back.</p></div>";\n    showApp("",true,b,false);$("#status").className="";openMobile(s[1]);return;\n  }\n  current=id;\n  if(id==="calc")appCalc();else if(id==="notes")appNotes();else if(id==="clock")appClock();else if(id==="settings")appSettings();else if(id==="safari")appSafari();\n  else if(id==="cal"){const m=melb();alertBox("Calendar","Today is "+m.long+" in Melbourne.");current=null;}\n  else{current=null;alertBox(name,"This app isn\\u2019t part of the sim. Try YouTube, Shorts, TikTok, Safari, Calculator, Notes, Clock or Settings.");}\n}\nfunction appCalc(){\n  const w=document.createElement("div");w.style.cssText="position:absolute;inset:0;display:flex;flex-direction:column;background:#000;padding-top:20px";\n  w.innerHTML="<div class=\'cdisp\'>0</div><div class=\'ckeys\'></div>";const K=w.querySelector(".ckeys");let opb=null;\n  const c=Calc(function(v,op){w.querySelector(".cdisp").textContent=v;w.querySelector(".cdisp").style.fontSize=v.length>7?"44px":"64px";K.querySelectorAll(".o").forEach(function(b){b.classList.toggle("on",b.textContent===op);});});\n  ["AC","\\u00b1","%","\\u00f7","7","8","9","\\u00d7","4","5","6","-","1","2","3","+","0",".","="].forEach(function(k){\n    const b=document.createElement("button");b.textContent=k;\n    if("AC\\u00b1%".indexOf(k)>=0)b.className="f";if("\\u00f7\\u00d7-+=".indexOf(k)>=0)b.className="o";if(k==="0")b.style.gridColumn="1/3";\n    b.onclick=function(){c.press(k);};K.appendChild(b);});\n  showApp("",true,w,false);\n}\nfunction appNotes(){\n  const t=document.createElement("textarea");t.className="notepad";t.placeholder="Write a note\\u2026";t.value=store("i_note")||"";t.oninput=function(){store("i_note",t.value);};\n  showApp("Notes",false,t);$("#nav").style.background="#f8e46b";\n}\nfunction appClock(){\n  const w=document.createElement("div");w.className="cities";\n  function up(){w.innerHTML="<div style=\'height:8px\'></div>"+CITIES.map(function(c,i){return "<div class=\'crow"+(i===0?" m":"")+"\'><span>"+c[0]+"<small>"+fmt(c[1],{weekday:"long"})+"</small></span><b>"+fmt(c[1],{hour:"numeric",minute:"2-digit",hour12:true}).replace(" ","<span style=\'font-size:16px\'> ")+(1?"</span>":"")+"</b></div>";}).join("");}\n  up();w._t=setInterval(function(){if(current!=="clock"){clearInterval(w._t);return;}up();},1000);\n  showApp("World Clock",true,w);\n}\nfunction appSettings(){\n  const w=document.createElement("div");w.style.cssText="background:#efeff4;min-height:100%";\n  w.innerHTML="<div class=\'sec\'>Connectivity</div><div class=\'srow\'>Airplane Mode<div class=\'tog\' data-t=\'air\'></div></div><div class=\'srow\'>Wi-Fi<div class=\'tog on\' data-t=\'wifi\'></div></div>"+\n  "<div class=\'sec\'>Brightness</div><div class=\'srow\'><input id=\'br\' type=\'range\' min=\'20\' max=\'100\' value=\'"+(store("i_br")||"100")+"\' style=\'width:100%\'></div>"+\n  "<div class=\'sec\'>Wallpaper</div><div class=\'swatches\'></div>"+\n  "<div class=\'sec\'>General</div><div class=\'srow\'>Software Version<span style=\'color:#8e8e93\'>7.1</span></div><div class=\'srow\'>Time Zone<span style=\'color:#8e8e93\'>Melbourne, Australia</span></div><div class=\'srow\'>Carrier<span style=\'color:#8e8e93\'>Telstra</span></div>";\n  w.querySelectorAll(".tog").forEach(function(t){t.onclick=function(){t.classList.toggle("on");};});\n  const br=w.querySelector("#br");br.oninput=function(){store("i_br",br.value);setBright(br.value);};\n  WALLS.forEach(function(g,i){const s=document.createElement("div");s.className="sw"+(i===wallIdx?" sel":"");s.style.background=g;s.onclick=function(){setWall(i);w.querySelectorAll(".sw").forEach(function(x){x.classList.remove("sel");});s.classList.add("sel");};w.querySelector(".swatches").appendChild(s);});\n  showApp("Settings",false,w);\n}\nfunction setBright(v){$("#dim").style.opacity=String((100-v)/100*0.75);}\nsetBright(store("i_br")||100);\nfunction appSafari(){\n  const w=document.createElement("div");w.className="saf";\n  w.innerHTML="<input placeholder=\'Search or enter website name\'><div class=\'stiles\'></div><div style=\'text-align:center;color:#8e8e93;font-size:12px;padding:0 20px\'>Sites open in a real window on top of the phone.</div>";\n  const inp=w.querySelector("input");\n  function go(v){const u=toUrl(v);if(u)openMobile(u);}\n  inp.addEventListener("keydown",function(e){if(e.key==="Enter")go(inp.value);});\n  [["&#128269;","Google","https://www.google.com"],["&#128214;","Wikipedia","https://en.m.wikipedia.org"],["&#9654;&#65039;","YouTube","https://m.youtube.com"],["&#128172;","Reddit","https://www.reddit.com"],["&#128240;","BBC","https://www.bbc.com/news"],["&#128049;","GitHub","https://github.com"],["&#127925;","TikTok","https://www.tiktok.com"],["&#127911;","Spotify","https://open.spotify.com"]].forEach(function(s){\n    const d=document.createElement("div");d.className="stile";d.innerHTML="<div>"+s[0]+"</div>"+s[1];d.onclick=function(){go(s[2]);};w.querySelector(".stiles").appendChild(d);});\n  showApp("Safari",false,w);\n}\n\n/* home button, power button, lock */\n$("#hb").onclick=function(){if($("#alertbg").classList.contains("open")){$("#alertbg").classList.remove("open");return;}if(!$("#lock").classList.contains("off"))return;closeApp();};\nfunction lockPhone(){closeApp();$("#lock").classList.remove("off");$("#knob").style.left="3px";}\nfunction unlock(){$("#lock").classList.add("off");}\n$("#pwr").onclick=lockPhone;\n(function(){\n  const knob=$("#knob"),sl=$("#slider");let drag=false,sx=0;\n  const max=function(){return sl.clientWidth-knob.clientWidth-6;};\n  knob.addEventListener("pointerdown",function(e){drag=true;sx=e.clientX-knob.offsetLeft;knob.setPointerCapture(e.pointerId);});\n  knob.addEventListener("pointermove",function(e){if(!drag)return;const k=parseFloat($("#phone").style.transform.replace(/[^0-9.]/g,"").replace(/^scale/,""))||1;let x=(e.clientX-sx);x=Math.max(3,Math.min(max()+3,x));knob.style.left=x+"px";});\n  knob.addEventListener("pointerup",function(){if(!drag)return;drag=false;if(knob.offsetLeft>max()*0.6)unlock();else knob.style.left="3px";});\n  $("#lock").addEventListener("dblclick",unlock);\n  addEventListener("keydown",function(e){if((e.key==="Enter"||e.key===" ")&&!$("#lock").classList.contains("off")&&document.activeElement.tagName!=="TEXTAREA")unlock();});\n})();\n\n/* clocks */\nfunction tick(){\n  const m=melb();\n  $("#stime").textContent=m.time;\n  $("#lt").textContent=m.time.replace(/\\s?[AP]M$/,"");$("#ld").textContent=m.long;$("#lz").textContent="Melbourne \\u00b7 "+m.zone;\n  const cw=document.getElementById("calw"),cd=document.getElementById("cald");if(cw){cw.textContent=m.weekday.slice(0,3);cd.textContent=m.day;}\n  const hh=document.getElementById("hh");if(hh){const h=m.hms[0]%12,mi=m.hms[1],s=m.hms[2];\n   hh.style.transform="rotate("+(h*30+mi/2)+"deg)";document.getElementById("mh").style.transform="rotate("+(mi*6)+"deg)";document.getElementById("sh").style.transform="rotate("+(s*6)+"deg)";}\n}\nsetInterval(tick,1000);tick();\n</script></body></html>\n\'\'\'\n\nMOBILE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "\n             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")\nPROFILE_ROOT = os.path.join(os.path.expanduser("~"), ".69ls_sims")\nTOKEN = secrets.token_urlsafe(12)\nSTATE = {"ping": 0.0, "stop": False, "browser": None}\n\n\ndef find_browser():\n    names = ["msedge", "microsoft-edge", "google-chrome", "chrome", "chromium", "chromium-browser"]\n    for n in names:\n        p = shutil.which(n)\n        if p:\n            return p\n    roots = [os.environ.get(k) for k in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA")]\n    rel = [r"Microsoft\\Edge\\Application\\msedge.exe", r"Google\\Chrome\\Application\\chrome.exe"]\n    for root in roots:\n        for r in rel:\n            if root and os.path.exists(os.path.join(root, r)):\n                return os.path.join(root, r)\n    return None\n\n\ndef launch(url, w, h, x, y, profile, mobile=False):\n    """Open url in its own app-style browser window."""\n    b = STATE["browser"]\n    if not b:\n        webbrowser.open(url)\n        return\n    args = [b, "--app=" + url, "--window-size=%d,%d" % (w, h), "--window-position=%d,%d" % (x, y),\n            "--user-data-dir=" + os.path.join(PROFILE_ROOT, profile),\n            "--no-first-run", "--no-default-browser-check",\n            "--autoplay-policy=no-user-gesture-required"]\n    if mobile:\n        args.append("--user-agent=" + MOBILE_UA)\n    subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n\n\ndef num(q, key, default, lo, hi):\n    try:\n        return max(lo, min(hi, int(float(q.get(key, [default])[0]))))\n    except (ValueError, TypeError):\n        return default\n\n\ndef make_handler(kind):\n    class Handler(BaseHTTPRequestHandler):\n        def log_message(self, *args):\n            pass\n\n        def reply(self, code, body, ctype="text/plain; charset=utf-8"):\n            data = body.encode("utf-8")\n            self.send_response(code)\n            self.send_header("Content-Type", ctype)\n            self.send_header("Content-Length", str(len(data)))\n            self.send_header("Cache-Control", "no-store")\n            self.end_headers()\n            self.wfile.write(data)\n\n        def do_GET(self):\n            host = (self.headers.get("Host") or "").split(":")[0]\n            if host not in ("127.0.0.1", "localhost"):\n                return self.reply(403, "no")\n            u = urllib.parse.urlparse(self.path)\n            q = urllib.parse.parse_qs(u.query)\n            if u.path == "/":\n                html = PAGES[kind].replace("/*COMMON*/", COMMON_JS).replace("__TOKEN__", TOKEN)\n                return self.reply(200, html, "text/html; charset=utf-8")\n            if q.get("token", [""])[0] != TOKEN:\n                return self.reply(403, "bad token")\n            if u.path == "/ping":\n                STATE["ping"] = time.time()\n                return self.reply(200, "ok")\n            if u.path == "/quit":\n                STATE["stop"] = True\n                return self.reply(200, "bye")\n            if u.path == "/open":\n                url = q.get("url", [""])[0]\n                if not url.lower().startswith(("http://", "https://")):\n                    return self.reply(400, "bad url")\n                mobile = q.get("mobile", ["0"])[0] == "1"\n                launch(url, num(q, "w", 1000, 240, 3000), num(q, "h", 680, 240, 2000),\n                       num(q, "x", 0, -2000, 6000), num(q, "y", 0, -200, 4000),\n                       "mobile" if mobile else "desktop", mobile)\n                return self.reply(200, "ok")\n            return self.reply(404, "nope")\n    return Handler\n\n\ndef start_server(kind):\n    handler = make_handler(kind)\n    try:\n        server = ThreadingHTTPServer(("127.0.0.1", 6969), handler)\n    except OSError:\n        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)\n    threading.Thread(target=server.serve_forever, daemon=True).start()\n    return server\n\n\ndef main(kind):\n    server = start_server(kind)\n    port = server.server_address[1]\n    STATE["browser"] = find_browser()\n    url = "http://127.0.0.1:%d/" % port\n    if kind == "ios":\n        launch(url, 430, 860, 220, 10, "ui")\n    else:\n        launch(url, 1180, 760, 60, 30, "ui")\n    if not STATE["browser"]:\n        print("  Couldn\'t find Microsoft Edge or Chrome, so I opened your default browser instead.")\n    started = time.time()\n    while not STATE["stop"]:\n        time.sleep(0.5)\n        if STATE["ping"] and time.time() - STATE["ping"] > 8:\n            break\n        if not STATE["ping"] and time.time() - started > 40:\n            print("  The sim window didn\'t open.")\n            break\n    server.shutdown()\n\n\nif __name__ == "__main__":\n    main(sys.argv[1] if len(sys.argv) > 1 else "windows")\n'



# Game 4: original arcade kart racer
GAME_CODE['4'] = 'import tkinter as tk\nimport math\n\nW, H = 900, 600\nroot = tk.Tk()\nroot.title("Kart Racer")\nc = tk.Canvas(root, width=W, height=H, bg="#398b45", highlightthickness=0)\nc.pack()\n\nkeys = set()\nroot.bind("<KeyPress>", lambda e: keys.add(e.keysym.lower()))\nroot.bind("<KeyRelease>", lambda e: keys.discard(e.keysym.lower()))\n\n# An original, arcade-style top-down kart track.\ncx, cy = W // 2, H // 2\nouter_rx, outer_ry = 365, 245\ninner_rx, inner_ry = 205, 105\nangle = -math.pi / 2\nspeed = 0.0\nlap = 0\nlast_angle = angle\nfinished = False\ncheckpoints = 0\n\ndef track_point(a, rx, ry):\n    return cx + math.cos(a) * rx, cy + math.sin(a) * ry\n\ndef draw_track():\n    c.create_oval(cx-outer_rx, cy-outer_ry, cx+outer_rx, cy+outer_ry,\n                  fill="#55585c", outline="#eeeeee", width=5)\n    c.create_oval(cx-inner_rx, cy-inner_ry, cx+inner_rx, cy+inner_ry,\n                  fill="#398b45", outline="#eeeeee", width=5)\n    c.create_oval(cx-285, cy-185, cx+285, cy+185,\n                  outline="#f4d35e", width=3, dash=(14, 12))\n    # Start/finish stripe on the top straight section.\n    x = cx\n    for i in range(8):\n        col = "white" if i % 2 == 0 else "#222222"\n        c.create_rectangle(x-18+i*5, cy-outer_ry+3, x-13+i*5,\n                           cy-outer_ry+30, fill=col, outline=col)\n\ndef kart(x, y, heading):\n    c.save = None\n    c.create_oval(x-17, y-12, x+17, y+12, fill="#222", outline="")\n    body = c.create_polygon(\n        x+math.cos(heading)*23, y+math.sin(heading)*23,\n        x+math.cos(heading+2.3)*17, y+math.sin(heading+2.3)*17,\n        x+math.cos(heading+math.pi)*13, y+math.sin(heading+math.pi)*13,\n        x+math.cos(heading-2.3)*17, y+math.sin(heading-2.3)*17,\n        fill="#e53935", outline="white", width=2)\n    # Driver helmet\n    hx = x + math.cos(heading)*2\n    hy = y + math.sin(heading)*2\n    c.create_oval(hx-7, hy-7, hx+7, hy+7, fill="#ffd166", outline="#222")\n\ndef update():\n    global angle, speed, lap, last_angle, finished, checkpoints\n    c.delete("all")\n    draw_track()\n\n    # Steering is stronger while moving.\n    if not finished:\n        if "w" in keys or "up" in keys:\n            speed = min(speed + 0.12, 5.5)\n        elif "s" in keys or "down" in keys:\n            speed = max(speed - 0.16, -2.2)\n        else:\n            speed *= 0.985\n        steer = 0\n        if "a" in keys or "left" in keys:\n            steer = -1\n        if "d" in keys or "right" in keys:\n            steer = 1\n        angle += steer * 0.045 * (0.35 + abs(speed)/5.5)\n\n    # Follow the oval circuit; leaving the road slows the kart.\n    x = cx + math.cos(angle) * 285\n    y = cy + math.sin(angle) * 185\n    # The kart is kept on the racing line for a friendly arcade feel.\n    if abs(speed) > 0.1:\n        angle += speed / 285\n    if speed < 0:\n        angle += speed / 285\n\n    # Count a lap when crossing the top of the course in the forward direction.\n    a = (angle + math.pi/2) % (2*math.pi)\n    old = (last_angle + math.pi/2) % (2*math.pi)\n    if old > 5.5 and a < 0.7 and speed > 0.5:\n        lap += 1\n    last_angle = angle\n\n    kart(x, y, angle + math.pi/2)\n    c.create_text(18, 18, anchor="nw", fill="white",\n                  font=("Arial", 17, "bold"),\n                  text=f"LAP {min(lap+1, 3)}/3     SPEED {int(abs(speed)*20)}")\n    c.create_text(18, H-20, anchor="sw", fill="white",\n                  font=("Arial", 11, "bold"),\n                  text="WASD / Arrow keys: drive and steer")\n    if lap >= 3:\n        finished = True\n        speed = 0\n        c.create_rectangle(W//2-170, H//2-55, W//2+170, H//2+55,\n                           fill="#111", outline="white", width=3)\n        c.create_text(W//2, H//2, fill="gold", font=("Arial", 28, "bold"),\n                      text="RACE COMPLETE!")\n        c.create_text(W//2, H//2+34, fill="white", font=("Arial", 12),\n                      text="Press SPACE to race again")\n    if "space" in keys and finished:\n        lap = 0\n        speed = 0\n        angle = -math.pi/2\n        last_angle = angle\n        finished = False\n    root.after(16, update)\n\nupdate()\nroot.mainloop()\n'

if __name__ == "__main__":
    main()