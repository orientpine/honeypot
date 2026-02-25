from typing import Any, Dict, List

import networkx as nx
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from mcp_kipris.kipris.api.korean.patent_detail_search_api import PatentDetailSearchAPI

patent_detail_search_api = PatentDetailSearchAPI()


async def get_patent_data(application_number: str) -> Dict[str, Any]:
    return await patent_detail_search_api.async_search(application_number)


def extract_keywords_llm(text: str) -> List[str]:
    llm = ChatOllama(model="exaone3.5:32b", base_url="http://192.168.0.11:11434")
    prompt = ChatPromptTemplate.from_template("""
    다음 텍스트는 특허의 요약 또는 청구항 내용입니다. 여기서 핵심적인 기술 키워드를 5~10개 추출해 주세요.
    출력은 JSON 배열 형식으로 주세요.

    텍스트:
    {text}

    출력 예시:
    ["플렉서블 디스플레이", "고분자 수지층", "박리 강도", "적층체"]
    """)
    chain = prompt | llm | JsonOutputParser()
    try:
        result = chain.invoke({"text": text})
        return result if isinstance(result, list) else []
    except Exception as e:
        print(f"❌ Keyword LLM extraction failed: {e}")
        return []


# --- Enhanced claim parsing for graph modeling ---
def extract_claim_components_llm(text: str) -> List[Dict[str, str]]:
    llm = ChatOllama(model="exaone3.5:7.8b", base_url="http://192.168.0.11:11434")
    prompt = ChatPromptTemplate.from_template("""
    다음은 특허 청구항입니다. 이 문장에서 핵심 기술 구성요소(component)와 그 속성(property)을 추출해서 JSON 배열로 정리해주세요. 가능한 한 명확한 기술 명칭과 특징적 수치를 포함해 주세요.

    청구항:
    {text}

    출력 형식 예시:
    [
        {{"component": "고분자 수지층", "property": "박리 강도"}},
        {{"component": "플렉서블 디스플레이 소자", "property": "적층 구조"}}
    ]
    """)
    chain = prompt | llm | JsonOutputParser()
    try:
        response = chain.invoke({"text": text})
        return response if isinstance(response, list) else []
    except Exception as e:
        print(f"LLM parsing failed: {e}")
        return []


def dict_to_graph(components: Dict[str, Any], graph: nx.Graph, patent_id: str) -> nx.Graph:
    for comp in components:
        component = comp.get("component", "").strip()
        if not component or component.lower() in {"component", "property"}:
            continue

        node = f"component:{component}"
        graph.add_node(node, label="component")
        graph.add_edge(patent_id, node)

        # 1. 단일 문자열 property 처리
        if "property" in comp and isinstance(comp["property"], str):
            prop = comp["property"].strip()
            if prop.lower() not in {"component", "property"}:
                prop_node = f"property:{prop}"
                graph.add_node(prop_node, label="property")
                graph.add_edge(node, prop_node)

        # 2. 딕셔너리 property 처리
        elif "property" in comp and isinstance(comp["property"], dict):
            for k, v in comp["property"].items():
                k_str = k.strip() if isinstance(k, str) else str(k)
                if isinstance(v, list):
                    for item in v:
                        item_str = str(item).strip()
                        if not k_str or not item_str or k_str.lower() in {"component", "property"}:
                            continue
                        prop_node = f"property:{k_str}: {item_str}"
                        graph.add_node(prop_node, label="property")
                        graph.add_edge(node, prop_node)
                else:
                    v_str = v.strip() if isinstance(v, str) else str(v)
                    if not k_str or not v_str or k_str.lower() in {"component", "property"}:
                        continue
                    prop_node = f"property:{k_str}: {v_str}"
                    graph.add_node(prop_node, label="property")
                    graph.add_edge(node, prop_node)

        # 3. 속성이 배열로 주어지는 properties 처리
        elif "properties" in comp and isinstance(comp["properties"], list):
            for prop_pair in comp["properties"]:
                attr = prop_pair.get("attribute", "").strip()
                value = prop_pair.get("value", "").strip()
                if not attr or not value or attr.lower() in {"component", "property"}:
                    continue
                prop_node = f"property:{attr}: {value}"
                graph.add_node(prop_node, label="property")
                graph.add_edge(node, prop_node)

    return graph


