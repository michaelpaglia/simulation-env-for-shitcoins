use anchor_lang::prelude::*;
use anchor_spl::token::{self, Burn, Mint, Token, TokenAccount, Transfer};

use crate::state::StakeAccount;

use super::complete_simulation::ESCROW_SEED;

#[derive(Accounts)]
pub struct EmergencyWithdraw<'info> {
    /// Stake owner requesting emergency withdraw
    #[account(mut)]
    pub user: Signer<'info>,

    /// Stake account to withdraw from
    #[account(
        mut,
        constraint = stake_account.owner == user.key(),
        close = user
    )]
    pub stake_account: Account<'info, StakeAccount>,

    /// User's token account to receive returned tokens
    #[account(
        mut,
        constraint = user_token_account.owner == user.key()
    )]
    pub user_token_account: Account<'info, TokenAccount>,

    /// Escrow token account holding staked tokens
    #[account(mut)]
    pub escrow_token_account: Account<'info, TokenAccount>,

    /// Token mint for burning the penalty
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

pub fn handler(ctx: Context<EmergencyWithdraw>) -> Result<()> {
    let stake_account = &ctx.accounts.stake_account;

    let return_amount = stake_account.emergency_return_amount();
    let penalty_amount = stake_account.amount.saturating_sub(return_amount);

    let escrow_seeds = &[ESCROW_SEED, &[ctx.bumps.escrow_authority]];
    let signer_seeds = &[&escrow_seeds[..]];

    // Burn the 30% penalty
    let burn_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        Burn {
            mint: ctx.accounts.token_mint.to_account_info(),
            from: ctx.accounts.escrow_token_account.to_account_info(),
            authority: ctx.accounts.escrow_authority.to_account_info(),
        },
        signer_seeds,
    );
    token::burn(burn_ctx, penalty_amount)?;

    // Transfer 70% back to user
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
        "Emergency withdraw: returned {} tokens, burned {} penalty for {}",
        return_amount,
        penalty_amount,
        ctx.accounts.user.key()
    );

    Ok(())
}
