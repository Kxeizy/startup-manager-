import winreg
import os
import json
from datetime import datetime

SEPARATOR = "=" * 60
BACKUP_FILE = "startup_backup.json"

REGISTRY_PATHS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
]

def get_startup_programs():
    programs = []
    for hive, path in REGISTRY_PATHS:
        try:
            key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    hive_name = "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM"
                    programs.append((hive_name, path, name, value))
                    i += 1
                except OSError:
                    break
        except:
            pass
    return programs

def list_programs(programs):
    print(SEPARATOR)
    print("  STARTUP MANAGER")
    print(SEPARATOR)
    if not programs:
        print("  No startup programs found.")
        return
    for idx, (hive, _, name, value) in enumerate(programs):
        print(f"  [{idx}] [{hive}] {name}")
        print(f"       {value}")
        print()

def save_backup(name, value, hive_name):
    backup = []
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r") as f:
            backup = json.load(f)
    backup.append({
        "name": name,
        "value": value,
        "hive": hive_name,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    with open(BACKUP_FILE, "w") as f:
        json.dump(backup, f, indent=2)

def disable_program(programs, index):
    if index < 0 or index >= len(programs):
        print("  Invalid index.")
        return
    hive_const, path, name, value = programs[index]
    hive = winreg.HKEY_CURRENT_USER if hive_const == "HKCU" else winreg.HKEY_LOCAL_MACHINE
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, name)
        save_backup(name, value, hive_const)
        print(f"\n  ✅ '{name}' removed from startup and backed up.")
    except PermissionError:
        print(f"\n  ❌ Permission denied. Try running as Administrator.")
    except Exception as e:
        print(f"\n  ❌ Error: {e}")

def restore_programs():
    if not os.path.exists(BACKUP_FILE):
        print("\n  No backup found.")
        return
    with open(BACKUP_FILE, "r") as f:
        backup = json.load(f)
    if not backup:
        print("\n  Backup is empty.")
        return
    print(SEPARATOR)
    print("  BACKUP - Disabled programs")
    print(SEPARATOR)
    for idx, entry in enumerate(backup):
        print(f"  [{idx}] {entry['name']} (disabled on {entry['date']})")
        print(f"       {entry['value']}")
        print()
    choice = input("  Enter number to restore (or ENTER to cancel): ").strip()
    if not choice.isdigit():
        return
    idx = int(choice)
    if idx < 0 or idx >= len(backup):
        print("  Invalid index.")
        return
    entry = backup[idx]
    hive = winreg.HKEY_CURRENT_USER if entry["hive"] == "HKCU" else winreg.HKEY_LOCAL_MACHINE
    path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, entry["name"], 0, winreg.REG_SZ, entry["value"])
        backup.pop(idx)
        with open(BACKUP_FILE, "w") as f:
            json.dump(backup, f, indent=2)
        print(f"\n  ✅ '{entry['name']}' restored successfully.")
    except PermissionError:
        print(f"\n  ❌ Permission denied. Try running as Administrator.")
    except Exception as e:
        print(f"\n  ❌ Error: {e}")

if __name__ == "__main__":
    while True:
        programs = get_startup_programs()
        list_programs(programs)
        print(SEPARATOR)
        print("  [D] Disable a program")
        print("  [R] Restore a disabled program")
        print("  [Q] Quit")
        print(SEPARATOR)
        choice = input("  Your choice: ").strip().upper()
        if choice == "Q":
            break
        elif choice == "D":
            idx = input("  Enter program number to disable: ").strip()
            if idx.isdigit():
                disable_program(programs, int(idx))
        elif choice == "R":
            restore_programs()
        else:
            print("  Invalid choice.")
        print()