# Book Marketplace Prototype

### Features
1. **Offer a Book**: Vendors can list books with details like title, author, and price.
2. **Search for Books**: Customers can search books by any field (e.g., title, author).
3. **Purchase a Book**: Customers can buy books, with shipping address shared with the vendor and optionally with marketing if opted in.

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