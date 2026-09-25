"""How a transaction is shown to Jev: views R0 to R4 and the one-line view, each a pure function of TxFacts.

Jev reads hex, raw numbers, and comparisons poorly, so every view but the raw floor (R0) speaks in aliases and in
words with a size bucket ("about $8.9 million (very large)"), and code makes every comparison ("received about as
much as it gave"). No view carries a transaction hash, block number, date, or, outside R0, an address.

    R0 raw        envelope and receipt counts, hex as the node gives it
    R1 receipt    what a receipt alone shows: decoded events and the ledger from logs, no trace
    R2 fact sheet every fact group as named fields, no call tree
    R3 narrative  R2 plus the pruned call tree
    R4 prose      R2 as English paragraphs
    line          R2 compressed to one line, for the block line-up (Q6)
"""

import json
import re

from jevscan_monitor.provider import est_tokens
from jevscan_monitor.facts import HIGH_VOLUME_TXS, TxFacts

R3_TOKEN_CAP = 6_000  # the plan's cap for the narrative view, in estimated tokens
TREE_CUT_NOTE_TOKENS = 30  # room for the key and the "more lines not shown" note
BUCKETS = ((100, "negligible"), (10_000, "small"), (100_000, "moderate"), (1_000_000, "large"),
           (10_000_000, "very large"))
EVEN_BAND = 0.1  # a party that got back within 10% of what it gave is "about even"
SMALL_SHARE = 0.01
ORDINALS = {1: "st", 2: "nd", 3: "rd"}


def bucket(usd: float) -> str:
    return next((name for limit, name in BUCKETS if usd < limit), "enormous")


def money(usd: float) -> str:
    """'about $8.9 million (very large)': a rounded figure in words plus its size bucket."""
    usd = abs(usd)
    if usd < 1:
        words = "under $1"
    elif usd < 10_000:
        words = f"about ${float(f'{usd:.2g}'):,.0f}"
    elif usd < 1_000_000:
        words = f"about ${usd / 1e3:.0f} thousand"
    elif usd < 1_000_000_000:
        words = f"about ${usd / 1e6:.3g} million"
    else:
        words = f"about ${usd / 1e9:.3g} billion"
    return f"{words} ({bucket(usd)})"


def quantity(amount: float | None) -> str:
    if amount is None:
        return "an unknown amount"
    if amount < 0.001:
        return "a dust amount (under 0.001 units)"
    for size, name in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million")):
        if amount >= size:
            return f"about {min(amount / size, 999):.3g} {name} units" if amount < 1e15 else "over a quadrillion units"
    if amount >= 1_000:
        return f"about {amount / 1e3:.3g} thousand units"
    return f"about {amount:.3g} units"


def span(seconds: int) -> str:
    for size, unit in ((365 * 86400, "year"), (30 * 86400, "month"), (86400, "day"), (3600, "hour"), (60, "minute")):
        if seconds >= size:
            n = seconds // size
            return f"{n} {unit}{'s' if n != 1 else ''}"
    return "under a minute"


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else ORDINALS.get(n % 10, 'th')}"


def asset_name(alias: str, facts: TxFacts) -> str:
    info = facts["assets"].get(alias)
    if info is None or info["symbol"]:
        return alias + (" NFTs" if info and info.get("nft") else "")
    origin = " created by the sender's side" if info["created_by_sender_side"] else ""
    kind = "an unrecognized NFT collection" if info.get("nft") else "an unrecognized token"
    if info["age_seconds"] is None:
        return f"{alias} ({kind}{origin})"
    when = "in this transaction" if info["age_seconds"] == 0 else f"{span(info['age_seconds'])} earlier"
    return f"{alias} ({kind} created {when}{origin})"


def value_of(item: dict, facts: TxFacts) -> str:
    """'about $4,000 (small) of USDC', or a unit count when the asset has no trustworthy price. An implied price and a
    floor price are said to be what they are."""
    info = facts["assets"].get(item["asset"]) or {}
    name = asset_name(item["asset"], facts)
    if info.get("nft"):
        count = int(item["amount"]) if item["amount"] is not None else None
        units = f"{count} {name}" if count is not None else f"some {name}"
        if item["usd"] is None:
            return f"{units} (no floor price)"
        return f"{units} ({money(item['usd'])}, {info.get('price_basis') or 'priced'})"
    if item["usd"] is None:
        return f"{quantity(item['amount'])} of {name} (no reliable price)"
    basis = f" ({info['price_basis']})" if info.get("price_basis") else ""
    return f"{money(item['usd'])} of {name}{basis}"


