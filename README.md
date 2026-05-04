# 🚀 Startup Manager

A Python CLI tool to manage Windows startup programs.

## 📋 Features
- List all startup programs (HKCU + HKLM)
- Disable programs from startup
- Automatic backup before disabling
- Restore disabled programs from backup

## ▶️ Usage
```bash
python startup_manager.py
```

## ⚠️ Note
Some HKLM entries require Administrator privileges to modify.

## 🛠️ Built With
- Python
- winreg (built-in)
- json (built-in)
