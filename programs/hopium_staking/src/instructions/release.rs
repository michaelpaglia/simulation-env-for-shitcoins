use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

use crate::errors::HopiumError;
use crate::state::StakeAccount;

use super::complete_simulation::ESCROW_SEED;

#[derive(Accounts)]
pub struct Release<'info> {
    /// Stake owner requesting release
    #[account(mut)]
    pub user: Signer<'info>,

    /// Stake account to release
    #[account(
        mut,
        constraint = stake_account.owner == user.key(),
        constraint = stake_account.simulation_used @ HopiumError::StakeNotUsed,
        constraint = stake_account.burned @ HopiumError::StakeNotUsed,
        close = user
    )]
    pub stake_account: Account<'info, StakeAccount>,

    /// User's token account to receive returned tokens
    #[account(
        mut,
        constraint = user_token_account.owner == user.key()
    )]
    pub user_token_account: Account<'info, TokenAccount>,

    /// Escrow token account holding remaining tokens
    #[account(mut)]
    pub escrow_token_account: Account<'info, TokenAccount>,

    /// Escrow authority PDA
    /// CHECK: Validated by seeds
    #[account(
        seeds = [ESCROW_SEED],
        bump
    )]
    pub escrow_authority: AccountInfo<'info>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<Release>) -> Result<()> {
    let clock = Clock::get()?;
    let stake_account = &ctx.accounts.stake_account;

    // Verify lock period has ended
    require!(
        stake_account.can_release(clock.unix_timestamp),
        HopiumError::LockPeriodActive
    );

    let return_amount = stake_account.return_amount();

    // Transfer remaining tokens back to user
    let escrow_seeds = &[ESCROW_SEED, &[ctx.bumps.escrow_authority]];
    let signer_seeds = &[&escrow_seeds[..]];

    let transfer_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.escrow_token_account.to_account_info(),
            to: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.escrow_authority.to_account_info(),
        },
        signer_seeds,
    );
    token::transfer(transfer_ctx, return_amount)?;

    msg!(
        "Released {} tokens to {} (stake {})",
        return_amount,
        ctx.accounts.user.key(),
        stake_account.key()
    );

    Ok(())
}