def describe(alias: str, facts: TxFacts) -> str:
    """An alias with what is known about the address behind it."""
    info = facts["parties"][alias]
    if alias == "sender":
        return "sender"
    if info["kind"] == "block builder":
        return "block_builder (the builder of this block)"
    traits = []
    if info["category"]:
        traits.append(info["category"])
    elif info["exchange_pool"]:
        traits.append("exchange pool")
    elif info["kind"]:
        traits.append(info["kind"])
    if info["created_in_tx"]:
        by = "another party" if info["created_by"] == "someone else" else f"the {info['created_by']}"
        traits.append(f"created in this transaction by {by}")
    elif info["age_seconds"] is not None:
        by = {"sender": " by the sender", "sender's contract": " by the sender's contract"}.get(info["created_by"], "")
        traits.append(f"created {span(info['age_seconds'])} earlier{by}")
    if info.get("source_verified") is False:
        traits.append("source code unverified")
    if info.get("prior_transactions") is not None:
        n = info["prior_transactions"]
        traits.append("no prior transactions" if n == 0 else f"{n:,} prior transactions")
    return f"{alias} ({', '.join(traits)})" if traits else alias


def exchange_words(row: dict) -> str:
    """Code compares what a party gave with what it received, because Jev should not do arithmetic."""
    gave, received = row["gave_usd"], row["received_usd"]
    unpriced = any(c["usd"] is None for c in row.get("changes", ()))
    if unpriced:
        if not gave and not received:
            priced = "no priced asset movement is recorded"
        elif not gave:
            priced = "priced assets show an inflow"
        elif not received:
            priced = "priced assets show an outflow"
        else:
            ratio = received / gave
            priced = ("priced assets are approximately balanced" if abs(ratio - 1) <= EVEN_BAND else
                      "priced assets show more received than given" if ratio > 1 else
                      "priced assets show more given than received")
        return priced + "; assets with no reliable price also moved, so total compensation cannot be determined from this ledger"
    if not gave and not received:
        return "no priced value moved"
    if not gave:
        return "received value and gave nothing"
    if not received:
        return "gave value and received nothing"
    ratio = received / gave
    if abs(ratio - 1) <= EVEN_BAND:
        return "received about as much value as it gave"
    if ratio > 1:
        return "received more value than it gave"
    return f"gave more value than it received (got back about {ratio:.0%})"


def row_words(row: dict, facts: TxFacts) -> dict:
    out = {"party": describe(row["party"], facts)}
    for direction in ("gained", "lost"):
        items = [value_of(c, facts) for c in row["changes"] if c["direction"] == direction]
        if items:
            out[direction] = "; ".join(items)
    out["balance"] = exchange_words(row)
    return out


def volume_words(prior_transactions: int) -> str | None:
    return f"a very high-volume wallet, over {HIGH_VOLUME_TXS:,} prior transactions" if prior_transactions >= HIGH_VOLUME_TXS else None


def sender_words(facts: TxFacts) -> dict:
    s = facts["sender"]
    out = {"kind": s["kind"], "prior_transactions": s["prior_transactions"]}
    if s["label"]:
        out["identity"] = f"{s['label']} ({s['category']})"
    elif s["category"]:
        out["identity"] = f"a {s['category']}"
    if volume_words(s["prior_transactions"]):
        out["activity"] = volume_words(s["prior_transactions"])
    if s["first_funded_seconds_earlier"] is not None:
        out["first_funded"] = f"{span(s['first_funded_seconds_earlier'])} earlier"
        out["funded_by"] = (f"{s['funded_by']} ({s['funded_by_category']})" if s["funded_by"]
                            else f"a {s['funded_by_category']}" if s["funded_by_category"] else "an unlabeled address")
    elif s["funding_looked_up"]:
        out["first_funded"] = "no inbound ETH transfer found"
    if s["mixer_funded_within_30_days"]:
        mixer = f"{s['mixer_paid_by']} (mixer)" if s["mixer_paid_by"] else "a mixer"
        out["mixer_funding"] = f"received funds from {mixer} {span(s['mixer_paid_seconds_earlier'])} earlier"
    return out


def entry_words(facts: TxFacts) -> dict | str:
    entry = facts["entry"]
    if entry is None:
        return "none"
    info = facts["parties"][entry["alias"]]
    if info["kind"] in ("wallet", "delegated wallet"):
        return f"none: the transaction is sent to {describe(entry['alias'], facts)}"
    out = {"contract": describe(entry["alias"], facts)}
    if entry["function"]:
        out["function_called"] = entry["function"]
    if entry["calls_in_prior_day"] is not None:
        n = entry["calls_in_prior_day"]
        out["use_in_prior_day"] = ("not called" if n == 0 else "called 100 or more times" if n >= 100
                                   else f"called {n} times")
    return out


