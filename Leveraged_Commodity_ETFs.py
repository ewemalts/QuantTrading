from intriniorealtime.client import IntrinioRealtimeClient


def on_quote(quote, backlog):
    print("QUOTE: ", quote, "BACKLOG LENGTH: ", backlog)


options = {
    'username': 'YOUR_INTRINIO_API_USERNAME',
    'password': 'YOUR_INTRINIO_API_PASSWORD',
    'provider': 'iex',
    'on_quote': on_quote
}

client = IntrinioRealtimeClient(options)
client.join(['AAPL', 'GE', 'MSFT'])
client.connect()
client.keep_alive()