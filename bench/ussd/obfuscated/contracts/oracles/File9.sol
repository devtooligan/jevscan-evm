
pragma solidity ^0.8.6;

import "./File12.sol";

import "../interfaces/File4.sol";
import "../interfaces/File5.sol";





contract Contract12 is Contract5 {
    Contract6 var91;
    Contract5 var88;

    constructor(address var92) {
        var91 = Contract6(
            0x982152A6C7f732Ec7C9EA998dDD9Ebde00Dfa16e
        );
        var88 = Contract5(var92);
    }

    function fn30() external view override returns (uint256) {
        address[] memory var74 = new address[](1);
        var74[0] = 0x982152A6C7f732Ec7C9EA998dDD9Ebde00Dfa16e;
        uint256 var93 = var91
            .fn38(
                1000000000000000000,
                0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2,
                0x2bA64EFB7A4Ec8983E22A49c81fa216AC33f383A,
                var74,
                600
            );

        uint256 var90 = var88.fn30();

        return (var90 * 1e18) / var93;
    }
}