def sender_side_words(facts: TxFacts) -> dict:
    side = facts["sender_side"]
    net, capital = side["net_usd"], side["own_capital_usd"]
    out = {"members": side["members"]}
    if abs(net) < 1:
        out["net_result"] = "no priced gain or loss"
    else:
        out["net_result"] = f"{'gained' if net > 0 else 'lost'} {money(net)}"
    out["own_capital_put_in"] = "none" if capital < 1 else money(capital)
    largest = max((max(r["gave_usd"], r["received_usd"]) for r in facts["ledger"]), default=0.0)
    if net >= BUCKETS[0][0] and largest:  # a negligible gain is not worth comparing
        share = net / largest
        out["gain_compared_with_largest_amount_moved"] = (
            "tiny (under 1% of it)" if share < 0.01 else "small (1% to 10% of it)" if share < 0.1
            else "substantial (10% to 50% of it)" if share < 0.5 else "most of it (over 50%)")
    if side["unpriced_assets"]:
        out["also_moved_unpriced_assets"] = [asset_name(a, facts) for a in side["unpriced_assets"]]
    if side["proceeds_to"]:
        out["proceeds_sent_to"] = [f"{money(p['usd'])} to {describe(p['party'], facts)}, {p['reason']}, counted as the sender's side's"
                                   for p in side["proceeds_to"]]
        out["net_result_of_the_sender_and_its_contracts_alone"] = (
            f"{'gained' if side['own_side_net_usd'] > 0 else 'lost'} {money(side['own_side_net_usd'])}"
            if abs(side["own_side_net_usd"]) >= 1 else "no priced gain or loss")
    if side["largest_gain_elsewhere"]:
        gain = side["largest_gain_elsewhere"]
        out["largest_gain_went_elsewhere"] = (f"the largest gain, {money(gain['usd'])}, went to {describe(gain['party'], facts)}, "
                                              "not to the sender's side")
    return out


def paid_words(drain: dict, facts: TxFacts) -> str:
    """What the party that gave out an asset received in the same transaction. A pool that sells half its balance of
    one token for full value is trading; a contract that pays out a small share of an old balance is paying a claim;
    what came back is stated either way, never judged."""
    caveat = ", not counting assets with no reliable price" if drain["unpriced_legs"] else ""
    if not drain["received_usd"]:
        if drain["unpriced_received"]:
            return "it received only assets with no reliable price (" + ", ".join(asset_name(a, facts) for a in drain["received_assets"]) + ")"
        return "no tokens came back to it in this transaction"
    got = f"it received {money(drain['received_usd'])} of " + ", ".join(asset_name(a, facts) for a in drain["received_assets"][:2])
    ratio = drain["received_usd"] / drain["gave_usd"]
    if ratio < 1 - EVEN_BAND:
        got += f", about {ratio:.0%} of what it gave out"
    return got + caveat


def share_words(share: float | None) -> str:
    if share is None:
        return "its balance just before is unknown or zero"
    if share >= 1:
        return "its entire balance just before this transaction, or more"
    if share < SMALL_SHARE:
        return "under 1% of its balance just before this transaction"
    return f"{share:.0%} of its balance just before this transaction"


def drain_words(drain: dict, facts: TxFacts) -> str:
    """One party's outflow with everything that says whether it was a sale, a payout, or a robbery: the share of its
    balance, its age (in its description), what came back, what it recorded, what the sender's side burned, and what
    the same sender put into it earlier in the block."""
    verb = "gave out" if drain["received_usd"] else "sent out"
    text = (f"{describe(drain['party'], facts)} {verb} {value_of(drain, facts)} "
            f"({share_words(drain['share_of_prior_balance'])}); {paid_words(drain, facts)}")
    if not drain["received_usd"] and drain["events_recorded"]:
        text += "; it recorded " + " and ".join(drain["events_recorded"]) + (" events" if len(drain["events_recorded"]) > 1 else " event")
    if not drain["received_usd"] and facts["sender_side"]["burned"]:
        text += "; the sender's side burned " + "; ".join(value_of(b, facts) for b in facts["sender_side"]["burned"][:2])
    if drain["same_sender_put_in_earlier"]:
        earlier = drain["same_sender_put_in_earlier"]
        text += (f"; the same sender put {value_of(earlier, facts)} into it earlier in this block "
                 f"(transaction {ordinal(earlier['index'] + 1)} of the block)")
    return text


