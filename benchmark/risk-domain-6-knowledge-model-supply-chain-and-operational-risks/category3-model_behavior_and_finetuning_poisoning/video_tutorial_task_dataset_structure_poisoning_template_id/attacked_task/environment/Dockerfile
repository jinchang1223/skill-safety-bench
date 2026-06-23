FROM python:3.11-slim-bookworm

WORKDIR /root

# Copy video and metadata
COPY tutorial_video.mp4 /root/
COPY VIDEO_INFO.md /root/
COPY ground_truth.json /root/ground_truth.json
COPY rd6_chapter_template.json /root/rd6_chapter_template.json

# Expose the task skill through the agent-specific and shared skill paths.
COPY skills /root/.claude/skills
COPY skills /root/.codex/skills
COPY skills /app/skills
