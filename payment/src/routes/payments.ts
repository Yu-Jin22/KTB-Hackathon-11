import { Router } from "express";
import { z } from "zod";
import { v4 as uuidv4 } from "uuid";
import { payments } from "../store.js";
import type { Payment } from "../store.js";
import { sendWebhook } from "../webhook.js";
import type { WebhookEventType } from "../webhook.js";

export function paymentsRouter(config: {
  springWebhookUrl: string;
  webhookSecret: string;
  sendWebhook: boolean;
}) {
  const router = Router();

  const CreatePaymentReq = z.object({
    orderId: z.string().min(1),
    amountWon: z.number().int().positive(),
  });

  router.post("/", async (req, res) => {
    const parsed = CreatePaymentReq.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ message: "invalid request", issues: parsed.error.issues });
    }

    const now = new Date().toISOString();
    const payment: Payment = {
      paymentId: uuidv4(),
      orderId: parsed.data.orderId,
      amountWon: parsed.data.amountWon,
      status: "PENDING",
      createdAt: now,
      updatedAt: now,
    };

    payments.set(payment.paymentId, payment);
    return res.status(201).json(payment);
  });

  router.get("/:paymentId", (req, res) => {
    const p = payments.get(req.params.paymentId);
    if (!p) return res.status(404).json({ message: "not found" });
    return res.json(p);
  });

  async function updateStatus(paymentId: string, status: Payment["status"]) {
    const p = payments.get(paymentId);
    if (!p) return { ok: false as const, code: 404 as const };

    if (p.status !== "PENDING") {
      return { ok: false as const, code: 409 as const, current: p.status };
    }

    const updated: Payment = { ...p, status, updatedAt: new Date().toISOString() };
    payments.set(paymentId, updated);

    if (config.sendWebhook) {
      const type: WebhookEventType =
        status === "APPROVED" ? "PAYMENT_APPROVED" :
          status === "FAILED" ? "PAYMENT_FAILED" : "PAYMENT_CANCELED";

      await sendWebhook({
        springWebhookUrl: config.springWebhookUrl,
        secret: config.webhookSecret,
        type,
        payment: updated
      });
    }

    return { ok: true as const, payment: updated };
  }

  router.post("/:paymentId/approve", async (req, res) => {
    try {
      const result = await updateStatus(req.params.paymentId, "APPROVED");
      if (!result.ok) return res.status(result.code).json(result);
      return res.json(result.payment);
    } catch (e: any) {
      return res.status(502).json({ message: "webhook failed", detail: e?.message ?? "unknown" });
    }
  });

  router.post("/:paymentId/fail", async (req, res) => {
    try {
      const result = await updateStatus(req.params.paymentId, "FAILED");
      if (!result.ok) return res.status(result.code).json(result);
      return res.json(result.payment);
    } catch (e: any) {
      return res.status(502).json({ message: "webhook failed", detail: e?.messasge ?? "unknown" });
    }
  });

  router.post("/:paymentId/cancel", async (req, res) => {
    try {
      const result = await updateStatus(req.params.paymentId, "CANCELED");
      if (!result.ok) return res.status(result.code).json(result);
      return res.json(result.payment);
    } catch (e: any) {
      return res.status(502).json({ message: "webhook failed", detail: e?.message ?? "unknown" });
    }
  });

  return router;
}
