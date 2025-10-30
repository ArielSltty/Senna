// contracts/SennaToken.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title SennaToken - SOMI Token Contract
 * @dev ERC-20 token for Somnia ecosystem
 */
contract SennaToken {
    string public constant name = "Somnia Token";
    string public constant symbol = "SOMI";
    uint8 public constant decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    address public owner;
    address public sennaWallet;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Mint(address indexed to, uint256 value);
    event Burn(address indexed from, uint256 value);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "SennaToken: caller is not owner");
        _;
    }
    
    modifier onlySennaWallet() {
        require(msg.sender == sennaWallet, "SennaToken: caller is not SennaWallet");
        _;
    }
    
    constructor(uint256 _initialSupply) {
        owner = msg.sender;
        sennaWallet = msg.sender;
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
        emit Transfer(address(0), msg.sender, _initialSupply);
    }
    
    function transfer(address _to, uint256 _value) external returns (bool) {
        require(balanceOf[msg.sender] >= _value, "SennaToken: insufficient balance");
        
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    function approve(address _spender, uint256 _value) external returns (bool) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint256 _value) external returns (bool) {
        require(balanceOf[_from] >= _value, "SennaToken: insufficient balance");
        require(allowance[_from][msg.sender] >= _value, "SennaToken: allowance exceeded");
        
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        
        emit Transfer(_from, _to, _value);
        return true;
    }
    
    function mint(address _to, uint256 _value) external onlySennaWallet {
        totalSupply += _value;
        balanceOf[_to] += _value;
        emit Mint(_to, _value);
        emit Transfer(address(0), _to, _value);
    }
    
    function burn(uint256 _value) external {
        require(balanceOf[msg.sender] >= _value, "SennaToken: insufficient balance");
        
        balanceOf[msg.sender] -= _value;
        totalSupply -= _value;
        emit Burn(msg.sender, _value);
        emit Transfer(msg.sender, address(0), _value);
    }
    
    function setSennaWallet(address _sennaWallet) external onlyOwner {
        sennaWallet = _sennaWallet;
    }
}