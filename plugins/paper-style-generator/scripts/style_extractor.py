#!/usr/bin/env python3
"""
Style Pattern Extractor for Academic Papers

Markdown 논문 컬렉션에서 스타일 패턴을 추출합니다.

Usage:
    python style_extractor.py --input-dir ./processed/ --output-file style_analysis.json

Analysis includes:
    - Voice/Tense ratios per section
    - Sentence structure patterns
    - High-frequency vocabulary
    - Narrative flow patterns
    - Field characteristics
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics


# 수동태 동사 패턴
PASSIVE_PATTERNS = [
    r'\b(was|were|been|being|is|are)\s+\w+ed\b',
    r'\b(was|were|been|being|is|are)\s+\w+en\b',
]

# 능동태 "We" 시작 패턴
WE_PATTERNS = [
    r'^We\s+\w+',
    r'^we\s+\w+',
]

# 시제 패턴
PAST_TENSE_PATTERNS = [
    r'\b\w+ed\b',
    r'\bwas\b', r'\bwere\b',
    r'\bhad\b',
]

PRESENT_TENSE_PATTERNS = [
    r'\bis\b', r'\bare\b', r'\bhas\b', r'\bhave\b',
    r'\b\w+s\b',  # 3인칭 단수
]

# 고빈도 동사 목록 (학술 논문)
ACADEMIC_VERBS = [
    'demonstrated', 'showed', 'revealed', 'achieved', 'obtained',
    'validated', 'confirmed', 'established', 'determined', 'measured',
    'detected', 'observed', 'found', 'identified', 'characterized',
    'developed', 'designed', 'constructed', 'fabricated', 'prepared',
    'analyzed', 'evaluated', 'assessed', 'compared', 'tested',
    'optimized', 'enhanced', 'improved', 'increased', 'reduced',
    'enabled', 'facilitated', 'allowed', 'provided', 'offered',
    'suggests', 'indicates', 'implies', 'supports', 'demonstrates',
]

# 연결어/전환어
TRANSITION_PHRASES = {
    'introduction': [
        'Here, we present', 'Here, we report', 'Here, we describe',
        'In this study', 'In this work', 'To address this',
        'Addressing', 'To meet this need',
    ],
    'methods': [
        'Briefly,', 'Following', 'According to', 'As previously described',
    ],
    'results': [
        'We first', 'We next', 'We then', 'Finally,',
        'To further', 'To validate', 'To demonstrate',
    ],
    'discussion': [
        'Our results', 'These findings', 'This study',
        'One limitation', 'Future work', 'In conclusion',
    ],
}

# 헷징 표현
HEDGING_EXPRESSIONS = [
    'may', 'might', 'could', 'would',
    'suggests', 'indicates', 'implies', 'appears',
    'possibly', 'potentially', 'likely', 'presumably',
    'it is possible', 'it is likely',
]


def extract_sections(content: str) -> Dict[str, str]:
    """Markdown에서 각 섹션 추출"""
    sections = {}
    
    # 섹션 마커 기반 추출
    section_pattern = r'<!-- SECTION_START: (\w+) -->(.*?)<!-- SECTION_END: \1 -->'
    matches = re.findall(section_pattern, content, re.DOTALL)
    
    if matches:
        for section_name, section_content in matches:
            sections[section_name.lower()] = section_content.strip()
    else:
        # 마커 없는 경우 헤더 기반 추출
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            header_match = re.match(r'^##\s+(\w+)', line)
            if header_match:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = header_match.group(1).lower()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
    
    return sections


def analyze_voice(text: str) -> Dict[str, float]:
    """능동태/수동태 비율 분석"""
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {'active': 0.5, 'passive': 0.5}
    
    passive_count = 0
    active_count = 0
    
    for sentence in sentences:
        is_passive = any(re.search(p, sentence, re.IGNORECASE) for p in PASSIVE_PATTERNS)
        if is_passive:
            passive_count += 1
        else:
            active_count += 1
    
    total = passive_count + active_count
    if total == 0:
        return {'active': 0.5, 'passive': 0.5}
    
    return {
        'active': round(active_count / total, 2),
        'passive': round(passive_count / total, 2)
    }


def analyze_tense(text: str) -> Dict[str, float]:
    """시제 분석"""
    past_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in PAST_TENSE_PATTERNS)
    present_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in PRESENT_TENSE_PATTERNS)
    
    total = past_count + present_count
    if total == 0:
        return {'past': 0.5, 'present': 0.5}
    
    return {
        'past': round(past_count / total, 2),
        'present': round(present_count / total, 2)
    }


def analyze_we_usage(text: str) -> Dict[str, any]:
    """'We' 문장 시작 비율 분석"""
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {'ratio': 0, 'count': 0, 'total': 0}
    
    we_count = sum(1 for s in sentences if re.match(r'^We\s', s))
    
    return {
        'ratio': round(we_count / len(sentences), 2),
        'count': we_count,
        'total': len(sentences)
    }


def extract_high_freq_verbs(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
    """고빈도 동사 추출"""
    words = re.findall(r'\b\w+\b', text.lower())
    verb_counts = Counter()
    
    for word in words:
        if word in ACADEMIC_VERBS:
            verb_counts[word] += 1
    
    return verb_counts.most_common(top_n)


def extract_transition_phrases(text: str, section: str) -> List[Dict]:
    """연결어/전환어 추출"""
    found_phrases = []
    
    phrases_to_check = TRANSITION_PHRASES.get(section, [])
    
    for phrase in phrases_to_check:
        count = text.count(phrase)
        if count > 0:
            found_phrases.append({
                'phrase': phrase,
                'count': count
            })
    
    return sorted(found_phrases, key=lambda x: x['count'], reverse=True)


def analyze_hedging(text: str) -> Dict:
    """헷징 표현 분석"""
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words)
    
    hedging_count = sum(1 for word in words if word in HEDGING_EXPRESSIONS)
    
    return {
        'ratio': round(hedging_count / total_words, 4) if total_words > 0 else 0,
        'count': hedging_count
    }


def analyze_measurement_format(text: str) -> Dict:
    """측정값 표기 형식 분석"""
    formats = {}
    
    # 온도
    temp_patterns = [
        (r'\d+\s*°C', 'X °C (space)'),
        (r'\d+°C', 'X°C (no space)'),
    ]
    for pattern, fmt in temp_patterns:
        if re.search(pattern, text):
            formats['temperature'] = fmt
            break
    
    # 농도
    conc_patterns = [
        (r'\d+\s+mg/mL', 'X mg/mL (space)'),
        (r'\d+mg/mL', 'Xmg/mL (no space)'),
    ]
    for pattern, fmt in conc_patterns:
        if re.search(pattern, text):
            formats['concentration'] = fmt
            break
    
    # 원심분리
    cent_patterns = [
        (r'\d+\s*×\s*g', 'X × g (spaces)'),
        (r'\d+×g', 'X×g (no spaces)'),
        (r'\d+\s*x\s*g', 'X x g'),
    ]
    for pattern, fmt in cent_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            formats['centrifugation'] = fmt
            break
    
    return formats


def analyze_citation_style(text: str) -> Dict:
    """인용 스타일 분석"""
    # 숫자 인용 [1], [2,3], [4-7]
    numbered = len(re.findall(r'\[\d+(?:[,\-]\d+)*\]', text))
    
    # 저자-연도 (Author, Year)
    author_year = len(re.findall(r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}\)', text))
    
    # 상첨자
    superscript = len(re.findall(r'<sup>\d+</sup>', text))
    
    styles = {'numbered': numbered, 'author_year': author_year, 'superscript': superscript}
    dominant = max(styles, key=styles.get)
    
    return {
        'format': dominant if styles[dominant] > 0 else 'unknown',
        'counts': styles
    }


def analyze_section(section_name: str, content: str) -> Dict:
    """섹션별 상세 분석"""
    analysis = {
        'voice': analyze_voice(content),
        'tense': analyze_tense(content),
        'word_count': len(content.split()),
        'sentence_count': len(re.split(r'[.!?]', content)),
    }
    
    # 섹션별 추가 분석
    if section_name == 'results':
        analysis['we_usage'] = analyze_we_usage(content)
    
    if section_name == 'methods':
        analysis['measurement_format'] = analyze_measurement_format(content)
    
    # 공통 분석
    analysis['high_freq_verbs'] = extract_high_freq_verbs(content)
    analysis['transitions'] = extract_transition_phrases(content, section_name)
    analysis['hedging'] = analyze_hedging(content)
    
    return analysis


def analyze_paper(md_path: Path) -> Dict:
    """단일 논문 분석"""
    content = md_path.read_text(encoding='utf-8')
    sections = extract_sections(content)
    
    analysis = {
        'file': str(md_path),
        'sections_found': list(sections.keys()),
        'section_analysis': {}
    }
    
    for section_name, section_content in sections.items():
        if section_content.strip():
            analysis['section_analysis'][section_name] = analyze_section(
                section_name, section_content
            )
    
    # 전체 문서 분석
    analysis['citation_style'] = analyze_citation_style(content)
    
    return analysis


def aggregate_analyses(analyses: List[Dict]) -> Dict:
    """여러 논문 분석 결과 집계"""
    aggregated = {
        'paper_count': len(analyses),
        'sections': {},
        'citation_style': {},
        'field_characteristics': {}
    }
    
    # 섹션별 집계
    section_data = {}
    
    for analysis in analyses:
        for section, data in analysis.get('section_analysis', {}).items():
            if section not in section_data:
                section_data[section] = {
                    'voice_active': [],
                    'voice_passive': [],
                    'tense_past': [],
                    'tense_present': [],
                    'word_count': [],
                    'we_ratio': [],
                    'verbs': Counter(),
                }
            
            sd = section_data[section]
            sd['voice_active'].append(data['voice']['active'])
            sd['voice_passive'].append(data['voice']['passive'])
            sd['tense_past'].append(data['tense']['past'])
            sd['tense_present'].append(data['tense']['present'])
            sd['word_count'].append(data['word_count'])
            
            if 'we_usage' in data:
                sd['we_ratio'].append(data['we_usage']['ratio'])
            
            for verb, count in data.get('high_freq_verbs', []):
                sd['verbs'][verb] += count
    
    # 집계 결과 계산
    for section, data in section_data.items():
        aggregated['sections'][section] = {
            'voice': {
                'active': {
                    'mean': round(statistics.mean(data['voice_active']), 2),
                    'std': round(statistics.stdev(data['voice_active']), 2) if len(data['voice_active']) > 1 else 0
                },
                'passive': {
                    'mean': round(statistics.mean(data['voice_passive']), 2),
                    'std': round(statistics.stdev(data['voice_passive']), 2) if len(data['voice_passive']) > 1 else 0
                }
            },
            'tense': {
                'past': {
                    'mean': round(statistics.mean(data['tense_past']), 2),
                    'std': round(statistics.stdev(data['tense_past']), 2) if len(data['tense_past']) > 1 else 0
                },
                'present': {
                    'mean': round(statistics.mean(data['tense_present']), 2),
                    'std': round(statistics.stdev(data['tense_present']), 2) if len(data['tense_present']) > 1 else 0
                }
            },
            'word_count': {
                'mean': round(statistics.mean(data['word_count'])),
                'std': round(statistics.stdev(data['word_count'])) if len(data['word_count']) > 1 else 0
            },
            'high_freq_verbs': data['verbs'].most_common(10),
            'sample_size': len(data['voice_active'])
        }
        
        if data['we_ratio']:
            aggregated['sections'][section]['we_usage'] = {
                'mean': round(statistics.mean(data['we_ratio']), 2),
                'std': round(statistics.stdev(data['we_ratio']), 2) if len(data['we_ratio']) > 1 else 0
            }
    
    # 인용 스타일 집계
    citation_counts = Counter()
    for analysis in analyses:
        style = analysis.get('citation_style', {}).get('format', 'unknown')
        citation_counts[style] += 1
    
    aggregated['citation_style'] = {
        'dominant': citation_counts.most_common(1)[0][0] if citation_counts else 'unknown',
        'distribution': dict(citation_counts)
    }
    
    return aggregated


def calculate_confidence(aggregated: Dict) -> Dict:
    """신뢰도 계산"""
    confidence = {
        'overall': 0,
        'by_section': {},
        'factors': {}
    }
    
    paper_count = aggregated['paper_count']
    
    # 샘플 크기 신뢰도 (10편 기준)
    sample_confidence = min(paper_count / 10, 1.0)
    confidence['factors']['sample_size'] = round(sample_confidence, 2)
    
    # 섹션별 신뢰도
    section_confidences = []
    
    for section, data in aggregated['sections'].items():
        # 일관성 (std가 낮을수록 높음)
        voice_consistency = 1 - min(data['voice']['active'].get('std', 0), 0.3) / 0.3
        tense_consistency = 1 - min(data['tense']['past'].get('std', 0), 0.3) / 0.3
        
        section_conf = (voice_consistency + tense_consistency) / 2 * sample_confidence
        confidence['by_section'][section] = round(section_conf, 2)
        section_confidences.append(section_conf)
    
    # 전체 신뢰도
    if section_confidences:
        confidence['overall'] = round(statistics.mean(section_confidences), 2)
    
    return confidence


def generate_confidence_report(aggregated: Dict, confidence: Dict) -> str:
    """신뢰도 리포트 생성"""
    report = f"""# 스타일 분석 신뢰도 리포트

