# Daily.dev Bot

Daily.dev에서 상위 게시글을 크롤링하고 한국어로 번역하여 Discord 웹훅을 통해 임베딩 메시지로 전송하는 봇입니다.

## 주요 기능

- 📊 Daily.dev 상위 게시글 10개 자동 크롤링
- 📖 **게시글 본문 내용 자동 수집 및 번역**
- 🌐 Google Translate를 활용한 한국어 번역 (제목, 설명, 본문)
- 💬 Discord 웹훅을 통한 풍부한 임베딩 메시지 전송
- ⏰ 스케줄링 (매일 오전 8시 자동 실행)
- 🌐 웹 API 엔드포인트 제공
- 🔧 다양한 실행 모드 지원
- ⚡ 본문 수집 옵션으로 성능 최적화

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/snowykte0426/Daily.Dev.Bot.git
cd Daily.Dev.Bot
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Chrome 드라이버 설치

이 봇은 Selenium을 사용하여 웹 크롤링을 수행합니다. `webdriver-manager`가 자동으로 Chrome 드라이버를 관리하므로 별도 설치가 필요 없습니다.

### 4. 환경 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값들을 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
DAILY_DEV_EMAIL=your-email@example.com
DAILY_DEV_PASSWORD=your-password
CHROME_DRIVER_PATH=/path/to/chromedriver  # 선택적 (자동 관리됨)
GOOGLE_TRANSLATE_API_KEY=your-google-translate-api-key  # 선택적 (기본 번역기 사용)
FETCH_CONTENT=true  # 본문 수집 여부 (true/false)
```

## Discord 웹훅 설정

1. Discord 서버에서 웹훅을 생성합니다
2. 웹훅 URL을 복사하여 `.env` 파일의 `DISCORD_WEBHOOK_URL`에 설정합니다

자세한 방법: [Discord 웹훅 만들기](https://support.discord.com/hc/ko/articles/228383668)

## 사용법 

### 1. 기본 스케줄러 모드

매일 오전 8시에 자동으로 실행:

```bash
python main.py
```

### 2. 즉시 실행 모드

테스트나 수동 실행용:

```bash
python main.py --run-once
```

### 3. API 서버 모드

웹 API를 통한 원격 제어:

```bash
python main.py --api
```

API 서버가 `http://localhost:8000`에서 실행됩니다.

### 4. 설정 검증

환경 설정이 올바른지 확인:

```bash
python main.py --validate
```

## API 엔드포인트

API 서버 모드에서 다음 엔드포인트들을 사용할 수 있습니다:

### GET `/`
- API 상태 확인

### POST `/scrape`
- 게시글 크롤링 및 Discord 전송 (비동기)
- 파라미터: `limit` (1-50, 기본값: 10)

### GET `/scrape-sync`
- 동기적 게시글 크롤링 (테스트용)
- 파라미터: `limit` (1-20, 기본값: 10)

### POST `/translate`
- 텍스트 번역
- 파라미터: `text`, `target_lang` (기본값: "ko")

### GET `/config`
- 현재 설정 정보 조회

### GET `/health`
- 헬스 체크

## 프로젝트 구조 📁

```
Daily.Dev.Bot/
├── main.py              # 메인 진입점
├── config.py            # 설정 관리
├── daily_scraper.py     # daily.dev 크롤링
├── translator.py        # 한국어 번역
├── discord_sender.py    # Discord 메시지 전송
├── scheduler.py         # 스케줄링 관리
├── web_api.py          # FastAPI 웹 서버
├── requirements.txt     # 의존성 목록
├── .env.example        # 환경 변수 템플릿
└── README.md           # 이 파일
```

## 로그 

봇의 실행 로그는 `daily_bot.log` 파일에 저장됩니다.

## 주의사항 

1. **Daily.dev 계정 필요**: daily.dev에 로그인이 필요하므로 유효한 계정이 있어야 합니다.
2. **크롤링 정책 준수**: 과도한 요청을 피하고 daily.dev의 서비스 약관을 준수하세요.
3. **Discord 레이트 리미트**: Discord 웹훅에는 레이트 리미트가 있으므로 너무 자주 실행하지 마세요.
4. **Chrome 브라우저 필요**: Selenium이 Chrome을 사용하므로 시스템에 Chrome이 설치되어 있어야 합니다.

## 문제 해결 

### Chrome 드라이버 문제
- `webdriver-manager`가 자동으로 드라이버를 관리합니다
- 문제가 발생하면 Chrome 브라우저를 최신 버전으로 업데이트하세요

### 로그인 문제
- daily.dev 이메일과 비밀번호가 정확한지 확인하세요
- 2FA가 활성화된 경우 비활성화하거나 앱 비밀번호를 사용하세요

### Discord 메시지가 전송되지 않는 경우
- 웹훅 URL이 정확한지 확인하세요
- Discord 서버에서 봇이 메시지를 보낼 권한이 있는지 확인하세요

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 기여하기

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!
