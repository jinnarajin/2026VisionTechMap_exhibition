# Judy TechMap

Apple Vision Pro의 visionOS를 활용한 몰입형 인터랙티브 전시 프로젝트입니다.

사용자는 창문 너머로 펼쳐지는 세 가지 풍경을 감상하며, 각 환경에 맞는 인터랙션을 경험할 수 있습니다.

## Architecture

**Feature-based MVVM + Coordinator**

SwiftUI와 RealityKit을 기반으로, 기능별로 코드를 분리하는 Feature-based 구조와 MVVM 패턴을 사용합니다.

- **Model**: 데이터 및 상태 정의
- **View**: SwiftUI UI 및 RealityKit 콘텐츠 표현
- **ViewModel**: View에 필요한 상태 관리 및 사용자 입력 처리
- **Coordinator**: 전시 흐름, 환경 전환 및 기능 간 연결 관리
- **Service / Controller**: 오디오 처리, RealityKit 엔티티 및 인터랙션 관리

모든 기능에 MVVM을 일괄 적용하지 않고, 기능의 특성과 책임에 따라 필요한 구성 요소를 사용합니다.

### Architecture Overview

```text
                   ExperienceCoordinator
                    모드 전환 · 전시 흐름
                             │
                             ▼
                    Environment Interface
                  공통 환경 로딩 · 정리 규칙
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
       Starry Night       Ocean View     Rainy Greenery
            │                │                │
      ├─ Time of Day    ├─ Wind          ├─ Rain
      ├─ Constellation  └─ Time of Day   └─ Fog
      └─ Moon Phase

                       Shared Systems
         Curtain · Portal · Window · Audio
                  (Echo · Recording · ASMR)
```

**구성 요소별 역할**

- **ExperienceCoordinator**: 전체 전시 흐름과 환경 간 전환을 관리합니다.
- **Environment Interface**: 각 환경이 공통적으로 따르는 로딩, 활성화 및 정리 규칙을 정의합니다.
- **Environment**: 해당 환경의 전체 장면을 구성하고 세부 기능을 연결합니다.
- **Interaction / Effect Controller**: 별자리 생성, 달의 위상 변화, 바람, 비와 안개 등 개별 인터랙션 및 효과를 담당합니다.
- **Shared Systems**: 커튼, 포털, 창문, 오디오 등 여러 환경에서 공통으로 사용하는 기능을 관리합니다.

Environment 하나에서 모든 인터랙션을 직접 처리하지 않고, 기능별 Controller나 System으로 책임을 분리합니다.

각 환경의 기능은 독립적으로 개발할 수 있도록 구성하며, 공통 기능과 환경별 기능이 불필요하게 결합되지 않도록 합니다.

## Project Structure

```text
Project/
├── App/             # 앱 진입점 및 앱 전역 설정
├── Core/            # 공통 모델, 상태 및 Coordinator
├── Features/        # 기능별 모듈
│   ├── Immersive/   # 몰입형 공간
│   ├── Curtain/     # 커튼 인터랙션
│   ├── Portal/      # 창문 및 포털
│   ├── Environments/
│   │   ├── StarryNight/
│   │   ├── Ocean/
│   │   └── RainyGreenery/
│   └── Audio/       # 에코, 녹음, 저장, 재생 및 ASMR
└── Resources/       # 이미지, 오디오 및 3D 에셋
```

위 구조는 기본적인 구성 방향을 나타내며, 개발 과정에서 기능과 책임에 따라 폴더 및 파일 구성이 변경될 수 있습니다.

## Development Guidelines

- 기능별로 코드를 분리하고 각 구성 요소의 역할을 명확히 합니다.
- View에는 가능한 한 표현 로직을 두고, 비즈니스 로직과 상태 관리는 분리합니다.
- Environment는 전체 장면을 구성하고, 개별 인터랙션 및 효과는 필요에 따라 Controller 또는 System으로 관리합니다.
- 여러 환경에서 사용하는 기능은 공통 모듈로 분리합니다.
- 환경별 기능은 독립적으로 개발하고 테스트할 수 있도록 구성합니다.
- ASMR 등 환경에 따라 다르게 적용되는 공통 기능은 재사용 가능한 시스템으로 관리합니다.
- 기존 기능의 동작을 유지하면서 점진적으로 리팩토링합니다.
- 새로운 파일이나 추상화는 필요할 때 추가하며 불필요한 복잡성을 지양합니다.

## Features

### Starry Night

- 창문 너머 풍경 감상
- 시간대 조절 (새벽~밤)
- 별을 이어 별자리 만들기
- 달의 위상 변화 인터랙션 (그믐달~보름달)

### Ocean View

- 창문 너머 풍경 감상
- 바람 세기 조절
- 시간대 조절 (새벽~밤)

### Rainy Greenery

- 창문 너머 풍경 감상
- 비 세기 조절
- 안개 및 뿌연 공기 표현

### Shared Experience

- 창문 및 포털을 통한 풍경 감상
- 커튼 인터랙션과 환경 전환
- 환경별 ASMR 및 배경음 재생
- 음성 에코 및 녹음
- 녹음 데이터의 안전한 저장과 향후 동의 기반 재생

## Contributing

협업 흐름, 이슈·브랜치·PR 작성 규칙은 [협업 규칙](CONTRIBUTING.md)을 참고하세요.

---

> 본 프로젝트의 아키텍처와 파일 구조는 개발 및 리팩토링 과정에서 변경될 수 있습니다. 기능 간 독립성과 유지보수성을 우선으로 구조를 개선합니다.
