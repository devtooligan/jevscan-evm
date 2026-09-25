"""Views are pure functions of TxFacts that speak in words and aliases, never in hashes, blocks, or addresses."""

import json
import re

import pytest

from jevscan_monitor import facts, views
from tests.helpers import (
    BLOCK_NUMBER,
    BOT,
    LENDER,
    MIXER,
    SENDER,
    VICTIM,
    chain_data,
    context,
    kinds,
)
from tests.test_facts import USDX, flash_loan_trace

HEX = re.compile(r"0x[0-9a-fA-F]{6,}")


@pytest.fixture
def attack() -> facts.TxFacts:
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER, VICTIM]),
                  balances_before={(VICTIM, facts_token(), BLOCK_NUMBER, 3): 400_000 * USDX},
                  funding={SENDER: {"timestamp": 1_750_000_000 - 240, "funder": LENDER}},
                  mixer_payouts={(SENDER, BLOCK_NUMBER, 3): (BLOCK_NUMBER - 25, MIXER)})
    return facts.finish(facts.extract(*chain_data(flash_loan_trace(repay=1_000_900 * USDX), nonce=0)), ctx)


def facts_token() -> str:
    from tests.helpers import TOKEN
    return TOKEN


@pytest.mark.parametrize("usd, words", [
    (0.4, "under $1 (negligible)"), (1_234, "about $1,200 (small)"), (412_345, "about $412 thousand (large)"),
    (8_900_000, "about $8.9 million (very large)"), (30_000_000, "about $30 million (enormous)"),
    (2_500_000_000, "about $2.5 billion (enormous)")])
def test_money_is_a_rounded_figure_in_words_with_a_size_bucket(usd: float, words: str):
    assert views.money(usd) == words


def test_spans_and_ordinals_read_as_words():
    assert [views.span(s) for s in (30, 540, 3 * 3600, 45 * 86400, 800 * 86400)] == \
        ["under a minute", "9 minutes", "3 hours", "1 month", "2 years"]
    assert [views.ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 102)] == \
        ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "102nd"]


@pytest.mark.parametrize("gave, received, words", [
    (0, 0, "no priced value moved"), (0, 50, "received value and gave nothing"),
    (50, 0, "gave value and received nothing"), (100, 95, "received about as much value as it gave"),
    (100, 140, "received more value than it gave"), (100, 25, "gave more value than it received (got back about 25%)")])
def test_code_makes_the_comparison_between_what_a_party_gave_and_received(gave, received, words):
    assert views.exchange_words({"gave_usd": gave, "received_usd": received}) == words


def test_only_the_raw_view_shows_addresses_and_no_view_shows_a_hash_or_block_number(attack):
    rendered = {name: json.dumps(view(attack)) for name, view in views.VIEWS.items()} | {"line": views.line(attack)}
    assert HEX.search(rendered["R0"])
    for name, text in rendered.items():
        assert attack["tx"]["hash"] not in text and str(BLOCK_NUMBER) not in text, name
        if name != "R0":
            assert not HEX.search(text), (name, HEX.search(text))


def test_the_fact_sheet_says_in_words_what_the_attack_did(attack):
    sheet = views.r2(attack)
    assert sheet["sender"] == {"kind": "wallet", "prior_transactions": 0, "first_funded": "4 minutes earlier",
                               "funded_by": "an unlabeled address",
                               "mixer_funding": "received funds from Some Mixer: 1 ETH (mixer) 5 minutes earlier"}
    assert sheet["entry_contract"]["contract"] == \
        "sender_contract_1 (contract, created in this transaction by the sender, source code unverified)"
    assert sheet["flash_loans"] == ["about $1 million (very large) of USDX from unknown_contract_2 (contract)"]
    assert sheet["sender_side"] == {"members": ["sender", "sender_contract_1"],
                                    "net_result": "gained about $299 thousand (large)", "own_capital_put_in": "none",
                                    "gain_compared_with_largest_amount_moved": "most of it (over 50%)"}
    assert sheet["largest_losses"] == [("unknown_contract_1 (contract) sent out about $300 thousand (large) of USDX "
                                        "(75% of its balance just before this transaction); no tokens came back to it "
                                        "in this transaction")]
    assert "call_tree" not in sheet and "call_tree" in views.r3(attack)


def test_unpriced_legs_make_the_ledger_comparison_explicitly_incomplete():
    row = {"gave_usd": 0, "received_usd": 500_000, "changes": [{"usd": None}]}
    assert views.exchange_words(row) == \
        "priced assets show an inflow; assets with no reliable price also moved, so total compensation cannot be determined from this ledger"


