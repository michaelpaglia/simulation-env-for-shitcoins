"""Solana RPC client wrapper for stake verification."""

import base64
import struct
import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

import httpx

from .constants import SOLANA_RPC_URL, HOPIUM_PROGRAM_ID, STAKE_SEED

logger = logging.getLogger(__name__)


@dataclass
class StakeAccountData:
    """Parsed stake account data from on-chain."""
    owner: str
    amount: int
    tier: int
    staked_at: datetime
    unlock_at: datetime
    simulation_used: bool
    simulation_id: str
    burned: bool
    bump: int

    @property
    def is_locked(self) -> bool:
        """Check if stake is still in lock period."""
        return datetime.utcnow() < self.unlock_at

    @property
    def can_release(self) -> bool:
        """Check if stake can be released."""
        return self.simulation_used and self.burned and not self.is_locked


class SolanaClient:
    """Lightweight Solana RPC client for stake verification."""

    def __init__(self, rpc_url: str = SOLANA_RPC_URL):
        self.rpc_url = rpc_url
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _rpc_call(self, method: str, params: list) -> dict:
        """Make an RPC call to Solana."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        response = await self._client.post(self.rpc_url, json=payload)
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        return result.get("result")

    async def get_account_info(self, pubkey: str) -> Optional[dict]:
        """Get account info for a public key."""
        result = await self._rpc_call(
            "getAccountInfo",
            [pubkey, {"encoding": "base64"}]
        )
        return result.get("value") if result else None

    async def get_stake_pda(self, owner: str, tier: int) -> str:
        """Derive stake account PDA address.

        Note: This is a simplified version. In production, use
        a proper PDA derivation library.
        """
        # For now, we'll call the RPC to verify the account exists
        # and return the expected address pattern
        # Real implementation would use nacl/ed25519 for PDA derivation
        return f"stake_{owner[:8]}_{tier}"  # Placeholder

    async def get_stake_account(self, pda_address: str) -> Optional[StakeAccountData]:
        """Fetch and parse a stake account.

        Args:
            pda_address: The stake account PDA address

        Returns:
            Parsed stake account data or None if not found
        """
        account_info = await self.get_account_info(pda_address)
        if not account_info:
            return None

        # Verify it's owned by our program
        if account_info.get("owner") != HOPIUM_PROGRAM_ID:
            logger.warning(f"Account {pda_address} not owned by program")
            return None

        # Parse the account data
        try:
            data_b64 = account_info["data"][0]
            data = base64.b64decode(data_b64)
            return self._parse_stake_account(data)
        except Exception as e:
            logger.error(f"Failed to parse stake account: {e}")
            return None

    def _parse_stake_account(self, data: bytes) -> StakeAccountData:
        """Parse stake account binary data.

        Account layout (Anchor):
        - 8 bytes: discriminator
        - 32 bytes: owner pubkey
        - 8 bytes: amount (u64)
        - 1 byte: tier (u8)
        - 8 bytes: staked_at (i64)
        - 8 bytes: unlock_at (i64)
        - 1 byte: simulation_used (bool)
        - 4 bytes: simulation_id string length
        - N bytes: simulation_id string data
        - 1 byte: burned (bool)
        - 1 byte: bump (u8)
        """
        offset = 8  # Skip discriminator

        # Owner (32 bytes)
        owner_bytes = data[offset:offset + 32]
        owner = base64.b64encode(owner_bytes).decode()  # Simplified
        offset += 32

        # Amount (8 bytes, little-endian u64)
        amount = struct.unpack_from("<Q", data, offset)[0]
        offset += 8

        # Tier (1 byte)
        tier = data[offset]
        offset += 1

        # Staked at (8 bytes, little-endian i64)
        staked_at_ts = struct.unpack_from("<q", data, offset)[0]
        staked_at = datetime.utcfromtimestamp(staked_at_ts)
        offset += 8

        # Unlock at (8 bytes, little-endian i64)
        unlock_at_ts = struct.unpack_from("<q", data, offset)[0]
        unlock_at = datetime.utcfromtimestamp(unlock_at_ts)
        offset += 8

        # Simulation used (1 byte)
        simulation_used = bool(data[offset])
        offset += 1

        # Simulation ID (4 byte length + string)
        sim_id_len = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        simulation_id = data[offset:offset + sim_id_len].decode("utf-8")
        offset += sim_id_len

        # Burned (1 byte)
        burned = bool(data[offset])
        offset += 1

        # Bump (1 byte)
        bump = data[offset]

        return StakeAccountData(
            owner=owner,
            amount=amount,
            tier=tier,
            staked_at=staked_at,
            unlock_at=unlock_at,
            simulation_used=simulation_used,
            simulation_id=simulation_id,
            burned=burned,
            bump=bump,
        )

    async def get_token_balance(self, wallet: str, mint: str) -> int:
        """Get SPL token balance for a wallet.

        Args:
            wallet: Wallet public key
            mint: Token mint address

        Returns:
            Token balance in base units
        """
        result = await self._rpc_call(
            "getTokenAccountsByOwner",
            [
                wallet,
                {"mint": mint},
                {"encoding": "jsonParsed"}
            ]
        )

        if not result or not result.get("value"):
            return 0

        # Sum balances from all token accounts for this mint
        total = 0
        for account in result["value"]:
            info = account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
            amount = info.get("tokenAmount", {}).get("amount", "0")
            total += int(amount)

        return total
