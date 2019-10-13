# BitForex Simple request lib
Python simple bitforex exchange requests library

Dependencies: 
requests

### Generic Request
```python
Exchange()\
.build_request('POST', '/fund/allAccount')
.finalize()

{'data': [{'active': 0, 'currency': 'btc', 'fix': 0, 'frozen': 0},
  {'active': 0, 'currency': 'eth', 'fix': 0, 'frozen': 0},
...
  {'active': 0, 'currency': 'ron', 'fix': 0, 'frozen': 0}],
 'success': True,
 'time': 1570969672516
}
```

### Request pieces
[Using BitForex example](https://github.com/bitforexapi/API_Doc_en/wiki/API-Call-Description "API Example")
```python
Exchange(log_level=logging.DEBUG)\
.with_keys(access_key='fd91cd9ba2cc78fed6bb40e0bcff29ba',
                    secret_key='82f192d903f363f22a031dfdbbeaf851')\
.with_params(amount=1, 
             nonce=1501234567890, 
             price=1000, 
             symbol='coin-usd-eth', 
             tradeType=1)\
.with_segment('/trade/placeOrder')\
.test()
```
#### Output:
```bash
DEBUG:bitforex:API str /api/v1/trade/placeOrder?accessKey=fd91cd9ba2cc78fed6bb40e0bcff29ba&amount=1&nonce=1501234567890&price=1000&symbol=coin-usd-eth&tradeType=1
DEBUG:bitforex:Endpoint https://api.bitforex.com/api/v1/trade/placeOrder
DEBUG:bitforex:Path str /api/v1/trade/placeOrder
DEBUG:bitforex:Query str accessKey=fd91cd9ba2cc78fed6bb40e0bcff29ba&amount=1&nonce=1501234567890&price=1000&symbol=coin-usd-eth&tradeType=1
DEBUG:bitforex:FURL https://api.bitforex.com/api/v1/trade/placeOrder?accessKey=fd91cd9ba2cc78fed6bb40e0bcff29ba&amount=1&nonce=1501234567890&price=1000&signData=2a0a848d76920a425190c5f2c509b45ef730956fac5331c79a988671223fd367&symbol=coin-usd-eth&tradeType=1
```
