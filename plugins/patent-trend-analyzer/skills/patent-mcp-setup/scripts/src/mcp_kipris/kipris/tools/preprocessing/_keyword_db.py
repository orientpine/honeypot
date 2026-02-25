"""[GJ] Consolidated keyword database for patent preprocessing tools.

Merges keyword patterns from 5 scattered files into a single structured database.
Supports Korean, English, and Japanese keywords.
"""

# 1. PROCESSING_LAYER_KEYWORDS - dict[str, dict[str, list[str]]]
# Keys: "OnSensor", "OnDevice", "Cloud"
# Sub-keys: "en", "ko", "ja"
# Values: list of keyword strings
# Include ALL keywords from us_patent_classifier.py EXTENDED_KEYWORDS["processing_layer"],
# patent_processor.py LAYER_KEYWORDS, and jp_keywords.py PROCESSING_LAYER_KEYWORDS

PROCESSING_LAYER_KEYWORDS = {
    "OnSensor": {
        "en": [
            "on-sensor", "onsensor", "in-sensor", "sensor-level",
            "near-sensor", "image sensor", "vision sensor", "smart sensor",
            "sensor processing", "sensor node", "CIS", "CMOS image",
            "pixel-level", "pixel level", "in-pixel", "focal plane",
            "imaging device", "camera sensor", "optical sensor",
            "lidar sensor", "radar sensor", "sensor fusion",
        ],
        "ko": [
            "뉴로모픽", "시냅스", "멤리스터", "아날로그 연산",
            "in-memory", "저전력 센서", "센서 퓨전", "MCU", "마이크로컨트롤러",
            "광학 신경망", "스파이킹", "저전력", "초저전력",
            "아날로그", "센서", "광학", "IoT", "사물인터넷",
            "바이오", "웨어러블", "에너지 효율", "펄스",
        ],
        "ja": [
            "センサー", "センサ", "イメージセンサ", "ピクセル", "画素",
            "撮像素子", "撮像装置", "CMOS", "CIS", "フォーカルプレーン",
            "センサー内", "オンセンサ", "ニアセンサ", "光学", "視覚センサ",
        ],
    },
    "OnDevice": {
        "en": [
            "on-device", "ondevice", "edge device", "edge computing", "edge AI",
            "mobile device", "embedded", "IoT", "MCU", "microcontroller",
            "wearable", "smartphone", "portable", "local processing",
            "neural network accelerator", "neural accelerator", "NPU",
            "neural processing unit", "hardware accelerator", "AI accelerator",
            "AI chip", "neural chip", "FPGA", "ASIC",
            "systolic array", "tensor processing", "processing-in-memory",
            "near-memory", "computational memory",
        ],
        "ko": [
            "NPU", "엣지", "임베디드", "가속기", "모바일",
            "온디바이스", "FPGA", "ASIC", "SoC",
            "뉴럴 프로세서", "뉴럴 엔진", "AI 칩",
            "하드웨어 가속", "전용 프로세서", "하드웨어",
            "칩", "프로세서", "연산기", "병렬", "실시간",
            "디바이스", "단말", "로컬", "오프라인",
        ],
        "ja": [
            "ハードウェア", "回路", "集積回路", "アクセラレータ",
            "加速器", "プロセッサ", "処理装置", "演算装置",
            "チップ", "半導体", "FPGA", "ASIC", "NPU", "TPU",
            "ニューラルプロセッサ", "AIチップ", "シストリック",
            "データフロー", "パイプライン", "メモリ", "インメモリ",
            "エッジ", "エッジデバイス", "組み込み", "オンデバイス",
            "モバイル", "端末", "低消費電力", "省電力",
        ],
    },
    "Cloud": {
        "en": [
            "cloud", "server", "datacenter", "data center", "distributed",
            "cluster", "GPU farm", "TPU pod", "remote processing",
            "large scale machine learning", "HPC", "multi-GPU",
        ],
        "ko": [
            "클라우드", "서버", "데이터센터", "분산",
            "다중 GPU", "멀티 GPU", "GPU 클러스터",
            "고성능 컴퓨팅", "원격", "호스팅",
        ],
        "ja": [
            "クラウド", "データセンター", "サーバ", "サーバー",
            "分散", "分散処理", "HPC", "高性能計算",
            "GPUクラスタ", "大規模並列",
        ],
    },
}

