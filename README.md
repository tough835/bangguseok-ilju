# 방구석러너

러닝머신·걷기·계단·자전거 운동을 실제 길 위 가상여행으로 — 함양·지리산·100대명산·해파랑길·세계 도시 코스.

- 앱 파일: `index.html` 하나 (외부 라이브러리 없음)
- 배포: 이 저장소의 `main`에 올리면 GitHub Pages가 자동 반영 → https://tough835.github.io/bangguseok-runner/
- 현재 상태·결정: Claude 프로젝트 문서 `방구석일주_현재상태_CURRENT`
- 옛 이름: 방구석일주 (2026-11-16 방구석러너로 변경)

## 안드로이드 앱 (APK)

- `app/` = 껍데기 앱 (Capacitor). 안에서 위 GitHub Pages 주소를 열고, 잠금 중 GPS·걸음 센서를 붙임
- 앱 이름표 `com.re2.bangguseokrunner` (옛 `com.dolgurum.bangguseok`과 다른 앱)
- `app/` 가 바뀌면 GitHub Actions가 APK를 만들어 Release에 올림
- 폰에서 받기: https://github.com/tough835/bangguseok-runner/releases/latest/download/bangguseok-runner.apk
- 화면·코스 수정은 `index.html`만 고치면 앱에도 반영 (앱 재설치 불필요)
- `keystore/re2-release.p12` = 앱 서명 열쇠(11/19 교체). 비밀번호는 GitHub Secrets `KEYSTORE_PASSWORD`에만. 바꾸지 말 것
