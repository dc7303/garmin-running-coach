"""
AI Coach module supporting multiple backends (Ollama, Gemini).

This module provides AI-powered running coaching feedback by analyzing
running data and generating personalized recommendations.
"""

from abc import ABC, abstractmethod
from typing import Optional

LANGUAGE_INSTRUCTIONS = {
    "en": "Please respond in English.",
    "ko": "한국어로 답변해 주세요."
}


class BaseAICoach(ABC):
    """Abstract base class for AI coaches."""

    def __init__(self, language: str = "en"):
        """Initialize with language setting."""
        self.language = language

    def _get_language_instruction(self) -> str:
        """Get the language instruction for prompts."""
        return LANGUAGE_INSTRUCTIONS.get(self.language, LANGUAGE_INSTRUCTIONS["en"])

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the AI model."""
        pass

    def _build_activity_prompt(self, activity: dict) -> str:
        """Build a prompt from activity data."""
        distance_km = activity.get("distance", 0) / 1000
        duration_min = activity.get("duration", 0) / 60
        avg_pace = duration_min / distance_km if distance_km > 0 else 0
        pace_min = int(avg_pace)
        pace_sec = int((avg_pace - pace_min) * 60)

        prompt = f"""Analyze this running activity and provide coaching feedback:

**Run Details:**
- Date: {activity.get("startTimeLocal", "Unknown")}
- Distance: {distance_km:.2f} km
- Duration: {duration_min:.1f} minutes
- Average Pace: {pace_min}:{pace_sec:02d} min/km
- Average Heart Rate: {activity.get("averageHR", "N/A")} bpm
- Max Heart Rate: {activity.get("maxHR", "N/A")} bpm
- Calories: {activity.get("calories", "N/A")}
- Elevation Gain: {activity.get("elevationGain", "N/A")} m
- Activity Type: {activity.get("activityType", {}).get("typeKey", "running")}

Please provide:
1. **Performance Summary**: Brief assessment of this run
2. **Heart Rate Analysis**: Zone analysis if HR data available
3. **Pace Consistency**: Assessment of pacing strategy
4. **Recovery Recommendation**: Suggested recovery based on intensity
5. **Training Tip**: One specific tip to improve

Keep the response concise and actionable (under 300 words).

{self._get_language_instruction()}"""
        return prompt

    def _build_weekly_prompt(self, weekly_stats: list, activities: list) -> str:
        """Build a prompt from weekly statistics."""
        stats_text = ""
        for week in weekly_stats:
            pace_min = int(week["avg_pace_min_km"])
            pace_sec = int((week["avg_pace_min_km"] - pace_min) * 60)
            stats_text += f"""
- Week of {week["week_start"]}:
  - Runs: {week["run_count"]}
  - Distance: {week["total_distance_km"]} km
  - Average Pace: {pace_min}:{pace_sec:02d} min/km
  - Avg HR: {week["avg_heart_rate"]:.0f} bpm"""

        recent_runs = ""
        for a in activities[:5]:
            distance_km = a.get("distance", 0) / 1000
            duration_min = a.get("duration", 0) / 60
            avg_pace = duration_min / distance_km if distance_km > 0 else 0
            pace_min = int(avg_pace)
            pace_sec = int((avg_pace - pace_min) * 60)
            recent_runs += f"- {a.get('startTimeLocal', 'Unknown')[:10]}: "
            recent_runs += f"{distance_km:.1f}km at {pace_min}:{pace_sec:02d}/km\n"

        prompt = f"""Analyze this runner's training pattern and provide coaching feedback:

**Weekly Training Summary (Last 4 weeks):**
{stats_text}

**Recent Runs:**
{recent_runs}

Please provide:
1. **Training Load Assessment**: Is the weekly volume appropriate? Any signs of overtraining?
2. **Consistency Analysis**: How consistent is the training pattern?
3. **Progress Trend**: Any improvement or decline in performance?
4. **Recommended Focus**: What should this runner focus on next week?
5. **Suggested Workout**: One specific workout recommendation

Keep the response practical and motivating (under 400 words).

