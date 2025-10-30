// contracts/hardhat.config.js
/**
 * ⚙️ Hardhat Configuration for Senna Wallet
 * Configured for Somnia Testnet deployment
 */

require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-etherscan");
require("hardhat-deploy");
require("hardhat-gas-reporter");
require("solidity-coverage");
require("dotenv").config();

// Environment variables
const SOMNIA_RPC_URL = process.env.SOMNIA_RPC_URL || "https://dream-rpc.somnia.network/";
const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000"; // Default empty private key
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const COINMARKETCAP_API_KEY = process.env.COINMARKETCAP_API_KEY || "";

// Task definitions
task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();
  console.log("📝 Available accounts:");
  accounts.forEach((account, index) => {
    console.log(`   ${index}: ${account.address}`);
  });
});

task("balance", "Prints the balance of an account")
  .addParam("account", "The account's address")
  .setAction(async (taskArgs, hre) => {
    const balance = await hre.ethers.provider.getBalance(taskArgs.account);
    console.log(`💰 Balance of ${taskArgs.account}: ${hre.ethers.utils.formatEther(balance)} STT`);
  });

task("deploy:token", "Deploy only SennaToken")
  .setAction(async (taskArgs, hre) => {
    const { deploy } = hre.deployments;
    const [deployer] = await hre.ethers.getSigners();
    
    console.log("🚀 Deploying SennaToken...");
    const initialSupply = hre.ethers.utils.parseEther("1000000"); // 1M tokens
    
    const token = await deploy("SennaToken", {
      from: deployer.address,
      args: [initialSupply],
      log: true,
      waitConfirmations: 2,
    });
    
    console.log(`✅ SennaToken deployed to: ${token.address}`);
    return token;
  });

task("deploy:wallet", "Deploy only SennaWallet")
  .addOptionalParam("token", "SennaToken address")
  .setAction(async (taskArgs, hre) => {
    const { deploy } = hre.deployments;
    const [deployer] = await hre.ethers.getSigners();
    
    console.log("🚀 Deploying SennaWallet...");
    
    const owners = [deployer.address, "0x0000000000000000000000000000000000000001"];
    const requiredConfirmations = 1;
    const aiAgent = owners[1];
    
    const wallet = await deploy("SennaWallet", {
      from: deployer.address,
      args: [owners, requiredConfirmations, aiAgent],
      log: true,
      waitConfirmations: 2,
    });
    
    console.log(`✅ SennaWallet deployed to: ${wallet.address}`);
    return wallet;
  });

task("verify:contracts", "Verify all contracts on block explorer")
  .setAction(async (taskArgs, hre) => {
    const { run } = hre;
    
    try {
      // Get deployment information
      const tokenDeployment = await hre.deployments.get("SennaToken");
      const walletDeployment = await hre.deployments.get("SennaWallet");
      
      console.log("🔍 Verifying SennaToken...");
      await run("verify:verify", {
        address: tokenDeployment.address,
        constructorArguments: [hre.ethers.utils.parseEther("1000000")],
      });
      
      console.log("🔍 Verifying SennaWallet...");
      await run("verify:verify", {
        address: walletDeployment.address,
        constructorArguments: [
          [tokenDeployment.receipt.from, "0x0000000000000000000000000000000000000001"],
          1,
          "0x0000000000000000000000000000000000000001"
        ],
      });
      
      console.log("✅ All contracts verified successfully!");
    } catch (error) {
      console.log("⚠️ Verification failed:", error.message);
    }
  });

task("fund:wallet", "Fund SennaWallet with STT and SOMI tokens")
  .addParam("wallet", "SennaWallet address")
  .addParam("amount", "Amount of STT to send")
  .setAction(async (taskArgs, hre) => {
    const [deployer] = await hre.ethers.getSigners();
    const walletAddress = taskArgs.wallet;
    const amount = hre.ethers.utils.parseEther(taskArgs.amount);
    
    console.log(`💰 Sending ${taskArgs.amount} STT to ${walletAddress}...`);
    
    const tx = await deployer.sendTransaction({
      to: walletAddress,
      value: amount,
    });
    
    await tx.wait();
    console.log(`✅ Successfully funded wallet. Transaction: ${tx.hash}`);
    
    // Check new balance
    const balance = await hre.ethers.provider.getBalance(walletAddress);
    console.log(`📊 New wallet balance: ${hre.ethers.utils.formatEther(balance)} STT`);
  });

task("wallet:info", "Get SennaWallet information")
  .addParam("address", "SennaWallet contract address")
  .setAction(async (taskArgs, hre) => {
    const wallet = await hre.ethers.getContractAt("SennaWallet", taskArgs.address);
    
    console.log("📊 SennaWallet Information:");
    console.log(`   Address: ${taskArgs.address}`);
    console.log(`   Balance: ${hre.ethers.utils.formatEther(await hre.ethers.provider.getBalance(taskArgs.address))} STT`);
    console.log(`   Owners: ${await wallet.getOwners()}`);
    console.log(`   Required Confirmations: ${await wallet.requiredConfirmations()}`);
    console.log(`   AI Agent: ${await wallet.aiAgent()}`);
    
    const settings = await wallet.settings();
    console.log(`   Daily Limit: ${hre.ethers.utils.formatEther(settings.dailyLimit)} STT`);
    console.log(`   Transaction Limit: ${hre.ethers.utils.formatEther(settings.transactionLimit)} STT`);
    console.log(`   Recovery Agent: ${settings.recoveryAgent}`);
    console.log(`   Active: ${settings.isActive}`);
    
    const txCount = await wallet.getTransactionCount();
    console.log(`   Transaction Count: ${txCount}`);
  });

