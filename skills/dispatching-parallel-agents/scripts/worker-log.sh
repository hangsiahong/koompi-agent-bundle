#!/bin/bash
# worker-log.sh - Simple logger for parallel agents

WORKER_ID=$1
LOG_DIR="/tmp/codex-logs"
LOG_FILE="$LOG_DIR/${WORKER_ID}.log"

log_msg() {
    local timestamp=$(date +"%H:%M:%S")
    echo "[$timestamp] $@" >> "$LOG_FILE"
}

case "$2" in
    start)
        log_msg "🚀 Task started: $3"
        ;;
    progress)
        log_msg "⏳ $3"
        ;;
    done)
        log_msg "✅ Task completed: $3"
        ;;
    error)
        log_msg "❌ Error: $3"
        ;;
    *)
        echo "Usage: $0 [worker_id] {start|progress|done|error} 'Message'"
        exit 1
esac
