# Virtual Terminal - Payment Processing Interface

A full-featured virtual terminal web application for processing card-not-present transactions, including **Unmatched Refund** support.

## Features

### Core Transaction Processing
- **Key Enter Card** - Manually enter card details for Sale, Auth Only, or Credit transactions
- **Swipe Card** - Process card-present transactions via card reader
- **Multiple Transactions** - Batch process multiple transactions
- **Batch Upload** - Upload CSV/TXT files for bulk processing

### Transaction Management
- **Void Transactions** - Cancel authorized transactions
- **Refund Transactions** - Process matched refunds against original transactions
- **Unmatched Refund** - Issue refunds without referencing an original transaction (standalone credit)
- **Capture Transactions** - Capture previously authorized transactions
- **Settle Transactions** - Batch settle all captured transactions

### Unmatched Refund Feature
The unmatched refund feature allows merchants to:
- Issue refunds to a card without a matching original transaction ID
- Specify refund reason (Customer Request, Duplicate Charge, Product Return, etc.)
- Add internal notes and customer information
- Requires explicit confirmation before processing
- Full audit trail with transaction logging

### Reporting & Data
- **View Transactions** - Search and filter transaction history
- **View Batch Reports** - Settlement batch history
- **Dashboard** - Real-time transaction statistics
- **QuickBooks® Report** - Export-ready reporting

## Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- Node.js (optional, for development server)

### Running the Application

**Option 1: Direct File Open**
```bash
open index.html
```

**Option 2: Using a Development Server**
```bash
npx serve .
```

**Option 3: Using Live Server**
```bash
npx live-server --port=3000
```

## Project Structure

```
├── index.html          # Main application HTML
├── css/
│   └── styles.css      # Application styles
├── js/
│   └── app.js          # Application logic and transaction processing
├── package.json        # Project metadata
└── README.md           # This file
```

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Custom properties, Flexbox, Grid, responsive design
- **Vanilla JavaScript** - No framework dependencies
- **Font Awesome 6** - Icon library (CDN)
- **LocalStorage** - Client-side transaction persistence

## Transaction Simulation

This is a demonstration/development interface. Transactions are simulated with:
- ~85% approval rate
- Various decline codes (Do Not Honor, Insufficient Funds, Invalid Card)
- All data stored in browser localStorage

## License

MIT
