import express from "express";
import dotenv from "dotenv";
import { paymentsRouter } from "./routes/payments.js";

dotenv.config();

const PORT = Number(process.env.PORT ?? 4000);
const SPRING_WEBHOOK_URL = process.env.SPRING_WEBHOOK_URL ?? "http://localhost:8080";
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET ?? "";
const SEND_WEBHOOK = (process.env.SEND_WEBHOOK ?? "true") === "true";

if (!SPRING_WEBHOOK_URL) throw new Error("SPRING_WEBHOOK_URL is required");
if (!WEBHOOK_SECRET) throw new Error("WEBHOOK_SECRET is required");

const app = express();
app.use(express.json({ limit: "1mb" }));

app.get("/health", (_req, res) => res.json({ ok: true }));

app.use("/payments", paymentsRouter({
  springWebhookUrl: SPRING_WEBHOOK_URL,
  webhookSecret: WEBHOOK_SECRET,
  sendWebhook: SEND_WEBHOOK,
}));

app.listen(PORT, () => {
  console.log(`[mock-payments] listening on :${PORT}`);
})
