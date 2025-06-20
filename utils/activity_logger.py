import json
import os
from datetime import datetime
from typing import List, Dict

class ActivityLogger:
    """
    Logs user activities and system events for audit and monitoring purposes.
    """
    
    def __init__(self, log_file='activity_logs.json'):
        self.log_file = log_file
        self.max_logs = 1000  # Maximum number of logs to keep
    
    def log_activity(self, activity: str, user: str = "system", details: Dict = None):
        """
        Log an activity with timestamp.
        
        Args:
            activity: Description of the activity
            user: User who performed the activity
            details: Additional details about the activity
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'activity': activity,
            'details': details or {}
        }
        
        try:
            # Read existing logs
            logs = self._read_logs()
            
            # Add new log
            logs.append(log_entry)
            
            # Keep only the most recent logs
            if len(logs) > self.max_logs:
                logs = logs[-self.max_logs:]
            
            # Write back to file
            self._write_logs(logs)
            
        except Exception as e:
            # If logging fails, don't break the application
            print(f"Warning: Failed to log activity: {str(e)}")
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """
        Get recent activity logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of recent log entries
        """
        try:
            logs = self._read_logs()
            return logs[-limit:] if logs else []
        except Exception:
            return []
    
    def get_logs_by_date(self, date_str: str) -> List[Dict]:
        """
        Get logs for a specific date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            List of log entries for the specified date
        """
        try:
            logs = self._read_logs()
            filtered_logs = []
            
            for log in logs:
                log_date = datetime.fromisoformat(log['timestamp']).date()
                if log_date.isoformat() == date_str:
                    filtered_logs.append(log)
            
            return filtered_logs
        except Exception:
            return []
    
    def get_logs_summary(self) -> Dict:
        """
        Get summary statistics of logged activities.
        
        Returns:
            Dictionary with summary statistics
        """
        try:
            logs = self._read_logs()
            
            if not logs:
                return {
                    'total_logs': 0,
                    'date_range': None,
                    'most_common_activities': [],
                    'users': []
                }
            
            # Count activities
            activity_counts = {}
            users = set()
            dates = []
            
            for log in logs:
                activity = log['activity']
                user = log['user']
                timestamp = log['timestamp']
                
                activity_counts[activity] = activity_counts.get(activity, 0) + 1
                users.add(user)
                dates.append(datetime.fromisoformat(timestamp).date())
            
            # Get most common activities
            most_common = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Date range
            if dates:
                date_range = {
                    'start': min(dates).isoformat(),
                    'end': max(dates).isoformat()
                }
            else:
                date_range = None
            
            return {
                'total_logs': len(logs),
                'date_range': date_range,
                'most_common_activities': most_common,
                'users': list(users)
            }
            
        except Exception:
            return {
                'total_logs': 0,
                'date_range': None,
                'most_common_activities': [],
                'users': []
            }
    
    def clear_logs(self):
        """Clear all activity logs."""
        try:
            self._write_logs([])
        except Exception as e:
            print(f"Warning: Failed to clear logs: {str(e)}")
    
    def export_logs(self, start_date: str = None, end_date: str = None) -> str:
        """
        Export logs to JSON string for backup or analysis.
        
        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            JSON string of filtered logs
        """
        try:
            logs = self._read_logs()
            
            if start_date or end_date:
                filtered_logs = []
                
                for log in logs:
                    log_date = datetime.fromisoformat(log['timestamp']).date()
                    
                    # Apply date filters
                    if start_date and log_date < datetime.fromisoformat(start_date).date():
                        continue
                    if end_date and log_date > datetime.fromisoformat(end_date).date():
                        continue
                    
                    filtered_logs.append(log)
                
                logs = filtered_logs
            
            return json.dumps(logs, indent=2, default=str)
            
        except Exception as e:
            return f"Error exporting logs: {str(e)}"
    
    def _read_logs(self) -> List[Dict]:
        """Read logs from file."""
        if not os.path.exists(self.log_file):
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_logs(self, logs: List[Dict]):
        """Write logs to file."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, default=str, ensure_ascii=False)
    
    def log_data_upload(self, filename: str, file_size: int, num_records: int):
        """Log data upload activity."""
        self.log_activity(
            f"Data file uploaded: {filename}",
            details={
                'filename': filename,
                'file_size_bytes': file_size,
                'num_records': num_records
            }
        )
    
    def log_analysis_start(self, parameters: Dict):
        """Log analysis start."""
        self.log_activity(
            "ECLAT analysis started",
            details=parameters
        )
    
    def log_analysis_complete(self, num_itemsets: int, num_rules: int, execution_time: float):
        """Log analysis completion."""
        self.log_activity(
            f"ECLAT analysis completed successfully",
            details={
                'num_frequent_itemsets': num_itemsets,
                'num_association_rules': num_rules,
                'execution_time_seconds': execution_time
            }
        )
    
    def log_analysis_error(self, error_message: str):
        """Log analysis error."""
        self.log_activity(
            f"ECLAT analysis failed",
            details={'error': error_message}
        )
    
    def log_report_download(self, report_type: str, filename: str):
        """Log report download."""
        self.log_activity(
            f"Report downloaded: {report_type}",
            details={
                'report_type': report_type,
                'filename': filename
            }
        )
    
    def log_recommendation_request(self, input_items: List[str], num_recommendations: int):
        """Log recommendation request."""
        self.log_activity(
            f"Recommendations generated for {len(input_items)} input items",
            details={
                'input_items': input_items,
                'num_recommendations': num_recommendations
            }
        )
