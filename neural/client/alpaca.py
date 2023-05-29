"""

"""
from typing import Optional, Dict, List, Callable, Tuple

import numpy as np
import pandas as pd

from alpaca.common.rest import RESTClient
from alpaca.data.historical import (StockHistoricalDataClient,
                                    CryptoHistoricalDataClient)
from alpaca.data.live import StockDataStream, CryptoDataStream
from alpaca.data.requests import (CryptoBarsRequest, CryptoTradesRequest,
                                  StockBarsRequest, StockQuotesRequest,
                                  StockTradesRequest, BaseTimeseriesDataRequest)
from alpaca.trading import TradingClient, MarketOrderRequest
from alpaca.trading.models import Order, TradeAccount, Asset
from alpaca.trading.enums import (AccountStatus, AssetExchange, AssetClass,
                                  AssetStatus, OrderSide, TimeInForce)

from neural.common.log import logger
from neural.common.constants import API_KEY, API_SECRET
from neural.client.base import (AbstractClient, AbstractTradeClient,
                                AbstractDataClient)
from neural.data.base import AlpacaDataSource, AlpacaAsset
from neural.data.enums import AssetType
from neural.utils.misc import objects_list_to_dataframe


class AlpacaClient(AbstractClient):
    """
    The AlpacaClient class is a wrapper for the Alpaca API. It provides
    a simple interface for connecting to the Alpaca API and retrieving
    data. It also provides a simple interface for placing orders.

    Args:
    ------
        key (str): The API key for the Alpaca API. secret (str): The
        secret key for the Alpaca API. paper (bool): Whether to use the
        paper trading API or the live
            trading API. Defaults to False.


    Methods:
    --------
        connect: 
            Connect to the Alpaca API and set up the REST clients. Will
            be called automatically when the client is instantiated.
        _validate_credentials:
            Ensure that the API key and secret are valid.
        _get_clients:
            Gets the rest client objects from Alpaca API. Rest clients
            include the trading client, the stock historical data
            client, and the crypto historical data client. The trading
            client is used to place orders and perform account related
            tasks. The stock historical data client is used to retrieve
            historical stock data. The crypto historical data client is
            used to retrieve historical crypto data. The clients are
            stored in a dictionary with the keys 'trade', 'stocks', and
            'crypto'.
        _get_account:
            The account object is used to perform account related tasks
            such as checking the account status, getting the account
            balance, and getting the account positions.
        
    Properties:
    -----------
        clients:
            Returns a dictionary of all clients available on Alpaca API.
            The corresponding values are the RESTClient objects.

        account:
            A TradeAccount object that contains information about the
            account. Functionalities of TradeAccount:
                - Get account status
                - Get account balance
                - Get account positions
                - Get account portfolio value
                - Get account pattern day trader status
                - Get account equity
                - Get account maintenance margin
                - Get account initial margin
                - Get account buying power
        assets:
            Returns a dataframe of all assets available on Alpaca API.
            Asset objects have the flowing attributes:
                - symbol
                - asset_class
                - exchange
                - status
                - tradable
                - marginable
                - shortable
                - easy_to_borrow
                - fractionable
                - maintenance_margin
                - initial_margin
                - day_trade_ratio
                - last_updated_at
        symbols:
            Returns a dictionary of all symbols available on Alpaca API.
            The corresponding values are the Asset objects. Asset
            objects have the flowing attributes:
                - symbol
                - asset_class
                - exchange
                - status
                - tradable
                - marginable
                - shortable
                - easy_to_borrow
                - fractionable
                - maintenance_margin
                - initial_margin
                - day_trade_ratio
                - last_updated_at
        asset_types:
            Returns the asset types available on Alpaca API. The asset
            types are:
                - STOCK
                - CRYPTOCURRENCY    
        exchanges:
            A list of exchanges available on Alpaca API. The exchanges
            are:
                - AMEX
                - ARCA
                - BATS
                - NYSE
                - NASDAQ
                - NYSEARCA
                - FTXU
                - CBSE
                - GNSS
                - ERSX
                - OTC
                - CRYPTO

    Examples:
    ---------

    Option 1: Instantiate an instance of the AlpacaClient class with
    your API key and secret.

    >>> client = AlpacaClient(key=..., secret=...)
    >>> assets = client.assets()

    Option 2: Instantiate an instance of the AlpacaClient by passing
    values to constants.

    >>> from neural.common.constants import API_KEY, API_SECRET
    >>> API_KEY = ...
    >>> API_SECRET = ...
    >>> client = AlpacaClient()

    Option 3: Instantiate an instance of the AlpacaClient class with
    environment variables.

    # Set the environment variables for API key and secret on #
    Unix-like operating systems (Linux, macOS, etc.): 
        BASH: export API_KEY = <your_api_key> BASH: export API_SECRET =
        <your_secret_key>

    # Instantiate an instance of the AlpacaClient class 
    
    >>> from neural.connect.alpaca import AlpacaClient 
    >>> client = AlpacaClient()
    """

    def __init__(self,
                 key: Optional[str] = None,
                 secret: Optional[str] = None,
                 paper: bool = False) -> None:
        
        """
        Initialize an instance of the AlpacaClient class.

        Args:
        ------
            key (str): 
                The API key for the Alpaca API.
            secret (str): 
                The secret key for the Alpaca API.
            paper (bool): 
                Whether to use the paper trading API or the
                live trading API. Defaults to False. If using
                paper account credentials, this should be set
                to True.
        """

        self.key = key if key is not None else API_KEY
        self.secret = secret if secret is not None else API_SECRET
        self.paper = paper

        self._clients = None
        self._account = None
        self._assets = None
        self._symbols = None
        self._asset_types = None
        self._exchanges = None

        super().__init__()

        return None

    def connect(self):
        """
        Connect to the Alpaca API and set up the client. Will be called
        automatically when the client is instantiated. Sets up the
        trading client, and the account object.
        """
        self._validate_credentials()
        self._clients = self._get_clients()
        self._account = self._get_account()

        return None

    def _validate_credentials(self) -> bool:
        """
        Ensure that the API key and secret are valid. If the API key and
        secret are not valid, an exception will be raised.

        Raises:
        -------
            ValueError: If the API key and secret are not valid.
        """
        if self.key is None or self.secret is None:
            raise ValueError(
                'API key and secret are required to connect to Alpaca API.')

        return None

    def _get_clients(self) -> RESTClient:
        """
        Gets the rest client objects from Alpaca API. The trading REST client
        is used to place orders and perform account related tasks.

        TradingClient functionalities:
            - Submit order
            - Cancel order
            - Get orders
            - Get positions
            - Get account
            - Get clock
            - Get calendar
            - Get assets

        Notes:
        ------
        Crypto does not need key, and secret but download will be faster if
        provided.
        """
        clients = dict()
        clients['trade'] = TradingClient(api_key=self.key,
                                         secret_key=self.secret,
                                         paper=self.paper)

        return clients

    def _get_account(self) -> TradeAccount:
        """
        The account object is used to perform account related tasks such
        as checking the account status, getting the account balance, and
        getting the account positions.

        Raises:
        -------
            Exception: If the account setup fails.

        Returns:
        ---------
            Account: The account object.
        """
        try:
            account = self.clients['trading'].get_account()
            if not self.account.status == AccountStatus.ACTIVE:
                logger.warning(f'Account Status: {self.account.status}')

        except Exception as exception:
            logger.exception(f'Account setup failed: {exception}')

        return account

    @property
    def clients(self) -> Dict[str:RESTClient]:
        """
        Returns a dictionary of all clients available on Alpaca API. The
        corresponding values are the RESTClient objects.

        Returns:
        ---------
            dict: A dictionary mapping client names to RESTClient
            objects.
        """
        return self._clients

    @property
    def account(self) -> TradeAccount:
        """
        A TradeAccount object that contains information about the
        account. Functionalities of TradeAccount:
            - Get account status
            - Get account balance
            - Get account positions
            - Get account portfolio value
            - Get account pattern day trader status
            - Get account equity
            - Get account maintenance margin
            - Get account initial margin
            - Get account buying power

        Returns:
        ---------
            Account: The account object.
        """
        return self._account

    @property
    def assets(self) -> pd.DataFrame:
        """
        Returns a dataframe of all assets available on Alpaca API. Asset
        objects have the flowing attributes:
            - symbol
            - asset_class
            - exchange
            - status
            - tradable
            - marginable
            - shortable
            - easy_to_borrow
            - fractionable
            - maintenance_margin
            - initial_margin
            - day_trade_ratio
            - last_updated_at
        
        Returns:
        ---------
            DataFrame: A dataframe of all assets available on Alpaca
            API.
        """

        if self._assets is None:
            self._assets = self.clients['trade'].get_all_assets()

        assets_dataframe = objects_list_to_dataframe(self._assets)

        return assets_dataframe

    @property
    def symbols(self) -> Dict[str, Asset]:
        """
        Returns a dictionary of all symbols available on Alpaca API. The
        corresponding values are the Asset objects. Asset objects have
        the flowing attributes:
            - symbol
            - asset_class
            - exchange
            - status
            - tradable
            - marginable
            - shortable
            - easy_to_borrow
            - fractionable
            - maintenance_margin
            - initial_margin
            - day_trade_ratio
            - last_updated_at

        Returns:
        ---------
            dict: A dictionary mapping symbols to Asset objects.
        """
        if self._symbols is None:
            self._symbols = {asset.symbol: asset for asset in self.assets}

        return self._symbols

    @property
    def asset_types(self) -> List[AssetType]:
        """
        Returns the asset types available on Alpaca API. The asset types
        are:
            - STOCK
            - CRYPTOCURRENCY    

        Returns:
        ---------
            list: A list of asset types available on Alpaca API.
        """
        asset_type_map = {AssetClass.US_EQUITY: AssetType.STOCK,
                            AssetClass.CRYPTO: AssetType.CRYPTOCURRENCY}
        
        if self._asset_types is None:
            self._asset_types = [asset_type_map[item] for item in AssetClass]

        return self._asset_types

    @property
    def exchanges(self) -> List[AssetExchange]:
        """
        A list of exchanges available on Alpaca API. The exchanges are:
            - AMEX
            - ARCA
            - BATS
            - NYSE
            - NASDAQ
            - NYSEARCA
            - FTXU
            - CBSE
            - GNSS
            - ERSX
            - OTC
            - CRYPTO

        Returns:
        ---------
            list: A list of exchanges available on Alpaca API.
        
        Notes:
        ------
        As of 05/23/2023, all stocks on Alpaca API are traded on NYSE
        timezone.
        """
        if self._exchanges is None:
            self._exchanges = [item for item in AssetExchange]

        exchanges = [item.value for item in self._exchanges]
        return exchanges


