"""A tripwire for the rule that results are only comparable within one TxFacts version: if what the facts or the views
produce changes, FACTS_VERSION must change with it, because every stored Jev answer was given to the old rendering."""

import hashlib
import json

from jevscan_monitor import facts, views
from tests.helpers import (
    BLOCK_NUMBER,
    BLOCK_TIME,
    BOT,
    LENDER,
    MIXER,
    POOL_A,
    SENDER,
    TOKEN,
    TOKEN_2,
    VICTIM,
    WALLET,
    addr,
    chain_data,
    context,
    frame,
    kinds,
    transfer,
)
from tests.test_facts import ONE, USDX, flash_loan_trace

# sha256 of every view of the transactions below, per TxFacts version. Add an entry when you bump FACTS_VERSION; never
# edit an old one.
GOLDEN = {
    1: "4da3da550cce1bfb32b36b4aa0d570372ef2b91b05f67b83eb57a3e9d0bcf677",
    2: "2703666e85eb2fed39a08ff2ae833d146e7bd4388f9cc0e9e49dcd2ae0fa0757",
    3: "fa66a9ea333ade6eb3f7acd2fc2fcae45484d954f1d5fe275be7eb8f0f5a99ba",
    4: "faf2de9cf0569ec1f4acb15e0f657f7d677ca469d29b7331de0b73c4fde1dd3d",
    5: "f63071befd1e065c4757cc59ee1d9eaf1cd4e413d610aaf9679a6dae2faff71b",
    6: "069ce1d6d25ce39ddce54e649850ff48adf5c6aaa6ce8d198b1cb9a49844bcea",
    7: "8b079104a1c4ae2adc0e5541dd5b0b7099175e6a0a2a51b57c4fd42d77551396",
    8: "620d41d531ad4b73a6376470dca00089fd4988bb1ff0eb194a70f601d37e026e",
    9: "58168dc97d1586725816e538a8935752553e1fdefba47a6f3e29ad94200300a7",
    10: "0798358b386cc6658ebe9c3846acb8fcbdb0095b0206588edeeb928e381cebab",
    12: "838e69b566305a9eb4b4caa5d8af1a72ab338046e8f1010a103fc15f8c0683d1",
    13: "3a6ef60d5dec9c06b1cac99b0e5bfc67ca3d49880627a61b2ea9b817038cde1e",
}
# sha256 of every question file, per version, from version 4 on. The wording has not changed since the first Jev call;
# this pins it, so that an answer to old wording can never be scored as an answer to new wording.
QUESTIONS_GOLDEN = {
    4: "abbb7d3dbc7f852a71cbd2cebc011ca566d154fbbd7d19c1add72b03777927aa",
    5: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # q7, the relatedness question, added; the other files unchanged
    6: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # unchanged from version 5
    7: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # unchanged from version 6
    8: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # unchanged from version 7
    9: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # unchanged from version 8
    10: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # unchanged from version 9
    12: "914cf5ab06ef6402284d7e1b2fd61f925db6192a952dc6708f7d266c6071d1f4",  # unchanged from version 10
}


def fixtures() -> list[facts.TxFacts]:
    pay = facts.SELECTOR["transfer(address,uint256)"]
    traces = [
        flash_loan_trace(repay=1_000_900 * USDX),
        frame(SENDER, WALLET, value=ONE, selector="0x"),
        frame(SENDER, BOT, value=2 * ONE, error="out of gas", calls=[frame(BOT, WALLET, value=ONE)]),
        frame(SENDER, POOL_A, calls=[frame(POOL_A, TOKEN, selector=pay, logs=[transfer(TOKEN, SENDER, POOL_A, 1_000 * USDX)]),
                                     frame(POOL_A, SENDER, value=ONE // 2, selector="0x")]),
        frame(SENDER, TOKEN_2, logs=[transfer(TOKEN_2, SENDER, facts.ZERO, 5 * ONE)], calls=[
            frame(TOKEN_2, TOKEN, selector=pay, logs=[transfer(TOKEN, TOKEN_2, SENDER, 1_000 * USDX)])]),
        frame(SENDER, BOT, kind="CREATE", calls=[
            frame(BOT, VICTIM, calls=[frame(VICTIM, TOKEN, logs=[transfer(TOKEN, facts.ZERO, BOT, 10_000_000 * USDX)])]),
            frame(BOT, VICTIM, calls=[frame(VICTIM, BOT, value=ONE, calls=[frame(BOT, VICTIM)])]),
            frame(BOT, TOKEN, selector=pay, logs=[transfer(TOKEN, BOT, POOL_A, 10_000_000 * USDX)])]),
    ]
    ctx = context(
        kinds=kinds(wallet=[SENDER, WALLET], contract=[BOT, LENDER, VICTIM, POOL_A, TOKEN_2]),
        labels={LENDER: {"name": "Big Lender: Pool", "category": "lending", "symbol": None}},
        creations={LENDER: {"creator": addr(98), "block": 5, "timestamp": BLOCK_TIME - 400 * 86400},
                   VICTIM: {"creator": addr(98), "block": 5, "timestamp": BLOCK_TIME - 90 * 86400}},
        balances_before={(VICTIM, TOKEN, BLOCK_NUMBER, i): 400_000 * USDX for i in range(8)}
        | {(POOL_A, facts.ETH, BLOCK_NUMBER, i): 40 * ONE for i in range(8)},
        decimals={TOKEN_2: 18}, function_names={"0x12345678": "flashLoan"},
        funding={SENDER: {"timestamp": BLOCK_TIME - 240, "funder": LENDER}},
        mixer_payouts={(SENDER, BLOCK_NUMBER, 3): (BLOCK_NUMBER - 25, MIXER)},
        prior_day_calls={(BOT, BLOCK_NUMBER): 0}, nonces_before={(WALLET, BLOCK_NUMBER): 0})
    return [facts.finish(facts.extract(*chain_data(trace, nonce=i)), ctx) for i, trace in enumerate(traces)]


def digest() -> str:
    rendered = [[record, *(view(record) for view in views.VIEWS.values()), views.line(record)] for record in fixtures()]
    return hashlib.sha256(json.dumps(rendered, sort_keys=True).encode()).hexdigest()


def test_facts_and_views_output_is_pinned_to_the_facts_version():
    assert facts.FACTS_VERSION in GOLDEN, "new FACTS_VERSION: add its digest to GOLDEN"
    assert digest() == GOLDEN[facts.FACTS_VERSION], (
        "what facts.py or views.py produce has changed: bump FACTS_VERSION and add the new digest, so answers Jev gave "
        f"to the old rendering are never scored as answers to the new one (new digest: {digest()})")
