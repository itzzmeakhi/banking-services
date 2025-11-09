import connectDB from "./config/db.js";
import app from "./app.js";

const PORT = process.env.PORT || 5001;
connectDB();

app.listen(PORT, () => {
  console.log(`🚀 Customer Service running on port ${PORT}`);
});
