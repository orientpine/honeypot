import datetime
import json
import logging
import traceback
import typing as t
from logging import getLogger
from xml.parsers.expat import ExpatError

import httpx
import requests
import re
import xmltodict

logger = logging.getLogger("mcp-kipris")


def mask_sensitive_data(url: str) -> str:
    """URL에서 민감한 키 정보(ServiceKey, accessKey)를 마스킹합니다."""
    if not url:
        return url
    # ServiceKey 또는 accessKey 파라미터 값을 마스킹
    # 예: ServiceKey=abcde12345 -> ServiceKey=****
    return re.sub(r"(ServiceKey|accessKey)=([^&]+)", r"\1=****", url)


def get_nested_key_value(dictionary: t.Dict, nested_key: str, sep: str = ".", default_value=None) -> t.Any:
    if dictionary is None:
        return default_value

    try:
        current = dictionary
        for keys in nested_key.split(sep):
            if isinstance(current, dict) and keys in current:
                current = current[keys]
            else:
                return default_value
        return current if current is not None else default_value
    except Exception as e:
        logger.error("get_nested_key_value error — input: %s, path: %s", dictionary, nested_key)
        logger.error(e)
        return default_value


def get_response(url: str) -> t.Dict:
    """_summary_
        url을 입력 받아서 해당 url에 대한 get 요청을 보내고, 결과를 json으로 반환함.
    Args:
        url (str): url 주소

    Returns:
        t.Any: url에 대한 get 요청 결과 json
    """

    try:
        key_str = datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S")

        # 타임아웃 설정 (연결 시도: 60초, 응답 대기: 600초)
        # 총 타임아웃: 10분 (MCP 서버 타임아웃보다 길게 설정)
        logger.info(f"HTTP 요청 시작: {mask_sensitive_data(url)}")
        start_time = datetime.datetime.now()

        response = None  # Initialize to avoid scope issues
        response_text = ""
        with requests.Session() as sess:
            response = sess.get(url, timeout=(60, 600))
            response.raise_for_status()
            response_text = response.text

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logger.info(f"HTTP 요청 완료: {elapsed_time:.2f}초 소요")

        try:
            dict_type = xmltodict.parse(response_text)
        except ExpatError:
            raise Exception(f"[async] response is not xml. check query url [{url}] response [{response_text[:100]}]")

        json_data = dict(dict_type)
        result_header = get_nested_key_value(json_data, "response.header", default_value="")
        logger.info("__kipris__:[%s]:[%s] :result header : [%s]", key_str, mask_sensitive_data(url)[24:], result_header)
        return json_data

    except requests.exceptions.Timeout as e:
        logger.error(f"타임아웃 발생 (60초 연결 시도, 600초 응답 대기): {str(e)}")
        return {}
    except requests.exceptions.ConnectionError as e:
        logger.error("connection Error:[%s]", e)
        return {}
    except requests.exceptions.HTTPError as e:
        logger.error("http Error:[%s]", e)
        return {}
    except requests.exceptions.RequestException as e:
        logger.error("request Exception Error:[%s]", e)
        return {}
    except Exception as e:
        logger.error("Exception Error:[%s]", e)
        logger.error("url error [%s]", mask_sensitive_data(url))
        if response is not None:
            logger.error("response error [%s]", response)
        logger.error(traceback.format_exc())
        return {}


async def get_response_async(url: str) -> t.Dict:
    """비동기 방식으로 url을 입력 받아 GET 요청을 보내고, 결과를 json으로 반환함."""
    response_text = ""
    response = None
    try:
        key_str = datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S")
        logger.info(f"[async] HTTP 요청 시작: {mask_sensitive_data(url)}")
        start_time = datetime.datetime.now()

        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=60.0)) as client:
            response = await client.get(url)
            response.raise_for_status()
            response_text = response.text

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logger.info(f"[async] HTTP 요청 완료: {elapsed_time:.2f}초 소요")

        try:
            dict_type = xmltodict.parse(response_text)
        except ExpatError:
            raise Exception(
                f"response is not xml. check query url [{mask_sensitive_data(url)}] response [{response_text[:100]}]"
            )
        json_data = dict(dict_type)
        result_header = get_nested_key_value(json_data, "response.header", default_value="")
        logger.info(
            "__kipris__:[async][%s]:[%s] :result header : [%s]", key_str, mask_sensitive_data(url)[24:], result_header
        )
        return json_data

    except httpx.TimeoutException as e:
        logger.error(f"[async] 타임아웃 발생 (60초 연결 시도, 600초 응답 대기): {str(e)}")
        return {}
    except httpx.RequestError as e:
        logger.error(f"[async] 요청 예외 발생: {e}")
        return {}
    except Exception as e:
        logger.error(f"[async] Exception Error:[{e}]")
        logger.error(f"[async] url error [{mask_sensitive_data(url)}]")
        if response is not None:
            logger.error(f"[async] response error [{response}]")
        logger.error(traceback.format_exc())
        return {}
