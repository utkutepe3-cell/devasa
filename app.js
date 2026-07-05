const form = document.getElementById("payment-form");
const output = document.getElementById("output");
const formTitle = document.getElementById("form-title");
const runButton = document.getElementById("runButton");
const txTabs = Array.from(document.querySelectorAll(".tx-tab"));

const fields = {
  cardNumber: document.getElementById("cardNumber"),
  expiry: document.getElementById("expiry"),
  cvv: document.getElementById("cvv"),
  amount: document.getElementById("amount"),
  zipCode: document.getElementById("zipCode"),
  invoice: document.getElementById("invoice"),
  referenceNo: document.getElementById("referenceNo"),
};

const txMeta = {
  charge: { title: "Charge (Sale)", button: "Run Charge", host: "SALE" },
  auth: { title: "Auth Only", button: "Run Auth", host: "AUTH" },
  void: { title: "Void Transaction", button: "Run Void", host: "VOID" },
  return: { title: "Return (Refund)", button: "Run Return", host: "RETURN" },
};

let activeTx = "charge";
let lastReferenceNo = "";

const appendLog = (text) => {
  output.textContent += `\n${text}`;
  output.scrollTop = output.scrollHeight;
};

const clearLog = () => {
  output.textContent = "";
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

const setModeUI = (mode) => {
  activeTx = mode;
  txTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.tx === mode));
  formTitle.textContent = txMeta[mode].title;
  runButton.textContent = txMeta[mode].button;
};

const validate = () => {
  const errors = [];
  const amountValue = Number(fields.amount.value.replace(",", "."));
  const expiryRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;
  const referenceValue = fields.referenceNo.value.trim();

  if (!isLuhnValid(fields.cardNumber.value)) errors.push("Card number is invalid.");
  if (!expiryRegex.test(fields.expiry.value)) errors.push("Expiration must be MM/YY.");
  if (!/^\d{3,4}$/.test(fields.cvv.value)) errors.push("CVV must be 3 or 4 digits.");
  if (!Number.isFinite(amountValue) || amountValue <= 0) errors.push("Amount must be greater than 0.");
  if ((activeTx === "void" || activeTx === "return") && !referenceValue && !lastReferenceNo) {
    errors.push("Void/Return formlarinda Original Ref # gereklidir.");
  }

  return errors;
};

const simulate = async (message) => {
  appendLog(message);
  await new Promise((resolve) => setTimeout(resolve, 430));
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

txTabs.forEach((tab) => {
  tab.addEventListener("click", () => setModeUI(tab.dataset.tx));
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearLog();

  const errors = validate();
  if (errors.length > 0) {
    appendLog("Validation failed:");
    errors.forEach((error) => appendLog(`- ${error}`));
    return;
  }

  const maskedCard = `${cleanCardNumber(fields.cardNumber.value).slice(0, 6)}******${cleanCardNumber(fields.cardNumber.value).slice(-4)}`;
  const amount = Number(fields.amount.value.replace(",", ".")).toFixed(2);
  const referenceInput = fields.referenceNo.value.trim();
  const refToUse = referenceInput || lastReferenceNo || `TSYS-${Date.now()}`;
  const authCode = Math.floor(100000 + Math.random() * 900000);

  await simulate(`Host Command: ${txMeta[activeTx].host}`);
  await simulate(`Card: ${maskedCard}`);
  await simulate(`Amount: ${amount} USD`);
  await simulate(`Invoice: ${fields.invoice.value.trim() || "-"}`);
  await simulate(`Billing ZIP: ${fields.zipCode.value.trim() || "-"}`);

  if (activeTx === "void" || activeTx === "return") {
    await simulate(`Original Ref #: ${refToUse}`);
  }

  await simulate("Sending request to TSYS gateway...");
  await simulate("Receiving response...");

  if (activeTx === "return") {
    appendLog("Result: APPROVED (REFUND)");
  } else if (activeTx === "void") {
    appendLog("Result: APPROVED (VOID)");
  } else if (activeTx === "auth") {
    appendLog("Result: APPROVED (AUTH ONLY)");
  } else {
    appendLog("Result: APPROVED (SALE)");
  }

  appendLog(`Auth Code: ${authCode}`);
  appendLog(`Reference #: ${refToUse}`);
  lastReferenceNo = refToUse;
  fields.referenceNo.value = refToUse;
});
