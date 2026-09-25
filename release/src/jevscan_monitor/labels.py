"""Address labels with the plan's leak filters, built from a pinned public dump of Etherscan's label cloud.

Use `jevscan-monitor prepare` to prepare the filtered label index.

Source: github.com/dawsbot/eth-labels (MIT), pinned by commit so a rebuild gives the same file. Three filters apply
here; the fourth, the 30-day age rule, needs the block and is applied when a label is used (facts.Naming.label).
  1. Category allowlist: only slugs mapped below to exchange, lending, bridge, mixer, or centralized exchange, plus
     the dump's token list. Everything else (exploiter tags, MEV bots, "take action", charities) is dropped.
  2. Keyword denylist: an address with any slug or name tag matching DENY is dropped whole, whatever else it carries.
  3. Plain names: a name tag reaches Jev, so it must be short and made of ordinary characters.
"""

import json
import re

from jevscan_monitor.facts import Label
from jevscan_monitor.rpc import CACHE_DIR

DUMP_COMMIT = "3a9e42dd8e68c9fba78de8d1cb2c8e60ec34f73e"  # 2026-07-10
DUMP_PATH = f"/dawsbot/eth-labels/{DUMP_COMMIT}/data/json"
LABELS_FILE = CACHE_DIR / "labels.json"
DENY = re.compile(r"exploit|hack|phish|heist|drainer|scam|fake|spam|attack|stolen|thief|rug", re.IGNORECASE)
PLAIN_NAME = re.compile(r"[A-Za-z0-9 .:_/&()+'#$-]{1,60}")
ADDRESS_TAIL = re.compile(r"[:\s]*0x[0-9a-fA-F]{6,}.*$")  # "Some Exchange Dep: 0x9c85..." names the address again
# When an address carries several allowlisted slugs, the first category in this order wins.
CATEGORY_ORDER = ("mixer", "centralized exchange", "bridge", "lending", "exchange")

SLUGS = {
    "mixer": "mixer tornado-cash typhoon-cash ethereum-mixer",
    "centralized exchange":
        "abcc allbit altcoin-trader ascendex azbit bgogo bigone bilaxy bitbank bitbuy bitfinex bitflyer bitget bithumb "
        "bitkan bitmart bitmex bitstamp bittrex bitvavo bitvenus blofin-exchange btcturk btse bullish catex cex-io "
        "changenow cobinhood coinbase coinbit coincheck coindcx coinex coinhako coinjar coinlist coinmetro coinone "
        "coinsbit coinspot coinsquare coinstore coinw coss-io crex24 crypto-com delta-exchange deribit dex-trade difx "
        "digifinex fairdesk fastex firi ftx gate-io gbx gemini gmo-coin hitbtc hoo-com hot-wallet hotbit indodax kanga "
        "korbit kraken kryptono kucoin latoken lcx-ag liquid maskex mexc nacdaq okx paribu poloniex quadrigacx "
        "remitano resfinex tidex topbtc trade-io upbit yunbi zb-com",
    "bridge":
        "across-protocol agglayer allbridge arbitrum arbitrum-nova arbitrum-one aurora axelar base blast bridge "
        "celer-network connext cross-chain debridge everclear hop-protocol ink kroma layer-2 layerzero linea "
        "manta-network mantle metis-andromeda mode multichain omg-network optics optimism polygon ren rhino-fi scroll "
        "scroll-network stargate starknet synapse taiko tbtc wormhole xy-finance zircuit zksync",
    "lending":
        "aave abracadabra-money alchemix-finance bzx compound cream-finance dforce dolomite euler fortube "
        "fringe-finance gearbox-protocol gravita impermax inverse-finance liquity loans maker maple morpho nuo-network "
        "rari-capital reflexer-finance reservelending sky spark timeswap unit-protocol venus",
    "exchange":
        "0x-protocol 1inch airswap ambient balancer bancor clipper cow-protocol curve-fi curve-finance dex dex-ag dydx "
        "idex kyberswap loopring maverick openocean pancakeswap paraswap router saddle-finance shapeshift solidly "
        "sudoswap sushiswap swipeswap tokenlon velora",
}
CATEGORY_BY_SLUG = {slug: category for category, slugs in SLUGS.items() for slug in slugs.split()}


def plain_symbol(symbol: str) -> bool:
    """Limit symbol syntax and length; this is not a proof against prompt injection."""
    return 0 < len(symbol) <= 12 and all(c.isascii() and (c.isalnum() or c in ".-+$") for c in symbol)


def build(accounts: list[dict], tokens: list[dict]) -> dict[str, Label]:
    """The filtered label table for mainnet, from the dump's two lists."""
    denied = {row["address"].lower() for row in accounts + tokens
              if DENY.search(row.get("label") or "") or DENY.search(row.get("nameTag") or row.get("name") or "")}
    labels: dict[str, Label] = {}
    for row in accounts:
        address, category = row["address"].lower(), CATEGORY_BY_SLUG.get(row.get("label"))
        name = ADDRESS_TAIL.sub("", (row.get("nameTag") or "").strip())  # no hex reaches Jev, not even in a name
        if row.get("chainId") != 1 or address in denied or category is None or not PLAIN_NAME.fullmatch(name):
            continue
        current = labels.get(address)
        if current is None or CATEGORY_ORDER.index(category) < CATEGORY_ORDER.index(current["category"]):
            labels[address] = {"name": name, "category": category, "symbol": None}
    for row in tokens:
        address, symbol = row["address"].lower(), (row.get("symbol") or "").strip()
        if row.get("chainId") != 1 or address in denied or not plain_symbol(symbol) or DENY.search(symbol):
            continue
        labels[address] = {"name": f"{symbol} token", "category": "token", "symbol": symbol}
    return labels


def load() -> dict[str, Label]:
    if not LABELS_FILE.is_file():
        raise RuntimeError("Label index missing: run jevscan-monitor prepare")
    if LABELS_FILE.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("Label index exceeds supported size")
    table = json.loads(LABELS_FILE.read_text())
    if not isinstance(table, dict):
        raise ValueError("Invalid label index")
    for address, item in table.items():
        if not re.fullmatch(r"0x[0-9a-f]{40}", address) or not isinstance(item, dict):
            raise ValueError("Invalid label record")
        name, category, symbol = item.get("name"), item.get("category"), item.get("symbol")
        if (not isinstance(name, str) or not PLAIN_NAME.fullmatch(name) or DENY.search(name)
                or category not in {*CATEGORY_ORDER, "token"}
                or (symbol is not None and (not isinstance(symbol, str) or not plain_symbol(symbol)))):
            raise ValueError("Label record does not satisfy the metadata filters")
    return table
