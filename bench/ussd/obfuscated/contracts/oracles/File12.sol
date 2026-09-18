
pragma solidity ^0.8.6;
pragma abicoder v2;

import '@openzeppelin/contracts/utils/Address.sol';
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol';
import '@uniswap/v3-periphery/contracts/libraries/PoolAddress.sol';
import '@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol';
import '../interfaces/File5.sol';





contract Contract15 is Contract6 {

  IUniswapV3Factory public immutable override fn31;

  uint8 public immutable override fn32;
  uint24[] internal var95;

  constructor(IUniswapV3Factory var96, uint8 var97) {
    fn31 = var96;
    fn32 = var97;


    var95.push(500);
    var95.push(3000);
    var95.push(10000);
  }


  function fn33() external view override returns (uint24[] memory) {
    return var95;
  }


  function fn34(address var98, address var99) external view override returns (bool) {
    uint256 var100 = var95.length;
    for (uint256 var26; var26 < var100; ++var26) {
      address var44 = PoolAddress.computeAddress(address(fn31), PoolAddress.getPoolKey(var98, var99, var95[var26]));
      if (Address.isContract(var44)) {
        return true;
      }
    }
    return false;
  }


  function fn35(address var98, address var99) public view override returns (address[] memory) {
    return fn51(var98, var99, var95);
  }


  function fn36(
    uint128 var101,
    address var102,
    address var103,
    uint32 var104
  ) external view override returns (uint256 var105, address[] memory var106) {
    var106 = fn50(var102, var103, var104);
    var105 = fn49(var101, var102, var103, var106, var104);
  }


  function fn37(
    uint128 var101,
    address var102,
    address var103,
    uint24[] calldata var107,
    uint32 var104
  ) external view override returns (uint256 var105, address[] memory var106) {
    var106 = fn51(var102, var103, var107);
    require(var106.length == var107.length, 'Given tier does not have pool');
    var105 = fn49(var101, var102, var103, var106, var104);
  }


  function fn38(
    uint128 var101,
    address var102,
    address var103,
    address[] calldata var108,
    uint32 var104
  ) external view override returns (uint256 var105) {
    return fn49(var101, var102, var103, var108, var104);
  }


  function fn39(
    address var98,
    address var99,
    uint32 var104
  ) external override returns (address[] memory var109) {
    return fn42(var98, var99, fn47(var104));
  }


  function fn40(
    address var98,
    address var99,
    uint24[] calldata var107,
    uint32 var104
  ) external override returns (address[] memory var109) {
    return fn43(var98, var99, var107, fn47(var104));
  }


  function fn41(address[] calldata var108, uint32 var104) external override {
    fn44(var108, fn47(var104));
  }


  function fn42(
    address var98,
    address var99,
    uint16 var110
  ) public override returns (address[] memory var109) {
    var109 = fn35(var98, var99);
    fn48(var109, var110);
  }


  function fn43(
    address var98,
    address var99,
    uint24[] calldata var107,
    uint16 var110
  ) public override returns (address[] memory var109) {
    var109 = fn51(var98, var99, var107);
    require(var109.length == var107.length, 'Given tier does not have pool');
    fn48(var109, var110);
  }


  function fn44(address[] calldata var108, uint16 var110) public override {
    fn48(var108, var110);
  }


  function fn45(uint24 var111) external override {
    require(fn31.feeAmountTickSpacing(var111) != 0, 'Invalid fee tier');
    for (uint256 var26; var26 < var95.length; var26++) {
      require(var95[var26] != var111, 'Tier already supported');
    }
    var95.push(var111);
  }

  function fn47(uint32 var104) internal view returns (uint16 var110) {

    var110 = uint16((var104 * fn32) / 60) + 1;
  }

  function fn48(address[] memory var108, uint16 var110) internal {
    for (uint256 var26; var26 < var108.length; var26++) {
      IUniswapV3Pool(var108[var26]).increaseObservationCardinalityNext(var110);
    }
  }

  function fn49(
    uint128 var101,
    address var102,
    address var103,
    address[] memory var108,
    uint32 var104
  ) internal view returns (uint256 var105) {
    require(var108.length > 0, 'No defined pools');
    OracleLibrary.WeightedTickData[] memory var112 = new OracleLibrary.WeightedTickData[](var108.length);
    for (uint256 var26; var26 < var108.length; var26++) {
      (var112[var26].tick, var112[var26].weight) = var104 > 0
        ? OracleLibrary.consult(var108[var26], var104)
        : OracleLibrary.getBlockStartingTickAndLiquidity(var108[var26]);
    }
    int24 var113 = var112.length == 1 ? var112[0].tick : OracleLibrary.getWeightedArithmeticMeanTick(var112);
    return OracleLibrary.getQuoteAtTick(var113, var101, var102, var103);
  }






  function fn50(
    address var98,
    address var99,
    uint32 var104
  ) internal view virtual returns (address[] memory var114) {
    address[] memory var115 = fn35(var98, var99);

    if (var104 == 0) return var115;

    var114 = new address[](var115.length);
    uint256 var116;
    for (uint256 var26; var26 < var115.length; var26++) {
      if (OracleLibrary.getOldestObservationSecondsAgo(var115[var26]) >= var104) {
        var114[var116++] = var115[var26];
      }
    }

    fn52(var114, var116);
  }






  function fn51(
    address var98,
    address var99,
    uint24[] memory var107
  ) internal view virtual returns (address[] memory var108) {
    var108 = new address[](var107.length);
    uint256 var116;
    for (uint256 var26; var26 < var107.length; var26++) {
      address var44 = PoolAddress.computeAddress(address(fn31), PoolAddress.getPoolKey(var98, var99, var107[var26]));
      if (Address.isContract(var44)) {
        var108[var116++] = var44;
      }
    }

    fn52(var108, var116);
  }

  function fn52(address[] memory var117, uint256 var118) internal pure {

    if (var117.length == var118) return;


    assembly {
      mstore(var117, var118)
    }
  }
}
