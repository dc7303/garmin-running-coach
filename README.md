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
   - **macOS**: See macOS installation below
   - **Windows**: Double-click `GarminRunningCoach.exe`
   - **Linux**: Run `./GarminRunningCoach`
3. Your browser will open automatically
4. Enter your Garmin credentials and select an AI backend

#### macOS Installation

Since the app is not signed with an Apple Developer certificate, macOS Gatekeeper will block it. To open:

**Method 1 (Recommended):**
1. Move `GarminRunningCoach.app` to Applications folder
2. Open **System Settings** > **Privacy & Security**
3. Scroll down and click **"Open Anyway"** next to the blocked app message

**Method 2:**
1. Right-click (or Control-click) on `GarminRunningCoach.app`
2. Select **"Open"** from the context menu
3. Click **"Open"** in the dialog that appears

**Method 3 (Terminal):**
```bash
xattr -cr /Applications/GarminRunningCoach.app
```

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

---

# 한국어 가이드

Garmin Connect에서 러닝 데이터를 가져와 시각화하고, AI 코칭 피드백을 제공하는 데스크톱 애플리케이션입니다.

## 주요 기능

- **러닝 대시보드**: 최근 러닝 활동과 주요 지표 확인
- **상세 분석**: 심박수 존, 페이스 차트, 고도 데이터
- **주간/월간 통계**: 훈련량과 진행 상황 추적
- **AI 코칭**: 개별 러닝에 대한 맞춤 피드백
- **훈련 분석**: AI 기반 훈련 패턴 분석
- **레이스 예측**: 훈련 데이터 기반 예상 기록
- **코치에게 질문**: 러닝 관련 질문에 대한 답변

## 다운로드

[Releases](https://github.com/dc7303/garmin-running-coach/releases) 페이지에서 최신 버전을 다운로드하세요.

| 플랫폼 | 파일 | 상태 |
|--------|------|------|
| macOS | `GarminRunningCoach-macOS.zip` | ✅ 사용 가능 |
| Windows | `GarminRunningCoach-windows.zip` | 🚧 준비 중 |
| Linux | `GarminRunningCoach-linux.tar.gz` | 🚧 준비 중 |

## macOS 설치 방법

앱이 Apple 개발자 인증서로 서명되지 않아 Gatekeeper가 차단합니다. 다음 방법으로 열 수 있습니다:

**방법 1 (권장):**
1. `GarminRunningCoach.app`을 Applications 폴더로 이동
2. **시스템 설정** > **개인 정보 보호 및 보안** 열기
3. 아래로 스크롤하여 차단된 앱 옆의 **"그래도 열기"** 클릭

**방법 2:**
1. `GarminRunningCoach.app`을 우클릭 (또는 Control-클릭)
2. 메뉴에서 **"열기"** 선택
3. 대화상자에서 **"열기"** 클릭

**방법 3 (터미널):**
```bash
xattr -cr /Applications/GarminRunningCoach.app
```

## AI 백엔드 선택

### 옵션 1: Ollama (권장 - 무료 & 로컬)

Ollama는 AI 모델을 로컬에서 실행합니다. API 키 불필요, 사용량 제한 없음.

1. [ollama.com](https://ollama.com)에서 설치하거나 Homebrew 사용:
   ```bash
   brew install ollama
   ```
2. 앱에서 Ollama 시작 및 모델 다운로드 안내를 따르세요

### 옵션 2: Google Gemini (클라우드 API)

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. "API 키 만들기" 클릭
4. 키를 복사하여 앱에 붙여넣기

> **참고**: 무료 티어는 분당 15회, 일일 1,500회 요청 제한이 있습니다.

## 개인정보 및 보안

- Garmin 자격 증명은 Garmin Connect 인증에만 **로컬에서** 사용됩니다
- Ollama 사용 시 모든 AI 처리가 로컬에서 수행됩니다
- Gemini 사용 시 러닝 데이터 요약만 Google API로 전송됩니다
- 다른 제3자 서버로 데이터가 저장되거나 전송되지 않습니다
