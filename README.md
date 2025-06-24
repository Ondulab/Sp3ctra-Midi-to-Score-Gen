# Sp3ctraScoreGen

Convert MIDI files into high-resolution graphical scores readable by the Sp3ctra scanner-synthesizer.

## Features
- Converts MIDI notes to vector graphics (SVG/PDF)
- 3456-pixel vertical resolution matching Sp3ctra sensor
- 8-octave range (C1–B8) mapped visually
- Supports continuous lines for held notes

## Usage

1. Activate your virtual environment
2. Place MIDI files in the `midi/` folder
3. Run the script:
   ```bash
   python midi_to_sp3ctra2.py midi/example.mid