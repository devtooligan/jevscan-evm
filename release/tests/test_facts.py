"""TxFacts extraction on small hand-made traces: python -m pytest monitor/tests."""

import pytest

from jevscan_monitor import facts
from jevscan_monitor.facts import ETH, TOPIC, WETH
from tests.helpers import (
    BLOCK_NUMBER,
    BLOCK_TIME,
    BOT,
    BUILDER,
    LENDER,
    MIXER,
    POOL_A,
    POOL_B,
    SENDER,
    TOKEN,
    TOKEN_2,
    VICTIM,
    WALLET,
    addr,
    amount_data,
    chain_data,
    context,
    frame,
    kinds,
    log,
    topic,
    transfer,
)

ONE = 10**18
USDX = 10**6  # TOKEN has six decimals and is worth $1


def core_of(trace: dict, **kwargs) -> facts.Core:
    return facts.extract(*chain_data(trace, **kwargs))


def net(core: facts.Core) -> dict:
    return facts.net_ledger(core.movements)


def test_a_reverted_frame_takes_its_descendants_eth_and_logs_with_it():
    trace = frame(SENDER, BOT, calls=[
        frame(BOT, POOL_A, value=5 * ONE, error="execution reverted", logs=[transfer(TOKEN, POOL_A, BOT, 9)], calls=[
            frame(POOL_A, WALLET, value=3 * ONE, calls=[frame(WALLET, TOKEN, logs=[transfer(TOKEN, WALLET, BOT, 4)])])]),
        frame(BOT, WALLET, value=1 * ONE)])
    core = core_of(trace)
    assert net(core) == {BOT: {ETH: -ONE}, WALLET: {ETH: ONE}}
    assert core.reverted_inner_calls == 1
    assert core.calls == 5


def test_trace_logs_that_survive_must_equal_the_receipt():
    trace = frame(SENDER, TOKEN, logs=[transfer(TOKEN, SENDER, WALLET, 5)])
    with pytest.raises(ValueError, match="differ from the receipt"):
        core_of(trace, receipt_logs=[])


def test_a_failed_transaction_stays_in_the_window_and_moves_nothing():
    trace = frame(SENDER, BOT, value=2 * ONE, error="out of gas", calls=[frame(BOT, WALLET, value=ONE)])
    core = core_of(trace)
    assert not core.succeeded
    assert core.movements == [] and core.log_movements == []
    record = facts.finish(core, context(kinds=kinds(wallet=[SENDER], contract=[BOT])))
    assert record["status"] == "failed" and record["ledger"] == []


def test_receipt_and_trace_disagreeing_about_success_is_an_error():
    block, tx, receipt, trace = chain_data(frame(SENDER, BOT))
    with pytest.raises(ValueError, match="disagree about success"):
        facts.extract(block, tx, receipt | {"status": "0x0"}, trace)


def test_weth_wrap_and_unwrap_keep_every_balance_right():
    deposit = log(WETH, [TOPIC["Deposit(address,uint256)"], topic(BOT)], amount_data(4 * ONE))
    withdrawal = log(WETH, [TOPIC["Withdrawal(address,uint256)"], topic(BOT)], amount_data(ONE), position=0)
    trace = frame(SENDER, BOT, value=4 * ONE, calls=[
        frame(BOT, WETH, value=4 * ONE, logs=[deposit]),
        frame(BOT, WETH, logs=[withdrawal], calls=[frame(WETH, BOT, value=ONE)]),
        frame(BOT, WETH, logs=[transfer(WETH, BOT, POOL_A, 3 * ONE)])])
    ledger = net(core_of(trace))
    assert ledger[SENDER] == {ETH: -4 * ONE}
    assert ledger[BOT] == {ETH: ONE}  # 4 in, 4 wrapped, 1 unwrapped, 3 WETH passed on: no WETH left
    assert ledger[POOL_A] == {WETH: 3 * ONE}
    assert WETH not in ledger  # the wrapper itself is not a party


def test_another_contracts_deposit_event_is_not_a_weth_wrap():
    fake = log(POOL_A, [TOPIC["Deposit(address,uint256)"], topic(BOT)], amount_data(ONE))
    assert facts.log_movement(fake) is None


def test_an_nft_transfer_moves_one_unit_of_its_collection_and_its_token_id_is_not_an_amount():
    nft = log(TOKEN_2, [facts.TRANSFER, topic(SENDER), topic(WALLET), "0x" + format(123456, "064x")])
    core = core_of(frame(SENDER, TOKEN_2, logs=[nft]))
    assert core.nft_transfers == 1 and core.nft_collections == {TOKEN_2}
    assert core.movements == [facts.Movement(TOKEN_2, SENDER, WALLET, 1)]


def test_delegatecall_repeats_its_parents_value_but_moves_nothing():
    trace = frame(SENDER, BOT, value=ONE, calls=[frame(BOT, POOL_A, kind="DELEGATECALL", value=ONE)])
    assert net(core_of(trace)) == {SENDER: {ETH: -ONE}, BOT: {ETH: ONE}}


def test_a_contract_creation_has_no_recipient_and_its_contract_joins_the_senders_side():
    trace = frame(SENDER, BOT, kind="CREATE", calls=[
        frame(BOT, POOL_A, kind="CREATE2"),
        frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, POOL_A, 500_000 * USDX)])])])
    core = core_of(trace, nonce=0)
    assert core.tx["to"] is None and core.root.target == BOT
    assert facts.created_side(core) == [SENDER, BOT, POOL_A]
    record = facts.finish(core, context(kinds=kinds(wallet=[SENDER], contract=[BOT, POOL_A, VICTIM])))
    assert record["tx"]["creates"] == BOT and record["tx"]["to"] is None
    assert record["sender_side"]["members"] == ["sender", "sender_contract_1", "sender_contract_2"]
    assert record["sender_side"]["net_usd"] == 500_000
    assert record["sender_side"]["own_capital_usd"] == 0
    assert record["parties"]["sender_contract_1"]["source_verified"] is False
    assert not record["trivial"]