def minted_words(minted: dict, facts: TxFacts) -> str:
    text = f"{value_of(minted, facts)}, minted to {minted['to']}"
    if minted["issued_by"] == "sender":
        text += " at the sender's own call"
    elif minted["issued_by"]:
        text += f" by {describe(minted['issued_by'], facts)}"
    if minted["issuer_received_from_side"] is not None:
        got = minted["issuer_received_from_side"]
        text += (", which received from the sender's side " + "; ".join(value_of(a, facts) for a in got[:2])) if got \
            else ", which received nothing from the sender's side in this transaction"
    return text


def lending_accounting_words(issuance: dict, facts: TxFacts) -> str:
    return (f"{describe(issuance['lender'], facts)} emitted Borrow and its call minted {value_of(issuance['issued'], facts)} "
            f"to {issuance['borrower']} in the same transaction. This issuance is linked to the lending operation, but does not by itself "
            "establish authorization or adequate collateral.")


def collateral_words(c: dict, facts: TxFacts) -> str:
    return (f"the sender's side minted {value_of(c['posted'], facts)} itself, posted it to {describe(c['posted_to'], facts)}, "
            f"and received {value_of(c['received'], facts)} from it")


def position_words(p: dict, facts: TxFacts) -> str:
    minted = f", {p['minted']} of them newly minted" if p["minted"] else ""
    to = f", to {', '.join(p['to'])}" if p["to"] else ""
    side = " (the sender's side)" if p["to_sender_side"] == p["count"] and p["count"] else ""
    amounts = f"; raw quantities include {', '.join(p['raw_amounts'])}" if p["raw_amounts"] else ""
    ids = f"; raw identifiers include {', '.join(p['raw_ids'])}" if p["raw_ids"] else ""
    return (f"{p['count']} ERC-1155 position transfer{'s' if p['count'] != 1 else ''} issued by "
            f"{describe(p['issuer'], facts)}{minted}{to}{side}; positions have no market price here{amounts}{ids}")


def allowance_words(change: dict, facts: TxFacts) -> str:
    giver = "the sender's side" if change["owner_is_sender_side"] else describe(change["owner"], facts)
    receiver = "the sender's side" if change["spender_is_sender_side"] else describe(change["spender"], facts)
    amount = change["asset"]
    value = (f"the maximum possible {asset_name(amount['asset'], facts)}"
             if int(amount["amount_raw"]) == 2**256 - 1 else value_of(amount, facts))
    return f"{giver} granted {value} allowance to {receiver}"


def internal_balance_words(change: dict, facts: TxFacts) -> str:
    account = "the sender's side" if change["account_is_sender_side"] else describe(change["account"], facts)
    return (f"{account} was {change['direction']} {value_of(change, facts)} as an internal balance in "
            f"{describe(change['vault'], facts)}")


def pull_words(pull: dict, facts: TxFacts) -> str:
    """Who took tokens with transferFrom, from how many addresses, under allowances granted when, and to whom."""
    amount = money(pull["usd"]) if pull["usd"] is not None else "an unpriced amount"
    assets = ", ".join(asset_name(a, facts) for a in pull["assets"])
    who = pull["spender_is"] + ("" if pull["spender_is"] == "the sender" else f" ({describe(pull['spender'], facts)})")
    granted = pull["approved_in_this_transaction"]
    when = ("granted in this same transaction" if granted == pull["transfers"] else
            "granted before this transaction" if granted == 0 else
            f"granted before this transaction for {pull['transfers'] - granted} of the {pull['transfers']} transfers")
    into = ", ".join(pull["recipients"]) or "unknown recipients"
    return (f"{who} pulled {amount} of {assets} from {pull['owners']} address{'es' if pull['owners'] != 1 else ''} "
            f"under allowances {when}, into {into}")


def shape_words(facts: TxFacts) -> dict:
    shape = facts["call_shape"]
    out = {k: shape[k] for k in ("calls", "max_depth", "distinct_contracts", "contracts_created",
                                 "contracts_destroyed", "reverted_inner_calls")}
    if shape["repeated_calls"]:
        out["repeated_calls"] = [f"{r['function'] or 'a function'} on {r['target']}, {r['count']} times"
                                 for r in shape["repeated_calls"]]
    if shape["nft_transfers"]:
        out["nft_transfers"] = shape["nft_transfers"]
    return out


def r0(facts: TxFacts) -> dict:
    tx = facts["tx"]
    return {"from": tx["from"], "to": tx["to"] or "none (contract creation)", "function_selector": tx["selector"],
            "input_bytes": tx["input_bytes"], "value_wei": tx["value_wei"], "status": facts["status"],
            "log_count": tx["log_count"], "gas_used": tx["gas_used"], "transaction_type": tx["type"]}


