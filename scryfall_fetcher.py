import traceback
import requests
import jsonpickle
import time
from typing import List

class ScryfallResponse:
    def __init__(self, data, was_successful=True, error_message=""):
        self.data: List = data
        self.was_successful: bool = was_successful
        self.error_message: str = error_message
        if error_message is not None and error_message != "":
            self.was_successful = False

class ScryfallFetcher:
    @staticmethod
    def fetch_data(url: str, raise_exceptions: bool) -> ScryfallResponse:
        data = []
        try:
            while True:
                response = requests.get(url)
                jsonpickled_response = None
                if "application/json" in response.headers['content-type']:
                    jsonpickled_response = jsonpickle.loads(response.text, safe=True)

                if not response.ok or jsonpickled_response is None:
                    error_message: str
                    if jsonpickled_response is not None \
                            and isinstance(jsonpickled_response, dict) \
                            and "details" in jsonpickled_response:
                        error_message = jsonpickled_response["details"]
                    else:
                        error_message = response.text

                    if raise_exceptions:
                        raise ConnectionError(error_message)
                    else:
                        return ScryfallResponse(data, was_successful=False, error_message=error_message)

                data.extend(jsonpickled_response["data"])
                if jsonpickled_response["has_more"]:
                    url = jsonpickled_response["next_page"]
                    time.sleep(.15)
                else:
                    break

        except Exception:
            if raise_exceptions:
                raise
            else:
                return ScryfallResponse(data, was_successful=False, error_message=traceback.format_exc())

        return ScryfallResponse(data)
