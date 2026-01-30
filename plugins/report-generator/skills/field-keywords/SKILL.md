---
name: field-keywords
description: "Domain-specific keyword mappings for research report generation. Includes ROS2, AI/ML, and general engineering keywords for chapter classification and content mapping."
---

# Field Keywords Skill

## Overview

This skill provides domain-specific keyword mappings for automatic research domain detection and chapter content mapping. It includes three domain keyword sets:

1. **ROS2**: Robot Operating System 2 development
2. **AI/ML**: Artificial Intelligence and Machine Learning
3. **GENERAL**: Generic engineering/research (fallback)

---

## ROS2 Keywords

```json
{
  "domain": "ROS2",
  "description": "ROS2 (Robot Operating System 2) 기반 로봇 시스템 개발 분야",
  "chapter_keywords": {
    "chapter_1_hardware": {
      "title": "하드웨어 통합 및 센서 융합",
      "primary_keywords": ["CAN", "SocketCAN", "CANopen", "센서", "경사계", "inclinometer", "압력센서", "유압", "통신", "인터페이스"],
      "secondary_keywords": ["can_bridge", "SDO", "PDO", "비트레이트", "버스", "멀티스레드", "타임스탬프", "동기화"]
    },
    "chapter_2_computation": {
      "title": "기구학 연산 시스템",
      "primary_keywords": ["기구학", "kinematics", "정기구학", "역기구학", "forward", "inverse", "DOF", "자유도"],
      "secondary_keywords": ["변환", "좌표", "관절", "링크", "엘보", "elbow", "해석적", "수치적"]
    },
    "chapter_3_generation": {
      "title": "궤적 생성 시스템",
      "primary_keywords": ["궤적", "trajectory", "경로", "path", "계획", "planning", "생성", "generator"],
      "secondary_keywords": ["시퀀스", "스케줄링", "배치", "batch", "포인트", "웨이포인트"]
    },
    "chapter_4_control": {
      "title": "제어 시스템",
      "primary_keywords": ["제어", "control", "PI", "PID", "게인", "gain", "피드백", "feedback"],
      "secondary_keywords": ["Kp", "Ki", "Kd", "스케줄링", "튜닝", "threshold", "오차", "error"]
    },
    "chapter_5_ai": {
      "title": "AI 강화학습 시스템",
      "primary_keywords": ["AI", "강화학습", "reinforcement", "learning", "정책", "policy", "에피소드", "episode"],
      "secondary_keywords": ["관측", "observation", "액션", "action", "리워드", "reward", "네트워크", "추론", "inference"]
    },
    "chapter_6_interface": {
      "title": "ROS2 통신 인터페이스",
      "primary_keywords": ["메시지", "msg", "서비스", "service", "액션", "action", "토픽", "topic"],
      "secondary_keywords": ["publisher", "subscriber", "client", "server", "QoS", "callback", "executor"]
    },
    "chapter_7_integration": {
      "title": "시스템 통합 및 검증",
      "primary_keywords": ["HMI", "GUI", "시뮬레이션", "simulation", "테스트", "test", "검증", "validation"],
      "secondary_keywords": ["PyQt", "Rviz", "Gazebo", "모니터링", "시각화", "visualization"]
    },
    "chapter_8_safety": {
      "title": "안정성 및 오류 처리",
      "primary_keywords": ["안전", "safety", "비상", "emergency", "에러", "error", "복구", "recovery"],
      "secondary_keywords": ["재시도", "retry", "타임아웃", "timeout", "백오프", "backoff", "임계값", "threshold"]
    }
  },
  "domain_specific_terms": {
    "generic_to_domain": {
      "모듈": "노드(node)",
      "처리": "퍼블리시(publish)",
      "설정": "파라미터(parameter)",
      "연결": "토픽/서비스(topic/service)",
      "입력": "구독(subscribe)",
      "출력": "발행(publish)",
      "함수 호출": "서비스 호출(service call)",
      "비동기 작업": "액션(action)"
    }
  },
  "common_packages": [
    "excavator_msgs",
    "excavator_signal_manager",
    "excavator_trajectory_planning",
    "excavator_control",
    "excavator_task_management"
  ],
  "common_file_extensions": [".py", ".cpp", ".hpp", ".yaml", ".launch.py", ".msg", ".srv", ".action"]
}
```

