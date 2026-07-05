#include <algorithm>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <sstream>
#include <string>

struct Transaction {
  std::string type;
  std::string reference;
  std::string maskedCard;
  std::string authCode;
  double amount{};
  std::string status;
  std::string parentReference;
};

static std::string onlyDigits(const std::string &value) {
  std::string result;
  for (char c : value) {
    if (std::isdigit(static_cast<unsigned char>(c))) {
      result.push_back(c);
    }
  }
  return result;
}

static bool isLuhnValid(const std::string &card) {
  const std::string digits = onlyDigits(card);
  if (digits.size() < 13 || digits.size() > 19) {
    return false;
  }

  int sum = 0;
  bool alternate = false;
  for (auto it = digits.rbegin(); it != digits.rend(); ++it) {
    int n = *it - '0';
    if (alternate) {
      n *= 2;
      if (n > 9) {
        n -= 9;
      }
    }
    sum += n;
    alternate = !alternate;
  }
  return sum % 10 == 0;
}

static std::string maskCard(const std::string &card) {
  const std::string digits = onlyDigits(card);
  if (digits.size() < 10) {
    return "INVALID";
  }
  return digits.substr(0, 6) + "******" + digits.substr(digits.size() - 4);
}

static bool isValidExpiry(const std::string &expiry) {
  std::string digits = onlyDigits(expiry);
  if (digits.size() != 4) {
    return false;
  }

  int mm = std::stoi(digits.substr(0, 2));
  int yy = std::stoi(digits.substr(2, 2));
  if (mm < 1 || mm > 12) {
    return false;
  }

  std::time_t now = std::time(nullptr);
  std::tm *lt = std::localtime(&now);
  int currentYY = lt->tm_year % 100;
  int currentMM = lt->tm_mon + 1;

  if (yy < currentYY) {
    return false;
  }
  if (yy == currentYY && mm < currentMM) {
    return false;
  }
  return true;
}

static std::string generateReference() {
  static std::mt19937 rng(std::random_device{}());
  static std::uniform_int_distribution<int> dist(100000, 999999);
  return "TSYS-" + std::to_string(std::time(nullptr)) + "-" + std::to_string(dist(rng));
}

static std::string generateAuthCode() {
  static std::mt19937 rng(std::random_device{}());
  static std::uniform_int_distribution<int> dist(100000, 999999);
  return std::to_string(dist(rng));
}

static void printHeader() {
  std::cout << "\n===========================================\n";
  std::cout << "       TSYS Virtual Terminal (C++)\n";
  std::cout << "===========================================\n";
  std::cout << "1) Charge (Sale)\n";
  std::cout << "2) Auth\n";
  std::cout << "3) Void\n";
  std::cout << "4) Return (Iade)\n";
  std::cout << "5) List Transactions\n";
  std::cout << "0) Exit\n";
  std::cout << "-------------------------------------------\n";
}

static bool readLine(const std::string &prompt, std::string &value) {
  std::cout << prompt;
  std::getline(std::cin, value);
  return !std::cin.fail();
}

static bool readAmount(double &amount) {
  std::string raw;
  if (!readLine("Amount (USD): ", raw)) {
    return false;
  }
  std::replace(raw.begin(), raw.end(), ',', '.');
  std::stringstream ss(raw);
  ss >> amount;
  return !ss.fail() && ss.eof() && amount > 0.0;
}

static bool readCardInputs(std::string &card, std::string &expiry, std::string &cvv, double &amount) {
  if (!readLine("Card Number: ", card)) {
    return false;
  }
  if (!isLuhnValid(card)) {
    std::cout << "Hata: Gecersiz kart numarasi.\n";
    return false;
  }

  if (!readLine("Expiry (MMYY): ", expiry)) {
    return false;
  }
  if (!isValidExpiry(expiry)) {
    std::cout << "Hata: Gecersiz son kullanma tarihi.\n";
    return false;
  }

  if (!readLine("CVV: ", cvv)) {
    return false;
  }
  const std::string cvvDigits = onlyDigits(cvv);
  if (cvvDigits.size() < 3 || cvvDigits.size() > 4) {
    std::cout << "Hata: CVV 3 veya 4 hane olmali.\n";
    return false;
  }

  if (!readAmount(amount)) {
    std::cout << "Hata: Gecersiz tutar.\n";
    return false;
  }
  return true;
}

