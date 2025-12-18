import crypto from "crypto";

export function signHmacSHA256(secret: string, message: string): string {
  return crypto.createHmac("sha256", secret).update(message).digest("hex");
}
