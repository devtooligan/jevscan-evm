
pragma solidity ^0.8.6;

import "./interfaces/File6.sol";

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";

import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/IERC20MetadataUpgradeable.sol";





contract Contract4 is AccessControlUpgradeable, Contract8 {
    using SafeERC20Upgradeable for IERC20Upgradeable;


    IUniswapV3Pool public var39;


    address public Contract2;


    uint256 private var40;


    uint256[] public var41;


    address private var42;


    bytes32 public constant var5 = keccak256("STABLECONTROL");

    function initialize(address var43) public initializer {
        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());

        var40 = 1e4;
        Contract2 = var43;
    }

    modifier fn3() {
        require(hasRole(var5, msg.sender), "control only");
        _;
    }

    function fn20(address var44) public fn3 {
      var39 = IUniswapV3Pool(var44);
    }

    function fn21() public view override returns (address) {
        return address(var39);
    }

    function fn22(uint256 var45) public fn3 {
      var40 = var45;
    }

    function fn23(uint256[] calldata var46) public fn3 {
      var41 = var46;
    }

    function fn24(address var47) public fn3 {
      var42 = var47;
    }


    function fn25() public view returns (uint256 var48) {
      (uint160 var49,,,,,,) =  var39.slot0();
      if(var39.token0() == Contract2) {
        var48 = uint(var49)*(uint(var49))/(1e6) >> (96 * 2);
      } else {
        var48 = uint(var49)*(uint(var49))*(1e18                                        ) >> (96 * 2);

        var48 = (1e24 / var48) / 1e12;
      }
    }


    function fn26() public view returns (uint256, uint256) {
      uint256 var50 = IERC20Upgradeable(var39.token0()).balanceOf(address(var39));
      uint256 var51 = IERC20Upgradeable(var39.token1()).balanceOf(address(var39));
      if (var39.token0() == Contract2) {
        return (var50, var51);
      }
      return (var51, var50);
    }

    function fn27() override public {
      uint256 var52 = fn25();
      (uint256 var53, uint256 var54) = fn26();
      if (var52 < 1e6 - var40) {

        fn28((var53 - var54 / 1e12)/2);
      } else if (var52 > 1e6 + var40) {





        Contract9(Contract2).fn14(((var54 / 1e12 - var53)/2) * 99 / 100);
        fn29();
      }
    }

    function fn28(uint256 var55) internal {
      Contract7[] memory var11 = Contract9(Contract2).fn4();

      uint var56 = var55 * 1e12;
      uint var57 = 0;

      for (uint256 var26 = 0; var26 < var11.length; var26++) {
        uint256 var58 = IERC20Upgradeable(var11[var26].var8).balanceOf(Contract2) * 1e18 / (10**IERC20MetadataUpgradeable(var11[var26].var8).decimals()) * var11[var26].var80.fn30() / 1e18;
        if (var58 > var56) {

          if (var11[var26].var82.length > 0) {
            uint256 var59 = IERC20Upgradeable(var42).balanceOf(Contract2);
            uint256 var60 = IERC20Upgradeable(var11[var26].var8).balanceOf(Contract2) * ((var56 * 1e18 / var58) / 1e18) / 1e18;
            Contract9(Contract2).fn18(var11[var26].var82, var60);
            var56 -= (IERC20Upgradeable(var42).balanceOf(Contract2) - var59);
            var57 += (IERC20Upgradeable(var42).balanceOf(Contract2) - var59);
          } else {

            var57 = IERC20Upgradeable(var11[var26].var8).balanceOf(Contract2) * var56 / var58;
          }
          break;
        } else {

          if (var58 >= var56 / 20) {
            uint256 var59 = IERC20Upgradeable(var42).balanceOf(Contract2);

            Contract9(Contract2).fn18(var11[var26].var82, IERC20Upgradeable(var11[var26].var8).balanceOf(Contract2));
            var56 -= (IERC20Upgradeable(var42).balanceOf(Contract2) - var59);
            var57 += (IERC20Upgradeable(var42).balanceOf(Contract2) - var59);
          }
        }
      }







      if (var57 > var55 * 1e12 * 99 / 100) {
        var57 = var55 * 1e12 * 99 / 100;
      }

      if (var57 > 0) {
        if (var39.token0() == Contract2) {
            Contract9(Contract2).fn18(bytes.concat(abi.encodePacked(var39.token1(), hex"0001f4", var39.token0())), var57);
        } else {
            Contract9(Contract2).fn18(bytes.concat(abi.encodePacked(var39.token0(), hex"0001f4", var39.token1())), var57);
        }
      }

      Contract9(Contract2).fn15(Contract9(Contract2).balanceOf(Contract2));
    }

    function fn29() internal {
      uint256 var33 = Contract9(Contract2).balanceOf(Contract2);

      uint256 var61 = 0;
      if (var39.token0() == Contract2) {
        var61 = IERC20Upgradeable(var42).balanceOf(Contract2);
        Contract9(Contract2).fn18(bytes.concat(abi.encodePacked(var39.token0(), hex"0001f4", var39.token1())), var33);
        var61 = IERC20Upgradeable(var42).balanceOf(Contract2) - var61;
      } else {
        var61 = IERC20Upgradeable(var42).balanceOf(Contract2);
        Contract9(Contract2).fn18(bytes.concat(abi.encodePacked(var39.token1(), hex"0001f4", var39.token0())), var33);
        var61 = IERC20Upgradeable(var42).balanceOf(Contract2) - var61;
      }


      uint256 var62 = Contract9(Contract2).fn12();
      uint256 var63 = 0;
      for (var63 = 0; var63 < var41.length; var63++) {
        if (var62 < var41[var63]) {
          break;
        }
      }

      Contract7[] memory var11 = Contract9(Contract2).fn4();
      uint var64 = 0;
      uint var52 = (fn25() * 1e18 / 1e6) * Contract9(Contract2).totalSupply() / 1e6;
      for (uint256 var26 = 0; var26 < var11.length; var26++) {
        uint256 var58 = IERC20Upgradeable(var11[var26].var8).balanceOf(Contract2) * 1e18 / (10**IERC20MetadataUpgradeable(var11[var26].var8).decimals()) * var11[var26].var80.fn30() / 1e18;
        if (var58 * 1e18 / var52 < var11[var26].var83[var63]) {
          var64++;
        }
      }

      for (uint256 var26 = 0; var26 < var11.length; var26++) {
        uint256 var58 = IERC20Upgradeable(var11[var26].var8).balanceOf(Contract2) * 1e18 / (10**IERC20MetadataUpgradeable(var11[var26].var8).decimals()) * var11[var26].var80.fn30() / 1e18;
        if (var58 * 1e18 / var52 < var11[var26].var83[var63]) {
          if (var11[var26].var8 != var39.token0() || var11[var26].var8 != var39.token1()) {

            Contract9(Contract2).fn18(var11[var26].var81, var61/var64);
          }
        }
      }
    }
}
