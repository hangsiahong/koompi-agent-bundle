#!/usr/bin/env python3
"""
Code Intelligence Indexer — LanceDB + Gemini Embeddings
Tracks indexed files, detects changes, cleans orphans, and supports incremental re-index.

Commands:
  --index PATH       Index (or re-index) a directory
  --search QUERY     Semantic search across indexed code
  --status           Show tracking status (new/changed/deleted counts)
  --clean            Remove orphaned chunks for deleted files
  --auto PATH        Run clean + index + status in one shot (smart mode)
  --project-root     Project root directory (for resolving DB path)
  --db               LanceDB path (default: <project-root>/.lancedb)
"""

import os
import sys
import lancedb
import requests
import argparse
import time
import json
from pathlib import Path
from datetime import datetime, timezone
import pathspec

# ── Configuration ──────────────────────────────────────────────────────────────

API_URL = "https://ai.koompi.cloud/v1/embeddings"
MODEL = "gemini-embedding-001"
BATCH_SIZE = 50
CHUNK_SIZE = 1000
SUPPORTED_EXTENSIONS = {
    '.py', '.md', '.txt', '.js', '.ts', '.tsx', '.jsx', '.sh', '.json',
    '.yml', '.yaml', '.toml', '.sql', '.rs', '.go', '.rb', '.java',
    '.c', '.cpp', '.h', '.hpp', '.css', '.html', '.svelte', '.vue',
}
SKIP_DIRS = {
    'node_modules', 'dist', '.git', '.next', '__pycache__', '.venv', 'venv',
    'experiment', 'repos', 'build', '.worktrees', '.lancedb', '.cache', 'coverage',
    '.achieve', '.agent', '.beads', '.claude', '.serena', '.codex', 'vendor',
    'target', 'bin', 'obj', '.gradle', '.idea', '.vscode', '.vs',
}


def load_gitignore_spec(project_root):
    """Load .gitignore patterns from project root and return a pathspec matcher.
    Returns None if no .gitignore found."""
    gitignore_path = os.path.join(project_root, ".gitignore")
    if not os.path.exists(gitignore_path):
        return None
    try:
        with open(gitignore_path, 'r') as f:
            patterns = f.read().splitlines()
        # Filter out comments and empty lines, keep the rest
        valid_patterns = [p for p in patterns if p and not p.startswith('#')]
        if not valid_patterns:
            return None
        return pathspec.PathSpec.from_lines("gitwildmatch", valid_patterns)
    except Exception:
        return None


def is_gitignored(rel_path_str, spec):
    """Check if a relative path matches gitignore patterns."""
    if spec is None:
        return False
    # Check both the full path and as a directory
    return spec.match_file(rel_path_str)


PROGRESS_FILENAME = ".indexed_files.json"
TABLE_NAME = "code_index"
TRACKING_VERSION = 2

# ── Embedding API ──────────────────────────────────────────────────────────────

