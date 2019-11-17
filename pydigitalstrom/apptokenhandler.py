from typing import Optional

from pydigitalstrom.requesthandler import DSRequestHandler
from pydigitalstrom.exceptions import DSException


class DSAppTokenHandler(DSRequestHandler):
    URL_APPTOKEN = (
        "/json/system/requestApplicationToken?applicationName=" "homeassistant"
    )
    URL_TEMPTOKEN = "/json/system/login?user={username}&password={password}"
    URL_ACTIVATE = (
        "/json/system/enableToken?applicationToken={apptoken}" "&token={temptoken}"
    )

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.username = username
        self.password = password

        super().__init__(host=host, port=port)

    async def request_apptoken(self) -> Optional[str]:
        """
        request a new app token from the server
        """
        # get fresh app token and activate it
        apptoken = await self.get_application_token_from_server()
        temptoken = await self.get_temp_token()
        if await self.activate_application_token(
            apptoken=apptoken, temptoken=temptoken
        ):
            return apptoken
        return None

    async def get_application_token_from_server(self) -> str:
        """
        request a fresh non-activated app token from the server
        """
        data = await self.raw_request(self.URL_APPTOKEN)
        if "result" not in data or "applicationToken" not in data["result"]:
            raise DSException("invalid api response")
        return data["result"]["applicationToken"]

    async def get_temp_token(self) -> str:
        """
        get an authenticated temp token
        """
        data = await self.raw_request(
            self.URL_TEMPTOKEN.format(username=self.username, password=self.password)
        )
        if "result" not in data or "token" not in data["result"]:
            raise DSException("invalid api response")
        return data["result"]["token"]

    async def activate_application_token(self, apptoken, temptoken) -> bool:
        """
        activate our app token using the authenticated temp token
        """
        await self.raw_request(
            self.URL_ACTIVATE.format(apptoken=apptoken, temptoken=temptoken)
        )
        return True
