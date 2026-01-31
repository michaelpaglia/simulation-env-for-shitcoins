use anchor_lang::prelude::*;

pub mod errors;
pub mod instructions;
pub mod state;

use instructions::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod hopium_staking {
    use super::*;

    /// Stake tokens to gain simulation access.
    /// Creates a StakeAccount PDA and transfers tokens to escrow.
    pub fn stake(ctx: Context<Stake>, tier: u8) -> Result<()> {
        instructions::stake::handler(ctx, tier)
    }

    /// Mark a stake as used for a simulation run.
    /// Only callable by the backend authority.
    pub fn use_stake(ctx: Context<UseStake>, simulation_id: String) -> Result<()> {
        instructions::use_stake::handler(ctx, simulation_id)
    }

    /// Complete simulation and burn 5% of staked tokens.
    /// Called after simulation finishes successfully.
    pub fn complete_simulation(ctx: Context<CompleteSimulation>) -> Result<()> {
        instructions::complete_simulation::handler(ctx)
    }

    /// Release remaining stake after lock period ends.
    /// Returns 95% of original stake to user.
    pub fn release(ctx: Context<Release>) -> Result<()> {
        instructions::release::handler(ctx)
    }

    /// Emergency withdraw with 30% penalty.
    /// Returns 70% immediately, burns 30%.
    pub fn emergency_withdraw(ctx: Context<EmergencyWithdraw>) -> Result<()> {
        instructions::emergency_withdraw::handler(ctx)
    }
}
