export type PaymentStatus = "PENDING" | "APPROVED" | "FAILED" | "CANCELED";

export type Payment = {
  paymentId: string;
  orderId: string;
  amountWon: number;
  status: PaymentStatus;
  createdAt: string;
  updatedAt: string;
}

export const payments = new Map<string, Payment>();