def test_own_capital_is_what_the_senders_side_held_before_not_what_it_borrowed():
    swap = frame(SENDER, POOL_A, calls=[
        frame(POOL_A, TOKEN, logs=[transfer(TOKEN, SENDER, POOL_A, 1_000 * USDX)]),
        frame(POOL_A, SENDER, value=ONE // 2)])
    record = facts.finish(core_of(swap), context(kinds=kinds(wallet=[SENDER], contract=[POOL_A])))
    assert record["sender_side"]["own_capital_usd"] == 1_000
    assert record["sender_side"]["net_usd"] == 0  # $1,000 of tokens out, half an ETH at $2,000 in


def flash_loan_trace(repay: int) -> dict:
    return frame(SENDER, BOT, kind="CREATE", calls=[frame(BOT, LENDER, calls=[
        frame(LENDER, TOKEN, logs=[transfer(TOKEN, LENDER, BOT, 1_000_000 * USDX)]),
        frame(LENDER, BOT, calls=[
            frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, BOT, 300_000 * USDX)])]),
            frame(BOT, TOKEN, logs=[transfer(TOKEN, BOT, LENDER, repay)])])])])


def test_a_flash_loan_is_found_from_its_shape_with_no_known_event():
    core = core_of(flash_loan_trace(repay=1_000_900 * USDX))
    assert core.flash_loans == [{"lender": LENDER, "asset": TOKEN, "amount": 1_000_000 * USDX, "source": "shape"}]
    record = facts.finish(core, context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER, VICTIM])))
    assert record["sender_side"]["own_capital_usd"] == 0
    assert record["sender_side"]["net_usd"] == 299_100


def test_funds_that_are_not_repaid_in_full_are_not_a_flash_loan():
    assert core_of(flash_loan_trace(repay=999_999 * USDX)).flash_loans == []


def test_an_arbitrage_cycle_is_not_a_flash_loan():
    """The bot's own funds go to the first pool and come back from the last one: nothing was borrowed."""
    trace = frame(SENDER, BOT, calls=[
        frame(BOT, TOKEN, logs=[transfer(TOKEN, BOT, POOL_A, 50_000 * USDX)]),
        frame(BOT, POOL_A, calls=[frame(POOL_A, TOKEN_2, logs=[transfer(TOKEN_2, POOL_A, POOL_B, 7)])]),
        frame(BOT, POOL_B, calls=[frame(POOL_B, TOKEN, logs=[transfer(TOKEN, POOL_B, BOT, 50_200 * USDX)])])])
    assert core_of(trace).flash_loans == []


def test_a_lenders_flash_loan_event_is_decoded():
    event = log(LENDER, [TOPIC["FlashLoan(address,address,uint256)"], topic(BOT), topic(TOKEN)], amount_data(4_000 * USDX))
    core = core_of(frame(SENDER, BOT, calls=[frame(BOT, LENDER, logs=[event | {"position": "0x1"}], calls=[
        frame(LENDER, TOKEN, logs=[transfer(TOKEN, LENDER, BOT, 4_000 * USDX)])])]))
    assert core.flash_loans == [{"lender": LENDER, "asset": TOKEN, "amount": 4_000 * USDX, "source": "event"}]


def test_reentrancy_through_the_senders_contract_is_found():
    trace = frame(SENDER, BOT, kind="CREATE", calls=[frame(BOT, VICTIM, calls=[
        frame(VICTIM, BOT, value=ONE, calls=[frame(BOT, VICTIM)])])])
    record = facts.finish(core_of(trace), context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM])))
    assert record["reentrancy"] == [{"contract": "unknown_contract_1", "through": "sender_contract_1", "read_only": False}]


def test_read_only_reentrancy_is_marked_as_such():
    """Another protocol reads the victim's state while the victim is mid-call through the sender's contract."""
    trace = frame(SENDER, BOT, kind="CREATE", calls=[frame(BOT, VICTIM, calls=[frame(VICTIM, BOT, value=ONE, calls=[
        frame(BOT, LENDER, calls=[frame(LENDER, VICTIM, kind="STATICCALL", value=None)])])])])
    record = facts.finish(core_of(trace), context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM, LENDER])))
    assert [(r["through"], r["read_only"]) for r in record["reentrancy"]] == [("sender_contract_1", True)]


def test_calling_a_flash_lender_back_inside_its_callback_is_not_reentrancy():
    record = facts.finish(core_of(flash_loan_trace(repay=1_000_900 * USDX) | {}),
                          context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER, VICTIM])))
    assert record["reentrancy"] == []
    nested = frame(SENDER, BOT, kind="CREATE", calls=[frame(BOT, LENDER, calls=[
        frame(LENDER, TOKEN, logs=[transfer(TOKEN, LENDER, BOT, 9 * USDX)]),
        frame(LENDER, BOT, calls=[frame(BOT, LENDER), frame(BOT, TOKEN, logs=[transfer(TOKEN, BOT, LENDER, 9 * USDX)])])])])
    core = core_of(nested)
    assert core.reentries and facts.reentries_shown(core, {}, False) == []


def test_a_router_calling_back_into_itself_through_a_pool_is_not_sender_controlled():
    """A labeled router is re-entered by a pool's callback in every swap; the sender controls neither."""
    trace = frame(SENDER, POOL_A, calls=[frame(POOL_A, POOL_B, calls=[frame(POOL_B, POOL_A)])])
    labels = {POOL_A: {"name": "Some Router", "category": "exchange", "symbol": None}}
    assert facts.reentries_shown(core_of(trace), labels, False) == []


def test_the_trivial_flag_covers_plain_transfers_and_proxied_token_transfers_only():
    assert core_of(frame(SENDER, WALLET, value=ONE, selector="0x")).trivial
    proxied = frame(SENDER, TOKEN, calls=[frame(TOKEN, addr(50), kind="DELEGATECALL", logs=[transfer(TOKEN, SENDER, WALLET, 5)])])
    assert core_of(proxied).trivial
    assert not core_of(frame(SENDER, BOT, calls=[frame(BOT, POOL_A)])).trivial
    assert not core_of(frame(SENDER, BOT, kind="CREATE")).trivial


def test_a_missing_required_field_fails_loudly_and_an_unknown_type_does_not():
    block, tx, receipt, trace = chain_data(frame(SENDER, WALLET, value=ONE), tx_type="0x7f")
    assert facts.extract(block, tx, receipt, trace).succeeded
    del tx["nonce"]
    with pytest.raises(ValueError, match="missing required field 'nonce'"):
        facts.extract(block, tx, receipt, trace)


def test_builder_payment_is_the_priority_fee_plus_direct_transfers():
    core = core_of(frame(SENDER, BOT, calls=[frame(BOT, BUILDER, value=ONE)]))
    assert core.fee_wei == 100_000 * 12 * 10**9
    assert core.builder_payment_wei == 100_000 * 2 * 10**9 + ONE