# 2. MODEL_SCALE_KEYWORDS - same structure
# Keys: "TinyML", "Lightweight", "LLM_VLM"

MODEL_SCALE_KEYWORDS = {
    "TinyML": {
        "en": [
            "tinyml", "tiny model", "ultra-light", "ultralight", "sub-MB",
            "kilobyte", "8-bit", "4-bit", "binary neural", "ternary neural",
            "MCU-based", "cortex-m", "RISC-V", "microcontroller",
            "ultra low power", "ultra-low-power",
        ],
        "ko": [],
        "ja": [
            "超小型", "マイコン", "マイクロコントローラ", "MCU",
            "組み込みAI", "バイナリニューラル", "二値化", "三値化",
            "超低消費電力", "キーワード検出", "常時オン",
        ],
    },
    "Lightweight": {
        "en": [
            "lightweight", "light-weight", "compact", "efficient", "small model",
            "mobilenet", "efficientnet", "squeezenet", "shufflenet",
            "compression", "model compression", "sparse", "sparsity",
            "pruning", "network pruning", "weight pruning",
            "quantization", "quantize", "quantized",
            "distillation", "knowledge distillation",
            "mixed precision", "reduced precision", "low-bit",
            "depthwise", "separable convolution", "bottleneck",
        ],
        "ko": [
            "경량화", "양자화", "가지치기", "압축",
            "지식증류", "모델 압축", "희소화",
        ],
        "ja": [
            "軽量", "軽量化", "コンパクト", "小型化",
            "圧縮", "モデル圧縮", "プルーニング", "枝刈り",
            "スパース", "量子化", "蒸留", "知識蒸留",
            "効率化", "最適化", "NAS", "MobileNet", "EfficientNet",
        ],
    },
    "LLM_VLM": {
        "en": [
            "large language", "LLM", "VLM", "vision language", "foundation model",
            "transformer", "GPT", "BERT", "billion parameter",
            "pre-trained", "pretrained", "generative AI",
            "language model", "vision transformer", "ViT", "CLIP",
            "diffusion model", "multi-modal", "multimodal",
            "autoregressive", "self-attention", "decoder-only",
            "text generation", "image generation",
        ],
        "ko": [
            "거대 언어", "대규모 언어", "대형 언어", "LLM",
            "GPT", "ChatGPT", "챗봇", "생성형", "생성 AI",
            "언어 모델", "트랜스포머", "BERT",
            "자연어 처리", "대규모 모델", "파운데이션 모델",
            "VLM", "비전 언어", "멀티모달", "CLIP", "DALL-E",
        ],
        "ja": [
            "大規模言語モデル", "大規模モデル", "言語モデル", "LLM",
            "トランスフォーマー", "Transformer", "アテンション",
            "生成モデル", "生成AI", "拡散モデル",
            "GPT", "BERT", "CLIP", "ViT",
            "マルチモーダル", "事前学習", "ファインチューニング",
            "基盤モデル",
        ],
    },
}

# 3. FUNCTION_KEYWORDS - same structure
# Keys: "Adaptive_Learning", "Inference", "Training"

