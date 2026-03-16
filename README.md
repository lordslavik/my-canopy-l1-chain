# 🔗 MyCanopy L1 Chain

A Layer 1 blockchain with smart contract support, built on the Canopy Network testnet using Python.

## Overview

MyCanopy L1 is a developer-first blockchain that goes beyond basic block creation.
It features an on-chain smart contract engine with a token standard and governance voting —
all written in pure Python with zero external dependencies.

## Features

- ⛓️ Block creation with SHA-256 cryptographic hashing
- 💸 Transaction model (sender → recipient → amount)
- ⛏️ Proof-of-work mining with adjustable difficulty
- ✅ Chain integrity validation
- 📜 Smart contract engine with on-chain state
- 🪙 ERC20-like token contract (mint, transfer, balanceOf)
- 🗳️ On-chain governance voting contract
- 🐍 Pure Python 3.10+ — zero dependencies

## Project Structure

```
my-canopy-l1-chain/
├── chain.py        # Core blockchain + contract integration
├── contracts.py    # Smart contract engine + example contracts
└── README.md       # Documentation
```

## Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/my-canopy-l1-chain
cd my-canopy-l1-chain

# Run the full demo (chain + contracts)
python chain.py

# Run contracts demo only
python contracts.py
```

## Smart Contracts

### Token Contract
ERC20-like fungible token with mint, transfer, and balance query:

```python
token_addr = bc.deploy_contract(
    owner="Alice",
    code=make_token_contract("Alice", total_supply=1_000_000),
    initial_state={"total_supply": 1_000_000, "balances": {}, "minted": 0}
)
bc.call_contract(token_addr, "mint", "Alice", {"to": "Alice", "amount": 1000})
bc.call_contract(token_addr, "transfer", "Alice", {"to": "Bob", "amount": 300})
```

### Voting Contract
On-chain governance — create proposals and vote yes/no:

```python
vote_addr = bc.deploy_contract(owner="Charlie", code=make_voting_contract())
r = bc.call_contract(vote_addr, "createProposal", "Charlie", {"title": "Upgrade consensus?"})
bc.call_contract(vote_addr, "vote", "Alice", {"proposal_id": r["proposal_id"], "vote": "yes"})
```

## How It Works

1. Contracts are deployed and registered with a unique on-chain address
2. Transactions and contract calls are added to a pending pool
3. A miner bundles them into a block and mines it with proof-of-work
4. The block (including contract state changes) is appended to the chain
5. Chain validity is verified cryptographically at any time

## Roadmap

- [x] Proof-of-work consensus
- [x] Transaction model
- [x] Smart contract engine
- [x] Token contract (ERC20-like)
- [x] Governance voting contract
- [ ] REST API
- [ ] Wallet & key management
- [ ] P2P networking

## Built With

- Language: Python 3.10+
- Network: Canopy Testnet
- Consensus: Proof of Work

## License

MIT — free to use, modify, and distribute.
