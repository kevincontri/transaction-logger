
## CLI Transaction logger 
#### A command-line application for transaction management with persistent JSON storage.

#### Features:
- Create multiple named ledgers (for example: Personal, Business, etc)
- Add transactions (with amount, category and as of type income or expense)
- View full transaction reports (total amounts, balance)
- Filter totals by category
- Edit existing transactions
- Delete transactions by index (index-1 based)
- Automatic JSON-based persistence (Each ledger is stored as a separate JSON file and will automatically be loaded on initialization)

#### Usage examples:
- Add a transaction:
```python transaction_logger.py add Personal -a 1500 -c salary -t income```

- View report:
```python transaction_logger.py report Personal```

- Filter by category:
```python transaction_logger.py report-category Personal food```

- Delete a transaction:
```python transaction_logger delete Personal 2```

- Edit a transaction:
```python transaction_logger edit Personal 1 -a 1800```

#### Structure Design
- A UUID is used as an internal transaction identity (for users a index-1 based is provided)
- JSON persistence ensures file state follows in-memory state.
- Ledger uses encapsulation logic and storage behavior.
