# PrescryptChain - a Python - SQL based lightweight, cryptographically enabled, centralised blockchain implementation – Originally forked from NaiveChain, but none of the original code remains.

### Motivation
All the current implementations of blockchains are tightly coupled with the larger context and problems they (e.g. Bitcoin or Ethereum) are trying to solve. This makes understanding blockchains a necessarily harder task, than it must be. Especially source-code-wisely. This project is an attempt to provide as concise and simple implementation of a blockchain as possible.


### What is blockchain
[From Wikipedia](https://en.wikipedia.org/wiki/Blockchain_(database)) : Blockchain is a distributed database that maintains a continuously-growing list of records called blocks secured from tampering and revision.

### Key concepts of Naivechain
Check also [this blog post](https://medium.com/@lhartikk/a-blockchain-in-200-lines-of-code-963cc1cc0e54#.dttbm9afr5) for a more detailed overview of the key concepts
* HTTP interface to control the node
* Use Websockets to communicate with other nodes (P2P)
* Super simple "protocols" in P2P communication
* Data is not persisted in nodes
* No proof-of-work or proof-of-stake: a block can be added to the blockchain without competition


### Quick start
(set up two connected nodes and mine 1 block)
```
cd ./PrescryptChain
python -m virtualenv venv/pychain
source venv/pychain/bin/activate
pip install -r requirements.txt
python manage.py runserver 8080
python manage.py client-prescrypto-2 9090
curl -H "Content-type:application/json" --data '{"data" : "Some data to the first block"}' http://localhost:8080/mineBlock
```



### HTTP API
##### Get blockchain
```
curl http://localhost:8080/api/v1/block
```
##### Create block
```
curl -H "Content-type:application/json" --data '{"data" : "Some data to the first block"}' http://localhost:8080/mineBlock
``