def test_privileged_events_name_who_gains_the_power():
    event = log(VICTIM, [TOPIC["OwnershipTransferred(address,address)"], topic(WALLET), topic(SENDER)])
    record = facts.finish(core_of(frame(SENDER, VICTIM, logs=[event])),
                          context(kinds=kinds(wallet=[SENDER, WALLET], contract=[VICTIM])))
    assert record["privileged_events"] == [{"contract": "unknown_contract_1", "event": "OwnershipTransferred", "subject": "sender"}]


def test_privileged_event_with_a_missing_indexed_subject_is_retained_without_guessing_one():
    event = log(VICTIM, [TOPIC["OwnershipTransferred(address,address)"]], amount_data(0) + amount_data(1)[2:])
    core = core_of(frame(SENDER, VICTIM, logs=[event]))

    assert core.privileged == [{"emitter": VICTIM, "event": "OwnershipTransferred", "subject": None}]


def test_drain_share_is_the_loss_over_the_balance_one_block_earlier():
    trace = frame(SENDER, BOT, calls=[frame(BOT, VICTIM, calls=[
        frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, BOT, 910_000 * USDX)])])])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM]),
                  balances_before={(VICTIM, TOKEN, BLOCK_NUMBER, 3): 1_000_000 * USDX})
    record = facts.finish(core_of(trace), ctx)
    assert [(d["party"], d["asset"], d["share_of_prior_balance"], d["usd"]) for d in record["drains"]] == \
        [("unknown_contract_2", "USDX", 0.91, 910_000)]
    assert (record["drains"][0]["gave_usd"], record["drains"][0]["received_usd"]) == (910_000, 0)


def test_an_unpriced_token_is_marked_and_kept_out_of_usd_totals():
    trace = frame(SENDER, BOT, calls=[frame(BOT, TOKEN_2, logs=[transfer(TOKEN_2, VICTIM, SENDER, 5 * ONE)])])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM]), decimals={TOKEN_2: 18})
    record = facts.finish(core_of(trace), ctx)
    change = record["ledger"][0]["changes"][0]
    assert (change["asset"], change["usd"], change["amount"]) == ("unrecognized_token_1", None, 5.0)
    side = record["sender_side"]
    assert side["net_usd"] == 0 and side["unpriced_assets"] == ["unrecognized_token_1"]


def labeled(address: str, age_days: int, category: str = "lending") -> dict:
    return {"labels": {address: {"name": "Big Protocol: Pool", "category": category, "symbol": None}},
            "creations": {address: {"creator": addr(98), "block": 5, "timestamp": BLOCK_TIME - age_days * 86400}}}


@pytest.mark.parametrize("age_days, alias", [(400, "Big Protocol: Pool"), (29, "unknown_contract_1")])
def test_a_label_shows_only_on_a_contract_older_than_thirty_days(age_days: int, alias: str):
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[VICTIM]), **labeled(VICTIM, age_days))
    record = facts.finish(core_of(frame(SENDER, VICTIM)), ctx)
    assert record["entry"]["alias"] == alias


def test_function_names_resolve_only_for_calls_into_established_labeled_contracts():
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[VICTIM, BOT]), function_names={"0x12345678": "flashLoan"},
                  **labeled(VICTIM, 400))
    assert facts.finish(core_of(frame(SENDER, VICTIM)), ctx)["entry"]["function"] == "flashLoan"
    assert facts.finish(core_of(frame(SENDER, BOT)), ctx)["entry"]["function"] is None


def test_lending_borrow_event_linked_to_same_pool_mint_is_exposed_without_assuming_authorization():
    borrow = log(LENDER, [TOPIC["Borrow(address,address,address,uint256,uint8,uint256,uint16)"]])
    trace = frame(SENDER, LENDER, logs=[borrow], calls=[
        frame(LENDER, TOKEN, logs=[transfer(TOKEN, facts.ZERO, SENDER, 1_000 * USDX)])
    ])
    record = facts.finish(core_of(trace), context(kinds=kinds(wallet=[SENDER], contract=[LENDER]), **labeled(LENDER, 400)))

    assert record["lending_accounting_issuances"] == [{
        "borrower": "sender", "lender": "Big Protocol: Pool",
        "issued": {"asset": "USDX", "amount_raw": str(1_000 * USDX), "amount": 1_000.0, "usd": 1_000.0},
    }]


def test_a_token_shows_a_symbol_only_when_it_is_labeled_and_older_than_thirty_days():
    priced, young = addr(60), addr(61)
    trace = frame(SENDER, BOT, calls=[frame(BOT, t, logs=[transfer(t, VICTIM, SENDER, 10**18)]) for t in (TOKEN, priced, young)])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM]),
                  labels={young: {"name": "NEW token", "category": "token", "symbol": "NEW"}},
                  prices={priced: {"usd": 1.0, "symbol": "USDC", "decimals": 18}},  # the symbol its deployer chose
                  creations={priced: {"creator": addr(97), "block": 9, "timestamp": BLOCK_TIME - 900 * 86400},
                             young: {"creator": addr(97), "block": 9, "timestamp": BLOCK_TIME - 3600}})
    record = facts.finish(core_of(trace), ctx)
    symbols = {info["address"]: info["symbol"] for info in record["assets"].values()}
    assert symbols == {TOKEN: "USDX", priced: None, young: None}


def test_the_call_tree_folds_proxies_drops_reads_and_token_calls_and_collapses_repeats():
    pay = facts.SELECTOR["transfer(address,uint256)"]
    loop = [frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, selector=pay, logs=[transfer(TOKEN, VICTIM, BOT, 1)])])
            for _ in range(37)]
    trace = frame(SENDER, BOT, calls=[
        frame(BOT, POOL_A, kind="STATICCALL", value=None),
        frame(BOT, POOL_A, kind="STATICCALL", value=None, selector=facts.SELECTOR["getReserves()"]),
        frame(BOT, POOL_B, calls=[frame(POOL_B, addr(70), kind="DELEGATECALL", calls=[frame(POOL_B, WALLET, value=ONE, selector="0x")])]),
        *loop])
    record = facts.finish(core_of(trace), context(kinds=kinds(wallet=[SENDER, WALLET], contract=[BOT, VICTIM, POOL_A, POOL_B])))
    bot, pool_b, victim, pool_a = (record["entry"]["alias"], *(f"unknown_contract_{n}" for n in (2, 3, 4)))
    assert record["call_tree"] == [
        f"{bot} reads a price from {pool_a}",
        f"{bot} calls {pool_b}",
        f"  {pool_b} pays unknown_wallet_1 with 1 ETH",
        f"{bot} calls {victim}  (x37)"]
    assert record["call_shape"]["repeated_calls"][0]["count"] == 37


