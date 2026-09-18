
pragma solidity ^0.8.6;

import "./File4.sol";

import "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";






struct Contract7 {
    address var8;
    bool var78;
    bool var79;
    Contract5 var80;
    bytes var81;
    bytes var82;
    uint256[] var83;
}

interface Contract8 {
    function fn27() external;
    function fn21() external returns(address var84);
}

interface Contract9 is IERC20Upgradeable {
    function fn14(uint256 var33) external;
    function fn15(uint256 var33) external;
    function fn4() external returns (Contract7[] calldata);
    function fn12() external returns(uint256);
    function fn18(bytes memory var36, uint256 var37) external;
}
