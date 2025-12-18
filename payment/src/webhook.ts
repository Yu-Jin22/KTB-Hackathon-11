import axios from "axios";
import { signHmacSHA256 } from "./utils/hmac.js";
import type { Payment } from "./store.js";
import { v4 as uuidv4 } from "uuid";

export type WebhookEventType = "PAYMENT_APPROVED" | "PAYMENT_FAILED" | "PAYMENT_CANCELED";

export async function sendWebhook(opts: {
  springWebhookUrl: string;
  secret: string;
  type: WebhookEventType;
  payment: Payment;
}) {
  const eventId = uuidv4();
  const timestamp = new Date().toISOString();

  const body = {
    eventId,
    type: opts.type,
    occurredAt: timestamp,
    data: {
      paymentId: opts.payment.paymentId,
      orderId: opts.payment.orderId,
      amountWon: opts.payment.amountWon,
      status: opts.payment.status
    }
  };

  const raw = `${timestamp}.${JSON.stringify(body)}`;
  const signature = signHmacSHA256(opts.secret, raw);

  await axios.post(opts.springWebhookUrl, body, {
    headers: {
      "content-type": "application/json",
      "x-webhook-timestamp": timestamp,
      "x-webhook-signature": signature,
    },
    timeout: 3000
  });
}
