# Flask backend for PeakeCoin atomic swap
# Handles: token receipt, swap to SWAP.HIVE, buy PEK, send PEK to user, and status API

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import uuid
from beem import Steem, Hive
from beem.account import Account
from beem.nodelist import NodeList
from beem.transactionbuilder import TransactionBuilder
from beemengine.engine import Engine

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
HIVE_NODE = 'https://api.hive.blog'
ENGINE_NODE = 'https://api.hive-engine.com/rpc'
SWAP_ACCOUNT = 'your_swap_account'  # Set to your backend's Hive account
SWAP_ACCOUNT_KEY = 'your_private_active_key'  # Store securely, never commit real key!

# --- In-memory swap status (use DB for production) ---
swaps = {}

# --- Helper: Start swap process in background ---
def process_swap(swap_id, user, token, amount):
    try:
        # 1. Wait for user to send token to SWAP_ACCOUNT
        # (In production, use beem/nectar to listen for incoming transfers)
        swaps[swap_id]['status'] = 'waiting_for_token'
        # Simulate wait
        time.sleep(10)
        # 2. Sell token for SWAP.HIVE
        swaps[swap_id]['status'] = 'selling_token'
        # TODO: Use Engine/nectar to marketSell token for SWAP.HIVE
        time.sleep(5)
        # 3. Buy PEK with SWAP.HIVE
        swaps[swap_id]['status'] = 'buying_pek'
        # TODO: Use Engine/nectar to marketBuy PEK
        time.sleep(5)
        # 4. Send PEK to user
        swaps[swap_id]['status'] = 'sending_pek'
        # TODO: Use Engine/nectar to transfer PEK to user
        time.sleep(3)
        swaps[swap_id]['status'] = 'complete'
    except Exception as e:
        swaps[swap_id]['status'] = 'error'
        swaps[swap_id]['error'] = str(e)

# --- API: Start swap ---
@app.route('/start_swap', methods=['POST'])
def start_swap():
    data = request.json
    user = data.get('user')
    token = data.get('token')
    amount = data.get('amount')
    if not user or not token or not amount:
        return jsonify({'error': 'Missing parameters'}), 400
    swap_id = str(uuid.uuid4())
    swaps[swap_id] = {'user': user, 'token': token, 'amount': amount, 'status': 'initiated'}
    threading.Thread(target=process_swap, args=(swap_id, user, token, amount), daemon=True).start()
    return jsonify({'swap_id': swap_id, 'swap_account': SWAP_ACCOUNT})

# --- API: Check swap status ---
@app.route('/swap_status/<swap_id>', methods=['GET'])
def swap_status(swap_id):
    swap = swaps.get(swap_id)
    if not swap:
        return jsonify({'error': 'Swap not found'}), 404
    return jsonify(swap)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
