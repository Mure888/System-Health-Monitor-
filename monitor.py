#!/usr/bin/env python3
"""
SysMon CLI - Production-Ready System & Network Telemetry Utility
Monitors host performance metrics, checks network service reachability,
evaluates operational thresholds, and exports structured event logs.
"""

import argparse
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
import psutil

DEFAULT_ENDPOINTS = [
    "https://1.1.1.1",
    "https://www.google.com",
    "https://github.com"
]

def parse_args():
    parser = argparse.ArgumentParser(
        description="SysMon CLI - Lightweight System & Network Telemetry Tool"
    )
    parser.add_argument("--cpu-limit", type=float, default=80.0, help="CPU alert threshold (%)")
    parser.add_argument("--ram-limit", type=float, default=80.0, help="RAM alert threshold (%)")
    parser.add_argument("--disk-limit", type=float, default=85.0, help="Disk alert threshold (%)")
    parser.add_argument("--interval", type=int, default=0, help="Polling interval in seconds (0 = single run)")
    parser.add_argument("--log-file", type=str, default="sysmon_telemetry.log", help="Path to JSON output log file")
    return parser.parse_args()

def collect_system_metrics():
    """Gathers CPU, memory, and disk telemetry."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))

        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used / (1024 ** 3), 2),
            "ram_total_gb": round(ram.total / (1024 ** 3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        }
    except Exception as e:
        return {"error": f"Failed to retrieve host metrics: {str(e)}"}

def ping_endpoint(url, timeout=3):
    """Measures latency and HTTP response status."""
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SysMon-Telemetry/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = round((time.time() - start) * 1000, 2)
            return {"url": url, "status_code": resp.status, "latency_ms": latency, "reachable": True}
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 2)
        return {"url": url, "status_code": e.code, "latency_ms": latency, "reachable": False}
    except Exception:
        return {"url": url, "status_code": "TIMEOUT", "latency_ms": None, "reachable": False}

def evaluate_thresholds(metrics, cpu_limit, ram_limit, disk_limit):
    """Evaluates metrics against configured limits and flags warnings."""
    warnings = []
    if metrics.get("cpu_percent", 0) > cpu_limit:
        warnings.append(f"HIGH_CPU: {metrics['cpu_percent']}% > {cpu_limit}%")
    if metrics.get("ram_percent", 0) > ram_limit:
        warnings.append(f"HIGH_RAM: {metrics['ram_percent']}% > {ram_limit}%")
    if metrics.get("disk_percent", 0) > disk_limit:
        warnings.append(f"HIGH_DISK: {metrics['disk_percent']}% > {disk_limit}%")
    return warnings

def write_json_log(log_path, record):
    """Appends structured JSON telemetry to log file."""
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def display_report(metrics, network_health, alerts):
    """Prints a clear console dashboard."""
    print("\n" + "=" * 55)
    print(f"  SYSMON TELEMETRY REPORT | {metrics.get('timestamp', 'N/A')}")
    print("=" * 55)
    
    print("\n[HOST RESOURCE UTILIZATION]")
    print(f"  • CPU Load:  {metrics.get('cpu_percent')}%")
    print(f"  • RAM Load:  {metrics.get('ram_percent')}% ({metrics.get('ram_used_gb')} / {metrics.get('ram_total_gb')} GB)")
    print(f"  • Disk Load: {metrics.get('disk_percent')}% ({metrics.get('disk_free_gb')} GB free)")

    print("\n[NETWORK PROBING]")
    for node in network_health:
        icon = "✔" if node["reachable"] else "✖"
        latency = f"{node['latency_ms']} ms" if node["latency_ms"] is not None else "N/A"
        print(f"  [{icon}] {node['url']:<28} Status: {str(node['status_code']):<10} Latency: {latency}")

    print("\n[HEALTH ALERTS]")
    if alerts:
        for alert in alerts:
            print(f"  ⚠  [ALERT] {alert}")
    else:
        print("  ✔  All metrics within healthy limits.")
    print("=" * 55)

def run_pipeline(args):
    metrics = collect_system_metrics()
    network_health = [ping_endpoint(url) for url in DEFAULT_ENDPOINTS]
    alerts = evaluate_thresholds(metrics, args.cpu_limit, args.ram_limit, args.disk_limit)
    
    display_report(metrics, network_health, alerts)
    
    telemetry_record = {
        "metrics": metrics,
        "network": network_health,
        "alerts": alerts
    }
    write_json_log(args.log_file, telemetry_record)

def main():
    args = parse_args()
    if args.interval > 0:
        print(f"Starting continuous telemetry monitor (Interval: {args.interval}s). Press Ctrl+C to stop.")
        try:
            while True:
                run_pipeline(args)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            sys.exit(0)
    else:
        run_pipeline(args)

if __name__ == "__main__":
    main()
  
