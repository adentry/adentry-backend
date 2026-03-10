# Dev Log

## 2026-03-11

Project restarted with clean architecture.

Removed experimental `core` app and cleared database.

New app structure:
- accounts: User and identity.
    User
    Profile

- ledger: Accounting layer. No payment logic here.
    LedgerAccount
    AccountType
    
- payments: Payment instruments.
    PaymentMode
    PaymentAccount

- entries: Transaction engine. This is the core financial record.
    Entry
    EntryItem

Goal:
Build a personal finance ledger system with proper accounting structure.

Next task:
Implement User + Profile models.