FUNCTION_KEYWORDS = {
    "Adaptive_Learning": {
        "en": [
            "adaptive learning", "continual learning", "continuous learning",
            "incremental learning", "lifelong learning", "online learning",
            "self-learning", "self-adaptive", "domain adaptation",
            "transfer learning", "meta-learning", "few-shot", "zero-shot",
            "personalized", "personalization",
        ],
        "ko": [
            "전이학습", "메타학습", "적응", "도메인 적응",
            "파인튜닝", "증분학습", "연속학습",
            "온라인 학습", "강화학습", "자기지도",
        ],
        "ja": [
            "転移学習", "ドメイン適応", "継続学習", "連続学習",
            "増分学習", "フューショット", "ゼロショット",
            "メタ学習", "適応学習", "オンライン学習",
            "ファインチューニング",
        ],
    },
    "Inference": {
        "en": [
            "inference", "prediction", "recognition", "detection",
            "classification", "classify", "forward pass", "deployment",
            "runtime", "real-time", "low-latency", "fast inference",
            "object detection", "image classification",
            "semantic segmentation", "feature extraction",
        ],
        "ko": [
            "추론", "CNN", "RNN", "LSTM", "GRU",
            "어텐션", "컨볼루션", "풀링",
            "분류", "검출", "인식", "예측", "세그멘테이션",
        ],
        "ja": [
            "推論", "推論処理", "推論装置", "予測", "認識",
            "検出", "分類", "物体検出",
            "セグメンテーション", "デプロイ", "リアルタイム",
        ],
    },
    "Training": {
        "en": [
            "training", "backpropagation", "gradient", "gradient descent",
            "loss function", "weight update",
            "supervised", "unsupervised", "semi-supervised",
            "reinforcement learning", "federated learning",
            "neural network training", "model training",
            "contrastive learning", "self-supervised",
            "optimizer", "Adam", "SGD", "learning rate",
            "regularization", "dropout", "batch normalization",
        ],
        "ko": [
            "학습", "훈련", "역전파", "최적화",
            "손실함수", "그래디언트", "배치",
        ],
        "ja": [
            "学習", "訓練", "機械学習", "深層学習",
            "勾配", "誤差逆伝播", "最適化",
            "SGD", "Adam", "教師あり", "教師なし",
            "自己教師あり", "連合学習", "分散学習",
        ],
    },
}

# 4. DOMAIN_EXCLUSION_KEYWORDS - dict[str, list[str]]
# Keys: "DATA_ANALYTICS", "NLP_LANGUAGE", "MEDICAL_HEALTH", "SECURITY_AUTH", "RECOMMENDATION"
# Values: list of English keywords (case-insensitive matching)

DOMAIN_EXCLUSION_KEYWORDS = {
    "DATA_ANALYTICS": [
        "BIG DATA", "DATA WAREHOUSE", "ETL", "DATA PIPELINE",
        "DATA MINING", "DATABASE", "BUSINESS INTELLIGENCE",
    ],
    "NLP_LANGUAGE": [
        "NATURAL LANGUAGE", "NLP", "TEXT PROCESSING",
        "SPEECH RECOGNITION", "SPEECH SYNTHESIS", "MACHINE TRANSLATION",
        "CHATBOT", "DIALOGUE", "SUMMARIZATION",
    ],
    "MEDICAL_HEALTH": [
        "MEDICAL DIAGNOSIS", "PATIENT", "CLINICAL", "EHR",
        "ONCOLOGY", "PATHOLOGY", "RADIOLOGY", "DRUG DISCOVERY",
        "HEALTHCARE", "DISEASE",
    ],
    "SECURITY_AUTH": [
        "CYBERSECURITY", "ENCRYPTION", "AUTHENTICATION",
        "INTRUSION DETECTION", "MALWARE", "FRAUD DETECTION",
        "BLOCKCHAIN", "PRIVACY",
    ],
    "RECOMMENDATION": [
        "RECOMMENDATION SYSTEM", "COLLABORATIVE FILTERING",
        "AD TARGETING", "ADVERTISEMENT", "PERSONALIZATION",
    ],
}

# 5. IPC_MAPPINGS - dict[str, dict[str, str]]
# Two sub-dicts: "processing_layer" and "function"
# Keys: IPC code (compact, no spaces), Values: category name

IPC_MAPPINGS = {
    "processing_layer": {
        "G06N3/063": "OnDevice",
        "G06N3/065": "OnSensor",
        "G06N3/067": "OnSensor",
    },
    "function": {
        "G06N3/096": "Adaptive_Learning",
        "G06N3/098": "Adaptive_Learning",
        "G06N3/092": "Adaptive_Learning",
        "G06N3/094": "Adaptive_Learning",
        "G06N3/0985": "Adaptive_Learning",
        "G06N3/0895": "Adaptive_Learning",
        "G06N3/09": "Adaptive_Learning",
        "G06N3/0464": "Inference",
        "G06N3/045": "Inference",
        "G06N3/0455": "Inference",
        "G06N3/0475": "Inference",
        "G06N3/042": "Inference",
        "G06N3/044": "Inference",
        "G06N3/0442": "Inference",
        "G06N3/0495": "Lightweight",
        "G06N3/08": "Training",
        "G06N3/082": "Training",
        "G06N3/084": "Training",
        "G06N3/088": "Training",
    },
}