def test_a_mixer_payout_shows_without_a_first_funding_line_and_the_names_switch_hides_the_mixer():
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER, VICTIM]),
                  mixer_payouts={(SENDER, BLOCK_NUMBER, 3): (BLOCK_NUMBER - 2 * 7_200, MIXER)})
    record = facts.finish(facts.extract(*chain_data(flash_loan_trace(repay=1_000_900 * USDX), nonce=40)), ctx)
    assert views.r2(record)["sender"] == {"kind": "wallet", "prior_transactions": 40,
                                          "mixer_funding": "received funds from Some Mixer: 1 ETH (mixer) 2 days earlier"}
    assert "It received funds from Some Mixer: 1 ETH (mixer) 2 days earlier." in views.r4(record)["description"]
    assert views.r2_anonymous(record)["sender"]["mixer_funding"] == "received funds from a mixer 2 days earlier"
    assert "mixer-funded" in views.line(record)


def test_a_sender_no_mixer_paid_has_no_mixer_line():
    ctx = context(kinds=kinds(wallet=[SENDER], contract=[BOT, LENDER, VICTIM]), mixer_payouts={(SENDER, BLOCK_NUMBER, 3): None})
    record = facts.finish(facts.extract(*chain_data(flash_loan_trace(repay=1_000_900 * USDX), nonce=40)), ctx)
    assert record["sender"]["mixer_funded_within_30_days"] is False
    assert views.r2(record)["sender"] == {"kind": "wallet", "prior_transactions": 40}
    assert "mixer" not in views.line(record)


def test_the_receipt_view_has_no_trace_facts(attack):
    receipt = views.r1(attack)
    assert "call_shape" not in receipt and "reentrancy" not in receipt and "largest_losses" not in receipt
    assert receipt["flash_loan_events"] == []  # this loan was found from the trace's shape, which a receipt lacks


def test_prose_carries_the_same_facts_as_the_sheet(attack):
    text = views.r4(attack)["description"]
    for phrase in ("had made 0 transactions before this one", "deploys and runs sender_contract_1",
                   "flash loan of about $1 million (very large) of USDX", "gained about $299 thousand (large)",
                   "put in none of its own capital", "75% of its balance just before this transaction"):
        assert phrase in text, phrase


def test_the_one_line_view_is_short(attack):
    text = views.line(attack)
    assert "mixer-funded" in text and "deploys and runs a new contract" in text
    assert len(text) / 3.5 < 120


def test_the_narrative_view_trims_its_tree_when_a_large_fact_sheet_leaves_less_room(attack):
    crowded = attack | {"call_tree": [f"unknown_contract_{i} calls unknown_contract_{i + 1}" for i in range(2_000)]}
    view = views.r3(crowded)
    assert len(json.dumps(view)) / 3.5 <= views.R3_TOKEN_CAP
    assert view["call_tree"][-1].endswith("more lines not shown)") and view["call_tree"][0] == crowded["call_tree"][0]
    assert views.r3(attack)["call_tree"] == attack["call_tree"]  # a tree that fits is left alone


def test_narrative_rejects_a_fact_sheet_that_alone_exceeds_cap(attack):
    with pytest.raises(ValueError, match="limit"):
        views.r3(attack | {"protocols_touched": ["x" * 100000]})


def test_anonymous_labels_do_not_rename_schema_keys(attack):
    party = next(iter(attack["parties"]))
    source = attack | {"parties": {"status": attack["parties"][party] | {
        "label": "status", "category": "exchange"}}}
    anonymous = views.anonymize(source)
    assert anonymous["status"] == source["status"]
    assert "status" not in anonymous["parties"]


def sale(received: float, unpriced: bool = False, unpriced_received: bool = False, **extra) -> dict:
    return {"party": "unknown_contract_1", "asset": "USDX", "usd": 500_000.0, "amount": 500_000.0, "amount_raw": "5",
            "share_of_prior_balance": 0.5, "gave_usd": 500_000.0, "received_usd": received, "unpriced_legs": unpriced,
            "unpriced_received": unpriced_received, "received_assets": ["WETH"] if received or unpriced_received else [],
            "events_recorded": [], "same_sender_put_in_earlier": None} | extra


@pytest.mark.parametrize("received, unpriced, words", [
    (498_000.0, False, "it received about $498 thousand (large) of WETH"),
    (150_000.0, False, "it received about $150 thousand (large) of WETH, about 30% of what it gave out"),
    (0.0, False, "no tokens came back to it in this transaction"),
    (0.0, True, "no tokens came back to it in this transaction")])
