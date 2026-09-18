
pragma solidity ^0.8.6;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

import "../interfaces/File4.sol";





contract Contract14 is Contract5 {
    AggregatorV3Interface var94;

    constructor() {
        var94 = AggregatorV3Interface(
            0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
        );
    }

    function fn30() external view override returns (uint256) {

        (, int256 var48, , , ) = var94.latestRoundData();

        return uint256(var48) * 1e10;
    }
}
