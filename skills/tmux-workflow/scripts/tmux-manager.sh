#!/bin/bash
# tmux-manager.sh - Integrated Worktree, Path, Index & Parallel Agent management

SESSION_NAME=${2:-"codex-superpowers"}
WORKTREE_PATH=$3
INDEXER_SCRIPT="/home/jiren/.codex/superpowers/skills/code-intelligence/scripts/indexer.py"
LOG_DIR="/tmp/codex-logs"

check_tmux() {
    if ! command -v tmux &> /dev/null; then
        echo "Error: tmux is not installed."
        exit 1
    fi
    mkdir -p "$LOG_DIR"
}

init_session() {
    check_tmux
    local target_dir=$WORKTREE_PATH
    local auto_index=false

    # Parse flags
    for arg in "$@"; do
        case "$arg" in
            --auto-index) auto_index=true ;;
        esac
    done

    # If no worktree path provided, try to find a matching local directory
    if [ -z "$target_dir" ]; then
        target_dir=$(readlink -f "$SESSION_NAME" 2>/dev/null)
    fi

    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo "Session $SESSION_NAME already exists."
    else
        if [ -d "$target_dir" ]; then
            echo "Initializing session $SESSION_NAME in $target_dir"
            tmux new-session -d -s "$SESSION_NAME" -n "Orchestrator" -c "$target_dir"
        else
            tmux new-session -d -s "$SESSION_NAME" -n "Orchestrator"
        fi

        sleep 0.1
        tmux split-window -h -t "$SESSION_NAME" -c "#{pane_current_path}"

        if [ "$auto_index" = true ] && [ -n "$target_dir" ]; then
            tmux send-keys -t "$SESSION_NAME:0.1" "python3 $INDEXER_SCRIPT --auto '$target_dir'" C-m
        else
            tmux send-keys -t "$SESSION_NAME:0.1" "echo 'Observability Monitor'" C-m
        fi

        tmux select-pane -t "$SESSION_NAME:0.0"
    fi
}

add_worker() {
    local worker_id=$1
    local task_name=$3
    check_tmux
    
    # Create a vertical split for the new worker
    tmux split-window -v -t "$SESSION_NAME" -c "#{pane_current_path}"
    
    # Get the ID of the new pane
    local pane_id=$(tmux display-message -p -F "#{pane_id}")
    
    # Prepare the log file
    local log_file="$LOG_DIR/${worker_id}.log"
    touch "$log_file"
    
    # Start tailing the log in that pane
    tmux send-keys -t "$pane_id" "clear && echo 'Worker: $worker_id ($task_name)' && echo '---' && tail -f $log_file" C-m
    
    # Distribute panes evenly
    tmux select-layout -t "$SESSION_NAME" tiled
    
    echo "$pane_id:$log_file"
}

reindex() {
    local target_dir=$2
    if [ -z "$target_dir" ]; then
        target_dir=$(tmux display-message -p -t "$SESSION_NAME" -F '#{pane_current_path}' 2>/dev/null)
    fi
    tmux send-keys -t "$SESSION_NAME:0.1" "" C-m
    tmux send-keys -t "$SESSION_NAME:0.1" "python3 $INDEXER_SCRIPT --auto '$target_dir'" C-m
}

status() {
    local target_dir=$2
    if [ -z "$target_dir" ]; then
        target_dir=$(tmux display-message -p -t "$SESSION_NAME" -F '#{pane_current_path}' 2>/dev/null)
    fi
    python3 "$INDEXER_SCRIPT" --status --project-root "$target_dir"
}

case "$1" in
    init)
        shift
        init_session "$@"
        ;;
    add-worker)
        add_worker "$SESSION_NAME" "$2" "$3"
        ;;
    reindex)
        reindex "$SESSION_NAME" "$3"
        ;;
    status)
        status "$SESSION_NAME" "$3"
        ;;
    *)
        echo "Usage: $0 {init|add-worker|reindex|status} [session_name] [path/task] [--auto-index]"
        exit 1
esac