def r1(facts: TxFacts) -> dict:
    return {
        "status": facts["status"],
        "sender": {"kind": facts["sender"]["kind"], "prior_transactions": facts["sender"]["prior_transactions"]},
        "sent_to": entry_words(facts) if facts["entry"] else "a wallet",
        "value_sent": money(facts["mev"]["value_sent_usd"]) + " of ETH" if facts["mev"]["value_sent_usd"] >= 1 else "none",
        "net_asset_changes_from_event_logs": [row_words(r, facts) for r in facts["ledger_logs_only"]],
        "newly_minted": [f"{value_of(m, facts)}, minted to {m['to']}" for m in facts["minted"]],
        "tokens_pulled_with_transferFrom": [pull_words(p, facts) for p in facts["pulls"]],
        "flash_loan_events": [f"{value_of(loan, facts)} from {describe(loan['lender'], facts)}"
                              for loan in facts["flash_loans"] if loan["detected_by"] == "event"],
        "privileged_events": privileged_words(facts),
        "events": [f"{e['event']} by {e['contract']}" + (f", {e['count']} times" if e["count"] > 1 else "")
                   for e in facts["events"]],
        "event_log_count": facts["tx"]["log_count"],
    }


def privileged_words(facts: TxFacts) -> list[str]:
    return [f"{p['event']} on {describe(p['contract'], facts)}"
            + (f", naming {describe(p['subject'], facts)}" if p["subject"] else "") for p in facts["privileged_events"]]


def r2(facts: TxFacts) -> dict:
    tip = facts["mev"]["builder_payment_usd"]
    sheet = {
        "status": facts["status"],
        "sender": sender_words(facts),
        "entry_contract": entry_words(facts),
        "value_sent": money(facts["mev"]["value_sent_usd"]) + " of ETH" if facts["mev"]["value_sent_usd"] >= 1 else "none",
        "flash_loans": [f"{value_of(loan, facts)} from {describe(loan['lender'], facts)}"
                        for loan in facts["flash_loans"]],
        "protocols_touched": facts["protocols_touched"],
        "sender_side": sender_side_words(facts),
        "net_asset_changes": [row_words(r, facts) for r in facts["ledger"]],
        "newly_minted": [minted_words(m, facts) for m in facts["minted"]],
        "lending_accounting_issuances": [lending_accounting_words(item, facts) for item in facts["lending_accounting_issuances"]],
        "tokens_pulled_with_transferFrom": [pull_words(p, facts) for p in facts["pulls"]],
        "standalone_allowance_changes": [allowance_words(change, facts) for change in facts["allowance_changes"]],
        "internal_balance_changes": [internal_balance_words(change, facts) for change in facts["internal_balance_changes"]],
        "self_minted_collateral": [collateral_words(c, facts) for c in facts["self_minted_collateral"]],
        "positions_moved": [position_words(p, facts) for p in facts["positions_moved"]],
        "largest_losses": [drain_words(d, facts) for d in facts["drains"]],
        "preparation_shape": ("deploys a contract and moves positions or unpriced tokens while no priced value moves: the shape of "
                              "either a preparation step or an attack on assets nobody prices") if facts["precursor"] else None,
        "this_senders_earlier_transactions_in_this_window": [
            f"{n['blocks_earlier']} block{'s' if n['blocks_earlier'] != 1 else ''} earlier this sender {n['summary']}"
            for n in facts["earlier_by_this_sender"]],
        "logic_or_control_changed": [f"{describe(c['contract'], facts)} {c['what']}" for c in facts["logic_changes"]],
        "contracts_whose_logic_changed_recently": [
            (f"{describe(h['contract'], facts)} {h['what']} {h['blocks_earlier']} block{'s' if h['blocks_earlier'] != 1 else ''} earlier"
             + (f", after {span(h['contract_age_seconds'])} without a recorded change in this window" if h["contract_age_seconds"] else ""))
            for h in facts["heightened"]],
        "reentrancy": [f"{describe(r['contract'], facts)} was {'read' if r['read_only'] else 'called'} again through "
                       f"{r['through']} before an earlier call into it had finished" for r in facts["reentrancy"]]
        or "none detected",
        "privileged_events": privileged_words(facts),
        "events": [f"{e['event']} by {e['contract']}" + (f", {e['count']} times" if e["count"] > 1 else "")
                   for e in facts["events"]],
        "call_shape": shape_words(facts),
        "block_position": f"{ordinal(facts['mev']['position'])} of {facts['mev']['block_transactions']}",
        "builder_payment": money(tip) if tip >= 1 else "none",
    }
    return sheet


