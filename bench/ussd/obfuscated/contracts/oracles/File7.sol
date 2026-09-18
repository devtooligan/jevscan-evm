
pragma solidity ^0.8.6;

import "../interfaces/File4.sol";


contract Contract10 is Contract5 {

    uint256 public var48;

    constructor(uint256 var85) {
        var48 = var85;
    }

    function fn30() override external view returns (uint256) {
        return var48;
    }

    function fn46(uint256 var85) public {
        var48 = var85;
    }
}
