"""
Check production API logs by querying CloudWatch directly
"""
import boto3
import time
from datetime import datetime, timedelta

def get_recent_logs():
    client = boto3.client('logs', region_name='us-east-1')
    
    log_group = '/aws/apprunner/teachgenie-api/8899ea3585a341948653bef09cc3b856/application'
    
    # Get logs from last 10 minutes
    start_time = int((datetime.now() - timedelta(minutes=10)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    
    print(f"Fetching logs from {log_group}...")
    print(f"Time range: Last 10 minutes\n")
    print("=" * 80)
    
    try:
        response = client.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            limit=100
        )
        
        events = response.get('events', [])
        
        if not events:
            print("No logs found in the last 10 minutes")
            return
        
        print(f"Found {len(events)} log entries\n")
        
        # Filter for errors
        error_logs = []
        for event in events:
            message = event['message']
            if any(keyword in message.lower() for keyword in ['error', 'exception', 'failed', 'traceback', 'history']):
                error_logs.append(message)
        
        if error_logs:
            print("ERROR LOGS:")
            print("=" * 80)
            for log in error_logs[-20:]:  # Last 20 errors
                print(log)
                print("-" * 80)
        else:
            print("Recent logs (last 20):")
            print("=" * 80)
            for event in events[-20:]:
                print(event['message'])
                
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    get_recent_logs()
