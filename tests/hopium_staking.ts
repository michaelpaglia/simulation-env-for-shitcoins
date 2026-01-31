import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { HopiumStaking } from "../target/types/hopium_staking";
import {
  createMint,
  createAccount,
  mintTo,
  getAccount,
  TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import { expect } from "chai";

describe("hopium_staking", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.HopiumStaking as Program<HopiumStaking>;

  let tokenMint: anchor.web3.PublicKey;
  let userTokenAccount: anchor.web3.PublicKey;
  let escrowTokenAccount: anchor.web3.PublicKey;
  let escrowAuthority: anchor.web3.PublicKey;
  let escrowBump: number;

  const user = anchor.web3.Keypair.generate();
  const mintAuthority = anchor.web3.Keypair.generate();

  const TIER_0_AMOUNT = 100_000_000; // 100 tokens with 6 decimals

  before(async () => {
    // Airdrop SOL to user
    const sig = await provider.connection.requestAirdrop(
      user.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    );
    await provider.connection.confirmTransaction(sig);

    // Create token mint
    tokenMint = await createMint(
      provider.connection,
      user,
      mintAuthority.publicKey,
      null,
      6 // 6 decimals like USDC
    );

    // Create user token account
    userTokenAccount = await createAccount(
      provider.connection,
      user,
      tokenMint,
      user.publicKey
    );

    // Mint tokens to user
    await mintTo(
      provider.connection,
      user,
      tokenMint,
      userTokenAccount,
      mintAuthority,
      1_000_000_000 // 1000 tokens
    );

    // Derive escrow authority PDA
    [escrowAuthority, escrowBump] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("escrow")],
      program.programId
    );

    // Create escrow token account (owned by PDA)
    escrowTokenAccount = await createAccount(
      provider.connection,
      user,
      tokenMint,
      escrowAuthority,
      undefined,
      undefined,
      TOKEN_PROGRAM_ID
    );
  });

  it("stakes tokens and creates PDA", async () => {
    const tier = 0; // 100 tokens, 7 day lock

    const [stakeAccount] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake"), user.publicKey.toBuffer(), Buffer.from([tier])],
      program.programId
    );

    const userBalanceBefore = (await getAccount(provider.connection, userTokenAccount)).amount;

    await program.methods
      .stake(tier)
      .accounts({
        user: user.publicKey,
        stakeAccount,
        userTokenAccount,
        escrowTokenAccount,
        tokenMint,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([user])
      .rpc();

    // Verify stake account was created
    const stake = await program.account.stakeAccount.fetch(stakeAccount);
    expect(stake.owner.toString()).to.equal(user.publicKey.toString());
    expect(stake.amount.toNumber()).to.equal(TIER_0_AMOUNT);
    expect(stake.tier).to.equal(tier);
    expect(stake.simulationUsed).to.be.false;
    expect(stake.burned).to.be.false;

    // Verify tokens were transferred
    const userBalanceAfter = (await getAccount(provider.connection, userTokenAccount)).amount;
    expect(Number(userBalanceBefore) - Number(userBalanceAfter)).to.equal(TIER_0_AMOUNT);

    const escrowBalance = (await getAccount(provider.connection, escrowTokenAccount)).amount;
    expect(Number(escrowBalance)).to.equal(TIER_0_AMOUNT);
  });

  it("prevents double stake for same tier", async () => {
    const tier = 0;

    const [stakeAccount] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake"), user.publicKey.toBuffer(), Buffer.from([tier])],
      program.programId
    );

    try {
      await program.methods
        .stake(tier)
        .accounts({
          user: user.publicKey,
          stakeAccount,
          userTokenAccount,
          escrowTokenAccount,
          tokenMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          systemProgram: anchor.web3.SystemProgram.programId,
        })
        .signers([user])
        .rpc();
      expect.fail("Should have thrown error");
    } catch (err) {
      // Expected: account already exists
      expect(err).to.exist;
    }
  });

  it("marks stake as used for simulation", async () => {
    const tier = 0;
    const simulationId = "sim_test_001";

    const [stakeAccount] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake"), user.publicKey.toBuffer(), Buffer.from([tier])],
      program.programId
    );

    // Note: In production, authority would be backend keypair
    // For testing, we use provider wallet
    await program.methods
      .useStake(simulationId)
      .accounts({
        authority: provider.wallet.publicKey,
        stakeAccount,
      })
      .rpc();

    const stake = await program.account.stakeAccount.fetch(stakeAccount);
    expect(stake.simulationUsed).to.be.true;
    expect(stake.simulationId).to.equal(simulationId);
  });

  it("prevents double use of stake", async () => {
    const tier = 0;

    const [stakeAccount] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake"), user.publicKey.toBuffer(), Buffer.from([tier])],
      program.programId
    );

    try {
      await program.methods
        .useStake("another_sim")
        .accounts({
          authority: provider.wallet.publicKey,
          stakeAccount,
        })
        .rpc();
      expect.fail("Should have thrown error");
    } catch (err) {
      expect(err.error.errorCode.code).to.equal("StakeAlreadyUsed");
    }
  });

  it("burns 5% on simulation completion", async () => {
    const tier = 0;

    const [stakeAccount] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake"), user.publicKey.toBuffer(), Buffer.from([tier])],
      program.programId
    );

    const escrowBalanceBefore = (await getAccount(provider.connection, escrowTokenAccount)).amount;

    await program.methods
      .completeSimulation()
      .accounts({
        authority: provider.wallet.publicKey,
        stakeAccount,
        escrowTokenAccount,
        tokenMint,
        escrowAuthority,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    const stake = await program.account.stakeAccount.fetch(stakeAccount);
    expect(stake.burned).to.be.true;

    // Verify 5% was burned
    const burnAmount = TIER_0_AMOUNT * 0.05;
    const escrowBalanceAfter = (await getAccount(provider.connection, escrowTokenAccount)).amount;
    expect(Number(escrowBalanceBefore) - Number(escrowBalanceAfter)).to.equal(burnAmount);
  });

  // Note: Release test would require waiting for lock period or mocking time
  // Emergency withdraw test can run immediately

  it("allows emergency withdraw with 30% penalty", async () => {
    // Create a new stake for emergency withdraw test
    const tier = 1; // 500 tokens

    const [stakeAccount] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake"), user.publicKey.toBuffer(), Buffer.from([tier])],
      program.programId
    );

    // First stake
    await program.methods
      .stake(tier)
      .accounts({
        user: user.publicKey,
        stakeAccount,
        userTokenAccount,
        escrowTokenAccount,
        tokenMint,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([user])
      .rpc();

    const userBalanceBefore = (await getAccount(provider.connection, userTokenAccount)).amount;

    // Emergency withdraw
    await program.methods
      .emergencyWithdraw()
      .accounts({
        user: user.publicKey,
        stakeAccount,
        userTokenAccount,
        escrowTokenAccount,
        tokenMint,
        escrowAuthority,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([user])
      .rpc();

    // Verify 70% returned (30% penalty)
    const tier1Amount = 500_000_000;
    const expectedReturn = tier1Amount * 0.7;
    const userBalanceAfter = (await getAccount(provider.connection, userTokenAccount)).amount;
    expect(Number(userBalanceAfter) - Number(userBalanceBefore)).to.equal(expectedReturn);
  });
});