def test_the_call_tree_stays_under_its_token_cap_however_large_the_trace():
    def nest(depth: int) -> list[dict]:
        return [] if depth == 0 else [frame(addr(200 + depth), addr(300 + depth * 10 + i), calls=nest(depth - 1)) for i in range(4)]
    record = facts.finish(core_of(frame(SENDER, BOT, calls=nest(6))), context(kinds=kinds(wallet=[SENDER], contract=[BOT])))
    assert sum(len(line) + 1 for line in record["call_tree"]) / 3.5 <= facts.TREE_TOKEN_CAP
    assert "not shown" in "\n".join(record["call_tree"])


def test_a_vault_that_pays_out_assets_is_seen_to_take_its_own_shares_back():
    """The burn of a vault's shares goes to the zero address; booked against the vault, the payout is a fair trade."""
    vault = TOKEN_2
    trace = frame(SENDER, vault, logs=[transfer(vault, SENDER, facts.ZERO, 5 * ONE)], calls=[
        frame(vault, TOKEN, logs=[transfer(TOKEN, vault, SENDER, 1_000 * USDX)])])
    ledger = net(core_of(trace))
    assert ledger[vault] == {TOKEN: -1_000 * USDX, vault: 5 * ONE}
    assert ledger[SENDER] == {TOKEN: 1_000 * USDX, vault: -5 * ONE}


def test_a_token_contract_that_only_issues_its_own_token_is_not_a_party_and_not_drained():
    mint = frame(SENDER, TOKEN, logs=[transfer(TOKEN, facts.ZERO, SENDER, 1_000_000 * USDX)])
    core = core_of(mint)
    assert net(core) == {SENDER: {TOKEN: 1_000_000 * USDX}}
    record = facts.finish(core, context(kinds=kinds(wallet=[SENDER], contract=[TOKEN])))
    assert record["drains"] == []
    assert [(m["asset"], m["to"], m["usd"]) for m in record["minted"]] == [("USDX", "sender", 1_000_000)]


def test_a_mint_to_the_senders_contract_is_reported_even_when_it_is_sold_at_once():
    trace = frame(SENDER, BOT, kind="CREATE", calls=[
        frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, logs=[transfer(TOKEN, facts.ZERO, BOT, 10_000_000 * USDX)])]),
        frame(BOT, TOKEN, logs=[transfer(TOKEN, BOT, POOL_A, 10_000_000 * USDX)])])
    record = facts.finish(core_of(trace), context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM, POOL_A])))
    assert [(m["to"], m["usd"]) for m in record["minted"]] == [("sender_contract_1", 10_000_000)]


def test_a_bot_reading_a_pool_inside_that_pools_callback_is_not_read_only_reentrancy():
    own_read = frame(SENDER, BOT, calls=[frame(BOT, POOL_A, calls=[
        frame(POOL_A, BOT, calls=[frame(BOT, POOL_A, kind="STATICCALL", value=None)])])])
    assert facts.reentries_shown(core_of(own_read), {}, False) == []
    fooled = frame(SENDER, BOT, calls=[frame(BOT, POOL_A, calls=[frame(POOL_A, BOT, calls=[
        frame(BOT, VICTIM, calls=[frame(VICTIM, POOL_A, kind="STATICCALL", value=None)])])])])
    assert facts.reentries_shown(core_of(fooled), {}, False) == [(POOL_A, BOT, True)]


def test_reentering_through_a_flash_accounting_unlock_is_how_it_is_used():
    unlock = facts.SELECTOR["unlock(bytes)"]
    trace = frame(SENDER, BOT, calls=[frame(BOT, POOL_A, selector=unlock, calls=[frame(POOL_A, BOT, calls=[frame(BOT, POOL_A)])])])
    assert facts.reentries_shown(core_of(trace), {}, False) == []
    plain = frame(SENDER, BOT, calls=[frame(BOT, POOL_A, calls=[frame(POOL_A, BOT, calls=[frame(BOT, POOL_A)])])])
    assert facts.reentries_shown(core_of(plain), {}, False) == [(POOL_A, BOT, False)]


def test_a_lenders_event_with_another_lenders_signature_is_read_from_the_transfer_it_matches():
    """One lender puts the borrower where another puts the token. The loan is whatever the lender actually sent."""
    event = log(LENDER, [TOPIC["FlashLoan(address,address,uint256)"], topic(SENDER), topic(BOT)], amount_data(9 * USDX))
    trace = frame(SENDER, BOT, calls=[frame(BOT, LENDER, logs=[event | {"position": "0x2"}], calls=[
        frame(LENDER, TOKEN, logs=[transfer(TOKEN, LENDER, BOT, 9 * USDX)]),
        frame(LENDER, BOT, calls=[frame(BOT, TOKEN, logs=[transfer(TOKEN, BOT, LENDER, 9 * USDX)])])])])
    assert core_of(trace).flash_loans == [{"lender": LENDER, "asset": TOKEN, "amount": 9 * USDX, "source": "event"}]
    unmatched = frame(SENDER, BOT, calls=[frame(BOT, LENDER, logs=[event])])
    assert core_of(unmatched).flash_loans == []


def test_a_deposit_and_larger_withdrawal_by_the_senders_contract_is_not_a_flash_loan_it_gave():
    """The loan's shape with the roles reversed: the sender's contract is where the funds came from and went back."""
    pay = facts.SELECTOR["transfer(address,uint256)"]
    trace = frame(SENDER, BOT, kind="CREATE", calls=[
        frame(BOT, TOKEN, selector=pay, logs=[transfer(TOKEN, BOT, VICTIM, 100 * USDX)]),
        frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, selector=pay, logs=[transfer(TOKEN, VICTIM, BOT, 150 * USDX)])])])
    core = core_of(trace)
    assert [loan["lender"] for loan in core.flash_loans] == [BOT]  # the raw shape matches
    assert facts.flash_loans_taken(core, {}, False) == []
    record = facts.finish(core, context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM])))
    assert record["flash_loans"] == []


