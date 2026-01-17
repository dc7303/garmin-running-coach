# Garmin Running AI Coach

A desktop application that fetches your running data from Garmin Connect, visualizes performance metrics, and provides AI-powered coaching feedback.

![Login Page](images/login_image.png)

## Features

- **Run Dashboard**: View recent running activities with key metrics
- **Detailed Analysis**: Heart rate zones, pace charts, and elevation data
- **Weekly/Monthly Statistics**: Track your training volume and progress over time
- **AI Coaching**: Get personalized feedback on individual runs
- **Training Analysis**: AI-powered analysis of your training patterns
- **Race Predictions**: Estimate race times based on your training data
- **Ask the Coach**: Get answers to running-related questions
- **Multi-language Support**: English and Korean

## Screenshots

| Workout List | Statistics | AI Coach |
|:---:|:---:|:---:|
| ![Workout List](images/workout_list.png) | ![Statistics](images/statistics.png) | ![AI Support](images/ai_support.png) |

---

## For Users

### Download

Download the latest release from the [Releases](https://github.com/dc7303/garmin-running-coach/releases) page:

| Platform | File | Status |
|----------|------|--------|
| macOS | `GarminRunningCoach-macOS.zip` | ✅ Available |
| Windows | `GarminRunningCoach-windows.zip` | 🚧 Coming Soon |
| Linux | `GarminRunningCoach-linux.tar.gz` | 🚧 Coming Soon |

> **Note**: Windows and Linux builds are not yet tested. Contributions welcome!

### Running the Application

1. Extract the downloaded archive
2. Run the application:
   - **macOS**: Double-click `GarminRunningCoach.app`
   - **Windows**: Double-click `GarminRunningCoach.exe`
   - **Linux**: Run `./GarminRunningCoach`
3. Your browser will open automatically
4. Enter your Garmin credentials and select an AI backend

### AI Backend Options

You can choose between two AI backends:

#### Option 1: Ollama (Recommended - Free & Local)

Ollama runs AI models locally on your computer. No API key required, no usage limits.

1. Install Ollama from [ollama.com](https://ollama.com) or via Homebrew:
   ```bash
   brew install ollama
   ```
2. The app will guide you to start Ollama and download a model

#### Option 2: Google Gemini (Cloud API)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in the app

> **Note**: Free tier has rate limits (15 requests/min, 1,500 requests/day)

---

## For Developers

### Prerequisites

- Python 3.9 or higher
- Garmin Connect account
- Ollama or Google Gemini API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dc7303/garmin-running-coach.git
   cd garmin-running-coach
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set up environment variables:
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   GARMIN_EMAIL=your_garmin_email@example.com
   GARMIN_PASSWORD=your_garmin_password
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Running in Development

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`.

### Building Executable

Install build dependencies:
```bash
pip install -r requirements-dev.txt
```

#### macOS / Linux
```bash
./build.sh
```
Output: `dist/GarminRunningCoach.app` (macOS) or `dist/GarminRunningCoach/` (Linux)

#### Windows
```cmd
build.bat
```
Output: `dist\GarminRunningCoach\GarminRunningCoach.exe`

#### Creating Distributable Archives

```bash
# macOS
cd dist && zip -r GarminRunningCoach-macOS.zip GarminRunningCoach.app

# Linux
tar -czvf GarminRunningCoach-linux.tar.gz -C dist GarminRunningCoach

# Windows (PowerShell)
Compress-Archive -Path dist\GarminRunningCoach -DestinationPath GarminRunningCoach-windows.zip
```

---

## Project Structure

```
garmin-running-coach/
├── app.py                 # Streamlit main application
├── garmin_client.py       # Garmin Connect data fetching
├── ai_coach.py            # AI coaching module (Ollama & Gemini)
├── launcher.py            # PyInstaller entry point
├── garmin_coach.spec      # PyInstaller configuration
├── build.sh               # Build script (macOS/Linux)
├── build.bat              # Build script (Windows)
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Development dependencies
└── README.md
```

## Tech Stack

- **Frontend**: Streamlit
- **Data Source**: Garmin Connect (via garminconnect library)
- **AI Backends**:
  - Ollama (local LLM - llama3.2, etc.)
  - Google Gemini API (gemini-2.0-flash)
- **Charts**: Plotly
- **Data Processing**: Pandas
- **Packaging**: PyInstaller

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Privacy & Security

- Your Garmin credentials are **only used locally** to authenticate with Garmin Connect
- When using Ollama, all AI processing happens locally on your computer
- When using Gemini, only running data summaries are sent to Google's API
- No data is stored or transmitted to any other third-party servers
