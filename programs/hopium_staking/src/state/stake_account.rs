use anchor_lang::prelude::*;

/// Stake tiers with amounts (in token base units) and lock periods (in seconds)
pub const STAKE_TIERS: [(u64, i64); 3] = [
    (100_000_000, 7 * 24 * 60 * 60),  // 100 tokens (assuming 6 decimals), 7 days
    (500_000_000, 3 * 24 * 60 * 60),  // 500 tokens, 3 days
    (1_000_000_000, 1 * 24 * 60 * 60), // 1000 tokens, 1 day
];

/// Burn rate as basis points (500 = 5%)
pub const BURN_RATE_BPS: u64 = 500;

/// Emergency withdraw penalty as basis points (3000 = 30%)
pub const EMERGENCY_PENALTY_BPS: u64 = 3000;

/// Maximum simulation ID length
pub const MAX_SIMULATION_ID_LEN: usize = 64;

/// PDA seed for stake accounts
pub const STAKE_SEED: &[u8] = b"stake";

/// Stake account storing user's staked tokens and lock state
#[account]
#[derive(Default)]
pub struct StakeAccount {
    /// Owner wallet that created this stake
    pub owner: Pubkey,

    /// Amount staked in token base units
    pub amount: u64,

    /// Tier index (0=100, 1=500, 2=1000)
    pub tier: u8,

    /// Unix timestamp when stake was created
    pub staked_at: i64,

    /// Unix timestamp when lock period ends
    pub unlock_at: i64,

    /// Whether this stake has been used for a simulation
    pub simulation_used: bool,

    /// ID of the simulation run (if used)
    pub simulation_id: String,

    /// Whether the 5% burn has been executed
    pub burned: bool,

    /// PDA bump seed
    pub bump: u8,
}

impl StakeAccount {
    /// Space required for the account
    /// 8 (discriminator) + 32 (owner) + 8 (amount) + 1 (tier) + 8 (staked_at)
    /// + 8 (unlock_at) + 1 (simulation_used) + 4 + 64 (simulation_id string)
    /// + 1 (burned) + 1 (bump)
    pub const LEN: usize = 8 + 32 + 8 + 1 + 8 + 8 + 1 + (4 + MAX_SIMULATION_ID_LEN) + 1 + 1;

    /// Check if stake can be released (lock period ended)
    pub fn can_release(&self, current_time: i64) -> bool {
        self.simulation_used && self.burned && current_time >= self.unlock_at
    }

    /// Calculate amount to return after burn (95%)
    pub fn return_amount(&self) -> u64 {
        let burn_amount = self.amount * BURN_RATE_BPS / 10_000;
        self.amount.saturating_sub(burn_amount)
    }

    /// Calculate emergency return amount (70%)
    pub fn emergency_return_amount(&self) -> u64 {
        let penalty = self.amount * EMERGENCY_PENALTY_BPS / 10_000;
        self.amount.saturating_sub(penalty)
    }

    /// Calculate burn amount (5%)
    pub fn burn_amount(&self) -> u64 {
        self.amount * BURN_RATE_BPS / 10_000
    }
}