def get_embedding(text, retries=5):
    api_key = os.environ.get("KCONSOLE_API_KEY")
    if not api_key:
        raise ValueError("KCONSOLE_API_KEY not found in environment")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-BACKEND": "gemini",
    }
    payload = {"model": MODEL, "input": text}
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['data'][0]['embedding']
            if response.status_code == 429 or 'rate_limit' in response.text or 'No API keys' in response.text:
                wait = min(30 * (attempt + 1), 120)
                print(f"  Rate limited, waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
                continue
            print(f"  API Error: {response.text[:150]}")
            return None
        except requests.exceptions.Timeout:
            print(f"  Timeout, retrying ({attempt+1}/{retries})...")
            time.sleep(10)
        except Exception as e:
            print(f"  Request error: {e}")
            return None
    print(f"  Skipped after {retries} retries")
    return None

# ── File utilities ─────────────────────────────────────────────────────────────

def chunk_file(file_path, chunk_size=CHUNK_SIZE):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.strip():
            return []
        return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    except Exception:
        return []


def should_skip(path):
    for part in path.parts:
        if part.startswith('.') and len(part) > 1:
            return True
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def file_fingerprint(path_str):
    """Return path + mtime as a fingerprint. Changes if file is edited."""
    try:
        mtime = os.path.getmtime(path_str)
        return f"{path_str}:{mtime:.0f}"
    except OSError:
        return None


def discover_files(target_dir, gitignore_spec=None):
    """Return a set of absolute path strings for all indexable files.
    Respects .gitignore patterns if a spec is provided."""
    target = Path(target_dir)
    files = []
    for path in target.rglob('*'):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if path.suffix not in SUPPORTED_EXTENSIONS:
            continue
        # Check gitignore
        if gitignore_spec is not None:
            try:
                rel = str(path.relative_to(target))
            except ValueError:
                rel = str(path)
            if is_gitignored(rel, gitignore_spec):
                continue
        files.append(str(path))
    return files

# ── Tracking file management ──────────────────────────────────────────────────

def progress_path(db_path):
    return os.path.join(db_path, PROGRESS_FILENAME)


def load_tracking(db_path):
    """Load tracking metadata. Returns (project_root, files_dict)."""
    pfile = progress_path(db_path)
    if not os.path.exists(pfile):
        return None, {}
    with open(pfile, 'r') as f:
        data = json.load(f)
    # v2 format
    if isinstance(data, dict) and data.get("version") == TRACKING_VERSION:
        return data.get("project_root", ""), data.get("files", {})
    # v1 format: {path: fingerprint} or legacy list
    if isinstance(data, dict) and "version" not in data:
        return None, data
    if isinstance(data, list):
        return None, {p: "legacy" for p in data}
    return None, {}


def save_tracking(db_path, project_root, files_dict):
    pfile = progress_path(db_path)
    os.makedirs(os.path.dirname(pfile), exist_ok=True)
    data = {
        "version": TRACKING_VERSION,
        "project_root": project_root,
        "last_index": datetime.now(timezone.utc).isoformat(),
        "total_chunks_est": sum(max(1, len(files_dict.get(p, "")) // CHUNK_SIZE) for p in files_dict),
        "files": files_dict,
    }
    with open(pfile, 'w') as f:
        json.dump(data, f, indent=2)

# ── Core operations ───────────────────────────────────────────────────────────

def flush_batch(db, batch, old_paths=None):
    """Flush batch to LanceDB, optionally deleting old chunks first."""
    if not batch:
        return 0
    try:
        table = db.open_table(TABLE_NAME)
        if old_paths:
            for old_path in old_paths:
                try:
                    table.delete(f'path = "{old_path}"')
                except Exception:
                    pass
        table.add(batch)
    except Exception:
        db.create_table(TABLE_NAME, data=batch)
    return len(batch)


def do_clean(db_path, target_dir, _stored_root=None):
    """Remove orphaned chunks for files that no longer exist on disk."""
    db = lancedb.connect(db_path)
    project_root, tracked = load_tracking(db_path)
    if not tracked:
        print("No tracking data found. Nothing to clean.")
        return 0

    # Use stored project_root as fallback
    effective_dir = target_dir
    if project_root and not Path(target_dir).is_relative_to(Path(project_root).parent):
        effective_dir = project_root
    gitignore_spec = load_gitignore_spec(effective_dir)
    current_files = set(discover_files(effective_dir, gitignore_spec))
    tracked_paths = set(tracked.keys())
    deleted_paths = tracked_paths - current_files

    if not deleted_paths:
        print("No deleted files to clean.")
        return 0

    print(f"Found {len(deleted_paths)} deleted file(s) to clean.")
    try:
        table = db.open_table(TABLE_NAME)
    except Exception:
        print("No index table found. Nothing to clean.")
        return 0

    cleaned = 0
    for path_str in deleted_paths:
        try:
            table.delete(f'path = "{path_str}"')
            del tracked[path_str]
            cleaned += 1
            print(f"  Cleaned: {Path(path_str).name}")
        except Exception as e:
            print(f"  Error cleaning {path_str}: {e}")

    save_tracking(db_path, project_root or target_dir, tracked)
    print(f"Cleaned {cleaned} orphaned file(s).")
    return cleaned



def safe_relative(path, base):
    """Safe relative_to that returns the path as-is if not a subpath."""
    try:
        return path.relative_to(base)
    except ValueError:
        return path


def do_status(db_path, target_dir, _stored_root=None):
    """Show tracking status."""
    project_root, tracked = load_tracking(db_path)
    # Use stored project_root as fallback when target_dir doesn't match
    effective_dir = target_dir
    if project_root and not Path(target_dir).is_relative_to(Path(project_root).parent):
        effective_dir = project_root
    gitignore_spec = load_gitignore_spec(effective_dir)
    current_files = set(discover_files(effective_dir, gitignore_spec))
    tracked_paths = set(tracked.keys())

    new_files = current_files - tracked_paths
    still_exist = tracked_paths & current_files
    changed_files = set()
    for p in still_exist:
        fp = file_fingerprint(p)
        if fp and tracked.get(p) != fp:
            changed_files.add(p)
    deleted_files = tracked_paths - current_files

    # DB stats
    row_count = 0
    try:
        db = lancedb.connect(db_path)
        table = db.open_table(TABLE_NAME)
        rc = table.count_rows
        row_count = rc() if callable(rc) else rc
    except Exception:
        pass

    # DB size on disk
    db_size = 0
    for dirpath, _, filenames in os.walk(db_path):
        for fn in filenames:
            try:
                db_size += os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                pass

    # Last index timestamp
    last_index = "never"
    pfile = progress_path(db_path)
    if os.path.exists(pfile):
        with open(pfile, 'r') as f:
            data = json.load(f)
        last_index = data.get("last_index", "unknown")

    def fmt_size(b):
        if b < 1024:
            return f"{b} B"
        if b < 1024 * 1024:
            return f"{b / 1024:.1f} KB"
        return f"{b / (1024 * 1024):.1f} MB"

    print("=" * 50)
    print("  CODE INDEX STATUS")
    print("=" * 50)
    print(f"  Project root : {target_dir}")
    print(f"  DB path      : {db_path}")
    print(f"  DB size      : {fmt_size(db_size)}")
    print(f"  Total chunks : {row_count}")
    print(f"  Last index   : {last_index}")
    print("-" * 50)
    print(f"  Tracked files: {len(tracked)}")
    print(f"  New files    : {len(new_files)}")
    print(f"  Changed files: {len(changed_files)}")
    print(f"  Deleted files: {len(deleted_files)}")
    print(f"  Up to date   : {len(still_exist) - len(changed_files)}")
    print("=" * 50)

    if new_files:
        print("\n  New files (sample):")
        for p in sorted(new_files)[:10]:
            print(f"     + {safe_relative(Path(p), effective_dir)}")
        if len(new_files) > 10:
            print(f"     ... and {len(new_files) - 10} more")

    if changed_files:
        print("\n  Changed files:")
        for p in sorted(changed_files)[:10]:
            print(f"     ~ {safe_relative(Path(p), effective_dir)}")
        if len(changed_files) > 10:
            print(f"     ... and {len(changed_files) - 10} more")

    if deleted_files:
        print("\n  Deleted files:")
        for p in sorted(deleted_files)[:10]:
            print(f"     - {safe_relative(Path(p), effective_dir)}")
        if len(deleted_files) > 10:
            print(f"     ... and {len(deleted_files) - 10} more")

    needs_work = len(new_files) + len(changed_files) + len(deleted_files)
    if needs_work == 0:
        print("\n  Everything is up to date!")
    else:
        print(f"\n  Run with --auto to sync ({needs_work} file(s) to process)")

    return needs_work


def do_index(db_path, target_dir):
    """Index new and changed files."""
    db = lancedb.connect(db_path)
    project_root, indexed = load_tracking(db_path)

    # Auto-migrate v1 tracking (no project_root) to v2
    if project_root is None and indexed:
        project_root = target_dir
        # Compute real fingerprints for existing entries
        migrated = {}
        for p in indexed:
            fp = file_fingerprint(p)
            migrated[p] = fp if fp else indexed[p]
        indexed = migrated
        save_tracking(db_path, project_root, indexed)
        print(f"  Migrated tracking from v1 to v2 (project_root={project_root})")

    new_files = []
    changed_files = []

    gitignore_spec = load_gitignore_spec(target_dir)
    current_files = discover_files(target_dir, gitignore_spec)
    for path_str in current_files:
        if path_str not in indexed:
            new_files.append(path_str)
        else:
            fp = file_fingerprint(path_str)
            if fp and indexed[path_str] != fp:
                changed_files.append(path_str)

    total = len(new_files) + len(changed_files)
    print(f"Tracked: {len(indexed)} | New: {len(new_files)} | Changed: {len(changed_files)}")

    if total == 0:
        print("Everything is up to date!")
        return

    all_files = [(p, p in changed_files) for p in new_files + changed_files]
    batch = []
    total_chunks = 0
    processed = 0
    changed_paths_accum = []

    for path_str, is_changed in all_files:
        processed += 1
        tag = "changed" if is_changed else "new"
        rel = Path(path_str).relative_to(target_dir)
        print(f"  [{processed}/{total}] {rel} ({tag})")

        chunks = chunk_file(path_str)
        if not chunks:
            indexed[path_str] = file_fingerprint(path_str) or "empty"
            continue

        for i, chunk in enumerate(chunks):
            vector = get_embedding(chunk)
            if vector:
                batch.append({
                    "vector": vector,
                    "text": chunk,
                    "path": path_str,
                    "path_relative": str(rel),
                    "chunk_id": i,
                })

        if is_changed:
            changed_paths_accum.append(path_str)

        fp = file_fingerprint(path_str)
        if fp:
            indexed[path_str] = fp

        if len(batch) >= BATCH_SIZE:
            count = flush_batch(db, batch, changed_paths_accum)
            total_chunks += count
            print(f"    Flushed {count} chunks (total: {total_chunks})")
            save_tracking(db_path, project_root or target_dir, indexed)
            batch = []
            changed_paths_accum = []

    if batch:
        count = flush_batch(db, batch, changed_paths_accum)
        total_chunks += count
        print(f"    Flushed final {count} chunks (total: {total_chunks})")

    save_tracking(db_path, project_root or target_dir, indexed)
    print(f"\nDone. {total_chunks} chunks from {processed} files.")


def do_auto(db_path, target_dir):
    """Smart mode: status -> clean -> index -> status."""
    print("Running auto-index...")
    print()
    do_clean(db_path, target_dir)
    print()
    do_index(db_path, target_dir)
    print()
    do_status(db_path, target_dir)


def do_search(db_path, query, limit=5):
    """Semantic search across indexed code."""
    db = lancedb.connect(db_path)
    try:
        table = db.open_table(TABLE_NAME)
    except Exception:
        print("No index found. Run --index first.")
        return

    query_vector = get_embedding(query)
    if not query_vector:
        return

    results = table.search(query_vector).limit(limit).to_pandas()
    for _, row in results.iterrows():
        print(f"\n--- Result (Score: {row.get('_distance', 'N/A')}) ---")
        print(f"Path: {row.get('path_relative', row.get('path', 'unknown'))}")
        print(f"Content: {row['text'][:300]}...")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Code Intelligence Indexer - LanceDB + Gemini Embeddings",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--index", metavar="PATH", help="Directory to index")
    group.add_argument("--search", metavar="QUERY", help="Semantic search query")
    group.add_argument("--status", action="store_true", help="Show tracking status")
    group.add_argument("--clean", action="store_true", help="Remove orphaned chunks for deleted files")
    group.add_argument("--auto", metavar="PATH", help="Smart mode: clean + index + status")

    parser.add_argument("--project-root", metavar="PATH",
                        help="Project root (default: same as --index/--auto path)")
    parser.add_argument("--db", metavar="PATH", help="LanceDB path (default: <project-root>/.lancedb)")
    parser.add_argument("--limit", type=int, default=5, help="Search result limit (default: 5)")
    args = parser.parse_args()

    # Resolve project root
    if args.project_root:
        project_root = os.path.abspath(args.project_root)
    elif args.index:
        project_root = os.path.abspath(args.index)
    elif args.auto:
        project_root = os.path.abspath(args.auto)
    elif args.search:
        project_root = None
    else:
        project_root = os.getcwd()

    # Resolve DB path
    if args.db:
        db_path = os.path.abspath(args.db)
    elif project_root:
        db_path = os.path.join(project_root, ".lancedb")
    else:
        print("Error: --db or --project-root required for search when no index path is set.")
        sys.exit(1)

    # Dispatch
    if args.status:
        target = project_root or os.getcwd()
        needs = do_status(db_path, target)
        sys.exit(1 if needs else 0)
    elif args.clean:
        target = project_root or os.getcwd()
        do_clean(db_path, target)
    elif args.auto:
        do_auto(db_path, os.path.abspath(args.auto))
    elif args.index:
        do_index(db_path, os.path.abspath(args.index))
    elif args.search:
        do_search(db_path, args.search, limit=args.limit)


if __name__ == "__main__":
    main()
