import DBInterface
import Communicator
import decimal
import Notifier
import datetime


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

    def check_sales(self):
        """
        Checks active alerts against current promo prices.
        Sends notifications if criterion met.
        """
        # @TODO find a more appropriate place for this functionality
        notification_interval: int = 86400 * 7  # Days in seconds
        ret: tuple = self.db_interface.retrieve_alerts()
        if ret[0] == -1:
            print(ret)
            exit(1)
        for alert in ret[1]:
            target_discount: int = alert['target_discount']
            upc: str = alert['upc']
            product_ret: tuple = self.get_product_details(upc)
            if product_ret[0] == -1:
                ...
                # @TODO log failures
                print(product_ret)
            else:
                data: dict = product_ret[1][0]['data']
                product_name: str = data['description']
                regular_price: decimal.Decimal = decimal.Decimal(data['items'][0]['price']['regular'])
                sale_price: decimal.Decimal = decimal.Decimal(data['items'][0]['price']['promo'])
                if sale_price == 0:  # No promo running
                    print(f'No promo for: {product_name}')
                    continue
                price_diff: decimal.Decimal = regular_price - sale_price
                discount: decimal.Decimal = price_diff / regular_price
                scaled_discount: decimal.Decimal = (discount * 100).quantize(decimal.Decimal('1.00'))
                print(f'{product_name} is on a {scaled_discount} percent sale')

                notification_due: bool = False
                now: float = datetime.datetime.now().timestamp()
                decision: str = ''
                if alert['last_notified'] < (now - notification_interval):  # Been long enough since last notification
                    if scaled_discount >= target_discount:
                        notification_due = True
                        decision = 'Notifying: Sufficient discount + delay time exceeded'
                    else:
                        decision = 'Not notifying: Insufficient discount + delay time exceeded'
                # Must quantize otherwise something extra is in there.
                # Somehow 33.36 was > 33.36 before adding the quantize.
                elif scaled_discount > decimal.Decimal(alert['last_discount_rate']).quantize(decimal.Decimal('1.00')):
                    last_discount_rate = alert['last_discount_rate']
                    print(f'scaled_discount: {scaled_discount}, last_discount_rate: {last_discount_rate}')
                    notification_due = True
                    decision = 'Notifying: Discount improved. Delay time not meet'
                else:
                    decision = 'Nothing new to report'

                print('\t' + decision)
                if notification_due:
                    print(f'{product_name} meets or exceeds its target of {target_discount}')

                    Notifier.Notifier.send_notification(f'{product_name} is {scaled_discount}% off at Fred Meyer')
                    timestamp: float = datetime.datetime.now().timestamp()
                    update_ret = self.db_interface.update_alert(alert['alert_id'], float(scaled_discount), timestamp)
                    if update_ret[0] == -1:
                        ...
                        # @TODO log failures
                    print(update_ret)

    def new_alert(self, product_name: str, upc: str, target_discount: int) -> tuple[int, str]:
        ret = self.db_interface.add_alert(product_name, upc, target_discount)
        return ret

    def delete_alert(self, alert_id: int) -> tuple[int, str]:
        return self.db_interface.delete_alert(alert_id)

    def get_alerts(self) -> tuple[int, tuple]:
        return self.db_interface.retrieve_alerts()
