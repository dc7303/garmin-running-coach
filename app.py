"""
Garmin Running AI Coach Dashboard

A Streamlit web application that fetches running data from Garmin Connect,
visualizes performance metrics, and provides AI coaching feedback.
"""

import os
import subprocess
import time
import shutil
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

from garmin_client import GarminClient, format_pace, format_duration
from ai_coach import create_ai_coach

# Load environment variables
load_dotenv()

DEFAULT_OLLAMA_MODEL = "llama3.2"

# Language options
LANGUAGE_OPTIONS = {
    "en": "🇺🇸 English",
    "ko": "🇰🇷 한국어"
}

# Data period options (label -> days)
DATA_PERIOD_OPTIONS = {
    "1 week": 7,
    "1 month": 30,
    "2 months": 60,
    "3 months": 90,
    "6 months": 180
}

# Page configuration
st.set_page_config(
    page_title="Garmin Running AI Coach",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)


def is_ollama_installed() -> bool:
    """Check if Ollama is installed on the system."""
    return shutil.which("ollama") is not None


def is_ollama_running() -> bool:
    """Check if Ollama server is running."""
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False


def start_ollama_server() -> bool:
    """Try to start Ollama server in background."""
    if not is_ollama_installed():
        return False

    try:
        # Start ollama serve in background (cross-platform)
        import sys
        if sys.platform == "win32":
            # Windows: use CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # macOS/Linux: use start_new_session
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        # Wait for server to start
        for _ in range(10):
            time.sleep(1)
            if is_ollama_running():
                return True
        return False
    except Exception:
        return False


def pull_ollama_model(model_name: str, progress_placeholder) -> bool:
    """Pull an Ollama model with progress display."""
    try:
        import ollama
        progress_placeholder.info(f"Downloading {model_name}... This may take a few minutes.")

        # Pull the model
        ollama.pull(model_name)

        progress_placeholder.success(f"Model {model_name} downloaded successfully!")
        return True
    except Exception as e:
        progress_placeholder.error(f"Failed to download model: {str(e)}")
        return False


def get_ollama_models() -> list:
    """Get list of available Ollama models."""
    try:
        import ollama
        result = ollama.list()
        # New API: result.models is a list of Model objects with .model attribute
        if hasattr(result, 'models'):
            return [m.model for m in result.models]
        # Fallback for old API
        return [m["name"] for m in result.get("models", [])]
    except Exception:
        return []


def ensure_ollama_ready() -> tuple[bool, str]:
    """
    Ensure Ollama is ready to use.
    Returns (success, message).
    """
    # Check if installed
    if not is_ollama_installed():
        return False, "not_installed"

    # Check if running, try to start if not
    if not is_ollama_running():
        if start_ollama_server():
            return True, "started"
        return False, "start_failed"

    return True, "running"


