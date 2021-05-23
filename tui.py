import Controller
import decimal


class Tui:
    """
    Tui will be an optional switch. Otherwise, cron mode by default.
    """

    def __init__(self, controller: Controller.Controller):
        self.controller = controller

    def mainloop(self):
        while True:
            ret = self.controller.get_alerts()
            if ret[0] == -1:
                # Error retrieving the alerts
                print(ret[1])
                exit(1)
            if len(ret[1]) == 0:
                print('No alerts are currently active')
            else:
                print('alert_id :::: product_name :::::: target_discount ')
                print('\n')
                for alert in ret[1]:
                    print(alert['alert_id'], end='')
                    print('  :::::::  ', end='')
                    print(alert['product_name'], end='')
                    print('  :::::::  ', end='')
                    print(alert['target_discount'])

            print('\n\n')
            print('[d]elete alert, [a]dd alert')
            user_input = input()
            if user_input == 'a':  # Adding an alert
                self._add_alert()

    def _add_alert(self):
        # Gathering UPC from user
        ret: tuple = self._input_upc()
        if ret[0] == 0:  # Valid UPC
            new_upc: str = ret[1]
            # Gathering desired discount rate from user
            ret = self._input_target_discount()
            if ret[0] == 0:  # Valid
                target_discount: decimal.Decimal = decimal.Decimal(int(ret[1]))
                ret = self.controller.get_product_details(new_upc)
                if ret[0] == -1:  # Error calling API
                    print(ret[1][0])
                else:
                    data: dict = ret[1][0]['data']
                    product_name: str = data['description']
                    product_price: decimal.Decimal = decimal.Decimal(data['items'][0]['price']['regular'])
                    target_price: decimal.Decimal = product_price * (1 - (target_discount/100))
                    print(f'{product_name} typically at {product_price} should alert when the promo price is '
                          f'{target_price}?')
                    while True:
                        user_input: str = input('y/n')
                        if user_input == 'y':
                            ret = self.controller.new_alert(product_name, new_upc, int(target_discount))
                            print(ret[1])
                            break
                        elif user_input == 'n':
                            break

    def _input_upc(self) -> tuple[int, str]:
        """
        Error checked fnx for getting the 13-digit UPC from the user.
        Caller should cast to int upon success.
        """
        try:
            user_input = input('Enter the upc')
            if len(user_input) != 13:
                print(f'UPC must be 13 characters. This one is {len(user_input)}')
                return -1, 'UPC wrong length'
            new_upc: int = int(user_input)
            return 0, user_input
        except ValueError:  # If unable to cast str to int
            print('Input contain non-integer values')
            return -1, 'Contains non-integer values'

    def _input_target_discount(self) -> tuple[int, str]:
        """
        Error checked fnx for getting a 2-digit int from the user.
        Caller should cast to int upon success.
        """
        user_input = input('Whats the targe discount rate? Must be 1 or 2 digit integer.')
        if len(user_input) < 1 or len(user_input) > 2:
            print('Invalid string length')
            return -1, 'Invalid string length'
        try:
            target_discount = int(user_input)
            return 0, user_input
        except ValueError:
            print('Input must be a 2-digit integer')
            return -1, 'Input must be a 2-digit integer'