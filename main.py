import sys
import asyncio
import json
import websockets
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from gui import *
import logging
import time
from trade import *

# Set up logging at the beginning of your script
logging.basicConfig(filename='pumpfunbot.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Worker(QObject):
    token_creation_event = pyqtSignal(dict)
    connection_status = pyqtSignal(str)

    def __init__(self, websocket_url, payload):
        super().__init__()
        self.websocket_url = websocket_url
        self.payload = payload
        self.retry_delay = 5
        self.max_retry_delay = 60

    async def handle_event(self, event):
        if 'mint' in event:
            self.token_creation_event.emit(event)

    async def subscribe_token_creation_event(self):
        while True:
            try:
                async with websockets.connect(self.websocket_url) as websocket:
                    self.connection_status.emit("Connected")
                    await websocket.send(self.payload)
                    self.retry_delay = 5
                    while True:
                        message = await websocket.recv()
                        event = json.loads(message)
                        await self.handle_event(event)
            except websockets.exceptions.ConnectionClosedError as e:
                self.connection_status.emit(f"Connection closed: {e}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
                self.retry_delay = min(self.retry_delay * 2, self.max_retry_delay)
            except Exception as e:
                self.connection_status.emit(f"Error: {e}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
                self.retry_delay = min(self.retry_delay * 2, self.max_retry_delay)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.subscribe_token_creation_event())
        loop.close()

class PumpFunSnipperBot:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_MainWindow()
        self.ui.show()

        self.api_key = ""
        self.slippage = 0
        self.priorityFee = 0
        self.tokenAddress = ""
        self.websocket_url = ""
        self.tradeAmount = 0
        self.denominatedInSol = "false"
        self.pumpUrl = ""
        self.pool = "pump"
        self.worker_thread = None
        self.worker = None
        self.wallet_balance = 0

        self.read_config()
        self.connect_signals()
            
    def read_config(self):
        try:
            self.trade_config = read_config('config.json')
            self.api_key = self.trade_config.api_key
            self.priorityFee = self.trade_config.priority_fee
            self.pool = self.trade_config.pool
            self.denominatedInSol = str(self.trade_config.denominated_in_sol).lower()
            self.websocket_url = "wss://pumpportal.fun/ws"  # Add this if not in config
            self.slippage = self.trade_config.slippage
            self.pumpUrl = "https://pumpportal.fun/api/trade?api-key=" + self.api_key
            self.wallet_address = self.trade_config.public_key
            print('Read config success!')
            self.start_worker()
            self.fetch_wallet_balance()
        except Exception as e:
            print(f"Config file read failed: {e}")
            logging.error(f"Config file read failed: {e}")

    def start_worker(self):
        payload = json.dumps({"method": "subscribeNewToken"})
        self.worker = Worker(self.websocket_url, payload)
        self.worker.token_creation_event.connect(self.handle_token_creation_event)
        self.worker.connection_status.connect(self.handle_connection_status)

        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def handle_token_creation_event(self, event):
        if 'mint' in event:
            self.ui.append_token_creation_log(f"#{event['mint']}")

    def handle_connection_status(self, status):
        self.ui.append_token_trade_log(status)
        
    def get_solana_balance(self, address):
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def fetch_wallet_balance(self):
        if not self.wallet_address:
            logging.error("Wallet address not found in config")
            return

        try:
            data = self.get_solana_balance(self.wallet_address)
            if 'result' in data:
                balance_lamports = data['result']['value']
                balance_sol = balance_lamports / 1e9
                self.wallet_balance = balance_sol
                logging.info(f"Fetched wallet balance: {self.wallet_balance} SOL")
                self.ui.update_balance_ui(self.wallet_balance)
            else:
                logging.error(f"Failed to fetch wallet balance: {data}")
        except Exception as e:
            logging.exception(f"Error fetching wallet balance: {e}")

    def connect_signals(self):
        self.ui.ui_buy_btn.clicked.connect(self.buy_token)
        self.ui.ui_sell_btn.clicked.connect(self.sell_token)

    def buy_token(self):
        try:
            trade_amount_str = self.ui.ui_buy_token_amount.text().strip()
            amount = trade_amount_str  # Keep as string for execute_local_trade
            self.tokenAddress = self.ui.ui_token_address.text()
            self.action = "buy"
            self.ui.append_token_trade_log(f"Buy token: {self.tokenAddress}, Amount: {trade_amount_str} SOL")
            self.make_trade(self.action, self.tokenAddress, amount)
        except ValueError:
            print("Invalid buy amount entered. Please enter a valid number.")
            logging.error("Invalid buy amount entered.")

    def sell_token(self):
        sell_amount_str = self.ui.ui_sell_token_amount.text().strip()
        if sell_amount_str:
            try:
                amount = sell_amount_str  # Keep as string for execute_local_trade
                self.tokenAddress = self.ui.ui_token_address.text()
                self.action = "sell"
                self.ui.append_token_trade_log(f"Sell token: {self.tokenAddress}, Amount: {sell_amount_str} SOL")
                self.make_trade(self.action, self.tokenAddress, amount)
            except ValueError:
                print("Invalid sell amount entered. Please enter a valid number.")
                logging.error("Invalid sell amount entered.")
        else:
            print("Sell amount cannot be empty. Please enter a valid number.")
            logging.error("Sell amount cannot be empty.")
            
    def execute_trade(self, action, mint, amount):
        try:
            tx_signature = execute_local_trade(self.trade_config, action, mint, amount)
            trade_status = f"Trade successful: {tx_signature}"
            logging.info(trade_status)
            
            # Monitor the transaction status
            if self.monitor_transaction_status(tx_signature):
                return f"{trade_status}\nTransaction confirmed."
            else:
                return f"{trade_status}\nTransaction was not confirmed in time."
        except ValueError as e:
            error_message = f"Error executing trade: {e}"
            logging.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"Unexpected error executing trade: {e}"
            logging.exception(error_message)
            return error_message

    def make_trade(self, action, mint, amount):
        self.ui.run_background_task(self.execute_trade, action, mint, amount)
        self.ui.append_token_trade_log("Trade execution started...")

    def monitor_transaction_status(self, transaction_signature, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                url = f"https://api.mainnet-beta.solana.com/transaction/{transaction_signature}"
                response = requests.get(url)
                if response.status_code == 200:
                    transaction_data = response.json()
                    if 'result' in transaction_data:
                        return True  # Transaction confirmed
                time.sleep(1)  # Wait before checking again
            except Exception as e:
                logging.error(f"Error checking transaction status: {e}")
                time.sleep(1)  # Wait before retrying

        return False  # Transaction not confirmed within timeout

    def run(self):
        return self.app.exec_()

if __name__ == '__main__':
    bot = PumpFunSnipperBot()
    sys.exit(bot.run())
