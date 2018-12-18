from trading.trading_api import TradingApi, ORDER_BUY, ORDER_SELL
from trading.alg_order import AlgOrder
from datetime import timedelta


class TradingApiFake(TradingApi):
    # override
    def __init__(self):
        self.positions = {}
        self.fees = 0
        self.nb_periods_price_to_buy = 1  # approx because actions will have delay
        self.orders = {}

    # override
    def check_status_api(self):
        return True, []

    # override
    def get_price(self, base_asset, quote_asset, key):
        close_price = 0
        trading_pair = base_asset + quote_asset
        if (key + timedelta(hours=self.nb_periods_price_to_buy)) in self.close_prices[trading_pair].index:
            close_price = self.close_prices[trading_pair][
                key + timedelta(hours=self.nb_periods_price_to_buy)]  # .values[0]
        else:
            # Retrieve last available price
            new_key = key
            i = 0
            while (new_key not in self.close_prices[trading_pair]) and i < 20:
                print('WARNING, missing price value for simulation')
                new_key = new_key - timedelta(hours=1)
                i = i + 1
            close_price = self.close_prices[trading_pair][new_key]  # .values[0]
        return close_price

    # override
    def get_available_amount_crypto(self, symbol):
        if symbol in self.positions:
            return self.positions[symbol]
        else:
            return 0.0

    # override => global class ?
    def get_portfolio_value(self, trading_pairs, cash_asset, key):
        total_value = 0
        close_price = 0
        for trading_pair, value in trading_pairs.items():
            amount = self.get_available_amount_crypto(value.base_asset)
            close_price = self.get_price(value.base_asset, value.quote_asset, key)
            total_value = total_value + (amount * close_price)
        total_value = total_value + self.get_available_amount_crypto(cash_asset)
        return total_value

    # market for the moment => to be scheduled with like market minus 0.5%
    # override
    def create_order(self, base_asset, quote_asset, side, quantity_from, key):  # ex: USDT, ETH, 1000, BUY
        # if cryptos exists
        from_crypto = ''
        to_crypto = ''
        if base_asset in self.positions and quote_asset in self.positions:
            from_crypto, to_crypto = self.get_from_to(base_asset, quote_asset, side)

            # calcul fees
            fees = quantity_from * self.fees
            fees_quote_asset = fees

            # get price
            price_init = self.get_price(base_asset, quote_asset, key)
            price = price_init

            # switch when Sell order
            if side == ORDER_SELL:
                fees_quote_asset = fees * price
                price = 1 / price

            # do exchange between cryptos
            self.positions[from_crypto] = self.positions[from_crypto] - quantity_from
            quantity_to = (quantity_from - fees) / price
            self.positions[to_crypto] = self.positions[to_crypto] + quantity_to
            base_asset_quantity, quote_asset_quantity = self.get_from_to(quantity_from, quantity_to, side)

            # create order already executed (for simulation needs)

            order = AlgOrder(len(self.orders), base_asset, quote_asset, side, base_asset_quantity, quote_asset_quantity,
                             price_init, fees, fees_quote_asset)
            self.orders[order.id_order] = order
            return order.id_order
        else:
            raise ValueError('ERROR (create_order):  cryptos doesn''t exists - ' + from_crypto + '/' + to_crypto)

    # override
    def get_order(self, id_order):
        return self.orders[id_order]

    # override
    def get_orders(self):
        return self.orders

    # override
    def cancel_open_orders(self):
        return True

    def init_from_backtesting_strategy(self, init_positions, fees, close_prices):
        self.positions = init_positions
        self.fees = fees
        self.close_prices = close_prices