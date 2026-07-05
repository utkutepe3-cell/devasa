const form = document.getElementById("payment-form");
const output = document.getElementById("output");

const fields = {
  merchantId: document.getElementById("merchantId"),
  terminalId: document.getElementById("terminalId"),
  cardNumber: document.getElementById("cardNumber"),
  expiry: document.getElementById("expiry"),
  cvv: document.getElementById("cvv"),
  amount: document.getElementById("amount"),
  orderId: document.getElementById("orderId"),
};

const appendLog = (text) => {
  const currentTime = new Date().toLocaleTimeString("tr-TR");
  output.textContent += `\n[${currentTime}] ${text}`;
  output.scrollTop = output.scrollHeight;
};

const cleanCardNumber = (value) => value.replace(/\D/g, "").slice(0, 16);
const formatCardNumber = (value) => cleanCardNumber(value).replace(/(.{4})/g, "$1 ").trim();

const formatExpiry = (value) => {
  const digits = value.replace(/\D/g, "").slice(0, 4);
  if (digits.length < 3) return digits;
  return `${digits.slice(0, 2)}/${digits.slice(2)}`;
};

const isLuhnValid = (cardNumber) => {
  const digits = cleanCardNumber(cardNumber).split("").reverse().map(Number);
  if (digits.length !== 16) return false;
  const total = digits.reduce((sum, digit, index) => {
    if (index % 2 === 1) {
      const doubled = digit * 2;
      return sum + (doubled > 9 ? doubled - 9 : doubled);
    }
    return sum + digit;
  }, 0);
  return total % 10 === 0;
};

const validate = () => {
  const errors = [];
  const amountValue = Number(fields.amount.value.replace(",", "."));
  const expiryRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;

  if (!fields.merchantId.value.trim()) errors.push("Merchant ID zorunludur.");
  if (!fields.terminalId.value.trim()) errors.push("Terminal ID zorunludur.");
  if (!isLuhnValid(fields.cardNumber.value)) errors.push("Kart numarası geçersiz.");
  if (!expiryRegex.test(fields.expiry.value)) errors.push("Son kullanma formatı AA/YY olmalıdır.");
  if (!/^\d{3,4}$/.test(fields.cvv.value)) errors.push("CVV 3 veya 4 haneli olmalıdır.");
  if (!Number.isFinite(amountValue) || amountValue <= 0) errors.push("Tutar 0'dan büyük olmalıdır.");
  if (!fields.orderId.value.trim()) errors.push("Sipariş numarası zorunludur.");

  return errors;
};

fields.cardNumber.addEventListener("input", () => {
  fields.cardNumber.value = formatCardNumber(fields.cardNumber.value);
});

fields.expiry.addEventListener("input", () => {
  fields.expiry.value = formatExpiry(fields.expiry.value);
});

fields.cvv.addEventListener("input", () => {
  fields.cvv.value = fields.cvv.value.replace(/\D/g, "").slice(0, 4);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  output.textContent = "Hazır...";

  const errors = validate();
  if (errors.length > 0) {
    appendLog("Doğrulama başarısız:");
    errors.forEach((error) => appendLog(`- ${error}`));
    return;
  }

  const maskedCard = `${cleanCardNumber(fields.cardNumber.value).slice(0, 6)}******${cleanCardNumber(fields.cardNumber.value).slice(-4)}`;

  appendLog("TSYS terminal bağlantısı hazırlanıyor...");
  appendLog(`Merchant: ${fields.merchantId.value} | Terminal: ${fields.terminalId.value}`);
  appendLog(`OrderId: ${fields.orderId.value} | Amount: ${fields.amount.value} TRY`);
  appendLog(`Card: ${maskedCard}`);

  await new Promise((resolve) => setTimeout(resolve, 850));
  appendLog("AUTH request gönderildi.");
  await new Promise((resolve) => setTimeout(resolve, 850));
  appendLog("Bankadan yanıt alındı.");
  await new Promise((resolve) => setTimeout(resolve, 500));

  const authCode = Math.floor(100000 + Math.random() * 900000);
  const referenceNo = `TSYS-${Date.now()}`;
  appendLog("SONUÇ: APPROVED");
  appendLog(`Auth Code: ${authCode}`);
  appendLog(`Reference: ${referenceNo}`);
});
