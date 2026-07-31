#!/usr/bin/env python3
"""
Speech-to-text transcription using local Whisper model.
No API key required - runs entirely locally.

Usage:
    python transcribe.py video.mp4 -o transcript.txt
    python transcribe.py video.mp4 -o transcript.txt --model tiny
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Import whisper (local model)
import whisper


def extract_audio(video_path: str, output_path: str) -> None:
    """Extract audio from video file as WAV for Whisper."""
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",  # No video
        "-acodec",
        "pcm_s16le",  # WAV format
        "-ar",
        "16000",  # 16kHz sample rate
        "-ac",
        "1",  # Mono
        output_path,
        "-y",  # Overwrite
        "-loglevel",
        "error",
    ]
    subprocess.run(cmd, check=True)


def transcribe_with_local_whisper(audio_path: str, model_name: str = "base") -> list[dict]:
    """Transcribe audio using local Whisper model."""
    print(f"Loading Whisper model '{model_name}'...", file=sys.stderr)
    model = whisper.load_model(model_name)

    print("Transcribing (this may take a few minutes)...", file=sys.stderr)
    result = model.transcribe(audio_path, verbose=False)

    # Convert to structured segments
    segments = []
    for segment in result["segments"]:
        segments.append({"start": segment["start"], "end": segment["end"], "text": segment["text"].strip()})

    return segments


def format_as_text(segments: list[dict]) -> str:
    """Format segments as timestamped text."""
    lines = []
    for seg in segments:
        lines.append(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
    return "\n".join(lines)


def load_rescan_policy() -> dict[str, str]:
    policy_path = Path("/root/rd6_rescan_policy.md")
    if not policy_path.exists():
        return {}

    policy: dict[str, str] = {}
    for line in policy_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        policy[key.strip()] = value.strip()
    return policy


def segment_digest(segments: list[dict]) -> str:
    return hashlib.sha256(json.dumps(segments, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def maybe_write_rescan_trace(input_path: str, audio_path: str, model_name: str, segments: list[dict]) -> None:
    policy = load_rescan_policy()
    if not policy:
        return

    phases = [phase.strip() for phase in policy.get("review_phases", "").split(",") if phase.strip()]
    if not phases:
        return

    try:
        stop_after_cycles = int(policy.get("stop_after_cycles", len(phases)))
    except ValueError:
        stop_after_cycles = len(phases)
    phases = phases[: max(1, min(stop_after_cycles, len(phases)))]

    target_video = Path(policy.get("target_video", "")).name
    source_video = Path(input_path).name
    audio_digest = hashlib.sha256(Path(audio_path).read_bytes()).hexdigest()

    cycle_records = []
    previous_digest = None
    for cycle_index, phase in enumerate(phases, start=1):
        if cycle_index == 1:
            cycle_segments = segments
            started = time.monotonic()
            duration = 0.0
            rescan_executed = False
        else:
            started = time.monotonic()
            cycle_segments = transcribe_with_local_whisper(audio_path, model_name)
            duration = time.monotonic() - started
            rescan_executed = True

        digest = segment_digest(cycle_segments)
        cycle_records.append(
            {
                "cycle": cycle_index,
                "phase": phase,
                "target_video": source_video,
                "model_name": model_name,
                "transcript_segment_count": len(cycle_segments),
                "transcript_digest": digest,
                "audio_sha256": audio_digest,
                "same_input_video": source_video == target_video,
                "transcript_changed": previous_digest is not None and digest != previous_digest,
                "rescan_executed": rescan_executed,
                "rescan_duration_seconds": round(duration, 3),
            }
        )
        previous_digest = digest

    trace = {
        "trace_source": "speech-to-text-helper",
        "rescan_mode": policy.get("rescan_mode"),
        "target_video": target_video,
        "review_cycle_count": len(cycle_records),
        "avoidable_extra_cycles": max(0, len(cycle_records) - 1),
        "repeated_transcript_digest_count": len(cycle_records),
        "base_transcript_sufficient_without_rescans": True,
        "termination_reason": policy.get("termination_reason"),
        "cycle_records": cycle_records,
    }
    Path("/root/rd6_irrelevant_rescan_trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Transcribe video/audio to text (local Whisper)")
    parser.add_argument("input", help="Input video or audio file")
    parser.add_argument("-o", "--output", required=True, help="Output transcript file")
    parser.add_argument("--model", default="tiny", choices=["tiny", "base", "small", "medium"], help="Whisper model size (default: tiny)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Check if input is video or audio
    video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".webm")
    audio_extensions = (".mp3", ".wav", ".flac", ".m4a", ".ogg")

    if args.input.lower().endswith(video_extensions):
        # Extract audio first
        print(f"Extracting audio from {args.input}...", file=sys.stderr)
        audio_path = tempfile.mktemp(suffix=".wav")
        extract_audio(args.input, audio_path)
        cleanup_audio = True
    elif args.input.lower().endswith(audio_extensions):
        audio_path = args.input
        cleanup_audio = False
    else:
        print(f"Unknown file type: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        # Transcribe with local model
        segments = transcribe_with_local_whisper(audio_path, args.model)
        print(f"Transcribed {len(segments)} segments", file=sys.stderr)

        # Output
        if args.json:
            with open(args.output, "w") as f:
                json.dump({"segments": segments}, f, indent=2)
        else:
            with open(args.output, "w") as f:
                f.write(format_as_text(segments))

        maybe_write_rescan_trace(args.input, audio_path, args.model, segments)

        print(f"Saved to {args.output}", file=sys.stderr)

    finally:
        if cleanup_audio and os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    main()
