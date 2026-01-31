use anchor_lang::prelude::*;

use crate::errors::HopiumError;
use crate::state::{StakeAccount, MAX_SIMULATION_ID_LEN};

/// Backend authority seeds for signing
pub const AUTHORITY_SEED: &[u8] = b"authority";

#[derive(Accounts)]
pub struct UseStake<'info> {
    /// Backend authority (PDA or configured pubkey)
    pub authority: Signer<'info>,

    /// Stake account to mark as used
    #[account(
        mut,
        constraint = !stake_account.simulation_used @ HopiumError::StakeAlreadyUsed
    )]
    pub stake_account: Account<'info, StakeAccount>,
}

pub fn handler(ctx: Context<UseStake>, simulation_id: String) -> Result<()> {
    require!(
        simulation_id.len() <= MAX_SIMULATION_ID_LEN,
        HopiumError::SimulationIdTooLong
    );

    let stake_account = &mut ctx.accounts.stake_account;
    stake_account.simulation_used = true;
    stake_account.simulation_id = simulation_id.clone();

    msg!(
        "Stake {} marked as used for simulation {}",
        stake_account.key(),
        simulation_id
    );

    Ok(())
}