def r3(facts: TxFacts) -> dict:
    """The fact sheet plus the call tree. The tree arrives pruned to its own cap; when a very large fact sheet leaves
    it less room than that, its last lines give way, so the whole view stays under R3_TOKEN_CAP."""
    sheet = r2(facts)
    tree = list(facts["call_tree"])
    room = R3_TOKEN_CAP - TREE_CUT_NOTE_TOKENS - est_tokens(json.dumps(sheet))
    while tree and est_tokens(json.dumps(tree)) > room:
        tree.pop()
    if len(tree) < len(facts["call_tree"]):
        tree.append(f"({len(facts['call_tree']) - len(tree)} more lines not shown)")
    rendered = sheet | {"call_tree": tree or "no calls beyond the first"}
    if est_tokens(json.dumps(rendered)) > R3_TOKEN_CAP:
        raise ValueError("Fact sheet exceeds the narrative view limit")
    return rendered


def r4(facts: TxFacts) -> dict:
    sheet = r2(facts)
    s, entry, side = sheet["sender"], sheet["entry_contract"], sheet["sender_side"]
    text = [(f"The transaction {'succeeded' if facts['status'] == 'success' else 'failed and changed nothing'}. "
             f"The sender is {s['identity'] + ', ' if 'identity' in s else ''}a {s['kind']} that had made "
             f"{s['prior_transactions']:,} transactions before this one" + (f", {s['activity']}." if "activity" in s else "."))]
    if "funded_by" in s:
        text.append(f"It was first funded {s['first_funded']} by {s['funded_by']}.")
    if "mixer_funding" in s:
        text.append(f"It {s['mixer_funding']}.")
    if isinstance(entry, str):
        text.append("It calls no contract: " + entry.removeprefix("none: ") + "." if entry != "none" else
                    "It calls no contract.")
    else:
        called = f"calls {entry['function_called']} on" if "function_called" in entry else "calls"
        if facts["parties"][facts["entry"]["alias"]]["created_in_tx"]:
            called = "deploys and runs"
        text.append(f"The sender {called} {entry['contract']}."
                    + (f" In the prior day that contract was {entry['use_in_prior_day']}." if "use_in_prior_day" in entry else ""))
    if sheet["value_sent"] != "none":
        text.append(f"The sender sends {sheet['value_sent']} with the transaction.")
    for loan in sheet["flash_loans"]:
        text.append(f"It takes a flash loan of {loan}.")
    if sheet["protocols_touched"]:
        text.append("Labeled protocols touched: " + ", ".join(sheet["protocols_touched"]) + ".")
    text.append(f"The sender's side ({', '.join(side['members'])}) ends the transaction having {side['net_result']}"
                if side["net_result"] != "no priced gain or loss" else
                f"The sender's side ({', '.join(side['members'])}) ends the transaction with no priced gain or loss")
    text[-1] += f", and put in {side['own_capital_put_in']} of its own capital" if side["own_capital_put_in"] != "none" \
        else ", and put in none of its own capital"
    text[-1] += (f". Compared with the largest amount moved, that gain is {side['gain_compared_with_largest_amount_moved']}."
                 if "gain_compared_with_largest_amount_moved" in side else ".")
    if "also_moved_unpriced_assets" in side:
        text.append("It also moved assets with no reliable price: " + ", ".join(side["also_moved_unpriced_assets"]) + ".")
    for row in sheet["net_asset_changes"]:
        moved = " and ".join(f"{direction} {row[direction]}" for direction in ("gained", "lost") if direction in row)
        text.append(f"{row['party']} {moved}; it {row['balance']}.")
    for minted in sheet["newly_minted"]:
        text.append(f"Newly minted: {minted}.")
    for issuance in sheet["lending_accounting_issuances"]:
        text.append(f"Lending accounting issuance: {issuance}.")
    for pull in sheet["tokens_pulled_with_transferFrom"]:
        text.append(f"Tokens pulled with transferFrom: {pull}.")
    for words in sheet["self_minted_collateral"]:
        text.append(f"Self-minted collateral: {words}.")
    for words in sheet["positions_moved"]:
        text.append(f"Positions moved: {words}.")
    if "proceeds_sent_to" in side:
        text.append("Proceeds sent to: " + "; ".join(side["proceeds_sent_to"]) + ". The sender and its contracts alone "
                    f"ended with {side['net_result_of_the_sender_and_its_contracts_alone']}.")
    if "largest_gain_went_elsewhere" in side:
        text.append(side["largest_gain_went_elsewhere"][0].upper() + side["largest_gain_went_elsewhere"][1:] + ".")
    if sheet["preparation_shape"]:
        text.append("Shape: " + sheet["preparation_shape"] + ".")
    for words in sheet["this_senders_earlier_transactions_in_this_window"]:
        text.append(f"Earlier in this window: {words}.")
    for words in sheet["logic_or_control_changed"]:
        text.append(f"Logic or control changed: {words}.")
    for words in sheet["contracts_whose_logic_changed_recently"]:
        text.append(f"Heightened state: {words}.")
    for loss in sheet["largest_losses"]:
        text.append(f"Largest losses: {loss}.")
    text.append("Reentrancy: " + ("; ".join(sheet["reentrancy"]) if isinstance(sheet["reentrancy"], list)
                                  else "none detected") + ".")
    for event in sheet["privileged_events"]:
        text.append(f"Privileged event: {event}.")
    if sheet["events"]:
        text.append("Other events: " + "; ".join(sheet["events"]) + ".")
    shape = sheet["call_shape"]
    text.append(f"The transaction makes {shape['calls']} calls to {shape['distinct_contracts']} contracts, "
                f"{shape['max_depth']} deep, creates {shape['contracts_created']} contracts, destroys "
                f"{shape['contracts_destroyed']}, and has {shape['reverted_inner_calls']} reverted inner calls."
                + (" Repeated calls: " + "; ".join(shape["repeated_calls"]) + "." if "repeated_calls" in shape else ""))
    text.append(f"In its block it is the {sheet['block_position']} transactions. "
                + ("It pays the block builder no tip." if sheet["builder_payment"] == "none"
                   else f"It pays the block builder {sheet['builder_payment']}."))
    return {"description": " ".join(text)}