def test_a_loss_line_states_what_came_back_and_never_says_received_nothing(attack, received, unpriced, words):
    assert views.paid_words(sale(received, unpriced), attack) == words
    assert "received nothing" not in views.drain_words(sale(received, unpriced), attack)


def test_a_pool_paid_in_a_token_nobody_prices_was_still_paid(attack):
    assert views.paid_words(sale(0.0, unpriced=True, unpriced_received=True), attack) == \
        "it received only assets with no reliable price (WETH)"
    assert views.paid_words(sale(150_000.0, unpriced=True, unpriced_received=True), attack) == \
        "it received about $150 thousand (large) of WETH, about 30% of what it gave out, not counting assets with no reliable price"


def test_a_pool_that_sells_half_an_asset_for_full_value_reads_as_a_sale(attack):
    traded = attack | {"drains": [sale(498_000.0)]}
    assert views.r2(traded)["largest_losses"] == [
        ("unknown_contract_1 (contract) gave out about $500 thousand (large) of USDX (50% of its balance just before "
         "this transaction); it received about $498 thousand (large) of WETH")]
    assert "unknown_contract_1 gave out 50% of an asset balance, paid about as much back" in views.line(traded)


def test_an_unpaid_payout_shows_the_payers_side_and_the_share_of_its_balance(attack):
    burned = [{"asset": "unrecognized_token_1", "usd": None, "amount": 12.5, "amount_raw": "125"}]
    claim = attack | {"drains": [sale(0.0, share_of_prior_balance=0.03, events_recorded=["Withdraw"])],
                      "sender_side": attack["sender_side"] | {"burned": burned}}
    line = views.r2(claim)["largest_losses"][0]
    assert line == ("unknown_contract_1 (contract) sent out about $500 thousand (large) of USDX (3% of its balance just "
                    "before this transaction); no tokens came back to it in this transaction; it recorded Withdraw "
                    "event; the sender's side burned about 12.5 units of unrecognized_token_1 (no reliable price)")
    assert "unknown_contract_1 sent out 3% of an asset balance, no tokens back, Withdraw event" in views.line(claim)


def test_a_sandwich_back_leg_names_the_front_legs_deposit(attack):
    earlier = {"index": 1, "asset": "USDX", "usd": 500_000.0, "amount": 500_000.0, "amount_raw": "5"}
    back = attack | {"drains": [sale(0.0, same_sender_put_in_earlier=earlier)]}
    assert views.r2(back)["largest_losses"][0].endswith(
        "; the same sender put about $500 thousand (large) of USDX into it earlier in this block (transaction 2nd of the block)")
    assert "the same sender put that in earlier in this block" in views.line(back)


def test_a_loss_under_one_percent_of_a_balance_is_not_printed_as_zero_percent(attack):
    tiny = attack | {"drains": [sale(0.0) | {"share_of_prior_balance": 0.0004}]}
    assert "of an asset balance" not in views.line(tiny) and "0%" not in views.line(tiny)
    assert "under 1% of its balance just before this transaction" in views.r2(tiny)["largest_losses"][0]


def test_a_labeled_very_active_sender_is_named_and_described_in_words(attack):
    exchange = attack | {"sender": attack["sender"] | {"label": "Big Exchange 7", "category": "centralized exchange",
                                                       "prior_transactions": 1_605_288}}
    sheet = views.r2(exchange)["sender"]
    assert sheet["identity"] == "Big Exchange 7 (centralized exchange)"
    assert sheet["activity"] == "a very high-volume wallet, over 100,000 prior transactions"
    assert "The sender is Big Exchange 7 (centralized exchange), a wallet that had made 1,605,288 transactions before " \
           "this one, a very high-volume wallet, over 100,000 prior transactions." in views.r4(exchange)["description"]
    assert views.line(exchange).startswith("sender Big Exchange 7 (centralized exchange) wallet with 1,605,288 prior txs (very high-volume)")
    assert "Big Exchange" not in json.dumps(views.r2_anonymous(exchange)) and \
        views.r2_anonymous(exchange)["sender"]["identity"] == "a centralized exchange"
    assert "identity" not in views.r2(attack)["sender"] and "activity" not in views.r2(attack)["sender"]


