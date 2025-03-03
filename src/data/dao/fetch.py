import traceback
from data.dto.shipment import Shipment
import json
from core.logger import logger
from core.playwright_runtime import PlaywrightRuntime

class FetchDao:
    def __init__(self, url):
        self.url = url
        self.playwright_runtime = PlaywrightRuntime()

    def get_data(self) -> list[Shipment] | None:
        raw_data = self._fetch_data()
        json_data = self._convert_shipment(raw_data)
        return json_data

    def _fetch_data(self) -> str:
        logger.info("request to web page")

        self.playwright_runtime.browser_page.goto(url=self.url, timeout=60000)
        self.playwright_runtime.browser_page.wait_for_selector("#json", timeout=60000)
        json_text = self.playwright_runtime.browser_page.inner_text("#json", timeout=60000)
        
        if json_text:
            logger.info("got data from web page")
            return json_text
        else:
            logger.warning("faild to get data from web page")
            return None

    def _convert_shipment(self, raw_data) -> list[Shipment] | None:
        try:
            raw_shipments = json.loads(raw_data)
            print(f"raw_shipments = {raw_shipments}")
            print(f"raw_shipments = {type(raw_shipments)}")
            data = [Shipment.model_validate(shipment) for shipment in raw_shipments['shipments']]
            logger.info("convert data to pydantic class")
            return data
        except Exception as e:
            logger.warning("faild to convert data to pydantic class")
            logger.warning(f"ERROR: {e}")
            traceback.print_exc()
            return None
