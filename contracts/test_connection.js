// contracts/scripts/test-connection.js - CommonJS
const { ethers } = require("hardhat");

async function main() {
  console.log("🔗 Testing connection to Somnia...");
  
  const [deployer] = await ethers.getSigners();
  console.log(`Account: ${deployer.address}`);
  
  const balance = await deployer.getBalance();
  console.log(`Balance: ${ethers.utils.formatEther(balance)} STT`);
  
  const network = await ethers.provider.getNetwork();
  console.log(`Network: ${network.name} (Chain ID: ${network.chainId})`);
  
  console.log("✅ Connection test completed!");
}

main().catch((error) => {
  console.error("❌ Connection failed:", error);
  process.exit(1);
});