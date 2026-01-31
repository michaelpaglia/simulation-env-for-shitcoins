use anchor_lang::prelude::*;

#[error_code]
pub enum HopiumError {
    #[msg("Invalid stake tier. Must be 0 (100), 1 (500), or 2 (1000).")]
    InvalidTier,

    #[msg("Stake has already been used for a simulation.")]
    StakeAlreadyUsed,

    #[msg("Stake has not been used yet. Run a simulation first.")]
    StakeNotUsed,

    #[msg("Burn has already been executed for this stake.")]
    AlreadyBurned,

    #[msg("Lock period has not ended. Cannot release yet.")]
    LockPeriodActive,

    #[msg("Unauthorized. Only backend authority can call this.")]
    Unauthorized,

    #[msg("Simulation ID too long. Max 64 characters.")]
    SimulationIdTooLong,

    #[msg("Insufficient token balance for staking.")]
    InsufficientBalance,

    #[msg("Arithmetic overflow occurred.")]
    Overflow,
}
