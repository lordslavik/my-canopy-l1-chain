# 🔗 MyCanopy L1 Chain

A minimal Layer 1 blockchain built on the Canopy Network testnet using Python.

## Overview

MyCanopy L1 is a developer-first blockchain that demonstrates core L1 mechanics:
block creation, transaction processing, and chain validation using proof-of-work consensus.
Built with pure Python — no external dependencies required.

## Features

- ⛓️ Block creation with cryptographic hashing (SHA-256)
- 💸 Simple transaction model (sender → recipient → amount)
- ⛏️ Proof-of-work mining with adjustable difficulty
- ✅ Chain integrity validation
- 🐍 Pure Python 3.10+ — zero dependencies

## Getting Started

clone the repo:
git clone https://github.com/lordslavik/my-canopy-l1-chain
cd my-canopy-l1-chain

run the chain:
python chain.py

## How It Works

1. Transactions are added to a pending pool
2. A miner calls mine_pending_transactions() to bundle them into a block
3. The block is hashed with proof-of-work and appended to the chain
4. Chain integrity can be verified at any time via is_valid()

## Project Structure

my-canopy-l1-chain/
├── chain.py       # Core blockchain logic
└── README.md      # Project documentation

## Roadmap

- [x] Basic proof-of-work consensus
- [x] Transaction model
- [ ] Peer-to-peer networking
- [ ] Wallet & key management
- [ ] Smart contract support (Canopy VM)

## Built With

- Language: Python 3.10+
- Network: Canopy Testnet
- Consensus: Proof of Work

## License

MIT — free to use, modify, and distribute.