class AlpacaDataClient(AlpacaClient, AbstractDataClient):
    """
    This is an extension of the AlpacaClient class. It provides a
    simple interface for retrieving data from the Alpaca API, in
    addition to the functionalities provided by the AlpacaClient class.

    Args:
    ------
        key (str):
            The API key for the Alpaca API.
        secret (str):
            The secret key for the Alpaca API.
        paper (bool):
            Whether to use the paper trading API or the live trading
            API. Defaults to False. If using paper account credentials,
            this should be set to True.

    Properties:
    -----------
        clients:
            Returns a dictionary of all clients available on Alpaca API.
            The corresponding values are the RESTClient objects.
        account:
            A TradeAccount object that contains information about the
            account. Functionalities of TradeAccount:
                - Get account status
                - Get account balance
                - Get account positions
                - Get account portfolio value

        assets:
            Returns a dataframe of all assets available on Alpaca API.
            Asset objects have the flowing attributes:
                - symbol
                - asset_class
                - exchange
                - status
                - tradable
                - marginable
                - shortable
                - easy_to_borrow
                - fractionable
                - maintenance_margin
                - initial_margin
                - day_trade_ratio
                - last_updated_at
        symbols:
            Returns a dictionary of all symbols available on Alpaca API.
            The corresponding values are the Asset objects.
        asset_types:
            Returns the asset types available on Alpaca API. The asset
            types are:
                - STOCK
                - CRYPTOCURRENCY
        exchanges:
            A list of exchanges available on Alpaca API. The exchanges
            are:
                - AMEX
                - ARCA
                - BATS
                - NYSE
                - NASDAQ
                - NYSEARCA
                - FTXU
                - CBSE
                - GNSS
                - ERSX
                - OTC
                - CRYPTO
        data_source:
            The data source for the Alpaca API. The data source is used
            to retrieve data from the Alpaca API.

    Methods:
    --------
        connect:
            Connect to the Alpaca API and set up the REST clients. Will
            be called automatically when the client is instantiated.
        _validate_credentials:
            Ensure that the API key and secret are valid.
        _get_clients:
            Gets the rest client objects from Alpaca API. Rest clients
            include the trading client, the stock historical data
            client, and the crypto historical data client. The trading
            client is used to place orders and perform account related
            tasks. The stock historical data client is used to retrieve
            historical stock data. The crypto historical data client is
            used to retrieve historical crypto data. The clients are
            stored in a dictionary with the keys 'trade', 'stocks', and
            'crypto'.
        safe_method_call:
            A helper method to safely call a method on an object. If the
            object does not have the specified method, an AttributeError
            will be raised.
        get_downloader_and_request:
            Returns the downloader and the request object for the
            specified dataset type and asset type.
        get_streamer:
            A method to get the streamer for the specified stream type
            and asset type. The streamer is used to retrieve live data.
        symbols_to_assets:
            This method converts a list of symbols to a list of Asset   
            objects. AlpacaAsset objects have the flowing attributes:
                - symbol
                - asset_type
                - fractionable
                - marginable
                - maintenance_margin
                - shortable
                - easy_to_borrow
        
    Examples:
    ---------
    Option 1: Instantiate an instance of the AlpacaDataClient class
    with your API key and secret.

    >>> client = AlpacaDataClient(key=..., secret=...)
    >>> assets = client.assets()

    Option 2: Instantiate an instance of the AlpacaDataClient by
    passing values to constants.
    
    >>> from neural.common.constants import API_KEY, API_SECRET
    >>> API_KEY = ...
    >>> API_SECRET = ...
    >>> client = AlpacaDataClient()

    Option 3: Instantiate an instance of the AlpacaClient class with
    environment variables.

    # Set the environment variables for API key and secret on #
    Unix-like operating systems (Linux, macOS, etc.): 
        BASH: export API_KEY = <your_api_key> BASH: export API_SECRET =
        <your_secret_key>

    # Instantiate an instance of the AlpacaClient class 
    
    >>> from neural.connect.alpaca import AlpacaDataClient 
    >>> client = AlpacaDataClient()
    """
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    @property
    def data_source(self):

        return AlpacaDataSource

    def _get_clients(self) -> RESTClient:
        """
        Adds the stock historical data client and the crypto historical data
        client to the clients dictionary. The stock historical data client is
        used to retrieve historical stock data. The crypto historical data
        client is used to retrieve historical crypto data.


        CryptoHistoricalDataClient functionalities:
            - Get crypto bars
            - Get crypto quotes
            - Get crypto trades

        StockHistoricalDataClient functionalities:
            - Get stock bars
            - Get stock quotes
            - Get stock trades
        """
        clients = super()._get_clients()

        clients['crypto'] = CryptoHistoricalDataClient(api_key=self.key,
                                                       secret_key=self.secret)
        clients['stocks'] = StockHistoricalDataClient(api_key=self.key,
                                                      secret_key=self.secret)
        return clients
    
    @staticmethod
    def safe_method_call(object, method_name):
        """"
        A helper method to safely call a method on an object. If the
        object does not have the specified method, an AttributeError
        will be raised.

        Args:
        ------
            object: 
                The object to call the method on.
            method_name:
                The name of the method to call.
            
        Returns:
        ---------
            The result of calling the method on the object. If the
            object does not have the specified method, an
            AttributeError will be raised.
        
        Raises:
        -------
            AttributeError: If the object does not have the specified
            method.
        """
        if hasattr(object, method_name):
            return getattr(object, method_name)
        else:
            raise AttributeError(f"Client does not have method '{method_name}'")

    def get_downloader_and_request(
            self,
            dataset_type: AlpacaDataSource.DatasetType,
            asset_type=AssetType) -> Tuple[Callable, BaseTimeseriesDataRequest]:
        """
        Get the downloader and the request object for the specified dataset
        type and asset type. The request object is used to specify the
        parameters for the data request. The downloader is used to retrieve
        the data. Request object for bars has the following attributes:
            - symbol_or_symbols
            - start
            - end
            - timeframe
        Request object for quotes and trades has the following attributes:
            - symbol_or_symbols
            - start
            - end
        
        Args:
        ------
            dataset_type:
                The type of dataset to retrieve. The dataset types are:
                    - BAR
                    - QUOTE 
                    - TRADE
            asset_type:
                The type of asset to retrieve. The asset types are:
                    - STOCK
                    - CRYPTOCURRENCY
            
        Returns:
        ---------
            tuple: A tuple containing the downloader and the request
            object.
        
        Raises:
        -------
            ValueError: If the dataset type or asset type is not valid.
        
        Notes:
        ------
            Crypto does not have quotes historical data in Alpaca API.
        """
        client_map = {
            AssetType.STOCK: self.clients['stocks'],
            AssetType.CRYPTOCURRENCY: self.clients['crypto']
        }

        client = client_map[asset_type]

        downloader_request_map = {
            AlpacaDataSource.DatasetType.BAR: {
                AssetType.STOCK: ('get_stock_bars', StockBarsRequest),
                AssetType.CRYPTOCURRENCY: ('get_crypto_bars', CryptoBarsRequest)
            },
            AlpacaDataSource.DatasetType.QUOTE: {
                AssetType.STOCK: ('get_stock_quotes', StockQuotesRequest)
            },
            AlpacaDataSource.DatasetType.TRADE: {
                AssetType.STOCK: ('get_stock_trades', StockTradesRequest),
                AssetType.CRYPTOCURRENCY:
                ('get_crypto_trades', CryptoTradesRequest)
            }
        }

        try:
            downloader_method_name, request = downloader_request_map[dataset_type][
                asset_type]
        except KeyError:
            raise ValueError(
                f'Dataset type {dataset_type}, asset type {asset_type} '
                 'is not a valid combination.'
            )
        downloader = AlpacaDataClient.safe_method_call(
            object=client, method_name=downloader_method_name)

        return downloader, request

    def get_streamer(
        self,
        stream_type: AlpacaDataSource.StreamType,
        asset_type: AssetType,
    ) -> Callable:
        """
        A method to get the streamer for the specified stream type and
        asset type. The streamer is used to retrieve live data.

        Args:
        ------
            stream_type:
                The type of stream to retrieve. The stream types are:
                    - BAR
                    - QUOTE
                    - TRADE
            asset_type:
                The type of asset to retrieve. The asset types are:
                    - STOCK
                    - CRYPTOCURRENCY

        Returns:
        ---------
            Callable: The streamer for the specified stream type and
            asset type.
        """
        stream_map = {
            AlpacaDataSource.StreamType.BAR: {
                AssetType.STOCK: ('subscribe_bars', StockDataStream),
                AssetType.CRYPTOCURRENCY: ('subscribe_bars', CryptoDataStream)
            },
            AlpacaDataSource.StreamType.QUOTE: {
                AssetType.STOCK: ('subscribe_quotes', StockDataStream),
                AssetType.CRYPTOCURRENCY: ('subscribe_quotes', CryptoDataStream)
            },
            AlpacaDataSource.StreamType.TRADE: {
                AssetType.STOCK: ('subscribe_trades', StockDataStream),
                AssetType.CRYPTOCURRENCY: ('subscribe_trades', CryptoDataStream)
            }
        }

        stream_method_name, stream = stream_map[stream_type][asset_type]

        streamer = AlpacaDataClient.safe_method_call(
            object=stream, method_name=stream_method_name)

        return streamer

    def symbols_to_assets(self, symbols: List[str]):
        """
        This method converts a list of symbols to a list of Asset
        objects. AlpacaAsset objects have the flowing attributes:
            - symbol
            - asset_type
            - fractionable
            - marginable
            - maintenance_margin
            - shortable
            - easy_to_borrow
        
        Args:
        ------
            symbols:
                A list of symbols to convert to Asset objects.

        Returns:
        ---------
            list: 
                A list of Asset objects.

        Raises:
        ------- 
            ValueError: 
                If a symbol is not a known symbol.  

        Notes:
        ------
            Asset objects are client dependent as each client can have
            individual representation/specifications for the same
            underlying asset. This method is specific to the Alpaca API
            client.
        """
        asset_type_map = {
            AssetClass.US_EQUITY: AssetType.STOCK,
            AssetClass.CRYPTO: AssetType.CRYPTOCURRENCY
        }

        assets = list()

        for symbol in symbols:

            alpaca_asset = self.symbols[symbol]

            if alpaca_asset is None:
                raise ValueError(f'Symbol {symbol} is not a known symbol.')

            if not alpaca_asset.tradable:
                logger.warning(f'Symbol {symbol} is not a tradable symbol.')

            if alpaca_asset.status != AssetStatus.ACTIVE:
                logger.warning(f'Symbol {symbol} is not an active symbol.')

            if not alpaca_asset.fractionable:
                logger.warning(f'Symbol {symbol} is not a fractionable symbol.')

            if not alpaca_asset.easy_to_borrow:
                logger.warning(f'Symbol {symbol} is not easy to borrow (ETB).')

            asset_type = asset_type_map[alpaca_asset.asset_class]

            assets.append(
                AlpacaAsset(symbol=symbol,
                            asset_type=asset_type,
                            fractionable=alpaca_asset.fractionable,
                            marginable=alpaca_asset.marginable,
                            maintenance_margin=alpaca_asset.
                            maintenance_margin_requirement,
                            shortable=alpaca_asset.shortable,
                            easy_to_borrow=alpaca_asset.easy_to_borrow))
        return assets


