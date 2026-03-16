import hashlib
import time
import json


class ContractExecutionError(Exception):
    pass


class SmartContract:
    def __init__(self, owner, code: dict, initial_state: dict = None):
        self.owner = owner
        self.code = code  # dict of method_name -> python lambda/function
        self.state = initial_state or {}
        self.address = self._generate_address()
        self.created_at = time.time()
        self.call_history = []

    def _generate_address(self):
        raw = json.dumps({"owner": self.owner, "code": str(self.code), "ts": time.time()})
        return "0x" + hashlib.sha256(raw.encode()).hexdigest()[:40]

    def call(self, method: str, caller: str, args: dict = None):
        if method not in self.code:
            raise ContractExecutionError(f"Method '{method}' not found in contract")
        args = args or {}
        try:
            result = self.code[method](self.state, caller, args)
            self.call_history.append({
                "method": method,
                "caller": caller,
                "args": args,
                "result": result,
                "timestamp": time.time()
            })
            return result
        except Exception as e:
            raise ContractExecutionError(f"Execution failed: {e}")

    def get_state(self):
        return self.state.copy()

    def __repr__(self):
        return f"<SmartContract address={self.address} owner={self.owner} methods={list(self.code.keys())}>"


class ContractRegistry:
    def __init__(self):
        self.contracts = {}

    def deploy(self, owner: str, code: dict, initial_state: dict = None) -> SmartContract:
        contract = SmartContract(owner, code, initial_state)
        self.contracts[contract.address] = contract
        print(f"Contract deployed at {contract.address}")
        return contract

    def get(self, address: str) -> SmartContract:
        if address not in self.contracts:
            raise ContractExecutionError(f"No contract at address {address}")
        return self.contracts[address]

    def call(self, address: str, method: str, caller: str, args: dict = None):
        contract = self.get(address)
        return contract.call(method, caller, args)


# ── Example contracts ──────────────────────────────────────────────

def make_token_contract(owner: str, total_supply: int) -> dict:
    """ERC20-like token contract."""
    return {
        "balanceOf": lambda state, caller, args: state["balances"].get(args.get("address", caller), 0),

        "transfer": lambda state, caller, args: _transfer(state, caller, args),

        "mint": lambda state, caller, args: _mint(state, caller, args, owner, total_supply),

        "totalSupply": lambda state, caller, args: state["total_supply"],
    }


def _transfer(state, caller, args):
    to = args.get("to")
    amount = args.get("amount", 0)
    balances = state.setdefault("balances", {})
    if balances.get(caller, 0) < amount:
        raise ContractExecutionError("Insufficient balance")
    balances[caller] = balances.get(caller, 0) - amount
    balances[to] = balances.get(to, 0) + amount
    return {"status": "ok", "from": caller, "to": to, "amount": amount}


def _mint(state, caller, args, owner, total_supply):
    if caller != owner:
        raise ContractExecutionError("Only owner can mint")
    to = args.get("to", caller)
    amount = args.get("amount", 0)
    if state.get("minted", 0) + amount > total_supply:
        raise ContractExecutionError("Exceeds total supply")
    state["balances"] = state.get("balances", {})
    state["balances"][to] = state["balances"].get(to, 0) + amount
    state["minted"] = state.get("minted", 0) + amount
    return {"status": "minted", "to": to, "amount": amount}


def make_voting_contract() -> dict:
    """Simple on-chain voting contract."""
    return {
        "createProposal": lambda state, caller, args: _create_proposal(state, caller, args),
        "vote": lambda state, caller, args: _vote(state, caller, args),
        "getResult": lambda state, caller, args: _get_result(state, args),
    }


def _create_proposal(state, caller, args):
    proposals = state.setdefault("proposals", {})
    pid = str(len(proposals))
    proposals[pid] = {"title": args.get("title", ""), "yes": 0, "no": 0, "voters": [], "creator": caller}
    return {"proposal_id": pid}


def _vote(state, caller, args):
    pid = args.get("proposal_id")
    proposal = state["proposals"].get(pid)
    if not proposal:
        raise ContractExecutionError("Proposal not found")
    if caller in proposal["voters"]:
        raise ContractExecutionError("Already voted")
    proposal["voters"].append(caller)
    if args.get("vote") == "yes":
        proposal["yes"] += 1
    else:
        proposal["no"] += 1
    return {"status": "voted"}


def _get_result(state, args):
    pid = args.get("proposal_id")
    proposal = state["proposals"].get(pid)
    if not proposal:
        raise ContractExecutionError("Proposal not found")
    return {"yes": proposal["yes"], "no": proposal["no"], "total": len(proposal["voters"])}


# ── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    registry = ContractRegistry()

    print("=== Token Contract ===")
    token = registry.deploy(
        owner="Alice",
        code=make_token_contract("Alice", total_supply=1_000_000),
        initial_state={"total_supply": 1_000_000, "balances": {}, "minted": 0}
    )
    registry.call(token.address, "mint", "Alice", {"to": "Alice", "amount": 500})
    registry.call(token.address, "transfer", "Alice", {"to": "Bob", "amount": 200})
    print("Alice balance:", registry.call(token.address, "balanceOf", "Alice", {"address": "Alice"}))
    print("Bob balance:  ", registry.call(token.address, "balanceOf", "Bob", {"address": "Bob"}))

    print("\n=== Voting Contract ===")
    vote = registry.deploy(owner="Charlie", code=make_voting_contract())
    r = registry.call(vote.address, "createProposal", "Charlie", {"title": "Add new feature?"})
    pid = r["proposal_id"]
    registry.call(vote.address, "vote", "Alice", {"proposal_id": pid, "vote": "yes"})
    registry.call(vote.address, "vote", "Bob",   {"proposal_id": pid, "vote": "no"})
    registry.call(vote.address, "vote", "Charlie", {"proposal_id": pid, "vote": "yes"})
    print("Result:", registry.call(vote.address, "getResult", "Alice", {"proposal_id": pid}))
