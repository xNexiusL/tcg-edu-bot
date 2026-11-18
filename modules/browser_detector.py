
import os
import winreg
from pathlib import Path


def get_default_browser_progid():
    """Lit l'association HTTPS de l'utilisateur Windows."""

    registry_path = (
        r"Software\Microsoft\Windows\Shell"
        r"\Associations\UrlAssociations\https\UserChoice"
    )

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            registry_path
        ) as key:
            progid, _ = winreg.QueryValueEx(
                key,
                "ProgId"
            )
            return progid

    except OSError:
        return None


def get_browser_command(progid):
    """Recherche la commande de lancement du navigateur."""

    if not progid:
        return None

    registry_path = (
        rf"{progid}\shell\open\command"
    )

    try:
        with winreg.OpenKey(
            winreg.HKEY_CLASSES_ROOT,
            registry_path
        ) as key:
            command, _ = winreg.QueryValueEx(
                key,
                None
            )
            return command

    except OSError:
        return None


def extract_executable(command):
    """
    Extrait le chemin de l'exécutable d'une commande
    Windows classique.
    """

    if not command:
        return None

    command = os.path.expandvars(command.strip())

    if command.startswith('"'):
        executable = command.split('"', 2)[1]
    else:
        lower = command.lower()
        index = lower.find(".exe")

        if index == -1:
            return None

        executable = command[:index + 4]

    path = Path(executable)

    if path.is_file():
        return str(path)

    return None



def detect_default_browser():
    """Détecte le navigateur HTTPS par défaut de Windows."""

    progid = get_default_browser_progid()
    command = get_browser_command(progid)
    executable = extract_executable(command)

    identity = " ".join(
        str(value)
        for value in (progid, executable)
        if value
    ).lower()

    firefox_names = (
        "firefox",
        "floorp",
        "librewolf",
        "waterfox",
        "zen"
    )

    chromium_names = (
        "chrome",
        "chromium",
        "msedge",
        "brave",
        "opera",
        "vivaldi"
    )

    if any(name in identity for name in firefox_names):
        engine = "firefox"

    elif any(name in identity for name in chromium_names):
        engine = "chromium"

    else:
        engine = "unknown"

    return {
        "progid": progid,
        "command": command,
        "executable": executable,
        "engine": engine
    }