// Main configuration
module.exports = {
  // Default network
  defaultNetwork: "hardhat",
  
  // Network configurations
  networks: {
    // Local development network
    hardhat: {
      chainId: 1337,
      allowUnlimitedContractSize: false,
      mining: {
        auto: true,
        interval: 5000
      },
      accounts: {
        mnemonic: "test test test test test test test test test test test junk",
        count: 10,
        accountsBalance: "10000000000000000000000" // 10000 ETH
      }
    },
    
    // Localhost network
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 1337,
      timeout: 200000,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
    
    // Somnia Testnet
    somnia: {
      url: SOMNIA_RPC_URL,
      chainId: 50312,
      gas: 2100000,
      gasPrice: 8000000000, // 8 Gwei
      timeout: 60000,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      verify: {
        etherscan: {
          apiUrl: "https://api.shannon-explorer.somnia.network/api", // Assuming similar to Etherscan
          apiKey: ETHERSCAN_API_KEY
        }
      }
    },
    
    // Somnia Mainnet (for future use)
    somniaMainnet: {
      url: process.env.SOMNIA_MAINNET_RPC_URL || "",
      chainId: 50313, // Assuming mainnet chain ID
      gas: 2100000,
      gasPrice: 5000000000, // 5 Gwei
      timeout: 60000,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
    },
    
    // Additional testnets for testing
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      chainId: 11155111,
      gas: 2100000,
      gasPrice: 2000000000, // 2 Gwei
      timeout: 60000,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
    },
    
    mumbai: {
      url: process.env.MUMBAI_RPC_URL || "https://rpc-mumbai.maticvigil.com",
      chainId: 80001,
      gas: 2100000,
      gasPrice: 2000000000, // 2 Gwei
      timeout: 60000,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
    }
  },
  
  // Solidty compiler configuration
  solidity: {
    compilers: [
      {
        version: "0.8.19",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
            details: {
              yul: true,
              yulDetails: {
                stackAllocation: true,
              },
            },
          },
          viaIR: true,
          evmVersion: "paris",
        },
      },
      {
        version: "0.8.9",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      {
        version: "0.6.12",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    ],
    overrides: {
      "contracts/SennaWallet.sol": {
        version: "0.8.19",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      "contracts/SennaToken.sol": {
        version: "0.8.19",
        settings: {
          optimizer: {
            enabled: true,
            runs: 1000, // Higher runs for token (more function calls)
          },
        },
      },
    },
  },
  
  // Etherscan verification configuration
  etherscan: {
    apiKey: {
      somnia: ETHERSCAN_API_KEY,
      somniaMainnet: ETHERSCAN_API_KEY,
      sepolia: process.env.ETHERSCAN_API_KEY || "",
      polygonMumbai: process.env.POLYGONSCAN_API_KEY || "",
    },
    customChains: [
      {
        network: "somnia",
        chainId: 50312,
        urls: {
          apiURL: "https://api.shannon-explorer.somnia.network/api",
          browserURL: "https://shannon-explorer.somnia.network"
        }
      },
      {
        network: "somniaMainnet",
        chainId: 50313,
        urls: {
          apiURL: "https://api.somnia-explorer.network/api", // Assuming mainnet explorer
          browserURL: "https://somnia-explorer.network"
        }
      }
    ]
  },
  
  // Gas reporter configuration
  gasReporter: {
    enabled: process.env.REPORT_GAS ? true : false,
    currency: "USD",
    coinmarketcap: COINMARKETCAP_API_KEY,
    token: "ETH",
    gasPrice: 20,
    excludeContracts: [
      "contracts/mocks/",
      "contracts/test/",
    ],
  },
  
  // Coverage configuration
  coverage: {
    exclude: [
      "contracts/mocks/",
      "contracts/test/",
      "deploy/",
      "hardhat.config.js",
    ],
  },
  
  // Deployment configuration
  namedAccounts: {
    deployer: {
      default: 0, // First account from mnemonic
      somnia: 0,
      somniaMainnet: 0,
    },
    aiAgent: {
      default: 1, // Second account for AI agent
      somnia: "0x0000000000000000000000000000000000000001", // Placeholder
    },
    owner1: {
      default: 2,
    },
    owner2: {
      default: 3,
    },
  },
  
  // Path configuration
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
    deployments: "./deployments",
  },
  
  // Typechain configuration
  typechain: {
    outDir: "typechain",
    target: "ethers-v5",
  },
  
  // Mocha testing configuration
  mocha: {
    timeout: 40000,
    color: true,
    reporter: "spec",
  },
  
  // Contract sourcify verification
  sourcify: {
    enabled: true,
    apiUrl: "https://sourcify.dev/server",
    browserUrl: "https://repo.sourcify.dev",
  }
};

// Environment validation
if (!PRIVATE_KEY || PRIVATE_KEY === "0x0000000000000000000000000000000000000000000000000000000000000000") {
  console.warn("⚠️  WARNING: No private key found. Please set PRIVATE_KEY environment variable for live network deployments.");
}

if (!SOMNIA_RPC_URL) {
  console.warn("⚠️  WARNING: No Somnia RPC URL found. Please set SOMNIA_RPC_URL environment variable.");
}

// Export for use in other scripts
module.exports.getNetworkConfig = function(network) {
  return module.exports.networks[network] || module.exports.networks.hardhat;
};

module.exports.getDeployerAccount = function() {
  return PRIVATE_KEY;
};