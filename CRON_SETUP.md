# 크론 작업 설정 가이드

## 매일 9시에 데이터 수집 및 매매 시그널 분석 실행하기

### 1. 크론 작업 설정

터미널에서 다음 명령어로 크론 편집기를 열어주세요:

```bash
crontab -e
```

### 2. 크론 작업 추가

다음 줄들을 추가하세요 (경로는 실제 프로젝트 경로로 수정):

```bash
# 매일 오전 9시에 일봉 데이터 수집
0 9 * * * /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/venv/bin/python /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/upload_s3_upbit.py >> /tmp/upbit_daily.log 2>&1

# 매일 오전 9시 5분에 공포탐욕지수 수집
5 9 * * * /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/venv/bin/python /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/upload_s3_feargreed.py >> /tmp/feargreed.log 2>&1

# 매일 오전 9시 10분에 매매 시그널 분석 (S3 기반)
10 9 * * * /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/venv/bin/python /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/daily_signal_alarm.py >> /tmp/crypto_signal.log 2>&1

# 매 5분마다 5분봉 데이터 수집
*/5 * * * * /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/venv/bin/python /Users/jinyoungwoo/StudioProjects/crypto-signal-platform/upload_s3_upbit_5m.py >> /tmp/upbit_5m.log 2>&1
```

### 3. 크론 작업 확인

설정한 크론 작업을 확인하려면:

```bash
crontab -l
```

### 4. 로그 확인

각 작업의 실행 로그를 확인하려면:

```bash
# 일봉 데이터 수집 로그
tail -f /tmp/upbit_daily.log

# 공포탐욕지수 수집 로그
tail -f /tmp/feargreed.log

# 매매 시그널 분석 로그
tail -f /tmp/crypto_signal.log

# 5분봉 데이터 수집 로그
tail -f /tmp/upbit_5m.log
```

### 5. 테스트 실행

크론 작업 설정 전에 수동으로 테스트해보세요:

```bash
# 일봉 데이터 수집 테스트
python upload_s3_upbit.py

# 공포탐욕지수 수집 테스트
python upload_s3_feargreed.py

# 매매 시그널 분석 테스트 (S3 기반)
python daily_signal_alarm.py

# 5분봉 데이터 수집 테스트
python upload_s3_upbit_5m.py
```

## 크론 시간 설정 예시

```bash
# 매일 오전 9시
0 9 * * *

# 매일 오전 9시 30분
30 9 * * *

# 평일만 오전 9시 (월-금)
0 9 * * 1-5

# 주 2회 (월, 목 오전 9시)
0 9 * * 1,4
```

## 주의사항

1. **절대 경로 사용**: 크론에서는 상대 경로가 작동하지 않으므로 절대 경로를 사용해야 합니다.

2. **환경변수**: 크론 작업에서는 기본 환경변수가 로드되지 않을 수 있습니다. 필요시 스크립트 내에서 환경변수를 설정하세요.

3. **로그 파일**: 실행 결과를 로그 파일로 저장하여 문제 발생 시 디버깅할 수 있습니다.

4. **권한 확인**: 스크립트 파일에 실행 권한이 있는지 확인하세요:
```bash
chmod +x daily_signal_alarm.py
```
