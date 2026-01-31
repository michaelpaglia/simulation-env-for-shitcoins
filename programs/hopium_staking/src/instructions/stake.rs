use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

use crate::errors::HopiumError;
use crate::state::{StakeAccount, STAKE_SEED, STAKE_TIERS};

#[derive(Accounts)]
#[instruction(tier: u8)]
pub struct Stake<'info> {
    /// User creating the stake
    #[account(mut)]
    pub user: Signer<'info>,

    /// Stake account PDA to be created
    #[account(
        init,
        payer = user,
        space = StakeAccount::LEN,
        seeds = [STAKE_SEED, user.key().as_ref(), &[tier]],
        bump
    )]
    pub stake_account: Account<'info, StakeAccount>,

    /// User's token account to transfer from
    #[account(
        mut,
        constraint = user_token_account.owner == user.key(),
        constraint = user_token_account.mint == token_mint.key()
    )]
    pub user_token_account: Account<'info, TokenAccount>,

    /// Escrow token account (PDA-owned) to hold staked tokens
    #[account(
        mut,
        constraint = escrow_token_account.mint == token_mint.key()
    )]
    pub escrow_token_account: Account<'info, TokenAccount>,

    /// HOPIUM token mint
    /// CHECK: Validated by token account constraints
    pub token_mint: AccountInfo<'info>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<Stake>, tier: u8) -> Result<()> {
    require!(tier <= 2, HopiumError::InvalidTier);

    let (amount, lock_seconds) = STAKE_TIERS[tier as usize];
    let clock = Clock::get()?;
    let now = clock.unix_timestamp;

    // Verify user has enough tokens
    require!(
        ctx.accounts.user_token_account.amount >= amount,
        HopiumError::InsufficientBalance
    );

    // Transfer tokens to escrow
    let transfer_ctx = CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.escrow_token_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        },
    );
    token::transfer(transfer_ctx, amount)?;

    // Initialize stake account
    let stake_account = &mut ctx.accounts.stake_account;
    stake_account.owner = ctx.accounts.user.key();
    stake_account.amount = amount;
    stake_account.tier = tier;
    stake_account.staked_at = now;
    stake_account.unlock_at = now.checked_add(lock_seconds).ok_or(HopiumError::Overflow)?;
    stake_account.simulation_used = false;
    stake_account.simulation_id = String::new();
    stake_account.burned = false;
    stake_account.bump = ctx.bumps.stake_account;

    msg!(
        "Staked {} tokens (tier {}) for {} until {}",
        amount,
        tier,
        ctx.accounts.user.key(),
        stake_account.unlock_at
    );

    Ok(())
}
