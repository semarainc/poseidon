# POSEIDON 🛒 — Point-Of-Sale System
Version: 1.0
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-green?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-orange)
![Docker](https://img.shields.io/badge/ready-Docker%20%26%20Podman-blue)

> **POSEIDON** is an open-source, lightweight yet powerful Point-Of-Sale web app designed for small & medium stores. It delivers an intuitive dashboard, quick-sale workflow, inventory tracking, supplier & customer management, and detailed sales reports — all wrapped in a responsive UI.

---

## ✨ Key Features

|                | Feature |
| -------------- | ------- |
| ⚡ **Fast Checkout** | Quick-add bestseller list & barcode search |
| 📦 **Inventory** | Stock alerts (low/soon-expired) & supplier linkage |
| 📈 **Reporting** | XLSX daily/period reports |
| 🔐 **Auth & Roles** | Admin / Cashier accounts via Flask-Login |
| 🗄️ **DB Options** | SQLite for quick start, PostgreSQL for production |
| 🐳 **Container Ready** | 1-command deployment with uWSGI |

---

## 📷 Screenshots

| Dashboard | Sales |
| --------- | ----- |
| ![Dashboard](screenshots/Dashboard.png) | ![Sales](screenshots/Sales.png) |

---

## 🚀 Quick Start

### 1. Local Python
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit DB_TYPE etc. if needed
python app.py  # browse http://localhost:5000
```

### 2. Docker / Podman
```bash
git clone https://github.com/semarainc/poseidon.git
cd poseidon
podman build -t poseidon-pos .
podman run -d --name poseidon -p 8999:8999 --env-file .env poseidon-pos
# uWSGI will serve on port 8999
```

---

## ⚙️ Configuration

| Variable | Example | Description |
| -------- | ------- | ----------- |
| `SECRET_KEY` | `super-secret` | Flask session key |
| `DB_TYPE` | `sqlite` / `postgres` | Select DB engine |
| `SQLITE_URI` | `sqlite:///instance/poseidon.db` | Override SQLite path |
| `POSTGRES_URI` | `postgresql://user:pass@host/db` | PostgreSQL URI |
| `POSEIDON_ENV` | `development` / `production` | Config profile |

See `.env` for template.

---

## 🏗️ Tech Stack

* Python 3.12, Flask 2, SQLAlchemy
* Bootstrap 5 & FontAwesome
* uWSGI, Docker / Podman

---

## 🤝 Contributing
Pull requests are welcome! Please open an issue first to discuss major changes.

```bash
git clone https://github.com/semarainc/poseidon.git
```

See `CONTRIBUTING.md` for coding standards & commit message style.

---

## 📜 License
Released under the MIT License — see `LICENSE` for details.

---
## 🙏 Credits & Attribution

- [Trident icon](https://www.flaticon.com/free-icons/trident) by **Freepik** on [Flaticon](https://www.flaticon.com/).

### Contributors
- **Ade Wira** ([Tradewr](https://github.com/Tradewr)) — Donatur & Initiator
- **Adi Purnama** ([AdiPurnama12](https://github.com/AdiPurnama12)) — Front-End Design

Huge thanks to the open-source community — Flask, Bootstrap, SQLAlchemy, and everyone who makes building web apps a joy!