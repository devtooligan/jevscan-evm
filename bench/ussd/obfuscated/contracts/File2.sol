
pragma solidity ^0.8.6;
pragma abicoder v2;

import "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";

import "./interfaces/File4.sol";
import "./interfaces/File6.sol";

import "@uniswap/swap-router-contracts/contracts/interfaces/IV3SwapRouter.sol";




contract Contract2 is
    Contract9,
    ERC20Upgradeable,
    AccessControlUpgradeable
{
    using SafeERC20Upgradeable for IERC20Upgradeable;
    using AddressUpgradeable for address payable;

    Contract8 public var4;


    bytes32 public constant var5 = keccak256("STABLECONTROL");

    function initialize(
        string memory name,
        string memory symbol
    ) public initializer {
        __Context_init_unchained();
        __AccessControl_init_unchained();
        __ERC20_init_unchained(name, symbol);

        _setupRole(DEFAULT_ADMIN_ROLE, _msgSender());


        _mint(msg.sender, 10_000 * 1e6);
    }

    function decimals() public view virtual override returns (uint8) {
        return 6;
    }




    modifier fn3() {
        require(hasRole(var5, msg.sender), "control only");
        _;
    }





    event Contract3(
        address indexed var6,
        address indexed var7,
        address var8,
        uint256 var9,
        uint256 var10
    );





    Contract7[] private var11;

    function fn4()
        public
        view
        override
        returns (Contract7[] memory)
    {
        return var11;
    }

    function fn5(
        address var12,
        address var13,
        bool _mint,
        bool var14,
        uint256[] calldata var15,
        bytes memory var16,
        bytes memory var17,
        uint256 var18
    ) public fn3 {
        Contract7 memory var19 = Contract7({
            var8: var12,
            var78: _mint,
            var79: var14,
            var80: Contract5(var13),
            var81: var16,
            var82: var17,
            var83: var15
        });
        if (var18 < var11.length) {
            var11[var18] = var19;
        } else {
            var11.push(var19);
        }
    }

    function fn6(
        uint256 var20,
        uint256 var21
    ) public fn3 {

        Contract7 memory var22 = var11[var20];
        var11[var20] = var11[var21];
        var11[var21] = var22;
    }

    function fn7(uint256 var23) public fn3 {
        var11[var23] = var11[var11.length - 1];
        var11.pop();
    }

    function fn8(
        address var24
    ) public view returns (uint256 var18) {
        for (var18 = 0; var18 < var11.length; var18++) {
            if (var11[var18].var8 == var24) {
                return var18;
            }
        }
    }

    function fn9(
        address var24
    ) public view returns (bool var25) {
        for (uint256 var26 = 0; var26 < var11.length; var26++) {
            if (var11[var26].var8 == var24 && var11[var26].var78) {
                return true;
            }
        }
        return false;
    }






    function fn10(
        address var8,
        uint256 var27,
        address var7
    ) public returns (uint256 var28) {
        require(fn9(var8), "unsupported token");

        IERC20Upgradeable(var8).safeTransferFrom(
            msg.sender,
            address(this),
            var27
        );
        var28 = fn11(var8, var27);
        _mint(var7, var28);

        emit Contract3(msg.sender, var7, var8, var27, var28);
    }


    function fn11(address var24, uint256 var29) public view returns (uint256 var28) {
        uint256 var30 = var11[fn8(var24)].var80.fn30();
        return (((var30 * var29) / 1e18) * (10 ** decimals())) / (10 ** IERC20MetadataUpgradeable(var24).decimals());
    }





    function fn12() public view override returns (uint256) {
        uint256 var31 = 0;
        for (uint256 var26 = 0; var26 < var11.length; var26++) {
            var31 +=
                (((IERC20Upgradeable(var11[var26].var8).balanceOf(
                    address(this)
                ) * 1e18) /
                    (10 **
                        IERC20MetadataUpgradeable(var11[var26].var8)
                            .decimals())) *
                    var11[var26].var80.fn30()) /
                1e18;
        }

        return (var31 * 1e6) / totalSupply();
    }





    function fn13(address var32) public fn3 {
        var4 = Contract8(var32);
    }

    function fn14(uint256 var33) public override {
        _mint(address(this), var33);
    }

    function fn15(uint256 var33) public override {
        _burn(address(this), var33);
    }

    modifier fn16() {
        require(msg.sender == address(var4), "bal");
        _;
    }





    IV3SwapRouter public var34;

    function fn17(address var35) public fn3 {
        var34 = IV3SwapRouter(var35);
    }

    function fn18(
        bytes memory var36,
        uint256 var37
    ) public override fn16 {
        IV3SwapRouter.ExactInputParams memory var38 = IV3SwapRouter
            .ExactInputParams({
                path: var36,
                recipient: address(this),

                amountIn: var37,
                amountOutMinimum: 0
            });
        var34.exactInput(var38);
    }

    function fn19(address var24) public {
        IERC20Upgradeable(var24).approve(
            address(var34),
            0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        );
    }
}
