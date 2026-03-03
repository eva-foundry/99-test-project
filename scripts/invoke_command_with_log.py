#!/usr/bin/env python3
"""
Universal Command Wrapper with Log File Pattern (Python version)

Solves terminal output capture bug in AI agent sessions.

Pattern:
1. Takes command + optional search pattern
2. Runs command with ALL output redirected to uniquely-named log file
3. Knows exact log file location (no searching)
4. Returns structured results
5. Auto-cleanup old logs

Location: 07-foundation-layer/scripts/invoke_command_with_log.py
Version: 1.0.0
Created: 2026-02-28

Usage:
    from invoke_command_with_log import run_with_log
    
    result = run_with_log(
        command="pytest services/ -x -q",
        search_pattern=r"passed|failed"
    )
    print(result['output'])
    print(f"Exit code: {result['exit_code']}")
"""

import subprocess
import tempfile
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


def run_with_log(
    command: str,
    search_pattern: Optional[str] = None,
    label: str = "cmd",
    working_directory: Optional[str] = None,
    return_full_log: bool = False,
    keep_log: bool = False,
    shell: bool = True
) -> Dict[str, Any]:
    """
    Run command with output captured to log file.
    
    Args:
        command: Command to execute
        search_pattern: Optional regex pattern to extract from output
        label: Label for log file naming
        working_directory: Optional working directory
        return_full_log: Return entire log instead of matched lines
        keep_log: Keep log file (default: auto-cleanup after 1 hour)
        shell: Run command through shell
        
    Returns:
        Dictionary with:
        - command: Original command
        - log_file: Full path to log file
        - exit_code: Process exit code
        - output: Matched lines or full log
        - duration: Execution time in seconds
        - timestamp: ISO 8601 timestamp
        - success: True if exit code is 0
    """
    
    # Generate unique log file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:19]  # milliseconds
    log_dir = Path(tempfile.gettempdir()) / "eva-command-logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"{label}_{timestamp}.log"
    start_time = datetime.now()
    
    try:
        # Write header
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== COMMAND LOG ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Command: {command}\n")
            f.write(f"WorkingDirectory: {working_directory or Path.cwd()}\n")
            f.write(f"Label: {label}\n")
            f.write("==================\n\n")
        
        # Execute command
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=300  # 5 minute timeout
        )
        
        # Write output to log
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)
        
        # Write footer
        duration = (datetime.now() - start_time).total_seconds()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n==================\n")
            f.write(f"Exit Code: {result.returncode}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write("==================\n")
        
        # Read log content
        log_content = log_file.read_text(encoding='utf-8')
        
        # Extract what user is looking for
        if return_full_log:
            output = log_content
        elif search_pattern:
            matches = re.findall(search_pattern, log_content, re.MULTILINE)
            output = '\n'.join(matches) if matches else ""
        else:
            # Return last 20 lines if no pattern
            lines = log_content.split('\n')
            output = '\n'.join(lines[-20:])
        
        # Cleanup old logs (older than 1 hour) unless keep_log
        if not keep_log:
            cutoff = datetime.now() - timedelta(hours=1)
            for old_log in log_dir.glob("*.log"):
                if datetime.fromtimestamp(old_log.stat().st_mtime) < cutoff:
                    old_log.unlink(missing_ok=True)
        
        # Return structured result
        return {
            "command": command,
            "log_file": str(log_file),
            "exit_code": result.returncode,
            "output": output,
            "duration": round(duration, 2),
            "timestamp": datetime.now().isoformat(),
            "success": result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "log_file": str(log_file),
            "exit_code": -1,
            "output": "TIMEOUT: Command exceeded 5 minute limit",
            "duration": 300.0,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "command": command,
            "log_file": str(log_file),
            "exit_code": -1,
            "output": str(e),
            "duration": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(e)
        }


def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run command with log file wrapper"
    )
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--search", help="Regex pattern to search for")
    parser.add_argument("--label", default="cmd", help="Log file label")
    parser.add_argument("--cwd", help="Working directory")
    parser.add_argument("--full", action="store_true", help="Return full log")
    parser.add_argument("--keep", action="store_true", help="Keep log file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    result = run_with_log(
        command=args.command,
        search_pattern=args.search,
        label=args.label,
        working_directory=args.cwd,
        return_full_log=args.full,
        keep_log=args.keep
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[{'PASS' if result['success'] else 'FAIL'}] Exit Code: {result['exit_code']}")
        print(f"Duration: {result['duration']}s")
        print(f"Log: {result['log_file']}")
        print(f"\nOutput:\n{result['output']}")


if __name__ == "__main__":
    main()
