
# 🛠️ Installation Guide – Sp3ctra MIDI to Score Generator

This guide explains how to set up the Python environment to run the `midi_to_sp3ctra.py` script
on **Windows**, **macOS (Apple Silicon)**, and **Linux**.

---

## 🪟 Windows

```powershell
# Open Command Prompt or PowerShell
cd "C:\path\to\Sp3ctraScoreGen"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python midi_to_sp3ctra.py midi\example.mid
```

---

## 🍎 macOS (Apple Silicon)

```bash
# Open Terminal
cd ~/path/to/Sp3ctraScoreGen

# (Optional) Ensure Python 3 is installed via Homebrew
brew install python

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python3 midi_to_sp3ctra.py midi/example.mid
```

---

## 🐧 Linux (Debian/Ubuntu)

```bash
# Open Terminal
sudo apt update
sudo apt install python3 python3-pip python3-venv

cd ~/Sp3ctraScoreGen

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python3 midi_to_sp3ctra.py midi/example.mid
```

---

## ✅ Recommended Python Version

- **Python ≥ 3.9** recommended
- Virtual environments are strongly advised for isolation

---

## 📦 Installing dependencies manually

```bash
pip install mido reportlab
```
