import express from "express";
import {
  createCustomer,
  getCustomers,
  getCustomerById,
  updateCustomer,
  deleteCustomer,
  updateKYCStatus
} from "../controllers/customerController.js";

const router = express.Router();

router.route("/").post(createCustomer).get(getCustomers);
router.route("/:id")
  .get(getCustomerById)
  .put(updateCustomer)
  .delete(deleteCustomer);
router.route("/:id/kyc").patch(updateKYCStatus);

export default router;
