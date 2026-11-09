# 협업 규칙

## 흐름

모든 변경은 **이슈 → 브랜치 → PR → 리뷰 1명 승인 → Squash 머지**로 진행합니다. `main`에 직접 push할 수 없습니다.

이슈 하나 = 작업 하나 = 브랜치 하나 = PR 하나.

## 타입

| 타입 | 언제 | 라벨 | 브랜치 예시 | 제목 예시 |
| --- | --- | --- | --- | --- |
| `feat` | 새 기능 | 🥸 feat | `feat/12-sphere-drag` | `feat: 구 드래그 추가` |
| `fix` | 버그 | 🛠️ fix | `fix/15-overlap-crash` | `fix: 겹침 판정 오류 수정` |
| `design` | 화면·에셋 | 🎨 design | `design/20-onboarding` | `design: 온보딩 화면 수정` |
| `docs` | 문서 | 📄 docs | `docs/1-contributing` | `docs: 협업 규칙 추가` |
| `refactor` | 구조 개선 | 🤴🏻 refactor | `refactor/30-mixing` | `refactor: 혼합 로직 분리` |
| `chore` | 설정·기타 | ⚙️ chore | `chore/2-gitignore` | `chore: gitignore 추가` |

## 이슈

Issues → **New issue**에서 양식을 고릅니다. 타입 라벨과 제목 말머리는 자동으로 붙습니다. 담당자는 자기 자신으로 지정합니다.

## 브랜치

`타입/이슈번호-짧은-설명` 형식이고, 소문자와 하이픈만 씁니다. 아래 명령은 브랜치를 만들어 이슈에 연결하고 이동까지 합니다. 웹에서는 이슈 오른쪽의 **Create a branch**를 씁니다.

```bash
gh issue develop 12 --name feat/12-sphere-drag --checkout
```

## PR

- 서로 배우며 리뷰할 수 있도록 PR은 작은 기능 하나 단위로 최대한 작게 만듭니다. 커질 것 같으면 이슈부터 나눕니다.
- 제목은 `타입: 무엇을 했는지` 형식입니다. Squash 머지하면 이 제목이 `main`의 커밋 메시지가 됩니다.
- 본문의 `Closes #번호`로 머지 시 이슈가 자동으로 닫힙니다. 화면이 바뀌면 스크린샷을 붙입니다.
- 작성자를 뺀 팀원 전원에게 리뷰가 자동 요청됩니다 (`.github/CODEOWNERS`). Draft PR은 Ready로 바꿀 때 요청됩니다.
- 담당자와 사람 라벨은 PR을 만들 때 직접 붙입니다.

```bash
gh pr create --assignee @me --label "🐹 Victoria"
```

- 머지된 브랜치는 자동으로 삭제됩니다.

## 충돌 예방

`project.pbxproj`처럼 함께 쓰는 파일을 고칠 것 같으면 시작 전에 팀에 먼저 알립니다.