def test_minted_tokens_name_their_issuer_and_what_it_received_from_the_senders_side(attack):
    mint = {"to": "sender_contract_1", "asset": "USDX", "usd": 9_900_000.0, "amount": 9_900_000.0, "amount_raw": "1",
            "issued_by": "unknown_contract_2", "issuer_received_from_side": [
                {"asset": "unrecognized_token_1", "usd": None, "amount": 0.0000001, "amount_raw": "1"}]}
    record = attack | {"minted": [mint]}
    assert views.r2(record)["newly_minted"] == [
        ("about $9.9 million (very large) of USDX, minted to sender_contract_1 by unknown_contract_2 (contract), which "
         "received from the sender's side a dust amount (under 0.001 units) of unrecognized_token_1 (no reliable price)")]
    assert "about $9.9 million (very large) newly minted to sender_contract_1 by unknown_contract_2" in views.line(record)
    delivery = attack | {"minted": [mint | {"to": "unknown_wallet_1", "issuer_received_from_side": None}]}
    assert views.r2(delivery)["newly_minted"][0].endswith("minted to unknown_wallet_1 by unknown_contract_2 (contract)")
    own = attack | {"minted": [mint | {"issued_by": "sender", "issuer_received_from_side": None}]}
    assert views.r2(own)["newly_minted"][0].endswith("minted to sender_contract_1 at the sender's own call")


def test_a_transferfrom_pull_says_who_pulled_under_which_allowances_and_where_it_went(attack):
    sweep = {"spender": "sender", "spender_is": "the sender", "owners": 3, "transfers": 3, "recipients": ["sender"],
             "approved_in_this_transaction": 0, "usd": 245_000.0, "assets": ["USDX"]}
    record = attack | {"pulls": [sweep]}
    assert views.r2(record)["tokens_pulled_with_transferFrom"] == [
        ("the sender pulled about $245 thousand (large) of USDX from 3 addresses under allowances granted before this "
         "transaction, into sender")]
    assert "the sender pulls about $245 thousand (large) from 3 addresses by transferFrom into sender" in views.line(record)
    drain = sweep | {"spender": "unknown_contract_2", "spender_is": "the contract the sender called", "owners": 127,
                     "transfers": 127, "approved_in_this_transaction": 2, "recipients": ["sender", "unknown_wallet_1"]}
    words = views.r2(attack | {"pulls": [drain]})["tokens_pulled_with_transferFrom"][0]
    assert words.startswith("the contract the sender called (unknown_contract_2 (contract)) pulled about $245 thousand (large) "
                            "of USDX from 127 addresses under allowances granted before this transaction for 125 of the 127 transfers")
    assert words.endswith("into sender, unknown_wallet_1")
    assert "Tokens pulled with transferFrom: the contract the sender called" in views.r4(attack | {"pulls": [drain]})["description"]


def test_huge_unit_counts_are_words_not_scientific_notation():
    assert [views.quantity(n) for n in (3.87e10, 2.5e12, 4.2e6, 1e18)] == \
        ["about 38.7 billion units", "about 2.5 trillion units", "about 4.2 million units", "over a quadrillion units"]


def test_the_sheet_says_where_proceeds_went_and_what_the_sender_alone_kept(attack):
    side = attack["sender_side"] | {"net_usd": 9_500_000.0, "own_side_net_usd": -3_000_000.0,
                                    "proceeds_to": [{"party": "unknown_wallet_1", "reason": "a wallet with no prior transactions", "usd": 6_500_000.0},
                                                    {"party": "Some Mixer: 1 ETH", "reason": "a labeled mixer", "usd": 3_000_000.0}]}
    parties = attack["parties"] | {"unknown_wallet_1": attack["parties"]["sender"] | {"kind": "wallet", "prior_transactions": 0, "category": None, "label": None},
                                   "Some Mixer: 1 ETH": attack["parties"]["sender"] | {"kind": "contract", "category": "mixer", "label": "Some Mixer: 1 ETH", "age_seconds": 10**8}}
    record = attack | {"sender_side": side, "parties": parties}
    sheet = views.r2(record)["sender_side"]
    assert sheet["proceeds_sent_to"] == [
        "about $6.5 million (very large) to unknown_wallet_1 (wallet, no prior transactions), a wallet with no prior transactions, counted as the sender's side's",
        "about $3 million (very large) to Some Mixer: 1 ETH (mixer, created 3 years earlier), a labeled mixer, counted as the sender's side's"]
    assert sheet["net_result"] == "gained about $9.5 million (very large)"
    assert sheet["net_result_of_the_sender_and_its_contracts_alone"] == "lost about $3 million (very large)"
    assert "sender side gains about $9.5 million (very large) counting proceeds sent elsewhere" in views.line(record)
    assert "about $6.5 million (very large) of proceeds to unknown_wallet_1 (a wallet with no prior transactions)" in views.line(record)
    elsewhere = attack | {"sender_side": attack["sender_side"] | {"largest_gain_elsewhere": {"party": "unknown_wallet_1", "usd": 7_700_000.0}}, "parties": parties}
    assert views.r2(elsewhere)["sender_side"]["largest_gain_went_elsewhere"] == \
        "the largest gain, about $7.7 million (very large), went to unknown_wallet_1 (wallet, no prior transactions), not to the sender's side"
    assert "largest gain about $7.7 million (very large) went to unknown_wallet_1, not the sender" in views.line(elsewhere)