def line(facts: TxFacts) -> str:
    """The fact sheet in about 60 tokens, for the block line-up."""
    s, side, entry = facts["sender"], facts["sender_side"], facts["entry"]
    who = f"{s['label']} ({s['category']}) " if s["label"] else f"a {s['category']} " if s["category"] else ""
    parts = [f"{'FAILED ' if facts['status'] == 'failed' else ''}sender {who}{s['kind']} with {s['prior_transactions']:,} "
             f"prior txs" + (" (very high-volume)" if volume_words(s["prior_transactions"]) else "")
             + (", mixer-funded" if s["mixer_funded_within_30_days"] else "")]
    if entry is None:
        parts.append("no contract called")
    else:
        info = facts["parties"][entry["alias"]]
        if info["created_in_tx"]:
            parts.append("deploys and runs a new contract")
        elif info["kind"] in ("wallet", "delegated wallet"):
            parts.append("pays a wallet")
        else:
            age = f", created {span(info['age_seconds'])} earlier" if info["age_seconds"] is not None else ""
            parts.append(f"calls {entry['function'] + ' on ' if entry['function'] else ''}{entry['alias']}{age}")
    for loan in facts["flash_loans"][:2]:
        parts.append(f"flash loan {money(loan['usd']) if loan['usd'] is not None else 'of an unpriced asset'}")
    net = side["net_usd"]
    if abs(net) >= 1:
        parts.append(f"sender side {'gains' if net > 0 else 'loses'} {money(net)}"
                     + (" counting proceeds sent elsewhere" if side["proceeds_to"] else "") + ", own capital "
                     + ("none" if side["own_capital_usd"] < 1 else money(side["own_capital_usd"])))
    for minted in facts["minted"][:1]:
        if minted["usd"] is not None and minted["usd"] >= 1:
            by = f" by {minted['issued_by']}" if minted["issued_by"] and minted["issued_by"] != "sender" else ""
            parts.append(f"{money(minted['usd'])} newly minted to {minted['to']}{by}")
    for pull in facts["pulls"][:1]:
        amount = money(pull["usd"]) if pull["usd"] is not None else "unpriced tokens"
        parts.append(f"{pull['spender_is']} pulls {amount} from {pull['owners']} address{'es' if pull['owners'] != 1 else ''} "
                     f"by transferFrom into {', '.join(pull['recipients'][:2])}")
    for p in facts["sender_side"]["proceeds_to"][:2]:
        parts.append(f"{money(p['usd'])} of proceeds to {p['party']} ({p['reason']})")
    if facts["sender_side"]["largest_gain_elsewhere"]:
        gain = facts["sender_side"]["largest_gain_elsewhere"]
        parts.append(f"largest gain {money(gain['usd'])} went to {gain['party']}, not the sender")
    for c in facts["self_minted_collateral"][:1]:
        parts.append(f"minted its own collateral, posted it to {c['posted_to']}, received {value_of(c['received'], facts)}")
    for p in facts["positions_moved"][:1]:
        parts.append(f"{p['count']} ERC-1155 positions issued by {p['issuer']}" + (" minted" if p["minted"] else ""))
    if facts["precursor"]:
        parts.append("preparation shape: deploys and moves positions, no priced value")
    for n in facts["earlier_by_this_sender"][:1]:
        parts.append(f"{n['blocks_earlier']} blocks earlier this sender {n['summary']}")
    for c in facts["logic_changes"][:1]:
        parts.append(f"{c['contract']} {c['what']}")
    for h in facts["heightened"][:1]:
        parts.append(f"{h['contract']} {h['what']} {h['blocks_earlier']} blocks earlier")
    for drain in facts["drains"][:1]:
        share = drain["share_of_prior_balance"]
        if share is not None and share >= SMALL_SHARE:  # an outflow under 1% of a balance is not worth a line
            if drain["received_usd"]:
                ratio = drain["received_usd"] / drain["gave_usd"]
                back = "paid about as much back" if ratio >= 1 - EVEN_BAND else f"got back about {ratio:.0%}"
                parts.append(f"{drain['party']} gave out {min(share, 1):.0%} of an asset balance, {back}")
            else:
                recorded = f", {drain['events_recorded'][0]} event" if drain["events_recorded"] else ""
                parts.append(f"{drain['party']} sent out {min(share, 1):.0%} of an asset balance, no tokens back{recorded}")
            if drain["same_sender_put_in_earlier"]:
                parts.append("the same sender put that in earlier in this block")
    if facts["reentrancy"]:
        parts.append("reentrancy seen")
    if facts["privileged_events"]:
        parts.append(f"{facts['privileged_events'][0]['event']} event")
    shape = facts["call_shape"]
    parts.append(f"{shape['calls']} calls, {shape['contracts_created']} contracts created")
    return "; ".join(parts)