{self._get_language_instruction()}"""
        return prompt

    def get_activity_feedback(self, activity: dict) -> str:
        """Generate AI feedback for a single activity."""
        prompt = self._build_activity_prompt(activity)
        try:
            return self.generate(prompt)
        except Exception as e:
            return f"Unable to generate feedback: {str(e)}"

    def get_weekly_analysis(self, weekly_stats: list, activities: list) -> str:
        """Generate AI analysis of weekly training pattern."""
        prompt = self._build_weekly_prompt(weekly_stats, activities)
        try:
            return self.generate(prompt)
        except Exception as e:
            return f"Unable to generate analysis: {str(e)}"

    def get_race_prediction(
        self,
        recent_activities: list,
        target_distance: str = "half_marathon"
    ) -> str:
        """Generate race time prediction based on training data."""
        if not recent_activities:
            return "Not enough data for prediction."

        distances = {
            "5k": "5 kilometers",
            "10k": "10 kilometers",
            "half_marathon": "21.1 kilometers (half marathon)",
            "marathon": "42.195 kilometers (marathon)"
        }

        distance_name = distances.get(target_distance, target_distance)

        recent_data = ""
        for a in recent_activities[:10]:
            distance_km = a.get("distance", 0) / 1000
            duration_min = a.get("duration", 0) / 60
            avg_pace = duration_min / distance_km if distance_km > 0 else 0
            pace_min = int(avg_pace)
            pace_sec = int((avg_pace - pace_min) * 60)
            recent_data += f"- {distance_km:.1f}km at {pace_min}:{pace_sec:02d}/km "
            recent_data += f"(HR: {a.get('averageHR', 'N/A')} bpm)\n"

        prompt = f"""Based on this runner's recent training data, predict their potential race time
for {distance_name}:

**Recent Runs:**
{recent_data}

Please provide:
1. **Predicted Finish Time**: Estimated time range
2. **Confidence Level**: How reliable is this prediction?
3. **Key Factors**: What training aspects influenced this prediction?
4. **Race Day Tips**: 2-3 specific tips for race day
5. **Training Gap**: What training might help improve the prediction?

Be realistic and base predictions on the actual training data shown.

{self._get_language_instruction()}"""

        try:
            return self.generate(prompt)
        except Exception as e:
            return f"Unable to generate prediction: {str(e)}"

    def get_custom_advice(self, question: str, context: dict) -> str:
        """Get custom coaching advice for a specific question."""
        context_text = ""
        if context.get("weekly_distance"):
            context_text += f"- Weekly running volume: ~{context['weekly_distance']} km\n"
        if context.get("avg_pace"):
            context_text += f"- Typical pace: {context['avg_pace']} min/km\n"
        if context.get("runs_per_week"):
            context_text += f"- Runs per week: {context['runs_per_week']}\n"

        prompt = f"""You are an experienced running coach. A runner has the following question:

**Runner Profile:**
{context_text if context_text else "No specific data provided."}

**Question:**
{question}

Please provide helpful, evidence-based coaching advice.
Keep the response focused and practical (under 300 words).

{self._get_language_instruction()}"""

        try:
            return self.generate(prompt)
        except Exception as e:
            return f"Unable to generate advice: {str(e)}"

    def set_language(self, language: str):
        """Update the language setting."""
        self.language = language


class OllamaCoach(BaseAICoach):
    """AI coach using Ollama (local LLM)."""

    def __init__(self, model: str = "llama3.2", language: str = "en"):
        """
        Initialize Ollama coach.

        Args:
            model: Ollama model name (e.g., llama3.2, gemma2, mistral)
            language: Response language ("en" or "ko")
        """
        super().__init__(language=language)
        self.model = model
        import ollama
        self._client = ollama

    def generate(self, prompt: str) -> str:
        """Generate response using Ollama."""
        response = self._client.generate(model=self.model, prompt=prompt)
        return response["response"]


class GeminiCoach(BaseAICoach):
    """AI coach using Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", language: str = "en"):
        """
        Initialize Gemini coach.

        Args:
            api_key: Google Gemini API key
            model: Gemini model name
            language: Response language ("en" or "ko")
        """
        super().__init__(language=language)
        self.api_key = api_key
        self.model_name = model
        from google import genai
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """Generate response using Gemini API."""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text


def create_ai_coach(
    backend: str = "ollama",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    language: str = "en"
) -> BaseAICoach:
    """
    Factory function to create an AI coach.

    Args:
        backend: "ollama" or "gemini"
        api_key: API key (required for Gemini)
        model: Model name (optional, uses default if not specified)
        language: Response language ("en" for English, "ko" for Korean)

    Returns:
        AI coach instance
    """
    if backend == "ollama":
        return OllamaCoach(model=model or "llama3.2", language=language)
    elif backend == "gemini":
        if not api_key:
            raise ValueError("API key required for Gemini backend")
        return GeminiCoach(api_key=api_key, model=model or "gemini-2.0-flash", language=language)
    else:
        raise ValueError(f"Unknown backend: {backend}")
