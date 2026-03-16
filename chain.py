import hashlib
import time
import json
from contracts import ContractRegistry, make_token_contract, make_voting_contract


class Block:
    def __init__(self, index, transactions, previous_hash, contract_calls=None, nonce=0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.contract_calls = contract_calls or []
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "contract_calls": self.contract_calls,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty=2):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block {self.index} mined: {self.hash}")


class Blockchain:
    def __init__(self):
        self.chain = [self._create_genesis_block()]
        self.pending_transactions = []
        self.pending_contract_calls = []
        self.difficulty = 2
        self.contract_registry = ContractRegistry()

    def _create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })

    def deploy_contract(self, owner, code, initial_state=None):
        contract = self.contract_registry.deploy(owner, code, initial_state)
        return contract.address

    def call_contract(self, address, method, caller, args=None):
        result = self.contract_registry.call(address, method, caller, args)
        self.pending_contract_calls.append({
            "address": address,
            "method": method,
            "caller": caller,
            "args": args,
            "result": str(result)
        })
        return result

    def mine_pending_transactions(self, miner_address):
        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash,
            contract_calls=self.pending_contract_calls
        )
        block.mine(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = [{"sender": "network", "recipient": miner_address, "amount": 1}]
        self.pending_contract_calls = []
        print(f"Block added. Chain length: {len(self.chain)}")

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True


if __name__ == "__main__":
    bc = Blockchain()
    print("=== MyCanopy L1 Chain with Smart Contracts ===\n")

    token_addr = bc.deploy_contract(
        owner="Alice",
        code=make_token_contract("Alice", 1_000_000),
        initial_state={"total_supply": 1_000_000, "balances": {}, "minted": 0}
    )

    vote_addr = bc.deploy_contract(owner="Charlie", code=make_voting_contract())

    bc.add_transaction("Alice", "Bob", 50)
    bc.call_contract(token_addr, "mint", "Alice", {"to": "Alice", "amount": 1000})
    bc.call_contract(token_addr, "transfer", "Alice", {"to": "Bob", "amount": 300})
    bc.mine_pending_transactions("miner1")

    r = bc.call_contract(vote_addr, "createProposal", "Charlie", {"title": "Upgrade consensus?"})
    pid = r["proposal_id"]
    bc.call_contract(vote_addr, "vote", "Alice",   {"proposal_id": pid, "vote": "yes"})
    bc.call_contract(vote_addr, "vote", "Bob",     {"proposal_id": pid, "vote": "yes"})
    bc.call_contract(vote_addr, "vote", "Charlie", {"proposal_id": pid, "vote": "no"})
    bc.mine_pending_transactions("miner1")

    print("\n--- Results ---")
    print("Chain valid:", bc.is_valid())
    print("Total blocks:", len(bc.chain))
    print("Alice token balance:", bc.call_contract(token_addr, "balanceOf", "Alice", {"address": "Alice"}))
    print("Bob token balance:  ", bc.call_contract(token_addr, "balanceOf", "Bob",   {"address": "Bob"}))
    print("Vote result:", bc.call_contract(vote_addr, "getResult", "Alice", {"proposal_id": pid}))