static void printTransaction(const Transaction &tx) {
  std::cout << "Type: " << tx.type << "\n";
  std::cout << "Status: " << tx.status << "\n";
  std::cout << "Reference: " << tx.reference << "\n";
  if (!tx.parentReference.empty()) {
    std::cout << "Parent Ref: " << tx.parentReference << "\n";
  }
  std::cout << "Auth Code: " << tx.authCode << "\n";
  std::cout << "Card: " << tx.maskedCard << "\n";
  std::cout << "Amount: " << std::fixed << std::setprecision(2) << tx.amount << " USD\n";
}

int main() {
  std::map<std::string, Transaction> transactions;
  std::string lastPrimaryReference;

  while (true) {
    printHeader();
    std::cout << "Select action: ";
    int action = -1;
    if (!(std::cin >> action)) {
      break;
    }
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    if (action == 0) {
      std::cout << "Cikis yapiliyor.\n";
      return 0;
    }

    if (action == 1 || action == 2) {
      std::string card, expiry, cvv;
      double amount = 0;
      if (!readCardInputs(card, expiry, cvv, amount)) {
        continue;
      }

      Transaction tx;
      tx.type = (action == 1) ? "CHARGE" : "AUTH";
      tx.status = "APPROVED";
      tx.reference = generateReference();
      tx.authCode = generateAuthCode();
      tx.maskedCard = maskCard(card);
      tx.amount = amount;
      transactions[tx.reference] = tx;
      lastPrimaryReference = tx.reference;

      std::cout << "\n--- Transaction Result ---\n";
      printTransaction(tx);
      std::cout << "--------------------------\n";
      continue;
    }

    if (action == 3 || action == 4) {
      std::string ref;
      if (!readLine("Original Reference # (or LAST): ", ref)) {
        continue;
      }
      if (ref == "LAST") {
        if (lastPrimaryReference.empty()) {
          std::cout << "Hata: LAST kullanimi icin once Charge/Auth islemi yapin.\n";
          continue;
        }
        ref = lastPrimaryReference;
      }

      auto original = transactions.find(ref);
      if (original == transactions.end()) {
        std::cout << "Hata: Referans bulunamadi.\n";
        continue;
      }

      if (action == 3) {
        if (original->second.status.find("VOIDED") != std::string::npos) {
          std::cout << "Hata: Islem daha once VOID edilmis.\n";
          continue;
        }

        Transaction tx;
        tx.type = "VOID";
        tx.status = "APPROVED (VOIDED)";
        tx.reference = generateReference();
        tx.parentReference = ref;
        tx.authCode = generateAuthCode();
        tx.maskedCard = original->second.maskedCard;
        tx.amount = original->second.amount;
        transactions[tx.reference] = tx;
        original->second.status = "APPROVED (VOIDED)";

        std::cout << "\n--- Transaction Result ---\n";
        printTransaction(tx);
        std::cout << "--------------------------\n";
        continue;
      }

      double returnAmount = 0;
      if (!readAmount(returnAmount)) {
        std::cout << "Hata: Gecersiz iade tutari.\n";
        continue;
      }
      if (returnAmount > original->second.amount) {
        std::cout << "Hata: Iade tutari orijinal tutardan buyuk olamaz.\n";
        continue;
      }

      Transaction tx;
      tx.type = "RETURN";
      tx.status = "APPROVED (REFUND)";
      tx.reference = generateReference();
      tx.parentReference = ref;
      tx.authCode = generateAuthCode();
      tx.maskedCard = original->second.maskedCard;
      tx.amount = returnAmount;
      transactions[tx.reference] = tx;

      std::cout << "\n--- Transaction Result ---\n";
      printTransaction(tx);
      std::cout << "--------------------------\n";
      continue;
    }

    if (action == 5) {
      if (transactions.empty()) {
        std::cout << "Heniz kayitli islem yok.\n";
        continue;
      }
      std::cout << "\n=== Transactions ===\n";
      for (const auto &entry : transactions) {
        std::cout << "\n[" << entry.first << "]\n";
        printTransaction(entry.second);
      }
      std::cout << "====================\n";
      continue;
    }

    std::cout << "Gecersiz secim.\n";
  }

  return 0;
}
