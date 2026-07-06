const txTabs = [...document.querySelectorAll(".tx-tab")];
const formTitle = document.getElementById("form-title");
const txTypeInput = document.getElementById("txType");
const runButton = document.getElementById("runButton");
const output = document.getElementById("output");
const form = document.getElementById("payment-form");
const cardNumberInput = document.getElementById("cardNumber");
const expiryInput = document.getElementById("expiry");
const cvvInput = document.getElementById("cvv");
const amountInput = document.getElementById("amount");
const referenceInput = document.getElementById("referenceNo");

const txConfig = {
  charge: { title: "Charge (Sale)", button: "Run Charge" },
  auth: { title: "Authorization", button: "Run Auth" },
  void: { title: "Void", button: "Run Void" },
  return: { title: "Return", button: "Run Return" },
};

function setFieldError(name, message) {
  const input = form.elements[name];
  const holder = form.querySelector(`[data-error-for="${name}"]`);
  if (!input || !holder) return;
  holder.textContent = message || "";
  input.classList.toggle("is-invalid", Boolean(message));
}

function clearErrors() {
  ["cardNumber", "expiry", "cvv", "amount", "zipCode", "invoice", "referenceNo"].forEach((name) =>
    setFieldError(name, ""),
  );
}

function setTab(nextType) {
  txTabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tx === nextType);
  });
  txTypeInput.value = nextType;
  formTitle.textContent = txConfig[nextType].title;
  runButton.textContent = txConfig[nextType].button;

  const isVoid = nextType === "void";
  const isReturn = nextType === "return";
  const needCard = !isVoid && !isReturn;
  const needAmount = !isVoid;
  const needRef = isVoid || isReturn;

  [cardNumberInput, expiryInput, cvvInput].forEach((el) => {
    el.required = needCard;
    el.disabled = !needCard;
  });
  amountInput.required = needAmount;
  amountInput.disabled = !needAmount;
  referenceInput.required = needRef;
}

txTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    clearErrors();
    setTab(tab.dataset.tx);
  });
});

cardNumberInput.addEventListener("input", () => {
  const digits = cardNumberInput.value.replace(/\D/g, "").slice(0, 19);
  cardNumberInput.value = digits.replace(/(\d{4})(?=\d)/g, "$1 ");
});

expiryInput.addEventListener("input", () => {
  expiryInput.value = expiryInput.value.replace(/\D/g, "").slice(0, 4);
});

cvvInput.addEventListener("input", () => {
  cvvInput.value = cvvInput.value.replace(/\D/g, "").slice(0, 4);
});

amountInput.addEventListener("input", () => {
  amountInput.value = amountInput.value.replace(/[^\d.]/g, "");
});

async function submitTransaction(event) {
  event.preventDefault();
  clearErrors();

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  runButton.disabled = true;
  runButton.textContent = "Processing...";
  output.textContent = "Sending request to TSYS Virtual Host...";

  try {
    const response = await fetch("./index.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok || result.ok === false) {
      if (result.errors && typeof result.errors === "object") {
        Object.entries(result.errors).forEach(([field, message]) => setFieldError(field, String(message)));
      }
      output.textContent = JSON.stringify(result, null, 2);
      return;
    }

    output.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    output.textContent = JSON.stringify(
      {
        ok: false,
        message: "İstek sırasında bağlantı hatası oluştu.",
        detail: error instanceof Error ? error.message : String(error),
      },
      null,
      2,
    );
  } finally {
    runButton.disabled = false;
    runButton.textContent = txConfig[txTypeInput.value].button;
  }
}

form.addEventListener("submit", submitTransaction);
setTab("charge");