def test_an_unlabeled_entry_contract_that_many_wallets_use_is_not_the_senders_tool():
    """A user calls an unlabeled protocol; its own cross-calls are not re-entry through the sender, and what it
    loses is a loss. The same trace through a private contract is both."""
    pay = facts.SELECTOR["transfer(address,uint256)"]
    trace = frame(SENDER, POOL_A, calls=[
        frame(POOL_A, VICTIM, calls=[frame(VICTIM, POOL_A, calls=[frame(POOL_A, VICTIM)])]),
        frame(POOL_A, TOKEN, selector=pay, logs=[transfer(TOKEN, POOL_A, SENDER, 50_000 * USDX)])])
    core = core_of(trace)
    assert facts.reentries_shown(core, {}, entry_is_public=False) == [(VICTIM, POOL_A, False)]
    assert facts.reentries_shown(core, {}, entry_is_public=True) == []
    prices = {TOKEN: {"usd": 1.0, "symbol": "USDX", "decimals": 6}}
    assert facts.cast(core, prices, 2_000.0, {}, entry_is_public=False).drains == []
    assert facts.cast(core, prices, 2_000.0, {}, entry_is_public=True).drains == [(POOL_A, TOKEN)]


def approval(token: str, owner: str, spender: str, position: int = 0) -> dict:
    return log(token, [TOPIC["Approval(address,address,uint256)"], topic(owner), topic(spender)], amount_data(10**30), position)


TRANSFER_FROM = facts.TRANSFER_FROM


def test_a_sweep_by_the_sender_and_a_pull_through_a_router_are_told_apart():
    # An exchange wallet calls transferFrom itself, under allowances its own deposit wallets gave it earlier.
    sweep = frame(SENDER, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, WALLET, SENDER, 245_000 * USDX)])
    pulls = facts.pulls_of(core_of(sweep, nonce=1_605_288), [SENDER])
    assert pulls == [{"spender": SENDER, "owner": WALLET, "recipient": SENDER, "asset": TOKEN, "amount": 245_000 * USDX,
                      "approved_now": False}]
    # A router the sender called pulls two wallets' tokens to the sender; one wallet approved it in this very transaction.
    victim_2 = addr(50)
    drain = frame(SENDER, BOT, calls=[
        frame(BOT, TOKEN, selector=TRANSFER_FROM, logs=[approval(TOKEN, WALLET, BOT), transfer(TOKEN, WALLET, SENDER, 5_000 * USDX, 1)]),
        frame(BOT, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, victim_2, SENDER, 7_000 * USDX)])])
    core = core_of(drain)
    assert (TOKEN, WALLET, BOT, 10**30) in core.approvals
    pulls = facts.pulls_of(core, [SENDER])
    assert [(p["spender"], p["owner"], p["approved_now"]) for p in pulls] == [(BOT, WALLET, True), (BOT, victim_2, False)]
    ctx = context(kinds=kinds(wallet=[SENDER, WALLET, victim_2], contract=[BOT]),
                  creations={BOT: {"creator": addr(77), "block": 1, "timestamp": BLOCK_TIME - 100 * 86400}})
    record = facts.finish(core, ctx)
    assert record["pulls"] == [{"spender": "unknown_contract_1", "spender_is": "the contract the sender called", "owners": 2,
                                "transfers": 2, "recipients": ["sender"], "approved_in_this_transaction": 1, "usd": 12_000.0,
                                "assets": ["USDX"]}]
    # A contract moving its own tokens with transferFrom, or the sender's side's tokens, is not a pull.
    own = frame(SENDER, BOT, calls=[frame(BOT, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, BOT, WALLET, 5 * USDX)]),
                                    frame(BOT, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, SENDER, WALLET, 5 * USDX)])])
    assert facts.pulls_of(core_of(own), [SENDER]) == []
    # A pull from a contract is protocol plumbing, and a small pull is not worth a line: neither reaches the record.
    plumbing = frame(SENDER, BOT, calls=[frame(BOT, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, LENDER, BOT, 9_000 * USDX)]),
                                         frame(BOT, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, WALLET, BOT, 5 * USDX)])])
    ctx = context(kinds=kinds(wallet=[SENDER, WALLET], contract=[BOT, LENDER]),
                  creations={BOT: {"creator": addr(77), "block": 1, "timestamp": BLOCK_TIME - 100 * 86400}})
    assert facts.finish(core_of(plumbing), ctx)["pulls"] == []


def test_sender_side_allowances_and_internal_credits_are_preserved_without_becoming_transfers():
    approval_to_vault = approval(TOKEN, BOT, LENDER)
    internal_credit = log(LENDER, [facts.INTERNAL_BALANCE_CHANGED, topic(BOT), topic(WETH)], amount_data(3 * ONE), position=1)
    trace = frame(SENDER, BOT, logs=[approval_to_vault, internal_credit])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER]),
                  creations={BOT: {"creator": SENDER, "block": 1, "timestamp": BLOCK_TIME - 60},
                             LENDER: {"creator": addr(77), "block": 1, "timestamp": BLOCK_TIME - 100 * 86400}},
                  prices={TOKEN: {"usd": 1.0, "symbol": "USDX", "decimals": 6},
                          WETH: {"usd": 2_000.0, "symbol": "WETH", "decimals": 18}})
    record = facts.finish(core_of(trace), ctx)
    assert record["ledger"] == []
    [allowance] = record["allowance_changes"]
    assert allowance["owner"] == "sender_contract_1" and allowance["owner_is_sender_side"] is True
    assert allowance["spender_is_sender_side"] is False and allowance["asset"]["amount_raw"] == str(10**30)
    [credit] = record["internal_balance_changes"]
    assert credit["account"] == "sender_contract_1" and credit["direction"] == "credited"
    assert credit["amount_raw"] == str(3 * ONE) and credit["amount"] == 3.0


def test_equal_valued_allowance_events_have_a_stable_raw_amount_tiebreaker():
    amounts = [2**256 - 1, 2**256 - 3, 2**256 - 2]
    trace = frame(SENDER, BOT, logs=[
        log(TOKEN, [TOPIC["Approval(address,address,uint256)"], topic(BOT), topic(LENDER)], amount_data(amount), position)
        for position, amount in enumerate(amounts)])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER]),
                  creations={BOT: {"creator": SENDER, "block": 1, "timestamp": BLOCK_TIME - 60},
                             LENDER: {"creator": addr(77), "block": 1, "timestamp": BLOCK_TIME - 100 * 86400}},
                  prices={TOKEN: {"usd": 1.0, "symbol": "USDX", "decimals": 6}})
    record = facts.finish(core_of(trace), ctx)
    assert [row["asset"]["amount_raw"] for row in record["allowance_changes"]] == [str(amount) for amount in sorted(amounts)]


