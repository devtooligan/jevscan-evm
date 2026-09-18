# Beedle: review of unmatched Staking.sol flags

Scope: the scanner flagged `src/Staking.sol` for three bug types at 70% or more, and no judged finding in that file has those types. I read all of `~/dev/beedle/src/Staking.sol` (96 lines) and checked it against the judged findings that name Staking.sol:

- H-12: fee-on-transfer TKN in `deposit` and `withdraw`.
- H-13: `update()` runs lazily, so WETH from `Fees` is spread over a stake supply that has since changed.
- H-16: front-running the first WETH top-up with a 1-wei stake.
- H-17: sandwiching a claim with a large deposit and withdraw. The index uses the current `TKN.balanceOf` at update time.
- H-24: WETH that arrives while nobody is staked stays stuck.
- H-25: `claim` sets `balance` to the full WETH balance, so top-ups that were never indexed are lost.
- M-10: the full reward goes to whoever deposits just before it, with no staking time required.
- M-9: floating pragma (not specific to this file).

Every judged Staking finding is in the accounting, token, or economic category. None is in business logic, access control, or DoS, which explains why these three flags show up as unmatched.

## B1. Business logic / state machine (85%): duplicate of judged findings H-17, H-25, and H-13

The per-function hits point at `withdraw:48`, `claim:55`, `update:70`, `updateFor:88`, and `deposit:41`. All of these are the reward-index state machine, and each flaw in it is already judged:

- **Stake is transferred in before the index updates.** `deposit` calls `TKN.transferFrom` at `Staking.sol:39` before `updateFor` at `:40`. As a result, `update()` divides WETH that has not yet been indexed by a `totalSupply` (`:62`, `TKN.balanceOf(this)`) that already includes the new stake. The depositor's `supplyIndex` is then set to the new index (`:92`), so the depositor's share is never credited and stays stuck. This is the same root cause as H-17 ("index uses current TKN balance at update time") and H-13.
- **`claim` resets `balance` to the live WETH balance.** At `:57`, `claim` drops WETH that was never indexed, including WETH that `update()` skipped because `_ratio` rounded to 0 (`:69`). This is H-25.
- **Nothing is distributed at zero supply.** When `totalSupply == 0`, `update()` does nothing, and the first depositor's `supplyIndex` jumps to the current index. This is H-24 and H-16.

`withdraw:48` underflowing when `_amount > balances[msg.sender]` is a normal checked revert, not a flaw. I found no state-transition bug outside the judged set.

## B2. Access control (72%): false positive

The hits cite missing access control on `withdraw`, `claim`, `update`, and `updateFor`.

- `withdraw` and `claim` act only on `msg.sender`, at `:47-49` and `:54-56`.
- `update()` (`:61`) is permissionless by design. It only moves `index` forward by the WETH that has actually arrived. Calling it early or often helps stakers, which is H-13's own recommendation. The only effect an attacker can force is extra rounding dust: each call loses less than `totalSupply / 1e18` wei, which is negligible, and the `_ratio > 0` guard at `:69` stops `balance` from advancing when the ratio rounds to 0.
- `updateFor(address)` (`:80`) is public and accepts any recipient. It credits `claimable[recipient]` with that recipient's correct share, then syncs the recipient's `supplyIndex`. That is the same state the recipient's own next action would produce, so a third party cannot reduce anyone's rewards through it.
- `Staking` inherits `Ownable` but defines no owner-only function, so there is no privileged surface.

## B3. DoS / griefing (70%): duplicate of judged finding H-17, plus one variant that is real but not reportable

The DoS hits sit on `claim:55` and `withdraw:49`, where the flagged patterns are a zero-value transfer and a blocked push transfer. Neither applies here:

- **Zero-value transfers.** WETH9 accepts them.
- **Blocked push transfers.** A user's TKN or WETH payout is made only to that user and cannot be blocked by anyone else.
- **Unbounded loops.** There are none.

The griefing that does exist is reward dilution through the `TKN.balanceOf` denominator, which is H-17's deposit-and-withdraw sandwich.

**Donation variant (real, not reportable).** An attacker can transfer TKN directly to `Staking` without calling `deposit`. That permanently inflates `totalSupply` at `:62`. The donated tokens have no owner in `balances`, so their pro-rata share of every future top-up is folded into `index`, can never be claimed, and stays stuck in the contract.

- It is not reportable separately because it has the same root cause as H-17 (using `balanceOf` instead of a tracked total stake), and the fix is the same.
- The attacker gives up the donated TKN, and the WETH leak is proportional to the donation. At most this is a Low-severity economic grief.