---

## AI/ML Keywords

```json
{
  "domain": "AI_ML",
  "description": "AI/ML (인공지능/머신러닝) 기반 시스템 개발 분야",
  "chapter_keywords": {
    "chapter_1_hardware": {
      "title": "데이터 수집 및 전처리 시스템",
      "primary_keywords": ["데이터", "data", "수집", "collection", "전처리", "preprocessing", "파이프라인", "pipeline"],
      "secondary_keywords": ["배치", "batch", "스트리밍", "streaming", "ETL", "정규화", "normalization"]
    },
    "chapter_2_computation": {
      "title": "모델 아키텍처 설계",
      "primary_keywords": ["모델", "model", "아키텍처", "architecture", "레이어", "layer", "네트워크", "network"],
      "secondary_keywords": ["CNN", "RNN", "Transformer", "attention", "embedding", "encoder", "decoder"]
    },
    "chapter_3_generation": {
      "title": "학습 데이터 생성 시스템",
      "primary_keywords": ["생성", "generation", "augmentation", "증강", "합성", "synthetic", "샘플링", "sampling"],
      "secondary_keywords": ["라벨링", "labeling", "어노테이션", "annotation", "밸런싱", "balancing"]
    },
    "chapter_4_control": {
      "title": "학습 프로세스 제어",
      "primary_keywords": ["학습", "training", "최적화", "optimization", "손실", "loss", "역전파", "backpropagation"],
      "secondary_keywords": ["학습률", "learning_rate", "에폭", "epoch", "배치", "batch_size", "그래디언트", "gradient"]
    },
    "chapter_5_ai": {
      "title": "추론 및 배포 시스템",
      "primary_keywords": ["추론", "inference", "배포", "deployment", "서빙", "serving", "예측", "prediction"],
      "secondary_keywords": ["ONNX", "TensorRT", "양자화", "quantization", "가속화", "acceleration"]
    },
    "chapter_6_interface": {
      "title": "API 및 서비스 인터페이스",
      "primary_keywords": ["API", "REST", "gRPC", "엔드포인트", "endpoint", "요청", "request", "응답", "response"],
      "secondary_keywords": ["FastAPI", "Flask", "Docker", "Kubernetes", "마이크로서비스"]
    },
    "chapter_7_integration": {
      "title": "모델 평가 및 검증",
      "primary_keywords": ["평가", "evaluation", "검증", "validation", "테스트", "test", "메트릭", "metric"],
      "secondary_keywords": ["정확도", "accuracy", "정밀도", "precision", "재현율", "recall", "F1", "AUC"]
    },
    "chapter_8_safety": {
      "title": "모델 안정성 및 모니터링",
      "primary_keywords": ["모니터링", "monitoring", "드리프트", "drift", "이상탐지", "anomaly", "로깅", "logging"],
      "secondary_keywords": ["MLOps", "버전관리", "versioning", "롤백", "rollback", "A/B테스트"]
    }
  },
  "domain_specific_terms": {
    "generic_to_domain": {
      "모듈": "모듈/레이어(module/layer)",
      "처리": "추론(inference)",
      "설정": "하이퍼파라미터(hyperparameter)",
      "연결": "레이어 연결(layer connection)",
      "입력": "입력 텐서(input tensor)",
      "출력": "출력 텐서(output tensor)",
      "반복": "에폭(epoch)",
      "저장": "체크포인트(checkpoint)"
    }
  },
  "common_frameworks": [
    "PyTorch",
    "TensorFlow",
    "Keras",
    "scikit-learn",
    "Hugging Face",
    "JAX"
  ],
  "common_file_extensions": [".py", ".ipynb", ".onnx", ".pt", ".pth", ".h5", ".yaml", ".json"]
}
```

---

## GENERAL Keywords

