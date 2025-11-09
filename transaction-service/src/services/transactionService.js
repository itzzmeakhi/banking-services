import axios from "axios";
import db from "../db/connection.js";
import { publishEvent } from "./eventPublisher.js";

const ACCOUNT_SERVICE_URL = process.env.ACCOUNT_SERVICE_URL || "http://account-service:8081/accounts";
const CUSTOMER_SERVICE_URL = process.env.CUSTOMER_SERVICE_URL || "http://customer-service:5001/customers";
const DAILY_LIMIT = 200000; // ₹2,00,000

// 🧩 Helper: Get Account from Account Service
async function getAccount(account_id) {
  try {
    const response = await axios.get(`${ACCOUNT_SERVICE_URL}/${account_id}`);
    return response.data;
  } catch (err) {
    await publishEvent("transaction.error", { account_id, error: "ACCOUNT_NOT_FOUND" });
    throw new Error("ACCOUNT_NOT_FOUND");
  }
}

// 🧩 Helper: Get Customer from Customer Service
async function getCustomer(customer_id) {
  try {
    const response = await axios.get(`${CUSTOMER_SERVICE_URL}/${customer_id}`);
    console.log(customer_id);
    console.log(`${CUSTOMER_SERVICE_URL}/${customer_id}`);
    const customer = response.data;
    console.log(customer);
    if (!customer || customer.data.kyc_status !== "VERIFIED") {
      await publishEvent("transaction.error", { customer_id, error: "KYC_NOT_VERIFIED" });
      throw new Error("KYC_NOT_VERIFIED");
    }
    return customer;
  } catch (err) {
    await publishEvent("transaction.error", { customer_id, error: "CUSTOMER_NOT_FOUND" });
    throw new Error("CUSTOMER_NOT_FOUND");
  }
}

// 🧩 Helper: Validate Account Status
async function checkAccountStatus(account) {
  if (!account) throw new Error("ACCOUNT_NOT_FOUND");
  if (account.status === "FROZEN" || account.status === "CLOSED") {
    await publishEvent("transaction.error", { account_id: account.account_id, error: "ACCOUNT_INACTIVE" });
    throw new Error("ACCOUNT_INACTIVE");
  }
}

// 🧩 Helper: Check daily withdrawal/transfer limit
async function checkDailyLimit(account_id, amount) {
  const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
  const result = await db.query(
    `SELECT COALESCE(SUM(amount),0) AS total FROM transactions
     WHERE account_id = $1 AND txn_type IN ('WITHDRAWAL','TRANSFER_OUT') AND created_at::date = $2`,
    [account_id, today]
  );
  if (parseFloat(result.rows[0].total) + amount > DAILY_LIMIT) {
    await publishEvent("transaction.error", { account_id, error: "DAILY_LIMIT_EXCEEDED" });
    throw new Error("DAILY_LIMIT_EXCEEDED");
  }
}

// 💰 Process Deposit
async function processDeposit({ account_id, amount, counterparty }) {
  const account = await getAccount(account_id);
  await checkAccountStatus(account);

  // Fetch customer (via account.customer_id)
  const customer = await getCustomer(account.customer_id);

  const newBalance = parseFloat(account.balance) + amount;

  // Update balance in Account Service
  await axios.patch(`${ACCOUNT_SERVICE_URL}/${account_id}`, { balance: newBalance });

  // Record transaction in local DB
  const txn = await db.query(
    `INSERT INTO transactions (account_id, amount, txn_type, counterparty)
     VALUES ($1, $2, 'DEPOSIT', $3)
     RETURNING *`,
    [account_id, amount, counterparty]
  );

  try {
    await publishEvent("transaction.deposit", {
      ...txn.rows[0],
      customer_id: customer.customer_id,
      kyc_status: customer.kyc_status,
      balance: newBalance
    });
  } catch (err) {
    console.error("Failed to publish deposit event:", err);
  }

  return txn.rows[0];
}

// 💸 Process Withdraw
async function processWithdraw({ account_id, amount, counterparty }) {
  const account = await getAccount(account_id);
  await checkAccountStatus(account);
  const customer = await getCustomer(account.customer_id);

  const currentBalance = parseFloat(account.balance);
  if (currentBalance < amount) {
    await publishEvent("transaction.error", { account_id, error: "INSUFFICIENT_FUNDS" });
    throw new Error("INSUFFICIENT_FUNDS");
  }

  await checkDailyLimit(account_id, amount);
  const newBalance = currentBalance - amount;

  // Update balance in Account Service
  await axios.patch(`${ACCOUNT_SERVICE_URL}/${account_id}`, { balance: newBalance });

  // Record transaction
  const txn = await db.query(
    `INSERT INTO transactions (account_id, amount, txn_type, counterparty)
     VALUES ($1, $2, 'WITHDRAW', $3)
     RETURNING *`,
    [account_id, amount, counterparty]
  );

  try {
    await publishEvent("transaction.withdraw", {
      ...txn.rows[0],
      customer_id: customer.customer_id,
      balance: newBalance
    });
  } catch (err) {
    console.error("Failed to publish withdraw event:", err);
  }

  return txn.rows[0];
}

// 📄 Get account statement
async function getStatement(account_id, limit = 50, offset = 0) {
  const account = await getAccount(account_id);
  await checkAccountStatus(account);

  const result = await db.query(
    `SELECT * FROM transactions
     WHERE account_id = $1
     ORDER BY created_at DESC
     LIMIT $2 OFFSET $3`,
    [account_id, limit, offset]
  );

  return result.rows;
}

// 📜 Get all transactions for account
async function getTransactionHistory(account_id) {
  const result = await db.query(
    `SELECT txn_id, amount, txn_type, counterparty, created_at
     FROM transactions
     WHERE account_id = $1
     ORDER BY created_at DESC`,
    [account_id]
  );
  return result.rows;
}

export default {
  processDeposit,
  processWithdraw,
  getStatement,
  getTransactionHistory,
};
