#!/usr/bin/env python3
"""
Resource monitoring script for shared hosting
"""

import os
import psutil
import time
from datetime import datetime

def check_resources():
    """Check current resource usage"""
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Process count
        process_count = len(psutil.pids())
        
        print(f"[{datetime.now()}] Resource Usage:")
        print(f"  Memory: {memory_percent:.1f}%")
        print(f"  CPU: {cpu_percent:.1f}%")
        print(f"  Disk: {disk_percent:.1f}%")
        print(f"  Processes: {process_count}")
        
        # Check if we're near limits
        if memory_percent > 80:
            print("⚠️  WARNING: High memory usage!")
        if cpu_percent > 80:
            print("⚠️  WARNING: High CPU usage!")
        if disk_percent > 90:
            print("⚠️  WARNING: High disk usage!")
            
    except Exception as e:
        print(f"Error monitoring resources: {e}")

if __name__ == "__main__":
    check_resources() 