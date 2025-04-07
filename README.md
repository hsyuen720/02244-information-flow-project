# Book Marketplace Prototype

This is a terminal-based prototype for an electronic book marketplace, built as part of the "02244 Logic for Security" course project. It demonstrates secure information flow using Myers' Decentralized Label Model, implemented in Python with SQLite as the database.

## Overview

The Book Marketplace allows:
- **Vendors** to offer books for sale.
- **Customers** to search for books and purchase them.
- Secure handling of sensitive data (e.g., shipping addresses) with explicit declassification.
- **Selling User Data**: Optional opt-in for customers to share purchase data for marketing purposes, with a small discount.

### Features
1. **Offer a Book**: Vendors can list books with details like title, author, and price.
2. **Search for Books**: Customers can search books by any field (e.g., title, author).
3. **Purchase a Book**: Customers can buy books, with shipping address shared with the vendor and optionally with marketing if opted in.

### Security Model
- Based on **Myers' Decentralized Label Model** (A. C. Myers and B. Liskov, 1997).
- Uses security labels to enforce confidentiality and integrity:
  - **Owners**: Control who can read/write data.
  - **Readers/Writers**: Defined in labels (e.g., `{"read_by": ["public"], "write_by": ["vendor_id", "platform"]}`).
  - **Declassification**: Explicitly relaxes constraints (e.g., sharing shipping address with vendors, or marketing data if opted in).

## Prerequisites

- **Python 3.x**: Ensure Python is installed (e.g., run `python3 --version` or `python --version`).
- No external libraries required beyond Python's standard library (`sqlite3`, `json`, etc.).

## Setup Instructions

1. **Clone or Download**:
   - If using Git: `git clone <repository-url>` (replace with your repo URL if hosted).
   - Otherwise, download and extract the project files to a directory (e.g., `book-marketplace/`).

2. **Project Files**:
   Ensure the following files are in your project directory:
   - `database.py`: Manages database setup and connections.
   - `security.py`: Implements access control with security labels.
   - `features.py`: Core functions (`offer`, `search`, `purchase`).
   - `utils.py`: Helper functions for name retrieval.
   - `menu.py`: Terminal-based user interface.
   - `main.py`: Program entry point.

3. **Run the Program**:
   - Open a terminal in the project directory.
   - Execute: `python main.py` (or `python3 main.py` on some systems).
   - The program creates a SQLite database (`book_marketplace.db`) with sample data.

## Usage Guide

Run `python main.py` to see: