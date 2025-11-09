import express from "express";
import cors from "cors";
import morgan from "morgan";
import dotenv from "dotenv";
import YAML from "yamljs";
import swaggerUi from "swagger-ui-express";
import { errorHandler } from "./middleware/errorHandler.js";
import customerRoutes from "./routes/customerRoutes.js";

dotenv.config();
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

const swaggerDocument = YAML.load("./swagger.yaml");
app.use("/docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));


app.use("/customers", customerRoutes);


app.get("/health", (req, res) => {
  res.status(200).json({ status: "UP", service: process.env.SERVICE_NAME });
});

app.use(errorHandler);

export default app;