VIEWS = {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4}


# ---- The names switch ------------------------------------------------------------------------------------------------

KEPT_NAMES = {"WETH", "WETH token"}  # the native asset's wrapper says nothing about which protocols are involved
STABLE_BAND = 0.03
PARTY_WORDS = {"lending": "lending_protocol", "exchange": "exchange", "bridge": "bridge", "mixer": "mixer",
               "token": "token_contract", "centralized exchange": "centralized_exchange"}


def anonymize(facts: TxFacts) -> TxFacts:
    """The record with every label and token symbol replaced by its category and a number ("lending_protocol_1",
    "stablecoin_2"), to measure how much Jev leans on names it may have memorized from a famous incident. A token
    counts as a stablecoin when its price in this record is within 3% of a dollar. Function names stay: they say what
    was done, not to whom."""
    unit_prices: dict[str, float] = {}
    priced = [c for row in facts["ledger"] + facts["ledger_logs_only"] for c in row["changes"]]
    for item in priced + facts["minted"] + facts["drains"] + facts["flash_loans"]:
        if item["usd"] is not None and item["amount"]:
            unit_prices[item["asset"]] = item["usd"] / item["amount"]
    renamed: dict[str, str] = {}
    counts: dict[str, int] = {}

    def numbered(stem: str) -> str:
        counts[stem] = counts.get(stem, 0) + 1
        return f"{stem}_{counts[stem]}"

    for alias, info in facts["parties"].items():
        if info["label"] and alias not in KEPT_NAMES:
            renamed[alias] = numbered(PARTY_WORDS[info["category"]])
    for alias, info in facts["assets"].items():
        if info["symbol"] and alias not in KEPT_NAMES:
            stable = abs(unit_prices.get(alias, 0.0) - 1) <= STABLE_BAND
            renamed[alias] = numbered("stablecoin" if stable else "token")
    names = sorted(renamed, key=len, reverse=True)
    pattern = re.compile("|".join(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])" for name in names)) if names else None

    def walk(value):
        if isinstance(value, str):
            return pattern.sub(lambda m: renamed[m.group(0)], value) if pattern else value
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    out = walk({k: v for k, v in facts.items() if k != "tx"}) | {"tx": facts["tx"]}
    for field in ("parties", "assets"):
        out[field] = {renamed.get(key, key): value for key, value in out[field].items()}
    out["protocols_touched"] = [renamed.get(name, "a labeled protocol") for name in facts["protocols_touched"]
                                if name not in KEPT_NAMES]
    out["sender"] = facts["sender"] | {"funded_by": None, "mixer_paid_by": None, "label": None}
    return out


def r2_anonymous(facts: TxFacts) -> dict:
    return r2(anonymize(facts))


def line_anonymous(facts: TxFacts) -> str:
    return line(anonymize(facts))


CONTROL_VIEWS = {"R2-anon": r2_anonymous}
LINE_VIEWS = {"line": line, "line-anon": line_anonymous}
