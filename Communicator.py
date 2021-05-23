import requests
import os
import datetime
import urllib.parse


class Communicator:
    """
    The program will fail if te refresh token is invalid.
    i.e. older than 6 months (as of 5/22/2021)

    It is up to the controller to ensure the latest refresh_token is placed into the database.
    """

    def __init__(self, refresh_token: str, refresh_token_timestamp: float):
        # API context
        self.api_base: str = 'https://api.kroger.com/v1/'
        self.api_token: str = 'connect/oauth2/token'
        self.location_id: str = os.getenv('kroger_api_location_id')
        # App credentials
        self.client_id = os.getenv('kroger_app_client_id')
        self.client_secret = os.getenv('kroger_app_client_secret')
        # Token vars
        self.refresh_token: str = refresh_token
        self.refresh_token_timestamp: float = refresh_token_timestamp
        self.access_token: str = ''             # updated in token_refresh
        self.access_token_timestamp: float = 0  # updated in token_refresh
        self.new_refresh_token: bool = False    # Indicator for Controller to update DB
        self.token_refresh()

    def token_refresh(self) -> None:
        """
        Pulls new access token and refresh token using the existing refresh token
        """
        # Prepping request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        target_url = self.api_base + self.api_token

        # Evaluating response
        req = requests.post(target_url, headers=headers, data=data, auth=(self.client_id, self.client_secret))
        if req.status_code != 200:
            print("Error refreshing access token")
            print(req.text)
            exit(5)
        req = req.json()

        # Updating token variables
        self.access_token = req['access_token']
        self.access_token_timestamp = datetime.datetime.now().timestamp()
        self.refresh_token = req['refresh_token']
        self.new_refresh_token = True

    def valid_token(self) -> bool:
        """
            Evaluates the access token timestamp for freshness. Spec says 30m minutes. Will enforce 25 minutes.
        """
        now = datetime.datetime.now().timestamp()
        diff_seconds = self.access_token_timestamp - now
        diff_minutes = diff_seconds / 60
        if diff_minutes >= 25:
            return False
        return True

    def get_product_details(self, upc: str) -> tuple[int, tuple]:
        """
        Pulls product details associated with the given upc
        """
        if not self.valid_token():
            self.token_refresh()

        # Preparing request
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        query_params = {
            'filter.locationId': self.location_id
        }
        encoded_params = urllib.parse.urlencode(query_params)
        target_url = f'{self.api_base}products/{upc}?{encoded_params}'
        # Requesting
        req = requests.get(target_url, headers=headers)
        if req.status_code != 200:
            return -1, (req.text,)
        req = req.json()
        return 0, (req,)
