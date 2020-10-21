import logging

from kiteconnect import KiteTicker

logging.basicConfig(level=logging.DEBUG)
# sl8x07lr209rk3aigxza2n8y8yfey016
# Initialise
# kite = KiteConnect(api_key="fact6majxka99prm")
#
kws = KiteTicker(api_key='fact6majxka99prm', access_token='ASwKVEaHAtdcG1Wdg9dvjNCovoJOKTcz')
# LYprqX6jLkGS8wi4HGnGJEopjcmjDMsI
#
# def on_ticks(ws, ticks):
#     # Callback to receive ticks.
#     print("this called")
#     logging.debug("Ticks: {}".format(ticks))
#     # print(type(ticks))
#     # return ticks


def on_connect(ws, response):
    pass
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    # ws.subscribe([738561, 5633])
    #
    # # Set RELIANCE to tick in `full` mode.
    # ws.set_mode(ws.MODE_FULL, [738561])


def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


# Assign the callbacks.
# kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
# kws.connect()