def test_minted_tokens_record_their_issuer_and_what_it_received_from_the_senders_side():
    dust_token = addr(60)
    # The sender's contract deposits dust into a market, which mints $9.9M of USDX to it.
    market = LENDER
    trace = frame(SENDER, BOT, calls=[
        frame(BOT, dust_token, logs=[transfer(dust_token, BOT, market, 1)]),
        frame(BOT, market, calls=[frame(market, TOKEN, logs=[transfer(TOKEN, facts.ZERO, BOT, 9_900_000 * USDX)])])])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, market, dust_token]),
                  creations={BOT: {"creator": SENDER, "block": 1, "timestamp": BLOCK_TIME - 60},
                             market: {"creator": addr(77), "block": 1, "timestamp": BLOCK_TIME - 100 * 86400}})
    record = facts.finish(core_of(trace), ctx)
    [mint] = record["minted"]
    assert mint["to"] == "sender_contract_1"
    assert mint["issued_by"] == next(alias for alias, info in record["parties"].items() if info["address"] == market)
    assert [(a["asset"], a["amount_raw"]) for a in mint["issuer_received_from_side"]] == [("unrecognized_token_1", "1")]
    # A bridge minting to a user who is not on the sender's side names the issuer only.
    delivery = frame(SENDER, market, calls=[frame(market, TOKEN, logs=[transfer(TOKEN, facts.ZERO, WALLET, 300 * USDX)])])
    record = facts.finish(core_of(delivery), context(kinds=kinds(wallet=[SENDER, WALLET], contract=[market]),
                                                     creations={market: {"creator": addr(77), "block": 1,
                                                                         "timestamp": BLOCK_TIME - 100 * 86400}}))
    [mint] = record["minted"]
    assert mint["to"] == "unknown_wallet_1" and mint["issued_by"] == "unknown_contract_1" and mint["issuer_received_from_side"] is None


def test_the_senders_label_and_the_sides_burns_are_facts():
    exchange = addr(70)
    trace = frame(exchange, TOKEN, selector=TRANSFER_FROM, logs=[transfer(TOKEN, WALLET, exchange, 245_000 * USDX)])
    ctx = context(kinds=kinds(wallet=[exchange, WALLET]),
                  labels={exchange: {"name": "Big Exchange 7", "category": "centralized exchange", "symbol": None}})
    record = facts.finish(core_of(trace, nonce=1_605_288), ctx)
    assert record["sender"]["label"] == "Big Exchange 7" and record["sender"]["category"] == "centralized exchange"
    assert record["pulls"][0]["spender_is"] == "the sender" and record["pulls"][0]["recipients"] == ["sender"]
    # A redemption: the sender burns shares and an old vault pays out 3% of its balance.
    shares = addr(61)
    redeem = frame(SENDER, VICTIM, calls=[frame(VICTIM, shares, logs=[transfer(shares, SENDER, facts.ZERO, 12_500)]),
                                          frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, SENDER, 30_000 * USDX)])])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[VICTIM, shares]),
                  creations={VICTIM: {"creator": addr(77), "block": 1, "timestamp": BLOCK_TIME - 400 * 86400}},
                  balances_before={(VICTIM, TOKEN, BLOCK_NUMBER, 3): 1_000_000 * USDX},
                  prior_day_senders={(VICTIM, BLOCK_NUMBER): 40})  # a public vault, not the sender's own contract
    record = facts.finish(core_of(redeem), ctx)
    assert [(b["asset"], b["amount_raw"]) for b in record["sender_side"]["burned"]] == [("unrecognized_token_1", "12500")]
    [drain] = record["drains"]
    assert drain["share_of_prior_balance"] == 0.03 and drain["received_usd"] == 0 and drain["received_assets"] == []
    assert record["sender"]["label"] is None


def nft_log(collection: str, sender: str, recipient: str, token_id: int, position: int = 0) -> dict:
    return log(collection, [facts.TRANSFER, topic(sender), topic(recipient), "0x" + format(token_id, "064x")], position=position)


def position_log(issuer: str, sender: str, recipient: str, position: int = 0) -> dict:
    single = TOPIC["TransferSingle(address,address,address,uint256,uint256)"]
    return log(issuer, [single, topic(BOT), topic(sender), topic(recipient)], amount_data(7, 10**18), position)


def old_creation(address: str, creator: str | None = None, days: int = 400) -> dict:
    return {address: {"creator": creator or addr(99), "block": 1, "timestamp": BLOCK_TIME - days * 86400}}


def test_a_contract_created_by_an_older_sender_contract_is_on_the_senders_side():
    """The sender's six-month-old contract deploys a fresh one and the proceeds land there."""
    fresh = addr(70)
    trace = frame(SENDER, BOT, calls=[frame(BOT, fresh, kind="CREATE"),
                                      frame(BOT, fresh, calls=[frame(fresh, VICTIM, calls=[
                                          frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, fresh, 731_000 * USDX)])])])])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, VICTIM]), creations=old_creation(BOT, SENDER, 180) | old_creation(VICTIM),
                  prior_day_senders={(VICTIM, BLOCK_NUMBER): 40})
    record = facts.finish(core_of(trace), ctx)
    assert record["sender_side"]["members"] == ["sender", "sender_contract_1", "sender_contract_2"]
    assert record["sender_side"]["net_usd"] == 731_000.0 and record["sender_side"]["proceeds_to"] == []


def test_proceeds_to_a_fresh_wallet_and_a_mixer_count_as_the_senders_and_are_named():
    fresh, pool = addr(71), MIXER
    trace = frame(SENDER, BOT, calls=[
        frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, fresh, 6_500_000 * USDX)])]),
        frame(BOT, pool, value=1_500 * ONE)])
    ctx = context(kinds=kinds(wallet=[SENDER, fresh], contract=[BOT, VICTIM, MIXER]),
                  creations=old_creation(BOT, SENDER, 1) | old_creation(VICTIM) | old_creation(MIXER),
                  nonces_before={(fresh, BLOCK_NUMBER): 0}, prior_day_senders={(VICTIM, BLOCK_NUMBER): 40})
    record = facts.finish(core_of(trace), ctx)
    side = record["sender_side"]
    assert [(p["reason"], p["usd"]) for p in side["proceeds_to"]] == [("a wallet with no prior transactions", 6_500_000.0),
                                                                       ("a labeled mixer", 3_000_000.0)]
    assert side["net_usd"] == 6_500_000.0 and side["own_side_net_usd"] == -3_000_000.0  # the side paid the mixer out of its own ETH
    assert side["largest_gain_elsewhere"] is None