```json
{
  "domain": "GENERAL",
  "description": "범용 연구/개발 분야 (특정 도메인 감지 실패 시 적용)",
  "chapter_keywords": {
    "chapter_1_hardware": {
      "title": "시스템 인프라 구축",
      "primary_keywords": ["센서", "sensor", "하드웨어", "hardware", "인터페이스", "interface", "통신", "communication"],
      "secondary_keywords": ["프로토콜", "protocol", "연결", "connection", "드라이버", "driver", "포트", "port"]
    },
    "chapter_2_computation": {
      "title": "핵심 연산 모듈",
      "primary_keywords": ["알고리즘", "algorithm", "연산", "computation", "처리", "processing", "변환", "transformation"],
      "secondary_keywords": ["함수", "function", "계산", "calculation", "수식", "formula", "모델", "model"]
    },
    "chapter_3_generation": {
      "title": "데이터/결과 생성 시스템",
      "primary_keywords": ["생성", "generation", "계획", "planning", "스케줄", "schedule", "시퀀스", "sequence"],
      "secondary_keywords": ["파이프라인", "pipeline", "워크플로우", "workflow", "자동화", "automation"]
    },
    "chapter_4_control": {
      "title": "제어 및 조절 시스템",
      "primary_keywords": ["제어", "control", "조절", "regulation", "피드백", "feedback", "루프", "loop"],
      "secondary_keywords": ["설정값", "setpoint", "오차", "error", "보정", "correction", "안정화", "stabilization"]
    },
    "chapter_5_ai": {
      "title": "지능형 시스템",
      "primary_keywords": ["AI", "ML", "학습", "learning", "예측", "prediction", "분류", "classification"],
      "secondary_keywords": ["모델", "model", "훈련", "training", "추론", "inference", "데이터", "data"]
    },
    "chapter_6_interface": {
      "title": "인터페이스 설계",
      "primary_keywords": ["API", "인터페이스", "interface", "프로토콜", "protocol", "통신", "communication"],
      "secondary_keywords": ["메시지", "message", "요청", "request", "응답", "response", "포맷", "format"]
    },
    "chapter_7_integration": {
      "title": "시스템 통합 및 검증",
      "primary_keywords": ["테스트", "test", "검증", "verification", "통합", "integration", "시뮬레이션", "simulation"],
      "secondary_keywords": ["유닛", "unit", "E2E", "성능", "performance", "벤치마크", "benchmark"]
    },
    "chapter_8_safety": {
      "title": "안정성 및 오류 처리",
      "primary_keywords": ["안전", "safety", "오류", "error", "예외", "exception", "복구", "recovery"],
      "secondary_keywords": ["로깅", "logging", "모니터링", "monitoring", "알림", "alert", "백업", "backup"]
    }
  },
  "domain_specific_terms": {
    "generic_to_domain": {
      "모듈": "모듈(module)",
      "처리": "처리(processing)",
      "설정": "설정(configuration)",
      "연결": "연결(connection)",
      "입력": "입력(input)",
      "출력": "출력(output)"
    }
  },
  "detection_hints": {
    "ros2_indicators": ["ROS", "ros2", "node", "topic", "service", "action", "msg", "launch"],
    "ai_ml_indicators": ["PyTorch", "TensorFlow", "model", "training", "inference", "neural", "deep learning"],
    "physics_indicators": ["quantum", "particle", "field", "energy", "wave", "equation"],
    "biotech_indicators": ["gene", "protein", "cell", "DNA", "RNA", "assay", "sequencing"]
  }
}
```

---

## Usage

### Domain Detection

Use keyword frequency analysis to detect research domain:

```
1. Count keyword occurrences in research notes
2. Calculate domain scores:
   - primary_keyword * 3 points
   - secondary_keyword * 1 point
3. Select domain with highest score
4. If score difference < 30%, use GENERAL
```

### Chapter Mapping

Use chapter keywords to map content to chapters:

```
1. For each file, calculate chapter relevance scores
2. Match file headers/keywords to chapter keywords
3. Assign files to chapters with highest scores
4. Calculate sufficiency score (0-100) per chapter
5. Skip chapters with score < 30
```

### Domain-Specific Term Substitution

Replace generic terms with domain-specific terms in generated reports:

```
ROS2: "모듈" → "노드(node)"
AI/ML: "모듈" → "모듈/레이어(module/layer)"
GENERAL: "모듈" → "모듈(module)"
```

---

## File Naming Convention

Keyword files follow the pattern: `{domain_normalized}_keywords.json`

Normalization rules:
- Lowercase domain name
- Replace "/" with "_"
- Examples:
  - "ROS2" → "ros2_keywords.json"
  - "AI/ML" → "ai_ml_keywords.json"
  - "GENERAL" → "general_keywords.json"
