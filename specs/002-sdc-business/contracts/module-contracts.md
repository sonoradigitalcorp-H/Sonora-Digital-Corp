# Internal Module Contracts: SDC Business Layer

**Feature**: `002-sdc-business`

## `Payments`

```python
def create_spei_payment(order: Order) -> SpeiReference  # returns CLABE + amount
def check_spei_payment(reference: str) -> PaymentStatus
def create_crypto_payment(order: Order, currency: str) -> CryptoPayment  # wallet address + QR
def check_crypto_payment(tx_hash: str) -> PaymentStatus
def process_webhook(payload: dict, provider: str) -> None
```

- SPEI via Conekta API (CLABE generation, webhook detection within 5 min)
- Crypto via blockchain RPC (BTC/ETH/SOL wallet generation, confirmation polling)
- Webhook retry with exponential backoff (3 attempts)

## `Gamification`

```python
def add_xp(user_id: str, action: str, amount: int) -> GamificationState
def get_tier(user_id: str) -> Tier
def check_progression(user_id: str) -> Tier  # returns new tier if promoted
def unlock_reward(user_id: str, tier: Tier) -> list[Reward]
```

- XP capped per action type (configurable)
- Tiers: Bronze (0), Silver (100), Gold (500), Platinum (2000)
- Rewards unlock automatically on progression

## `Affiliates`

```python
def generate_referral_link(user_id: str) -> str  # unique URL + QR
def track_referral(referral_code: str, purchase_id: str) -> Referral
def calculate_commission(referral: Referral) -> float
def process_withdrawal(user_id: str, amount: float, method: str) -> WithdrawalStatus
```

- Self-referral detection (reject if referrer == referee)
- Commission: flat % configurable per product category
- Payout via SPEI or crypto within 48 hours
