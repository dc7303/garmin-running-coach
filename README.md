# Garmin Running AI Coach

A web application that fetches running data from Garmin Connect, visualizes performance metrics, and provides AI-powered coaching feedback using Google Gemini.

## Features

- **Run Dashboard**: View recent running activities with key metrics
- **Detailed Analysis**: Heart rate zones, pace charts, and elevation data
- **Weekly/Monthly Statistics**: Track your training volume and progress over time
- **AI Coaching**: Get personalized feedback on individual runs
- **Training Analysis**: AI-powered analysis of your training patterns
- **Race Predictions**: Estimate race times based on your training data
- **Ask the Coach**: Get answers to running-related questions

## Download (For Users)

Download the latest release for your platform:

| Platform | Download |
|----------|----------|
| Windows | `GarminRunningCoach-windows.zip` |
| macOS | `GarminRunningCoach-macOS.zip` |
| Linux | `GarminRunningCoach-linux.tar.gz` |

### Running the Application

1. Extract the downloaded archive
2. Run the application:
   - **Windows**: Double-click `GarminRunningCoach.exe`
   - **macOS**: Double-click `GarminRunningCoach.app`
   - **Linux**: Run `./GarminRunningCoach`
3. Your browser will open automatically at `http://localhost:8501`
4. Enter your Garmin credentials and Gemini API key

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in the app

The free tier allows 60 requests per minute, which is more than enough for personal use.

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Garmin Connect account
- Google Gemini API key (free tier available)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/garmin-running-coach.git
cd garmin-running-coach
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_garmin_password
GEMINI_API_KEY=your_gemini_api_key
```

### Running in Development

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

---

## Building Executable

To build a standalone executable that can be distributed to users:

### macOS / Linux

```bash
./build.sh
```

Output:
- macOS: `dist/GarminRunningCoach.app`
- Linux: `dist/GarminRunningCoach/GarminRunningCoach`

### Windows

```cmd
build.bat
```

Output: `dist\GarminRunningCoach\GarminRunningCoach.exe`

### Creating Distributable Archives

**macOS:**
```bash
cd dist && zip -r GarminRunningCoach-macOS.zip GarminRunningCoach.app
```

**Linux:**
```bash
tar -czvf GarminRunningCoach-linux.tar.gz -C dist GarminRunningCoach
```

**Windows:**
```
Compress dist\GarminRunningCoach folder to GarminRunningCoach-windows.zip
```

---

## Usage Guide

### Login
Enter your Garmin Connect credentials and Gemini API key on the login page.

### Dashboard
- View summary metrics of your recent runs
- Click on any activity to see detailed analysis and AI feedback
- Use the tabs to switch between Dashboard, Statistics, and AI Analysis

### AI Features
- **Activity Feedback**: Get AI coaching feedback on individual runs
- **Weekly Analysis**: Analyze your training patterns over the past weeks
- **Race Prediction**: Get estimated race times for 5K, 10K, Half Marathon, or Marathon
- **Ask Coach**: Ask any running-related question

---

## Project Structure

```
garmin-running-coach/
├── app.py                 # Streamlit main application
├── garmin_client.py       # Garmin Connect data fetching module
├── ai_coach.py            # Google Gemini AI coaching module
├── launcher.py            # PyInstaller entry point
├── garmin_coach.spec      # PyInstaller configuration
├── build.sh               # Build script for macOS/Linux
├── build.bat              # Build script for Windows
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Development dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Tech Stack

- **Frontend**: Streamlit
- **Data Fetching**: garminconnect library
- **AI**: Google Gemini API (gemini-1.5-flash model)
- **Charts**: Plotly
- **Data Processing**: Pandas
- **Packaging**: PyInstaller

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Privacy & Security

- Your Garmin credentials are **only used locally** to authenticate with Garmin Connect
- No data is stored or transmitted to any third-party servers (except Garmin and Google Gemini API)
- When using the standalone executable, all processing happens on your computer
