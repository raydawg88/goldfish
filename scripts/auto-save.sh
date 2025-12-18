#!/bin/bash
# 🐠 Goldfish Auto-Save
# Captures raw transcripts. Run /gfsave for quality summaries.

GOLDFISH_DIR="$HOME/.goldfish"
LOCK_FILE="$GOLDFISH_DIR/state/lock"
LAST_SAVE_FILE="$GOLDFISH_DIR/state/last-save"
LOG_FILE="$GOLDFISH_DIR/logs/goldfish.log"
CONFIG_FILE="$GOLDFISH_DIR/config.json"
COOLDOWN_SECONDS=180  # 3 minutes

# Get memory path from config or environment
if [ -n "$GOLDFISH_MEMORY_PATH" ]; then
    MEMORY_PATH="$GOLDFISH_MEMORY_PATH"
elif [ -f "$CONFIG_FILE" ]; then
    MEMORY_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['memory_path'])" 2>/dev/null)
fi

if [ -z "$MEMORY_PATH" ]; then
    echo "ERROR: Could not determine memory path" >> "$LOG_FILE"
    exit 1
fi

# Expand ~ if present
MEMORY_PATH="${MEMORY_PATH/#\~/$HOME}"

# Ensure directories exist
mkdir -p "$GOLDFISH_DIR/logs" "$GOLDFISH_DIR/state"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Check if already running
if [ -f "$LOCK_FILE" ]; then
    lock_age=$(($(date +%s) - $(stat -f %m "$LOCK_FILE" 2>/dev/null || stat -c %Y "$LOCK_FILE" 2>/dev/null)))
    if [ $lock_age -lt 300 ]; then
        log "Already running, skipping"
        exit 0
    fi
fi

# Check cooldown
if [ -f "$LAST_SAVE_FILE" ]; then
    last_save=$(cat "$LAST_SAVE_FILE")
    now=$(date +%s)
    elapsed=$((now - last_save))

    if [ $elapsed -lt $COOLDOWN_SECONDS ]; then
        log "Saved ${elapsed}s ago, cooldown not met, skipping"
        exit 0
    fi
fi

# Create lock
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

log "Starting auto-save"

cd "$GOLDFISH_DIR/scripts"

# Run reader
python3 reader.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: reader.py failed"
    exit 1
fi

# Run transcript appender
python3 transcript-appender.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: transcript-appender.py failed"
    exit 1
fi

# Record success
date +%s > "$LAST_SAVE_FILE"
log "Auto-save complete. Run /gfsave for quality summaries."