class AlpacaTradeClient(AlpacaClient, AbstractTradeClient):
    """
    This is an extension of the AlpacaClient class. It provides a simple
    interface for placing orders, in addition to the functionalities
    provided by the AlpacaClient class. The Trader class will use the
    functionality provided by this class to realize orders specified by
    the agent in the environment.

    Args:
    ------
        key (str):
            The API key for the Alpaca API.
        secret (str):
            The secret key for the Alpaca API.
        paper (bool):
            Whether to use the paper trading API or the live trading
            API. Defaults to False. If using paper account credentials,
            this should be set to True.
        
    Properties:
    -----------
        clients:
            Returns a dictionary of all clients available on Alpaca API.
            The corresponding values are the RESTClient objects.
        account:
            A TradeAccount object that contains information about the
            account. Functionalities of TradeAccount:
                - Get account status
                - Get account balance
                - Get account positions
                - Get account portfolio value
                - Get account pattern day trader status
                - Get account equity
                - Get account maintenance margin
                - Get account initial margin
                - Get account buying power
        assets:
            Returns a dataframe of all assets available on Alpaca API.
            Asset objects have the flowing attributes:
                - symbol
                - asset_class
                - exchange
                - status
                - tradable
                - marginable
                - shortable
                - easy_to_borrow
                - fractionable
                - maintenance_margin
                - initial_margin
                - day_trade_ratio
                - last_updated_at
        symbols:
            Returns a dictionary of all symbols available on Alpaca API.
            The corresponding values are the Asset objects. 
        asset_types:
            Returns the asset types available on Alpaca API. The asset
            types are:
                - STOCK
                - CRYPTOCURRENCY
        exchanges:
            A list of exchanges available on Alpaca API. The exchanges
            are:
                - AMEX
                - ARCA
                - BATS
                - NYSE
                - NASDAQ
                - NYSEARCA
                - FTXU
                - CBSE
                - GNSS
                - ERSX
                - OTC
        cash:
            The current amount of cash available to the trader. This
            will be used by agent to make decisions.
        asset_quantities:
            Returns a dictionary of symbols and asset quantities for the
            trader's current positions. This will be used by agent to
            make decisions.
        equity:
            The current net worth of the trader. This along with market
            data will be used by agent to make decisions.
        
    Methods:
    --------
        
    """
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._cash = None
        self._asset_quantities = None
        self._equity = None
        self._longs = None
        self._shorts = None

    @property
    def cash(self):
        """
        The current amount of cash available to the trader.

        Returns:
        ---------
            float: The current amount of cash available to the trader.
        """

        self._cash = self.account.cash

        return self._cash

    @property
    def asset_quantities(self, assets: List[AlpacaAsset]) -> np.ndarray[float]:
        """
        Returns a numpy array of symbols and asset quantities for the
        specified list of assets.

        Returns:
        ---------
            array: A numpy array of asset quantities for the specified 
            list of assets.
        """

        asset_quantities = list()

        positions_dataframe = self.get_positions_dataframe()
        symbols_in_portfolio = positions_dataframe['symbol'].unique()

        for asset in assets:
            if asset.symbol not in symbols_in_portfolio:
                asset_quantities.append(0)
                continue
            row = positions_dataframe.loc[positions_dataframe['symbol'] ==
                                          asset.symbol].iloc[0]
            quantity = row['qty'] if row['side'] == 'long' else -1 * row['qty']

            asset_quantities.append(quantity)
            asset_quantities = np.array(asset_quantities)
        return asset_quantities

    @property
    def equity(self) -> float:
        """
        The current net worth of the trader. More concretely, the equity
        in a margin account is defined as E = L + C - S where 
            - E is equity
            - L is long market value
            - C is cash balance
            - S is short market value
        
        Equity thus shows the total value of the account if all the
        positions were closed at the current market prices. This along
        with market data will be used by agent to make decisions.

        Returns:
        ---------
            float: The current equity of the trader.
        """

        self._equity = self.account.portfolio_value

        return self._equity

    def get_positions_dataframe(self) -> pd.DataFrame:
        """
        Get all current positions in the account. Position is defined as
        the notional value of each asset in portfolio whether it is long
        (owned), or short (borrowed). The position value is calculated
        as the product of the asset price and the number of shares held.

        Returns:
        ---------
            DataFrame: A dataframe of all current positions in the
            account.
        """

        self._positions = self.clients['trading'].get_all_positions()

        positions_dataframe = objects_list_to_dataframe(self._positions)

        return positions_dataframe

    def check_connection(self):
        """
        Check if the connection to the Alpaca API is active. Used by 
        trader to before letting agent start trading.

        Returns:
        ---------
            bool: True if the connection is active, False otherwise.
        """

        status = True if self.account.status == AccountStatus.ACTIVE else False
        return status

    def place_order(
        self,
        asset: AlpacaAsset,
        quantity: float,
        time_in_force: str = 'ioc',
    ) -> None | Order:
        """
        This method places orders in Alpaca API uses quantity of asset
        to buy or sell. If quantity is positive, the order is a buy
        order. If quantity is negative, the order is a sell order. 

        All order are market orders. Market orders are the most likely
        type of order to be executed. Link:
        https://alpaca.markets/docs/trading/orders/. A market order is
        an order to buy or sell an asset at current market price. Time
        in force options:
        
           - Day order = "day"
           - Good 'til cancelled = "gtc"
           - Immediate or cancel = "ioc"
           - Fill or kill = "fok"

        Day order is the default time in force option. Day order is an
        order that is valid until the end of the trading day on which it
        was placed. If the order is not filled by the end of the trading
        day, it will be cancelled. Good 'til cancelled is an order that
        is valid until it is filled or cancelled. Immediate or cancel is
        an order that must be filled immediately or cancelled. Fill or
        kill is an order that must be filled immediately or cancelled.

        Args:
        ------
            asset:
                The asset to buy or sell.
            quantity:
                The quantity of the asset to buy or sell. If quantity is
                positive, the order is a buy order. If quantity is
                negative, the order is a sell order.
            time_in_force:
                The time in force for the order. Defaults to "ioc". Time
                in force options:
                    - Day order = "day"
                    - Good 'til cancelled = "gtc"
                    - Immediate or cancel = "ioc"
                    - Fill or kill = "fok"

        Returns:
        ---------
            None | Order: The order object. if quantity is zero, None is
            returned.
        
        Raises:
        -------
            ValueError: If the time in force is not valid.
            ValueError: If the time in force is not valid for

        Notes:
        ------
        Time in force options for crypto assets:
            Good 'til cancelled = "gtc" Immediate or cancel = "ioc"

        Trader typically cancels all unfufilled orders before submitting
        new orders for decisions that agent make. Thus for example 'day'
        and 'gtc' orders will only stay open at most for a single
        trading interval determined by the trading resolution (e.g.
        '1Min', '1H').
        """

        if quantity == 0:
            return None

        if time_in_force not in ['day', 'gtc', 'ioc', 'fok']:
            raise ValueError(
                f'Time in force {time_in_force} is not valid.'
                'valid options are: "day", "gtc", "ioc", "fok"')

        if asset.asset_type == AssetType.CRYPTOCURRENCY:
            if time_in_force not in ['gtc', 'ioc']:
                raise ValueError(
                    f'Time in force {time_in_force} is not valid for '
                    'cryptocurrency assets.')

        side = OrderSide.BUY if np.sign(quantity) > 0 else OrderSide.SELL
        time_in_force = TimeInForce(time_in_force)

        market_order_request = MarketOrderRequest(symbol=asset.symbol,
                                                  qty=abs(quantity),
                                                  side=side,
                                                  time_in_force=time_in_force)

        market_order = self.clients['trade'].submit_order(
            order_data=market_order_request)

        return market_order