def compare_patents(patent_id1: str, patent_id2: str) -> Dict[str, Any]:
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    patent_data1, patent_data2 = loop.run_until_complete(
        asyncio.gather(get_patent_data(patent_id1), get_patent_data(patent_id2))
    )

    # Extract necessary information for comparison
    summary1 = patent_data1.get("abstract", "")
    summary2 = patent_data2.get("abstract", "")

    claims1 = patent_data1.get("claims", "")
    claims2 = patent_data2.get("claims", "")

    # Use a basic text similarity metric for demonstration (can be replaced with embedding model)
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([summary1, summary2])
    similarity_score = cosine_similarity(vectors[0], vectors[1])[0, 0]

    async def run_llm_extraction():
        return await asyncio.gather(
            asyncio.to_thread(extract_keywords_llm, summary1),
            asyncio.to_thread(extract_keywords_llm, summary2),
            asyncio.to_thread(extract_keywords_llm, claims1),
            asyncio.to_thread(extract_keywords_llm, claims2),
            asyncio.to_thread(extract_claim_components_llm, claims1),
            asyncio.to_thread(extract_claim_components_llm, claims2),
        )

    (keywords1, keywords2, claim_keywords1, claim_keywords2, components1, components2) = loop.run_until_complete(
        run_llm_extraction()
    )

    tech_similarity_score = extract_tech_similarity(summary1 + "\n" + claims1, summary2 + "\n" + claims2)

    G1 = nx.Graph()
    G2 = nx.Graph()
    G1.add_node(patent_id1)
    G2.add_node(patent_id2)
    for kw in keywords1:
        G1.add_node(kw)
        G1.add_edge(patent_id1, kw)
    for kw in keywords2:
        G2.add_node(kw)
        G2.add_edge(patent_id2, kw)

    # Parse components from claims
    G1 = dict_to_graph(components1, G1, patent_id1)
    G2 = dict_to_graph(components2, G2, patent_id2)

    # Extract IPC and applicant data
    ipc1 = patent_data1.get("ipc", [])
    ipc2 = patent_data2.get("ipc", [])
    applicants1 = patent_data1.get("applicants", [])
    applicants2 = patent_data2.get("applicants", [])

    ipc_codes1 = [entry.replace(" ", "")[:4] for entry in ipc1 if isinstance(entry, str)]
    ipc_codes2 = [entry.replace(" ", "")[:4] for entry in ipc2 if isinstance(entry, str)]

    applicant_names1 = [app.get("applicant_name", "") for app in applicants1]
    applicant_names2 = [app.get("applicant_name", "") for app in applicants2]

    # Add IPC and applicant nodes to graphs
    for code in ipc_codes1:
        node = f"ipc:{code}"
        G1.add_node(node, label="ipc")
        G1.add_edge(patent_id1, node)

    for code in ipc_codes2:
        node = f"ipc:{code}"
        G2.add_node(node, label="ipc")
        G2.add_edge(patent_id2, node)

    for name in applicant_names1:
        node = f"applicant:{name}"
        G1.add_node(node, label="applicant")
        G1.add_edge(patent_id1, node)

    for name in applicant_names2:
        node = f"applicant:{name}"
        G2.add_node(node, label="applicant")
        G2.add_edge(patent_id2, node)

    # Calculate similarity scores
    ipc_set1 = set(ipc_codes1)
    ipc_set2 = set(ipc_codes2)
    ipc_jaccard_sim = len(ipc_set1 & ipc_set2) / len(ipc_set1 | ipc_set2) if (ipc_set1 | ipc_set2) else 0.0

    applicant_set1 = set(applicant_names1)
    applicant_set2 = set(applicant_names2)
    applicant_jaccard_sim = (
        len(applicant_set1 & applicant_set2) / len(applicant_set1 | applicant_set2)
        if (applicant_set1 | applicant_set2)
        else 0.0
    )

    # Compare component names for Jaccard similarity
    comp_set1 = set([c["component"] for c in components1])
    comp_set2 = set([c["component"] for c in components2])
    component_jaccard_sim = len(comp_set1 & comp_set2) / len(comp_set1 | comp_set2) if (comp_set1 | comp_set2) else 0.0

    # Add claim keyword nodes and edges to the graphs
    for kw in claim_keywords1:
        G1.add_node(f"claim:{kw}")
        G1.add_edge(patent_id1, f"claim:{kw}")
    for kw in claim_keywords2:
        G2.add_node(f"claim:{kw}")
        G2.add_edge(patent_id2, f"claim:{kw}")

    # Compute Jaccard similarity for claim keywords
    claim_set1 = set(claim_keywords1)
    claim_set2 = set(claim_keywords2)
    claim_jaccard_sim = (
        len(claim_set1 & claim_set2) / len(claim_set1 | claim_set2) if (claim_set1 | claim_set2) else 0.0
    )

    # Compute Jaccard similarity between keyword sets
    set1 = set(keywords1)
    set2 = set(keywords2)
    jaccard_sim = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0.0

    graph1 = G1
    graph2 = G2
    nx.write_graphml(graph1, f"{patent_id1}.graphml")
    nx.write_graphml(graph2, f"{patent_id2}.graphml")

    return {
        "patents": {"source": patent_id1, "target": patent_id2},
        "summary_similarity": round(similarity_score, 4),
        "graph_similarity": {
            "abstract_keywords": round(jaccard_sim, 4),
            "claim_keywords": round(claim_jaccard_sim, 4),
            "claim_components": round(component_jaccard_sim, 4),
            "ipc_codes": round(ipc_jaccard_sim, 4),
            "applicants": round(applicant_jaccard_sim, 4),
        },
        "summaries": {patent_id1: summary1, patent_id2: summary2},
        "technical_similarity": round(tech_similarity_score, 4),
        "overall_similarity": round(
            0.2 * jaccard_sim
            + 0.2 * claim_jaccard_sim
            + 0.2 * component_jaccard_sim
            + 0.1 * ipc_jaccard_sim
            + 0.1 * applicant_jaccard_sim
            + 0.2 * tech_similarity_score,
            4,
        ),
    }


def extract_tech_similarity(text1: str, text2: str) -> float:
    prompt = ChatPromptTemplate.from_template("""
    특허 A 설명:
    {text1}

    특허 B 설명:
    {text2}

    두 특허는 기술적으로 얼마나 유사한가요?
    기술 분야, 문제 해결 방식, 핵심 구성 요소를 기준으로 0~100 점 사이의 숫자만 한 줄로 출력하세요.
    숫자 외에 다른 설명은 절대 하지 마세요.
    예시 출력: 75
    """)
    llm = ChatOllama(model="exaone3.5:32b", base_url="http://192.168.0.11:11434")
    chain = prompt | llm

    try:
        result = chain.invoke({"text1": text1, "text2": text2})
        import re

        match = re.search(r"\b(\d{1,3})\b", str(result))
        score = int(match.group(1)) if match else 0
        return max(0, min(score / 100, 1.0))  # normalize to 0~1
    except Exception as e:
        print(f"❌ extract_tech_similarity failed: {e}")
        return 0.0
