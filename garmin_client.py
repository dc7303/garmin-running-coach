"""
Garmin Connect data fetching module.

This module handles authentication and data retrieval from Garmin Connect API
using the garminconnect library.
"""

from datetime import datetime, timedelta
from typing import Optional
from garminconnect import Garmin, GarminConnectAuthenticationError


class GarminClient:
    """Client for interacting with Garmin Connect API."""

    def __init__(self, email: str, password: str):
        """
        Initialize Garmin client with credentials.

        Args:
            email: Garmin Connect account email
            password: Garmin Connect account password
        """
        self.email = email
        self.password = password
        self.client: Optional[Garmin] = None
        self._logged_in = False

    def login(self) -> bool:
        """
        Authenticate with Garmin Connect.

        Returns:
            True if login successful, False otherwise

        Raises:
            GarminConnectAuthenticationError: If authentication fails
        """
        try:
            self.client = Garmin(self.email, self.password)
            self.client.login()
            self._logged_in = True
            return True
        except GarminConnectAuthenticationError as e:
            self._logged_in = False
            raise e

    @property
    def is_logged_in(self) -> bool:
        """Check if client is authenticated."""
        return self._logged_in and self.client is not None

    def get_activities(self, limit: int = 20) -> list:
        """
        Fetch recent activities from Garmin Connect.

        Args:
            limit: Maximum number of activities to fetch

        Returns:
            List of activity dictionaries
        """
        if not self.is_logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        activities = self.client.get_activities(0, limit)
        return activities

    def get_running_activities(self, limit: int = 20) -> list:
        """
        Fetch recent running activities only.

        Args:
            limit: Maximum number of activities to fetch

        Returns:
            List of running activity dictionaries
        """
        activities = self.get_activities(limit * 2)  # Fetch more to filter
        running_activities = [
            a for a in activities
            if a.get("activityType", {}).get("typeKey", "").lower() in [
                "running", "trail_running", "treadmill_running", "track_running"
            ]
        ]
        return running_activities[:limit]

    def get_activity_details(self, activity_id: int) -> dict:
        """
        Get detailed data for a specific activity.

        Args:
            activity_id: The Garmin activity ID

        Returns:
            Dictionary containing detailed activity data
        """
        if not self.is_logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        return self.client.get_activity(activity_id)

    def get_activity_hr_data(self, activity_id: int) -> list:
        """
        Get heart rate time series data for an activity.

        Args:
            activity_id: The Garmin activity ID

        Returns:
            List of heart rate data points
        """
        if not self.is_logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        try:
            hr_data = self.client.get_activity_hr_in_timezones(activity_id)
            return hr_data
        except Exception:
            return []

    def get_activity_splits(self, activity_id: int) -> list:
        """
        Get split data (per km/mile) for an activity.

        Args:
            activity_id: The Garmin activity ID

        Returns:
            List of split dictionaries
        """
        if not self.is_logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        try:
            details = self.client.get_activity_splits(activity_id)
            return details.get("lapDTOs", [])
        except Exception:
            return []

    def get_activity_hr_zones(self, activity_id: int) -> list:
        """
        Get heart rate zone data for an activity.

        Args:
            activity_id: The Garmin activity ID

        Returns:
            List of HR zone dictionaries with time spent in each zone
        """
        if not self.is_logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        try:
            hr_data = self.client.get_activity_hr_in_timezones(activity_id)
            return hr_data
        except Exception:
            return []

    def get_activity_weather(self, activity_id: int) -> dict:
        """
        Get weather data for an activity.

        Args:
            activity_id: The Garmin activity ID

        Returns:
            Dictionary with weather information
        """
        if not self.is_logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        try:
            weather = self.client.get_activity_weather(activity_id)
            return weather
        except Exception:
            return {}

    def get_weekly_stats(self, weeks: int = 4) -> list:
        """
        Calculate weekly running statistics.

        Args:
            weeks: Number of weeks to analyze

        Returns:
            List of weekly stat dictionaries
        """
        # Fetch enough activities to cover the requested weeks
        # Assume max ~7 runs per week
        limit = max(100, weeks * 7)
        activities = self.get_running_activities(limit=limit)
        weekly_stats = []

        today = datetime.now()
        for week_offset in range(weeks):
            week_start = today - timedelta(days=today.weekday() + 7 * week_offset)
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)

            week_activities = [
                a for a in activities
                if week_start <= datetime.fromisoformat(
                    a.get("startTimeLocal", "2000-01-01").replace("Z", "")
                ) < week_end
            ]

            total_distance = sum(
                a.get("distance", 0) for a in week_activities
            ) / 1000  # Convert to km

            total_duration = sum(
                a.get("duration", 0) for a in week_activities
            ) / 60  # Convert to minutes

            avg_pace = (total_duration / total_distance) if total_distance > 0 else 0

            avg_hr = 0
            hr_count = 0
            for a in week_activities:
                if a.get("averageHR"):
                    avg_hr += a.get("averageHR", 0)
                    hr_count += 1
            avg_hr = avg_hr / hr_count if hr_count > 0 else 0

            weekly_stats.append({
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_end": week_end.strftime("%Y-%m-%d"),
                "run_count": len(week_activities),
                "total_distance_km": round(total_distance, 2),
                "total_duration_min": round(total_duration, 1),
                "avg_pace_min_km": round(avg_pace, 2),
                "avg_heart_rate": round(avg_hr, 0)
            })

        return weekly_stats

    def get_monthly_stats(self, months: int = 3) -> list:
        """
        Calculate monthly running statistics.

        Args:
            months: Number of months to analyze

        Returns:
            List of monthly stat dictionaries
        """
        # Fetch enough activities to cover the requested months
        # Assume max ~30 runs per month
        limit = max(200, months * 30)
        activities = self.get_running_activities(limit=limit)
        monthly_stats = []

        today = datetime.now()
        for month_offset in range(months):
            month = today.month - month_offset
            year = today.year
            while month <= 0:
                month += 12
                year -= 1

            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)

            month_activities = [
                a for a in activities
                if month_start <= datetime.fromisoformat(
                    a.get("startTimeLocal", "2000-01-01").replace("Z", "")
                ) < month_end
            ]

            total_distance = sum(
                a.get("distance", 0) for a in month_activities
            ) / 1000

            total_duration = sum(
                a.get("duration", 0) for a in month_activities
            ) / 60

            avg_pace = (total_duration / total_distance) if total_distance > 0 else 0

            monthly_stats.append({
                "month": month_start.strftime("%Y-%m"),
                "run_count": len(month_activities),
                "total_distance_km": round(total_distance, 2),
                "total_duration_min": round(total_duration, 1),
                "avg_pace_min_km": round(avg_pace, 2)
            })

        return monthly_stats


def format_pace(pace_min_per_km: float) -> str:
    """
    Format pace as MM:SS per km.

    Args:
        pace_min_per_km: Pace in minutes per kilometer

    Returns:
        Formatted pace string (e.g., "5:30")
    """
    if pace_min_per_km <= 0:
        return "--:--"
    minutes = int(pace_min_per_km)
    seconds = int((pace_min_per_km - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


def format_duration(duration_seconds: float) -> str:
    """
    Format duration as HH:MM:SS or MM:SS.

    Args:
        duration_seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if duration_seconds <= 0:
        return "0:00"

    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"
