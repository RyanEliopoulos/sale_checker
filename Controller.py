import DBInterface
import Communicator


class Controller:
    """
    Subsequent to every API call made through Communicator it must check for
    "self.communicator.new_refresh_token" and update the DB if needed.
    """

    def __init__(self, db_path: str):
        self.db_interface = DBInterface.DBInterface(db_path)
        self.communicator = self._make_communicator()
        self._commit_new_token()  # Instantiating communicator means new refresh token

    def _make_communicator(self) -> Communicator.Communicator:
        ret: tuple[int, tuple] = self.db_interface.retrieve_tokens()
        if ret[0] == -1:  # Failed to retrieve token
            print(ret[1])
            exit(1)
        refresh_token: str = ret[1][0]
        unix_timestamp: int = ret[1][1]
        communicator = Communicator.Communicator(refresh_token, unix_timestamp)
        return communicator

    def _commit_new_token(self):
        """
        Checks if Communicator received a new refresh token,
        committing it to the database if so.
        """
        if self.communicator.new_refresh_token:
            new_token: str = self.communicator.refresh_token
            new_timestamp: float = self.communicator.refresh_token_timestamp
            self.communicator.new_refresh_token = False
            ret = self.db_interface.update_tokens(new_token, new_timestamp)
            if ret[0] == -1:
                # @TODO Somehow alert myself that the program has failed to refresh the token.
                print(ret)

    def get_product_details(self, upc: str) -> tuple[int, tuple]:
        """
        Pulls item details. Updates database with new token, if applicable
        """
        ret: tuple = self.communicator.get_product_details(upc)
        self._commit_new_token()
        return ret

    def new_alert(self, product_name: str, upc: str, target_discount: int) -> tuple[int, str]:
        ret = self.db_interface.add_alert(product_name, upc, target_discount)
        return ret

    def delete_alert(self, alert_id: int) -> tuple[int, str]:
        return self.db_interface.delete_alert(alert_id)

    def get_alerts(self) -> tuple[int, tuple]:
        return self.db_interface.retrieve_alerts()
