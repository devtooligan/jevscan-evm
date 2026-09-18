

pragma solidity >=0.7.6 <0.9.0;

import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol';



interface Contract6 {



  function fn31() external view returns (IUniswapV3Factory);




  function fn32() external view returns (uint8);



  function fn33() external view returns (uint24[] memory);




  function fn34(address var65, address var66) external view returns (bool);




  function fn35(address var65, address var66) external view returns (address[] memory);










  function fn36(
    uint128 var67,
    address var68,
    address var69,
    uint32 var70
  ) external view returns (uint256 var71, address[] memory var72);











  function fn37(
    uint128 var67,
    address var68,
    address var69,
    uint24[] calldata var73,
    uint32 var70
  ) external view returns (uint256 var71, address[] memory var72);









  function fn38(
    uint128 var67,
    address var68,
    address var69,
    address[] calldata var74,
    uint32 var70
  ) external view returns (uint256 var71);







  function fn39(
    address var65,
    address var66,
    uint32 var70
  ) external returns (address[] memory var75);








  function fn40(
    address var65,
    address var66,
    uint24[] calldata var73,
    uint32 var70
  ) external returns (address[] memory var75);




  function fn41(address[] calldata var74, uint32 var70) external;







  function fn42(
    address var65,
    address var66,
    uint16 var76
  ) external returns (address[] memory var75);








  function fn43(
    address var65,
    address var66,
    uint24[] calldata var73,
    uint16 var76
  ) external returns (address[] memory var75);




  function fn44(address[] calldata var74, uint16 var76) external;




  function fn45(uint24 var77) external;
}
