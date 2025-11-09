import mongoose from "mongoose";

const customerSchema = new mongoose.Schema(
  {
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    phone: { type: String, required: true },
    kyc_status: { type: String, enum: ["PENDING", "VERIFIED", "REJECTED"], default: "PENDING" },
    created_at: { type: Date, default: Date.now }
  },
  { timestamps: true }
);

const Customer = mongoose.model("Customer", customerSchema);
export default Customer;
