
pragma solidity ^0.8.6;









contract Contract1 {
    address public var1;
    uint public var2;

    modifier fn1() {
        if (msg.sender == var1) _;
    }

    constructor() {
        var1 = msg.sender;
    }

    function fn2(uint var3) public fn1 {
        var2 = var3;
    }
}
