# 방구석일주

운동한 만큼 함양·서울·부산·제주 코스를 가상으로 이동하는 웹앱.

- 앱 파일: `index.html` 하나 (외부 라이브러리 없음)
- 배포: 이 저장소의 `main`에 올리면 Netlify가 자동으로 새 버전을 띄움
- 현재 상태·결정: Claude 프로젝트 문서 `방구석일주_현재상태_CURRENT`

## 안드로이드 앱 (APK)

- `app/` = 껍데기 앱 (Capacitor). 안에서 위 Netlify 주소를 열고, 잠금 중 GPS를 붙임
- `app/` 가 바뀌면 GitHub Actions가 APK를 만들어 Release에 올림
- 폰에서 받기: https://github.com/tough835/bangguseok-ilju/releases/latest/download/bangguseok.apk
- 화면·코스 수정은 `index.html`만 고치면 앱에도 1분 안에 반영 (앱 재설치 불필요)
- `keystore/` = 앱 서명 열쇠. 바꾸면 기존 앱 위에 덮어 설치가 안 됨 (지우고 다시 깔아야 해서 기록이 사라짐)
