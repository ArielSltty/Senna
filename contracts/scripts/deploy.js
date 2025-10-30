// contracts/scripts/deploy.js
const { ethers } = require("hardhat");

async function main() {
  console.log("🔐 Checking environment...");
  
  const [deployer] = await ethers.getSigners();
  console.log(`Deployer: ${deployer.address}`);
  
  const balance = await deployer.getBalance();
  console.log(`Balance: ${ethers.utils.formatEther(balance)} STT`);
  
  if (balance.eq(0)) {
    throw new Error("Insufficient balance for deployment. Get STT from faucet.");
  }
  
  console.log("🚀 Starting deployment...");
  
  // Deploy SennaToken
  console.log("📦 Deploying SennaToken...");
  const SennaToken = await ethers.getContractFactory("SennaToken");
  const sennaToken = await SennaToken.deploy(ethers.utils.parseEther("1000000"));
  await sennaToken.deployed();
  console.log(`✅ SennaToken: ${sennaToken.address}`);
  
  // Deploy SennaWallet
  console.log("📦 Deploying SennaWallet...");
  const SennaWallet = await ethers.getContractFactory("SennaWallet");
  const owners = [deployer.address, "0x0000000000000000000000000000000000000001"];
  const sennaWallet = await SennaWallet.deploy(owners, 1, owners[1]);
  await sennaWallet.deployed();
  console.log(`✅ SennaWallet: ${sennaWallet.address}`);
  
  // Configure integration
  console.log("🔗 Configuring integration...");
  const tx = await sennaToken.setSennaWallet(sennaWallet.address);
  await tx.wait();
  console.log("✅ Integration complete");
  
  console.log("\n🎉 DEPLOYMENT SUCCESSFUL!");
  console.log("==========================================");
  console.log(`SOMI_TOKEN_ADDRESS=${sennaToken.address}`);
  console.log(`SENNA_WALLET_ADDRESS=${sennaWallet.address}`);
  console.log("==========================================");
  
  console.log("\n📋 Next steps:");
  console.log("1. Add above addresses to backend/.env");
  console.log("2. Start backend: cd backend && source venv/bin/activate && uvicorn main:app --reload");
  console.log("3. Start frontend: cd frontend && python -m http.server 3000");
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error.message);
  process.exit(1);
});