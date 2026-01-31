use anchor_lang::prelude::*;
use anchor_spl::token::{self, Burn, Mint, Token, TokenAccount};

use crate::errors::HopiumError;
use crate::state::StakeAccount;

/// Escrow authority seeds
pub const ESCROW_SEED: &[u8] = b"escrow";

#[derive(Accounts)]
pub struct CompleteSimulation<'info> {
    /// Backend authority
    pub authority: Signer<'info>,

    /// Stake account to complete
    #[account(
        mut,
        constraint = stake_account.simulation_used @ HopiumError::StakeNotUsed,
        constraint = !stake_account.burned @ HopiumError::AlreadyBurned
    )]
    pub stake_account: Account<'info, StakeAccount>,

    /// Escrow token account holding the staked tokens
    #[account(
        mut,
        constraint = escrow_token_account.mint == token_mint.key()
    )]
    pub escrow_token_account: Account<'info, TokenAccount>,

    /// Token mint for burning
    #[account(mut)]
    pub token_mint: Account<'info, Mint>,

    /// Escrow authority PDA
    /// CHECK: Validated by seeds
    #[account(
        seeds = [ESCROW_SEED],
        bump
    )]
    pub escrow_authority: AccountInfo<'info>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<CompleteSimulation>) -> Result<()> {
    let stake_account = &mut ctx.accounts.stake_account;
    let burn_amount = stake_account.burn_amount();

    // Burn 5% of staked tokens
    let escrow_seeds = &[ESCROW_SEED, &[ctx.bumps.escrow_authority]];
    let signer_seeds = &[&escrow_seeds[..]];

    let burn_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        Burn {
            mint: ctx.accounts.token_mint.to_account_info(),
            from: ctx.accounts.escrow_token_account.to_account_info(),
            authority: ctx.accounts.escrow_authority.to_account_info(),
        },
        signer_seeds,
    );
    token::burn(burn_ctx, burn_amount)?;

    stake_account.burned = true;

    msg!(
        "Burned {} tokens (5%) from stake {}",
        burn_amount,
        stake_account.key()
    );

    Ok(())
}
