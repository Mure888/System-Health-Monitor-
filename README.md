# System-Health-Monitor

A lightweight, production-grade telemetry and diagnostic CLI tool designed to monitor system health, test network reachability, and log structured performance events.

## Features
- **Host Metrics:** Tracks real-time CPU, RAM, and Disk consumption.
- **Network Probing:** Measures HTTP latency and availability against DNS and cloud endpoints.
- **Threshold Alerting:** Triggers warnings when system metrics breach configurable limits.
- **Structured JSON Logging:** Writes events to a persistent JSON log stream for downstream analysis.
- **Containerized:** Includes a `Dockerfile` for isolated runtime environments.


## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mure888/Sysmon-cli.git
   cd Sysmon-cli

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the utility:**
   ```bash
   # Single check
   python monitor.py

   # Continuous monitoring every 5 seconds with custom CPU threshold
   python monitor.py --interval 5 --cpu-limit 75.0
   ```

## Docker Usage
```bash
docker build -t sysmon-cli .
docker run --rm sysmon-cli
```
