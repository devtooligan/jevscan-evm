// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "./IERC20.sol";

interface IThing {
    function thing(uint256 a) external returns (uint256);
    receive() external payable;
}

/* block comment with braces } { and a fake function evil() { } */
contract Edge is IThing {
    uint256 public total; // trailing comment with } brace
    string constant OPEN = "{ not a brace";
    string constant CLOSE = '} also not a brace \' still string }';
    mapping(address => uint256) internal balances;
    function(uint256) internal pure returns (uint256) hook;

    modifier onlyOwner {
        require(msg.sender == address(0), "owner } only");
        _;
    }

    modifier gated(uint256 x) { require(x > 0); _; }

    constructor(uint256 start) { total = start; }

    function thing(uint256 a) external override(IThing) onlyOwner gated(a) returns (uint256 r) {
        unchecked {
            for (uint256 i; i < a; ++i) {
                if (i % 2 == 0) { r += i; } else { r -= 1; }
            }
        }
        assembly {
            let p := mload(0x40)
            if iszero(p) { revert(0, 0) }
        }
        // closing brace in comment }
        /* and { another } one */
        emit Log("}");
    }

    function abstractish() external virtual;

    receive() external payable {}

    fallback() external payable { total += 1; }

    event Log(string s);
}

library L {
    function f(uint256 x) internal pure returns (uint256) { return x.receive(); }
}
