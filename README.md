# AKA_UKA Fast Food Telegram Bot

A professional, feature-rich Telegram bot built for fast food ordering and management. It features multi-language support (Uzbek & Russian), a dynamic menu system, a robust shopping cart, and a full administrative dashboard.

## 🌟 Features

- **Multi-language Support**: Seamless switching between Uzbek and Russian.
- **Interactive Menu**: Browse categories, subcategories, and products with high-quality images and descriptions.
- **Dynamic Shopping Cart**: 
  - Add/remove items with a single tap.
  - Adjust quantities before adding.
  - View real-time totals and itemized breakdowns.
- **Smart Checkout Flow**:
  - Location-based delivery address picking.
  - Payment method selection (Cash or Card).
  - Admin notifications for new orders.
- **Order Tracking**: Users can view their order history and current status.
- **Admin Dashboard**:
  - Manage categories and products directly from the bot.
  - Fast-track order processing and status updates.
- **Production Ready**: Optimized with Docker, environment variables, and asynchronous database handling.

## 🛠 Tech Stack

- **Core Framework**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Database**: SQLite with `aiosqlite` for asynchronous I/O.
- **Environment Management**: `python-dotenv`.
- **Infrastructure**: Docker & Docker Compose.

## 🚀 Getting Started

### Local Development

1. **Clone the project**:
   ```bash
   git clone https://github.com/Komron0412/Aka_uka-fast_food.git
   cd Aka_uka-fast_food
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Open .env and fill in your TOKEN and ADMIN_ID
   ```

5. **Run the Bot**:
   ```bash
   python main.py
   ```

### Docker Deployment (Recommended)

1. **Configure Environment**: Create and edit your `.env` file as shown above.
2. **Launch with Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```

## 📂 Project Structure

- `main.py`: Entry point, command handlers, and core application loop.
- `inlines.py`: Intelligent callback handler for all inline interactions.
- `messages.py`: Logic for processing text messages and state management.
- `database.py`: Database schema and asynchronous repository methods.
- `admin.py`: Specialized handlers for the administrative interface.
- `globals.py`: Centralized constants, translations, and UI labels.
- `methods.py`: Reusable UI components and message builders.
- `register.py`: User registration and onboarding state machine.

## 👨‍💻 Author

**Komron**

## 📜 License

Distributed under the MIT License.
