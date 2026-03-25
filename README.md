# Society Management System - Backend API

This is the backend for our Society Management System built using **FastAPI** and **PostgreSQL**. Made this as a college project. It handles user registration, login, complaints, e-pass requests, notices and more.

---

## What this project does

- Users can register, login and manage their profile
- Users can submit complaints and request e-passes for guests
- Admin can approve/reject complaints and e-passes
- OTP based email verification for registration and password reset
- Google and GitHub OAuth login support
- QR code generation for users and approved guests
- JWT based authentication
- Rate limiting to prevent brute force attacks

---

## Tech Stack

- **Python** - FastAPI
- **PostgreSQL** - database
- **SQLAlchemy** - ORM (async)
- **Alembic** - database migrations
- **JWT** - authentication
- **Passlib / bcrypt** - password hashing
- **SMTP** - sending OTP emails
- **qrcode** - QR code generation

---

## Project Structure

```
├── app/
│   ├── main.py              # entry point
│   ├── models.py            # database models
│   ├── schemas.py           # pydantic schemas
│   ├── database.py          # db connection
│   ├── oauth2.py            # JWT logic
│   ├── utils.py             # helper functions
│   ├── tasks.py             # background tasks (email)
│   ├── api_services.py      # weather API
│   ├── state.py             # in-memory rate limit state
│   ├── exception/           # custom exceptions
│   └── routers/
│       ├── auth/            # login, register, email OTP, OAuth
│       ├── user/            # profile, vehicles, resident, support
│       ├── admin/           # admin actions
│       └── misls/           # QR token verification
├── alembic/                 # migrations
├── test/                    # pytest test suite
├── .env                     # environment variables (not pushed)
└── requirements.txt
```

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/society-management.git
cd society-management
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=society_db

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

ADMIN_CODE=your_admin_registration_code

sender=youremail@gmail.com
password=your_gmail_app_password

API_KEY=your_openweathermap_api_key
base_url=http://127.0.0.1:8000/verify

client_id_google=your_google_client_id
client_secret_google=your_google_client_secret

client_id_github=your_github_client_id
client_secret_github=your_github_client_secret
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

API will be running at `http://127.0.0.1:8000`

Swagger docs at `http://127.0.0.1:8000/docs`

---

## Main API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/user/` | Register a new user |
| POST | `/auth/register/admin/` | Register admin (needs admin key) |
| POST | `/auth/login/` | Login and get JWT token |
| POST | `/auth/verify-email/` | Check if email is already taken |
| POST | `/auth/email/` | Send OTP to email |
| POST | `/auth/verify-otp/` | Verify OTP |
| POST | `/auth/forget-password/` | Initiate password reset |
| PUT | `/auth/update-password/` | Update password after OTP verification |
| GET | `/auth/google/` | Google OAuth login |
| GET | `/auth/github/` | GitHub OAuth login |

### User
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/profile/` | Get own profile |
| PUT | `/user/personal/` | Update personal details |
| PUT | `/user/resident/` | Update resident/address details |
| POST | `/user/vehicle/add/` | Add a vehicle |
| DELETE | `/user/vehicle/remove/` | Remove a vehicle |
| GET | `/user/weather` | Get weather for your city |
| GET | `/user/notice` | Get notices |

### Support (User)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/user/support/complaint/` | Submit a complaint |
| GET | `/user/support/complaint/` | Get complaint status |
| POST | `/user/support/epass/` | Request an e-pass for guest |
| GET | `/user/support/epass/` | Get e-pass status |
| GET | `/user/support/status/` | Get all your tickets at once |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List all users |
| GET | `/admin/user/` | View a user's full profile |
| GET | `/admin/users/logs` | View user activity logs |
| GET | `/admin/complaints/` | View all complaints |
| PUT | `/admin/complaint/action` | Update complaint status |
| GET | `/admin/epass` | View all e-pass requests |
| PUT | `/admin/epass/action` | Approve/reject e-pass |
| POST | `/admin/notice` | Post a notice |
| GET | `/admin/notice` | View all notices |

### Misc
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/verify/` | Verify QR token (for gate entry) |

---

## Running Tests

Tests use a separate test database so your actual data is safe.

```bash
pip install pytest httpx
pytest -v
```

---

## Notes

- Make sure PostgreSQL is running before starting the server
- Gmail App Password is required for sending OTPs (not your regular gmail password)
- OAuth redirect URIs need to be set correctly in Google/GitHub developer console for OAuth to work
- The `ADMIN_CODE` in `.env` is needed to register admin accounts

---

## Authors

Made by [Your Name] as part of college minor project.
