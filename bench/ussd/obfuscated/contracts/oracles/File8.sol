
pragma solidity ^0.8.6;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./File12.sol";

import "../interfaces/File4.sol";
import "../interfaces/File5.sol";









contract Contract11 is Contract5 {
    AggregatorV3Interface var86;
    Contract6 var87;
    Contract5 var88;

    constructor() {
        var86 = AggregatorV3Interface(
            0x773616E4d11A78F511299002da57A0a94577F1f4
        );
        var87 = Contract6(
            0x982152A6C7f732Ec7C9EA998dDD9Ebde00Dfa16e
        );
        var88 = Contract5(0x0000000000000000000000000000000000000000);
    }

    function fn30() external view override returns (uint256) {
        address[] memory var74 = new address[](1);
        var74[0] = 0x60594a405d53811d3BC4766596EFD80fd545A270;
        uint256 var89 = var87.fn38(
            1000000000000000000,
            0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2,
            0x6B175474E89094C44Da98b954EedeAC495271d0F,
            var74,
            600
        );

        uint256 var90 = var88.fn30();



        (, int256 var48, , , ) = var86.latestRoundData();

        return
            (var90 * 1e18) /
            ((var89 + uint256(var48) * 1e10) / 2);
    }
}