# 6. SEARCH_IPC_CODES - list of IPC codes used for API search queries
SEARCH_IPC_CODES = [
    "G06N 3/096",  # Transfer learning
    "G06N 3/0464", # CNN
    "G06N 3/0495", # Quantization/Pruning
    "G06N 3/06",   # Hardware implementation (broad)
]

# 7. SEARCH_KEYWORDS - dict[str, list[str]] organized by language
SEARCH_KEYWORDS = {
    "en": ["embedded", "edge", "microprocessor", "NPU", "accelerator", "on-device", "TinyML"],
    "ko": ["임베디드", "엣지", "마이크로프로세서", "MCU"],
}

# 8. Helper functions

def get_all_keywords_flat(category_dict: dict, lang: str = None) -> list[str]:
    """Get all keywords from a category dict, optionally filtered by language."""
    result = []
    for category, lang_dict in category_dict.items():
        if lang:
            result.extend(lang_dict.get(lang, []))
        else:
            for l, keywords in lang_dict.items():
                result.extend(keywords)
    return list(set(result))


def get_keywords_for_category(category_dict: dict, category: str, lang: str = None) -> list[str]:
    """Get keywords for a specific category, optionally filtered by language."""
    if category not in category_dict:
        return []
    lang_dict = category_dict[category]
    if lang:
        return lang_dict.get(lang, [])
    result = []
    for l, keywords in lang_dict.items():
        result.extend(keywords)
    return result


def find_keyword_overlaps(keywords_a: list[str], keywords_b: list[str]) -> list[str]:
    """Find keywords that appear in both lists (case-insensitive)."""
    set_a = {k.lower() for k in keywords_a}
    set_b = {k.lower() for k in keywords_b}
    return sorted(set_a & set_b)


def classify_by_ipc(ipc_code: str) -> dict[str, str]:
    """Classify a patent by its IPC code.

    Returns dict with 'processing_layer' and 'function' keys.
    Values are category names or 'Unknown'.
    """
    # Normalize: remove spaces
    normalized = ipc_code.replace(" ", "")

    result = {"processing_layer": "Unknown", "function": "Unknown"}

    # Check from most specific to least specific
    for code, category in sorted(IPC_MAPPINGS["processing_layer"].items(), key=lambda x: -len(x[0])):
        if normalized.startswith(code) or normalized == code:
            result["processing_layer"] = category
            break

    for code, category in sorted(IPC_MAPPINGS["function"].items(), key=lambda x: -len(x[0])):
        if normalized.startswith(code) or normalized == code:
            result["function"] = category
            break

    return result


def classify_by_keywords(text: str, lang: str = "en") -> dict[str, str]:
    """Classify a patent title/abstract by keyword matching.

    Returns dict with 'processing_layer', 'model_scale', 'function' keys.
    """
    text_lower = text.lower()
    result = {"processing_layer": "Unknown", "model_scale": "Unknown", "function": "Unknown"}

    # Processing layer
    for category in ["OnSensor", "OnDevice", "Cloud"]:
        keywords = get_keywords_for_category(PROCESSING_LAYER_KEYWORDS, category, lang)
        if any(kw.lower() in text_lower for kw in keywords):
            result["processing_layer"] = category
            break

    # Model scale
    for category in ["TinyML", "Lightweight", "LLM_VLM"]:
        keywords = get_keywords_for_category(MODEL_SCALE_KEYWORDS, category, lang)
        if any(kw.lower() in text_lower for kw in keywords):
            result["model_scale"] = category
            break

    # Function (priority order: Adaptive > Inference > Training)
    for category in ["Adaptive_Learning", "Inference", "Training"]:
        keywords = get_keywords_for_category(FUNCTION_KEYWORDS, category, lang)
        if any(kw.lower() in text_lower for kw in keywords):
            result["function"] = category
            break

    return result


def check_domain_exclusion(title: str) -> str | None:
    """Check if a patent title matches any exclusion domain.

    Returns domain name if excluded, None if not excluded.
    """
    title_upper = title.upper()
    for domain, keywords in DOMAIN_EXCLUSION_KEYWORDS.items():
        if any(kw in title_upper for kw in keywords):
            return domain
    return None