def test_the_largest_gain_going_to_an_old_wallet_is_said_and_a_wallet_the_sender_funded_is_counted():
    payout = addr(72)
    trace = frame(SENDER, BOT, calls=[frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, logs=[transfer(TOKEN, VICTIM, payout, 7_700_000 * USDX)])])])
    base = {"kinds": kinds(wallet=[SENDER, payout], contract=[BOT, VICTIM]), "creations": old_creation(BOT, SENDER, 400) | old_creation(VICTIM),
            "nonces_before": {(payout, BLOCK_NUMBER): 610}, "prior_day_senders": {(VICTIM, BLOCK_NUMBER): 40}}
    record = facts.finish(core_of(trace, nonce=48_980), context(**base))
    assert record["sender_side"]["proceeds_to"] == [] and record["sender_side"]["net_usd"] == 0
    assert record["sender_side"]["largest_gain_elsewhere"] == {"party": "unknown_wallet_1", "usd": 7_700_000.0}
    funded = context(**base, funding={payout: {"timestamp": BLOCK_TIME - 90 * 86400, "funder": SENDER}})
    record = facts.finish(core_of(trace, nonce=48_980), funded)
    assert record["sender_side"]["proceeds_to"] == [{"party": "unknown_wallet_1", "reason": "a wallet the sender's side funded", "usd": 7_700_000.0}]
    assert record["sender_side"]["net_usd"] == 7_700_000.0
    same_source = context(**base, funding={payout: {"timestamp": 1, "funder": addr(90)}, SENDER: {"timestamp": 2, "funder": addr(90)}})
    assert facts.finish(core_of(trace, nonce=48_980), same_source)["sender_side"]["proceeds_to"][0]["reason"] == \
        "a wallet funded from the same source as the sender"


def test_an_unpriced_asset_is_valued_by_what_a_pool_paid_for_it_in_the_same_transaction():
    """The pool takes 1,000 units of a token nobody quotes and gives out $50,000 of USDX: the token is worth $50."""
    odd = addr(73)
    trace = frame(SENDER, POOL_A, logs=[transfer(odd, SENDER, POOL_A, 1_000 * ONE), transfer(TOKEN, POOL_A, SENDER, 50_000 * USDX, 1)])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[POOL_A, odd]), decimals={odd: 18}, creations=old_creation(POOL_A))
    core = core_of(trace)
    implied = facts.implied_prices(core, [SENDER], ctx.prices, ctx.eth_usd, ctx.decimals)
    assert implied == {odd: {"usd": 50.0, "symbol": None, "decimals": 18, "implied": True, "max_amount": 10_000 * ONE}}
    record = facts.finish(core, ctx)
    [row] = [r for r in record["ledger"] if r["party"] == "sender"]
    assert row["gave_usd"] == 50_000.0 and row["received_usd"] == 50_000.0
    assert record["assets"]["unrecognized_token_1"]["price_basis"] == "implied from what it was exchanged for in this transaction"
    # an exchange under $1,000 implies nothing
    small = frame(SENDER, POOL_A, logs=[transfer(odd, SENDER, POOL_A, 1_000 * ONE), transfer(TOKEN, POOL_A, SENDER, 500 * USDX, 1)])
    assert facts.implied_prices(core_of(small), [SENDER], ctx.prices, ctx.eth_usd, ctx.decimals) == {}
    # the implied price reaches ten times the exchanged quantity and no further: a runaway mint stays unpriced
    assert implied[odd]["max_amount"] == 10_000 * ONE
    assert facts.usd_value(odd, 10_000 * ONE, implied, ctx.eth_usd) == 500_000.0 and facts.usd_value(odd, 10_001 * ONE, implied, ctx.eth_usd) is None
    # an NFT collection is never priced by one exchange: each token is different
    apes = addr(69)
    sale = frame(SENDER, POOL_A, logs=[nft_log(apes, SENDER, POOL_A, 7), transfer(TOKEN, POOL_A, SENDER, 50_000 * USDX, 1)])
    assert facts.implied_prices(core_of(sale), [SENDER], ctx.prices, ctx.eth_usd, ctx.decimals | {apes: 0}) == {}


def test_collateral_the_side_minted_itself_and_borrowed_against_is_a_fact():
    collateral, stable, vault = addr(74), addr(75), addr(76)
    trace = frame(SENDER, BOT, calls=[
        frame(BOT, collateral, logs=[transfer(collateral, facts.ZERO, BOT, 3 * ONE)]),
        frame(BOT, vault, calls=[frame(vault, collateral, logs=[transfer(collateral, BOT, vault, 3 * ONE)])]),
        frame(BOT, vault, calls=[frame(vault, stable, logs=[transfer(stable, facts.ZERO, BOT, 99 * ONE)])])])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, collateral, stable, vault]), creations=old_creation(BOT, SENDER, 1) | old_creation(vault),
                  decimals={collateral: 18, stable: 18})
    record = facts.finish(core_of(trace), ctx)
    [fact] = record["self_minted_collateral"]
    assert fact["posted_to"] == "unknown_contract_1" and fact["posted"]["amount"] == 3.0 and fact["received"]["amount"] == 99.0
    assert record["assets"][fact["posted"]["asset"]]["address"] == collateral
    assert record["assets"][fact["received"]["asset"]]["address"] == stable


def test_nft_collections_are_valued_at_their_floor_and_positions_name_their_issuer():
    apes, issuer = addr(77), addr(78)
    trace = frame(SENDER, BOT, calls=[frame(BOT, apes, logs=[nft_log(apes, VICTIM, BOT, 1), nft_log(apes, VICTIM, BOT, 2, 1)]),
                                      frame(BOT, issuer, logs=[position_log(issuer, facts.ZERO, BOT)])])
    ctx = context(kinds=kinds(wallet=[SENDER, VICTIM], contract=[BOT, apes, issuer]),
                  creations=old_creation(BOT, SENDER, 1) | old_creation(apes) | old_creation(issuer),
                  prices={apes: {"usd": 13_000.0, "symbol": "Bored Ape Yacht Club", "decimals": 0}},  # a floor, as enrich sets it
                  nfts={apes: {"name": "Bored Ape Yacht Club", "verified": True, "floor_usd": 13_000.0}}, decimals={apes: 0})
    record = facts.finish(core_of(trace), ctx)
    assert record["assets"]["unrecognized_nft_1"] == {"address": apes, "symbol": None, "priced": True, "age_seconds": 400 * 86400,
                                                       "created_by_sender_side": False, "price_basis": "current floor price", "nft": True}
    assert record["sender_side"]["net_usd"] == 26_000.0
    assert record["positions_moved"] == [{"issuer": "unknown_contract_1", "count": 1, "to": ["sender_contract_1"], "to_sender_side": 1,
                                           "minted": 1, "raw_ids": ["7"], "raw_amounts": [str(10**18)]}]
    # an unverified collection keeps a numbered name and no price
    ctx = context(kinds=kinds(wallet=[SENDER, VICTIM], contract=[BOT, apes, issuer]), creations=old_creation(BOT, SENDER, 1) | old_creation(apes),
                  nfts={apes: {"name": "Bored Ape Yacht Club", "verified": False, "floor_usd": None}}, decimals={apes: 0})
    record = facts.finish(core_of(trace), ctx)
    assert "unrecognized_nft_1" in record["assets"] and record["assets"]["unrecognized_nft_1"]["priced"] is False


