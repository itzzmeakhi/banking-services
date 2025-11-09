import fs from "fs";
import csv from "csv-parser";
import mongoose from "mongoose";
import dotenv from "dotenv";
import Customer from "./src/models/Customer.js";
import connectDB from "./src/config/db.js";

dotenv.config();

const results = [];

const importData = async () => {
  await connectDB();

  fs.createReadStream("./data/customers.csv")
    .pipe(csv())
    .on("data", (data) => results.push(data))
    .on("end", async () => {
      try {
        await Customer.deleteMany({});
        await Customer.insertMany(results);
        console.log(`Inserted ${results.length} customers`);
        mongoose.connection.close();
      } catch (err) {
        console.error("Error inserting data:", err.message);
        mongoose.connection.close();
      }
    });
};

importData();
