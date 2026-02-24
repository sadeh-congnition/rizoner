import requests
from typing import Optional, Dict, Any, List, Tuple


def fetch_threads(api_url: str) -> List[Dict[str, Any]]:
    response = requests.get(f"{api_url}/api/statement/threads")
    response.raise_for_status()
    return response.json()


def create_thread(api_url: str) -> Dict[str, Any]:
    response = requests.post(f"{api_url}/api/statement/threads")
    response.raise_for_status()
    return response.json()


def create_statement(
    api_url: str, thread_id: str, content: str, is_main: bool
) -> Dict[str, Any]:
    response = requests.post(
        f"{api_url}/api/statement/threads/{thread_id}/statements",
        json={"content": content, "is_main": is_main},
    )
    response.raise_for_status()
    return response.json()


def fetch_thread(api_url: str, thread_id: str) -> Optional[Dict[str, Any]]:
    response = requests.get(f"{api_url}/api/statement/threads/{thread_id}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def fetch_statements(api_url: str, thread_id: str) -> List[Dict[str, Any]]:
    response = requests.get(f"{api_url}/api/statement/threads/{thread_id}/statements")
    response.raise_for_status()
    return response.json()


def verify_llm_auth_connection(api_url: str) -> Dict[str, Any]:
    response = requests.post(f"{api_url}/api/configuration/test-llm-auth")
    response.raise_for_status()
    return response.json()


def check_llm_config(api_url: str) -> List[Dict[str, Any]]:
    response = requests.get(f"{api_url}/api/configuration/llm-config")
    response.raise_for_status()
    return response.json()


def save_llm_configs(api_url: str, configs: List[Tuple[str, str]]) -> None:
    for name, value in configs:
        resp = requests.post(
            f"{api_url}/api/configuration/llm-config",
            json={"name": name, "value": value},
        )
        resp.raise_for_status()
