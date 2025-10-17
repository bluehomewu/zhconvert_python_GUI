# api_client.py
import requests
import json
from typing import Optional, Dict, Union


def fetch_service_info() -> Optional[Dict]:
    url = "https://api.zhconvert.org/service-info"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('data')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching service info: {e}")
        return None


def convert_text_online(payload: dict) -> Union[Dict, str]:
    """
    發送轉換請求。
    成功時回傳包含所有總結資訊的 data 物件 (dict)。
    失敗時回傳錯誤訊息 (str)。
    """
    url = "https://api.zhconvert.org/convert"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'ModularCustomTkinterApp/1.0 (Python)'
    }
    try:
        print("--- Sending Payload ---\n" +
              json.dumps(payload, indent=2, ensure_ascii=False) +
              "\n-----------------------")
        response = requests.post(url,
                                 json=payload,
                                 headers=headers,
                                 timeout=30)
        response.raise_for_status()
        result_data = response.json()

        if result_data.get('code') == 0:
            # --- 關鍵修改：回傳整個 data 物件 ---
            return result_data.get('data', {})
        else:
            return f"API 錯誤：{result_data.get('msg', '未知錯誤')}"

    except requests.exceptions.RequestException as e:
        return f"網路錯誤：{e}"
    except Exception as e:
        return f"未知錯誤：{e}"