## 요약
- **전체 신뢰도**: {confidence['overall'] * 100:.1f}%
- **분석 논문 수**: {aggregated['paper_count']}편

## 섹션별 신뢰도

| 섹션 | 신뢰도 | Voice 일관성 | Tense 일관성 |
|------|--------|-------------|-------------|
"""
    
    for section, conf in confidence['by_section'].items():
        section_data = aggregated['sections'].get(section, {})
        voice_std = section_data.get('voice', {}).get('active', {}).get('std', 0)
        tense_std = section_data.get('tense', {}).get('past', {}).get('std', 0)
        
        voice_status = "높음" if voice_std < 0.1 else "중간" if voice_std < 0.2 else "낮음"
        tense_status = "높음" if tense_std < 0.1 else "중간" if tense_std < 0.2 else "낮음"
        
        report += f"| {section.title()} | {conf * 100:.0f}% | {voice_status} | {tense_status} |\n"
    
    report += """
## 주요 패턴

"""
    
    for section, data in aggregated['sections'].items():
        voice = data.get('voice', {})
        tense = data.get('tense', {})
        
        report += f"### {section.title()}\n"
        report += f"- Voice: {voice.get('active', {}).get('mean', 0)*100:.0f}% active / "
        report += f"{voice.get('passive', {}).get('mean', 0)*100:.0f}% passive\n"
        report += f"- Tense: {tense.get('past', {}).get('mean', 0)*100:.0f}% past / "
        report += f"{tense.get('present', {}).get('mean', 0)*100:.0f}% present\n"
        
        if 'we_usage' in data:
            report += f"- 'We' 시작 비율: {data['we_usage'].get('mean', 0)*100:.0f}%\n"
        
        report += "\n"
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Extract style patterns from academic papers"
    )
    parser.add_argument(
        "--input-dir", "-i",
        type=Path,
        required=True,
        help="Directory containing processed Markdown files"
    )
    parser.add_argument(
        "--output-file", "-o",
        type=Path,
        default=Path("style_analysis.json"),
        help="Output JSON file (default: style_analysis.json)"
    )
    parser.add_argument(
        "--confidence-report",
        type=Path,
        default=Path("confidence_report.md"),
        help="Confidence report file (default: confidence_report.md)"
    )
    parser.add_argument(
        "--depth",
        choices=["shallow", "medium", "deep"],
        default="deep",
        help="Analysis depth (default: deep)"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return 1
    
    # Markdown 파일 수집
    md_files = list(args.input_dir.glob("*.md"))
    md_files = [f for f in md_files if f.name not in ['conversion_report.json', 'confidence_report.md']]
    
    print(f"Found {len(md_files)} Markdown files")
    print(f"Analysis depth: {args.depth}")
    print("-" * 50)
    
    # 각 논문 분석
    analyses = []
    for i, md_path in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] Analyzing: {md_path.name}")
        analysis = analyze_paper(md_path)
        analyses.append(analysis)
        print(f"  Sections: {', '.join(analysis['sections_found'])}")
    
    print("-" * 50)
    
    # 집계
    aggregated = aggregate_analyses(analyses)
    
    # 신뢰도 계산
    confidence = calculate_confidence(aggregated)
    
    # 결과 저장
    result = {
        'aggregated': aggregated,
        'confidence': confidence,
        'individual_analyses': analyses
    }
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis saved: {args.output_file}")
    
    # 신뢰도 리포트 생성
    report = generate_confidence_report(aggregated, confidence)
    args.confidence_report.write_text(report, encoding='utf-8')
    print(f"Confidence report saved: {args.confidence_report}")
    
    print(f"\nOverall confidence: {confidence['overall'] * 100:.1f}%")
    
    return 0


if __name__ == "__main__":
    exit(main())
