#!/usr/bin/env python3
"""
Convert a monophonic MIDI file into a vector PDF score readable by the Sp3ctra
instrument.

Layout summary
--------------
* **Page size**          : A4 portrait (210 mm × 297 mm).
* **Vertical pitch band**: 216.7 mm mapped to C1–B8 (3 456 sensor points).
* **Time scale**         : 5 mm per quarter‑note (black note).
* **Calibration mark**   : solid 1 mm × 1 mm square at absolute bottom‑left.
* **Offsets**            :
    * `BOTTOM_OFFSET_MM` – 49.5 mm (sensor band starts above page bottom).
    * `START_OFFSET_MM`  – 23.0 mm (first MIDI event starts from left edge).
* **Velocity → ink**     : MIDI velocity 0–127 → greyscale 0 %–100 % black.
* Notes outside C1–B8 are dropped with a warning.

Author : ChatGPT (OpenAI) – 2025‑06‑14
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Tuple

from mido import MidiFile
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ────────────────────────────────────────────────────────────────────────────────
# Physical constants
# ────────────────────────────────────────────────────────────────────────────────
MM_PER_QUARTER: float = 7.0        # horizontal scale (mm per quarter‑note)
NOTE_HEIGHT_MM: float = 0.25        # printed bar thickness
PITCH_BAND_MM: float = 216.7       # height of the pitch band
CAPTOR_POINTS: int = 3456          # sensor resolution
SEMITONES: int = 12                # per octave

BOTTOM_OFFSET_MM: float = 49.5     # Y‑offset for sensor band origin (calage)
START_OFFSET_MM: float = 23.0      # X‑offset before first MIDI event
CALIB_MARK_MM: float = 1.0         # calibration square size

MIDI_C1: int = 24                  # MIDI note of C1
MIDI_B8: int = 119                 # MIDI note of B8

# Derived constants
MM_PER_POINT: float = PITCH_BAND_MM / CAPTOR_POINTS            # ≃ 0.0627 mm
POINTS_PER_SEMITONE: int = CAPTOR_POINTS // (SEMITONES * 8)    # 36
MM_TO_PT: float = 72.0 / 25.4                                   # 1 mm → pt


# ────────────────────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────────────────────

def mm_to_pt(mm: float) -> float:
    """Convert millimetres to PostScript points."""
    return mm * MM_TO_PT


def note_to_y_mm(note: int) -> float:
    """Map MIDI note number → vertical Y‑coordinate in millimetres."""
    return BOTTOM_OFFSET_MM + (note - MIDI_C1) * POINTS_PER_SEMITONE * MM_PER_POINT


def velocity_to_gray(velocity: int) -> colors.Color:
    """Convert MIDI velocity (0‑127) to a greyscale Color object.

    Velocity 0 ⇒ white (0 % black), 127 ⇒ black (100 % black).
    """
    intensity: float = 1.0 - (velocity / 127.0)  # 1 = white, 0 = black
    return colors.Color(intensity, intensity, intensity)


def extract_notes(mid: MidiFile) -> List[Tuple[int, int, int, int]]:
    """Return list of (note, velocity, start_tick, end_tick) from the first track.
    Assumes monophony (single voice)."""
    events: List[Tuple[int, int, int, int]] = []
    active: dict[int, Tuple[int, int]] = {}  # note → (velocity, start_tick)
    abs_tick: int = 0

    track = mid.tracks[0]
    for msg in track:
        abs_tick += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            if msg.note in active:
                logging.warning("Overlapping note %d at tick %d – ignoring.", msg.note, abs_tick)
            active[msg.note] = (msg.velocity, abs_tick)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            stored = active.pop(msg.note, None)
            if stored is not None:
                velocity, start = stored
                events.append((msg.note, velocity, start, abs_tick))

    # Close dangling notes
    for note, (velocity, start) in active.items():
        events.append((note, velocity, start, abs_tick))

    return events


# ────────────────────────────────────────────────────────────────────────────────
# Core routine
# ────────────────────────────────────────────────────────────────────────────────

def midi_to_pdf(midi_path: Path, pdf_path: Path) -> None:
    """Convert *midi_path* into *pdf_path* following Sp3ctra conventions."""
    mid = MidiFile(midi_path)
    ppqn: int = mid.ticks_per_beat
    mm_per_tick: float = MM_PER_QUARTER / ppqn

    raw_notes = extract_notes(mid)
    if not raw_notes:
        logging.error("No notes found in %s", midi_path)
        sys.exit(1)

    # Filter C1–B8
    notes: List[Tuple[int, int, int, int]] = []
    for note, vel, start, end in raw_notes:
        if MIDI_C1 <= note <= MIDI_B8:
            notes.append((note, vel, start, end))
        else:
            logging.warning("Dropping note %d (outside C1–B8)", note)

    if not notes:
        logging.error("All notes were outside C1–B8; nothing to render.")
        sys.exit(1)

    # Horizontal span
    last_tick: int = max(end for _, _, _, end in notes)
    width_mm: float = START_OFFSET_MM + (last_tick * mm_per_tick) + 10.0  # right margin

    pdf = canvas.Canvas(str(pdf_path), pagesize=(mm_to_pt(width_mm), mm_to_pt(297.0)))

    # Calibration mark
    pdf.setFillColor(colors.black)
    pdf.rect(0.0, 0.0, mm_to_pt(CALIB_MARK_MM), mm_to_pt(CALIB_MARK_MM), stroke=0, fill=1)

    # Render notes
    for note, vel, start, end in notes:
        x_mm: float = START_OFFSET_MM + (start * mm_per_tick)
        y_mm: float = note_to_y_mm(note)
        w_mm: float = (end - start) * mm_per_tick

        pdf.setFillColor(velocity_to_gray(vel))
        pdf.rect(
            mm_to_pt(x_mm),
            mm_to_pt(y_mm),
            mm_to_pt(w_mm),
            mm_to_pt(NOTE_HEIGHT_MM),
            stroke=0,
            fill=1,
        )

    pdf.showPage()
    pdf.save()

    logging.info(
        "Written %s – %.1f mm × 297 mm | start offset %.1f mm | bottom offset %.1f mm",
        pdf_path,
        width_mm,
        START_OFFSET_MM,
        BOTTOM_OFFSET_MM,
    )


# ────────────────────────────────────────────────────────────────────────────────
# CLI interface
# ────────────────────────────────────────────────────────────────────────────────

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Sp3ctra‑compatible PDF from a monophonic MIDI file.")
    parser.add_argument("input", type=Path, help="Input MIDI file (.mid)")
    parser.add_argument("output", type=Path, nargs="?", help="Output PDF file (.pdf)")
    parser.add_argument("--log", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    # Génération automatique du nom de fichier PDF si absent
    if args.output is None:
        args.output = args.input.parent.parent / "pdf" / args.input.with_suffix(".pdf").name

    logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO), format="%(levelname)s: %(message)s")

    midi_to_pdf(args.input, args.output)


if __name__ == "__main__":
    main()
