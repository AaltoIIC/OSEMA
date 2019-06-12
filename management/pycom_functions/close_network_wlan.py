"""Closes WLAN"""
def close_network(network):
    network.disconnect()
    network.deinit()