def test_a_preparation_shaped_transaction_is_marked_and_remembered_for_the_senders_next_one():
    issuer = addr(78)
    setup = frame(SENDER, BOT, kind="CREATE", calls=[frame(BOT, issuer, logs=[position_log(issuer, facts.ZERO, BOT)])])
    ctx = context(kinds=kinds(wallet=[SENDER, WALLET], contract=[issuer]), creations=old_creation(issuer))
    first = facts.finish(core_of(setup, nonce=0, index=3), ctx)
    assert first["precursor"] is True and first["earlier_by_this_sender"] == []
    later = frame(SENDER, issuer, logs=[transfer(TOKEN, issuer, SENDER, 1_730_000 * USDX)])
    second = facts.finish(core_of(later, nonce=1, index=9), ctx)  # same block, later index; a later block also works
    assert second["precursor"] is False
    assert second["earlier_by_this_sender"] == [{"blocks_earlier": 0, "summary": "deployed 1 contract and moved 1 positions or unpriced tokens while no priced value moved"}]
    # another sender's transaction remembers nothing
    assert facts.finish(core_of(frame(WALLET, issuer, logs=[transfer(TOKEN, issuer, WALLET, 5 * USDX)]), nonce=3, index=10), ctx)["earlier_by_this_sender"] == []


def test_an_old_contract_running_fresh_code_by_delegatecall_is_a_logic_change_and_later_callers_see_it():
    safe, module = addr(79), addr(80)
    executed = log(safe, [TOPIC["ExecutionSuccess(bytes32,uint256)"]], amount_data(1, 0))
    swap = frame(SENDER, safe, calls=[frame(safe, module, kind="DELEGATECALL")], logs=[executed])
    ctx = context(kinds=kinds(wallet=[SENDER, WALLET], contract=[safe, module]),
                  creations=old_creation(safe, addr(97), 4 * 365) | {module: {"creator": addr(98), "block": 1, "timestamp": BLOCK_TIME - 3600}},
                  prior_day_senders={(safe, BLOCK_NUMBER): 1}, balances_before={(safe, TOKEN, BLOCK_NUMBER, 8): 400_000_000 * USDX})
    record = facts.finish(core_of(swap, nonce=42, index=3), ctx)
    assert record["logic_changes"] == [{"contract": "unknown_contract_1", "what": "ran code from a contract created 1 hour earlier by delegatecall",
                                        "contract_age_seconds": 4 * 365 * 86400}]
    # the drain runs on the swapped logic and emits no Safe event; the watch still makes the Safe's loss a loss
    drain = frame(WALLET, safe, calls=[frame(safe, TOKEN, logs=[transfer(TOKEN, safe, WALLET, 400_000_000 * USDX)])])
    later = facts.finish(core_of(drain, nonce=7, index=8), ctx)
    assert later["heightened"] == [{"contract": "unknown_contract_1", "what": "ran code from a contract created 1 hour earlier by delegatecall",
                                    "blocks_earlier": 0, "contract_age_seconds": 4 * 365 * 86400}]
    assert [d["party"] for d in later["drains"]] == ["unknown_contract_1"] and later["drains"][0]["share_of_prior_balance"] == 1.0
    # the sender's own two-day-old contract run by delegatecall is a logic change whatever its age, and a wallet
    # contract delegating into a second target is never a trivial transaction (a proxy running one implementation is)
    own = addr(81)
    swap_own = frame(SENDER, safe, calls=[frame(safe, module, kind="DELEGATECALL", calls=[frame(safe, own, kind="DELEGATECALL")])], logs=[executed])
    assert core_of(swap_own).trivial is False and core_of(frame(SENDER, safe, calls=[frame(safe, module, kind="DELEGATECALL")])).trivial is True
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[safe, own]),
                  creations=old_creation(safe, addr(97), 4 * 365) | old_creation(own, SENDER, 2), prior_day_senders={(safe, BLOCK_NUMBER): 1})
    assert facts.finish(core_of(swap_own, nonce=42), ctx)["logic_changes"] == [
        {"contract": "unknown_contract_1", "what": "ran code from the sender's own contract (created 2 days earlier) by delegatecall",
         "contract_age_seconds": 4 * 365 * 86400}]
    # an ordinary proxy delegating to its year-old implementation is not a change
    proxy_call = frame(SENDER, safe, calls=[frame(safe, VICTIM, kind="DELEGATECALL")])
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[safe, VICTIM]), creations=old_creation(safe) | old_creation(VICTIM))
    assert facts.finish(core_of(proxy_call), ctx)["logic_changes"] == []
    # a fresh deployment's OwnershipTransferred is boilerplate, and a busy public contract's upgrade is not watched
    owned = log(BOT, [TOPIC["OwnershipTransferred(address,address)"], topic(facts.ZERO), topic(SENDER)])
    deploy = frame(SENDER, BOT, kind="CREATE", logs=[owned])
    assert facts.finish(core_of(deploy), context(kinds=kinds(wallet=[SENDER])))["logic_changes"] == []
    upgraded = log(VICTIM, [TOPIC["Upgraded(address)"], topic(WALLET)])
    ctx = context(kinds=kinds(wallet=[SENDER, WALLET], contract=[VICTIM]), creations=old_creation(VICTIM), prior_day_senders={(VICTIM, BLOCK_NUMBER): 40})
    upgrade = facts.finish(core_of(frame(SENDER, VICTIM, logs=[upgraded]), index=1), ctx)
    assert upgrade["logic_changes"] == [{"contract": "unknown_contract_1", "what": "Upgraded event", "contract_age_seconds": 400 * 86400}]
    assert facts.finish(core_of(frame(WALLET, VICTIM), nonce=9, index=2), ctx)["heightened"] == []