def test_nfts_implied_prices_positions_collateral_preparation_and_logic_changes_read_in_words(attack):
    assets = attack["assets"] | {
        "Bored Ape Yacht Club": {"address": "0x" + "a" * 40, "symbol": "Bored Ape Yacht Club", "priced": True, "age_seconds": 10**8,
                                 "created_by_sender_side": False, "price_basis": "current floor price", "nft": True},
        "unrecognized_token_9": {"address": "0x" + "b" * 40, "symbol": None, "priced": True, "age_seconds": 10**6, "created_by_sender_side": False,
                                 "price_basis": "implied from what it was exchanged for in this transaction", "nft": False}}
    record = attack | {"assets": assets}
    assert views.value_of({"asset": "Bored Ape Yacht Club", "usd": 26_000.0, "amount": 2.0, "amount_raw": "2"}, record) == \
        "2 Bored Ape Yacht Club NFTs (about $26 thousand (moderate), current floor price)"
    assert views.value_of({"asset": "unrecognized_token_9", "usd": 50_000.0, "amount": 1000.0, "amount_raw": "1"}, record) == \
        ("about $50 thousand (moderate) of unrecognized_token_9 (an unrecognized token created 11 days earlier) "
         "(implied from what it was exchanged for in this transaction)")
    record = attack | {
        "self_minted_collateral": [{"posted_to": "unknown_contract_2", "posted": {"asset": "USDX", "usd": None, "amount": 3.4e20, "amount_raw": "1"},
                                    "received": {"asset": "USDX", "usd": None, "amount": 9.9e10, "amount_raw": "2"}}],
        "positions_moved": [{"issuer": "unknown_contract_2", "count": 4, "to": ["sender_contract_1"], "to_sender_side": 4, "minted": 4,
                               "raw_ids": [], "raw_amounts": []}],
        "precursor": True, "earlier_by_this_sender": [{"blocks_earlier": 14, "summary": "deployed 5 contracts and moved 4 positions or unpriced tokens while no priced value moved"}],
        "logic_changes": [{"contract": "unknown_contract_2", "what": "ran code from a contract created 2 hours earlier by delegatecall", "contract_age_seconds": 4 * 365 * 86400}],
        "heightened": [{"contract": "unknown_contract_2", "what": "ChangedMasterCopy event", "blocks_earlier": 13, "contract_age_seconds": 4 * 365 * 86400}]}
    sheet = views.r2(record)
    assert sheet["self_minted_collateral"] == [("the sender's side minted over a quadrillion units of USDX (no reliable price) itself, posted it to "
                                                "unknown_contract_2 (contract), and received about 99 billion units of USDX (no reliable price) from it")]
    assert sheet["positions_moved"] == [("4 ERC-1155 position transfers issued by unknown_contract_2 (contract), 4 of them newly minted, to sender_contract_1 "
                                         "(the sender's side); positions have no market price here")]
    assert sheet["preparation_shape"].startswith("deploys a contract and moves positions")
    assert sheet["this_senders_earlier_transactions_in_this_window"] == [
        "14 blocks earlier this sender deployed 5 contracts and moved 4 positions or unpriced tokens while no priced value moved"]
    assert sheet["logic_or_control_changed"] == ["unknown_contract_2 (contract) ran code from a contract created 2 hours earlier by delegatecall"]
    assert sheet["contracts_whose_logic_changed_recently"] == [
        "unknown_contract_2 (contract) ChangedMasterCopy event 13 blocks earlier, after 4 years without a recorded change in this window"]
    line = views.line(record)
    for phrase in ("minted its own collateral, posted it to unknown_contract_2", "4 ERC-1155 positions issued by unknown_contract_2 minted",
                   "preparation shape", "14 blocks earlier this sender deployed 5 contracts", "unknown_contract_2 ran code from a contract created",
                   "unknown_contract_2 ChangedMasterCopy event 13 blocks earlier"):
        assert phrase in line, phrase
    prose = views.r4(record)["description"]
    assert "Self-minted collateral:" in prose and "Heightened state:" in prose and "Earlier in this window:" in prose