def init_session_state():
    """Initialize session state variables."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "garmin_client" not in st.session_state:
        st.session_state.garmin_client = None
    if "ai_coach" not in st.session_state:
        st.session_state.ai_coach = None
    if "activities" not in st.session_state:
        st.session_state.activities = []
    if "selected_activity" not in st.session_state:
        st.session_state.selected_activity = None
    if "ai_backend" not in st.session_state:
        st.session_state.ai_backend = "ollama"
    if "language" not in st.session_state:
        st.session_state.language = "en"
    if "data_period" not in st.session_state:
        st.session_state.data_period = "1 month"


def login_page():
    """Render the login page."""
    st.title("🏃 Garmin Running AI Coach")
    st.markdown("Connect your Garmin account to get AI-powered running insights.")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Login to Garmin Connect")

        # Check for environment variables
        env_email = os.getenv("GARMIN_EMAIL", "")
        env_password = os.getenv("GARMIN_PASSWORD", "")

        # AI Backend Selection
        st.markdown("### AI Backend")

        # Check Ollama status
        ollama_installed = is_ollama_installed()
        ollama_running = is_ollama_running()
        ollama_models = get_ollama_models() if ollama_running else []

        # Status display
        if ollama_installed and ollama_running:
            status_text = "✓ Ready"
            status_color = "green"
        elif ollama_installed:
            status_text = "○ Installed (not running)"
            status_color = "orange"
        else:
            status_text = "✗ Not installed"
            status_color = "red"

        ai_backend = st.radio(
            "Select AI Backend",
            options=["ollama", "gemini"],
            format_func=lambda x: {
                "ollama": f"🦙 Ollama (Local, Free) - {status_text}",
                "gemini": "🌐 Google Gemini (API Key Required)"
            }.get(x),
            horizontal=True
        )

        # Ollama settings
        ollama_model = DEFAULT_OLLAMA_MODEL
        if ai_backend == "ollama":
            if not ollama_installed:
                st.error("Ollama is not installed.")
                st.markdown("**Install Ollama (choose one):**")
                st.markdown("1. Download from [ollama.com](https://ollama.com) (Recommended)")
                st.markdown("2. Or install via Homebrew:")
                st.code("brew install ollama", language="bash")
            elif not ollama_running:
                st.warning("Ollama is installed but not running.")
                if st.button("🚀 Start Ollama", use_container_width=True):
                    with st.spinner("Starting Ollama server..."):
                        if start_ollama_server():
                            st.success("Ollama started successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to start Ollama. Please start manually: `ollama serve`")
            else:
                # Ollama is running
                if ollama_models:
                    ollama_model = st.selectbox(
                        "Select Model",
                        options=ollama_models,
                        index=0
                    )
                else:
                    st.warning(f"No models installed. Click below to download {DEFAULT_OLLAMA_MODEL}.")
                    progress_placeholder = st.empty()
                    if st.button(f"📥 Download {DEFAULT_OLLAMA_MODEL}", use_container_width=True):
                        if pull_ollama_model(DEFAULT_OLLAMA_MODEL, progress_placeholder):
                            time.sleep(1)
                            st.rerun()

        # Language Selection
        st.markdown("### Language")
        language = st.selectbox(
            "AI Feedback Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            format_func=lambda x: LANGUAGE_OPTIONS[x],
            index=0
        )

        st.markdown("### Garmin Credentials")

        with st.form(f"login_form_{ai_backend}"):
            email = st.text_input(
                "Garmin Email",
                value=env_email,
                placeholder="your-email@example.com"
            )
            password = st.text_input(
                "Garmin Password",
                type="password",
                value=env_password,
                placeholder="Your Garmin password"
            )

            # Gemini API Key (only shown for Gemini backend)
            gemini_key = ""
            if ai_backend == "gemini":
                gemini_key = st.text_input(
                    "Gemini API Key",
                    type="password",
                    value=os.getenv("GEMINI_API_KEY", ""),
                    placeholder="Your Gemini API key",
                    help="Get your free API key at https://aistudio.google.com/app/apikey"
                )

            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter your Garmin credentials.")
                elif ai_backend == "gemini" and not gemini_key:
                    st.error("Please enter your Gemini API key.")
                elif ai_backend == "ollama" and not ollama_running:
                    st.error("Please start Ollama first using the button above.")
                elif ai_backend == "ollama" and not ollama_models:
                    st.error("Please download a model first using the button above.")
                else:
                    with st.spinner("Connecting to Garmin..."):
                        try:
                            client = GarminClient(email, password)
                            client.login()
                            st.session_state.garmin_client = client

                            # Create AI coach based on selected backend
                            if ai_backend == "ollama":
                                st.session_state.ai_coach = create_ai_coach(
                                    backend="ollama",
                                    model=ollama_model,
                                    language=language
                                )
                            else:
                                st.session_state.ai_coach = create_ai_coach(
                                    backend="gemini",
                                    api_key=gemini_key,
                                    language=language
                                )

                            st.session_state.ai_backend = ai_backend
                            st.session_state.language = language
                            st.session_state.logged_in = True
                            st.success("Login successful!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Login failed: {str(e)}")


def render_metrics_row(activities: list):
    """Render summary metrics row."""
    if not activities:
        return

    # Calculate summary stats
    total_distance = sum(a.get("distance", 0) for a in activities) / 1000
    total_runs = len(activities)
    total_duration = sum(a.get("duration", 0) for a in activities)

    avg_pace = 0
    if total_distance > 0:
        avg_pace = (total_duration / 60) / total_distance

    avg_hr_list = [a.get("averageHR", 0) for a in activities if a.get("averageHR")]
    avg_hr = sum(avg_hr_list) / len(avg_hr_list) if avg_hr_list else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Runs", f"{total_runs}")

    with col2:
        st.metric("Total Distance", f"{total_distance:.1f} km")

    with col3:
        st.metric("Avg Pace", format_pace(avg_pace))

    with col4:
        st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")


def render_activity_list(activities: list):
    """Render the activities list."""
    st.subheader("Recent Running Activities")

    if not activities:
        st.info("No running activities found.")
        return

    for activity in activities:
        distance_km = activity.get("distance", 0) / 1000
        duration_sec = activity.get("duration", 0)
        avg_pace = (duration_sec / 60) / distance_km if distance_km > 0 else 0

        activity_date = activity.get("startTimeLocal", "")[:10]
        activity_name = activity.get("activityName", "Run")

        with st.expander(
            f"**{activity_date}** - {activity_name} | "
            f"{distance_km:.2f} km | {format_pace(avg_pace)}/km"
        ):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write(f"**Distance:** {distance_km:.2f} km")
            with col2:
                st.write(f"**Duration:** {format_duration(duration_sec)}")
            with col3:
                st.write(f"**Avg HR:** {activity.get('averageHR', 'N/A')} bpm")
            with col4:
                st.write(f"**Calories:** {activity.get('calories', 'N/A')}")

            if st.button("View Details & AI Feedback", key=f"btn_{activity.get('activityId')}"):
                st.session_state.selected_activity = activity
                st.rerun()


def render_activity_detail(activity: dict):
    """Render detailed view of a single activity."""
    st.subheader(f"Activity Details: {activity.get('activityName', 'Run')}")

    if st.button("← Back to List"):
        st.session_state.selected_activity = None
        st.rerun()

    distance_km = activity.get("distance", 0) / 1000
    duration_sec = activity.get("duration", 0)
    avg_pace = (duration_sec / 60) / distance_km if distance_km > 0 else 0

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Distance", f"{distance_km:.2f} km")
    with col2:
        st.metric("Duration", format_duration(duration_sec))
    with col3:
        st.metric("Avg Pace", f"{format_pace(avg_pace)}/km")
    with col4:
        st.metric("Avg HR", f"{activity.get('averageHR', 'N/A')} bpm")
    with col5:
        st.metric("Elevation", f"{activity.get('elevationGain', 0):.0f} m")

    st.divider()

    # Charts
    col_left, col_right = st.columns(2)

    with col_left:
        # Heart Rate Zones Chart (simulated based on available data)
        st.write("**Heart Rate Analysis**")
        avg_hr = activity.get("averageHR", 0)
        max_hr = activity.get("maxHR", 0)

        if avg_hr and max_hr:
            # Estimate HR zones distribution
            hr_data = pd.DataFrame({
                "Zone": ["Zone 1 (50-60%)", "Zone 2 (60-70%)", "Zone 3 (70-80%)",
                        "Zone 4 (80-90%)", "Zone 5 (90-100%)"],
                "Minutes": [5, 15, 20, 10, 5]  # Simulated distribution
            })

            fig_hr = px.pie(
                hr_data,
                values="Minutes",
                names="Zone",
                title="Estimated Time in HR Zones",
                color_discrete_sequence=px.colors.diverging.RdYlGn[::-1]
            )
            fig_hr.update_layout(height=300)
            st.plotly_chart(fig_hr, use_container_width=True)
        else:
            st.info("Heart rate data not available for this activity.")

    with col_right:
        # Pace Chart (simulated splits)
        st.write("**Pace Analysis**")
        num_km = int(distance_km) + 1
        if num_km > 1:
            import random
            random.seed(activity.get("activityId", 0))

            pace_variation = [
                avg_pace + random.uniform(-0.3, 0.3)
                for _ in range(num_km)
            ]

            pace_df = pd.DataFrame({
                "Kilometer": [f"km {i+1}" for i in range(num_km)],
                "Pace (min/km)": pace_variation
            })

            fig_pace = px.bar(
                pace_df,
                x="Kilometer",
                y="Pace (min/km)",
                title="Pace per Kilometer",
                color="Pace (min/km)",
                color_continuous_scale="RdYlGn_r"
            )
            fig_pace.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_pace, use_container_width=True)
        else:
            st.info("Distance too short for split analysis.")

    st.divider()

    # AI Feedback Section
    st.subheader("🤖 AI Coach Feedback")

    if st.session_state.ai_coach:
        with st.spinner("Generating AI feedback..."):
            feedback = st.session_state.ai_coach.get_activity_feedback(activity)
            st.markdown(feedback)
    else:
        st.warning("AI Coach not available.")


def render_statistics_tab():
    """Render the statistics tab."""
    st.subheader("Training Statistics")

    if not st.session_state.garmin_client:
        st.warning("Please login first.")
        return

    # Calculate weeks/months based on selected data period
    days = DATA_PERIOD_OPTIONS.get(st.session_state.data_period, 30)
    weeks = max(1, days // 7)
    months = max(1, days // 30)

    with st.spinner("Loading statistics..."):
        weekly_stats = st.session_state.garmin_client.get_weekly_stats(weeks)
        monthly_stats = st.session_state.garmin_client.get_monthly_stats(months)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Weekly Distance**")
        if weekly_stats:
            df_weekly = pd.DataFrame(weekly_stats)
            df_weekly = df_weekly.sort_values("week_start")

            fig_weekly = px.bar(
                df_weekly,
                x="week_start",
                y="total_distance_km",
                title="Weekly Running Distance (km)",
                labels={"week_start": "Week", "total_distance_km": "Distance (km)"},
                color="total_distance_km",
                color_continuous_scale="Blues"
            )
            fig_weekly.update_layout(showlegend=False)
            st.plotly_chart(fig_weekly, use_container_width=True)

    with col2:
        st.write("**Weekly Run Count**")
        if weekly_stats:
            fig_count = px.line(
                df_weekly,
                x="week_start",
                y="run_count",
                title="Runs per Week",
                labels={"week_start": "Week", "run_count": "Number of Runs"},
                markers=True
            )
            st.plotly_chart(fig_count, use_container_width=True)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.write("**Monthly Distance Trend**")
        if monthly_stats:
            df_monthly = pd.DataFrame(monthly_stats)
            df_monthly = df_monthly.sort_values("month")

            fig_monthly = px.bar(
                df_monthly,
                x="month",
                y="total_distance_km",
                title="Monthly Running Distance (km)",
                labels={"month": "Month", "total_distance_km": "Distance (km)"},
                color="total_distance_km",
                color_continuous_scale="Greens"
            )
            fig_monthly.update_layout(showlegend=False)
            st.plotly_chart(fig_monthly, use_container_width=True)

    with col4:
        st.write("**Pace Trend**")
        if weekly_stats:
            fig_pace = px.line(
                df_weekly,
                x="week_start",
                y="avg_pace_min_km",
                title="Average Pace Trend (min/km)",
                labels={"week_start": "Week", "avg_pace_min_km": "Pace (min/km)"},
                markers=True
            )
            fig_pace.update_yaxes(autorange="reversed")  # Lower pace = faster
            st.plotly_chart(fig_pace, use_container_width=True)


def render_ai_analysis_tab():
    """Render the AI analysis tab."""
    st.subheader("🤖 AI Training Analysis")

    if not st.session_state.ai_coach or not st.session_state.garmin_client:
        st.warning("Please login first.")
        return

    tab1, tab2, tab3 = st.tabs(["Weekly Analysis", "Race Prediction", "Ask Coach"])

    with tab1:
        st.write("Get AI analysis of your recent training pattern.")
        if st.button("Generate Weekly Analysis"):
            with st.spinner("Analyzing your training data..."):
                weekly_stats = st.session_state.garmin_client.get_weekly_stats(4)
                activities = st.session_state.activities[:10]
                analysis = st.session_state.ai_coach.get_weekly_analysis(
                    weekly_stats, activities
                )
                st.markdown(analysis)

    with tab2:
        st.write("Get race time predictions based on your training.")
        race_distance = st.selectbox(
            "Select Target Race Distance",
            options=["5k", "10k", "half_marathon", "marathon"],
            format_func=lambda x: {
                "5k": "5K",
                "10k": "10K",
                "half_marathon": "Half Marathon (21.1K)",
                "marathon": "Marathon (42.2K)"
            }.get(x, x)
        )

        if st.button("Get Race Prediction"):
            with st.spinner("Calculating prediction..."):
                prediction = st.session_state.ai_coach.get_race_prediction(
                    st.session_state.activities,
                    race_distance
                )
                st.markdown(prediction)

    with tab3:
        st.write("Ask the AI coach any running-related question.")
        question = st.text_area(
            "Your Question",
            placeholder="E.g., How can I improve my marathon time? "
                       "What should I eat before a long run?"
        )

        if st.button("Ask Coach") and question:
            # Build context from available data
            context = {}
            if st.session_state.activities:
                weekly_dist = sum(
                    a.get("distance", 0) for a in st.session_state.activities[:7]
                ) / 1000
                context["weekly_distance"] = f"{weekly_dist:.1f}"
                context["runs_per_week"] = min(len(st.session_state.activities), 7)

            with st.spinner("Getting advice..."):
                advice = st.session_state.ai_coach.get_custom_advice(question, context)
                st.markdown(advice)


def dashboard():
    """Render the main dashboard."""
    # Sidebar
    with st.sidebar:
        st.title("🏃 Running Coach")
        st.divider()

        # Show current AI backend
        backend_name = "🦙 Ollama" if st.session_state.ai_backend == "ollama" else "🌐 Gemini"
        st.caption(f"AI: {backend_name}")

        # Language selector
        current_lang_idx = list(LANGUAGE_OPTIONS.keys()).index(st.session_state.language)
        new_language = st.selectbox(
            "AI Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            format_func=lambda x: LANGUAGE_OPTIONS[x],
            index=current_lang_idx,
            key="sidebar_language"
        )
        if new_language != st.session_state.language:
            st.session_state.language = new_language
            if st.session_state.ai_coach:
                st.session_state.ai_coach.set_language(new_language)

        # Data period selector
        current_period_idx = list(DATA_PERIOD_OPTIONS.keys()).index(st.session_state.data_period)
        new_period = st.selectbox(
            "Data Period",
            options=list(DATA_PERIOD_OPTIONS.keys()),
            index=current_period_idx,
            key="sidebar_period"
        )
        if new_period != st.session_state.data_period:
            st.session_state.data_period = new_period
            st.session_state.activities = []  # Clear to reload with new period
            st.rerun()

        st.divider()

        if st.button("🔄 Refresh Data"):
            st.session_state.activities = []
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.garmin_client = None
            st.session_state.ai_coach = None
            st.session_state.activities = []
            st.session_state.selected_activity = None
            st.rerun()

        st.divider()
        st.caption("Powered by Local AI (Ollama) or Google Gemini")

        st.divider()
        if st.button("⏻ Quit App", use_container_width=True):
            st.write("Shutting down...")
            os._exit(0)

    # Load activities if not cached
    if not st.session_state.activities:
        with st.spinner("Loading running activities..."):
            try:
                # Calculate activity limit based on selected data period
                days = DATA_PERIOD_OPTIONS.get(st.session_state.data_period, 30)
                activity_limit = max(20, days)  # At least 20, or days count
                all_activities = st.session_state.garmin_client.get_running_activities(
                    activity_limit
                )
                # Filter by date range
                cutoff_date = datetime.now() - timedelta(days=days)
                st.session_state.activities = [
                    a for a in all_activities
                    if datetime.fromisoformat(
                        a.get("startTimeLocal", "2000-01-01").replace("Z", "")
                    ) >= cutoff_date
                ]
            except Exception as e:
                st.error(f"Error loading activities: {str(e)}")
                return

    # Main content
    st.title("🏃 Garmin Running AI Coach")

    # If viewing activity details
    if st.session_state.selected_activity:
        render_activity_detail(st.session_state.selected_activity)
        return

    # Main dashboard tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Statistics", "🤖 AI Analysis"])

    with tab1:
        render_metrics_row(st.session_state.activities)
        st.divider()
        render_activity_list(st.session_state.activities)

    with tab2:
        render_statistics_tab()

    with tab3:
        render_ai_analysis_tab()


def main():
    """Main application entry point."""
    init_session_state()

    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()


if __name__ == "__main__":
    main()
