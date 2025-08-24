# PostgreSQL Integration Guide

This document explains how the GainzAPI now supports PostgreSQL for production environments while maintaining SQLite for development.

## 🔧 Configuration

The application automatically detects whether to use PostgreSQL or SQLite based on the `DATABASE_URL` environment variable:

- **Development (SQLite)**: If `DATABASE_URL` is not set or points to a local file
- **Production (PostgreSQL)**: If `DATABASE_URL` starts with `postgresql://` or `postgres://`

## 🌍 Environment Variables

### Development (Local)
No configuration needed. The app will use SQLite at `data/exercises.db`.

### Production (Render, Heroku, etc.)
Set the following environment variable:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

Example for Render:
```bash
DATABASE_URL=postgresql://gainz_user:secure_password@dpg-xxxxx-a.oregon-postgres.render.com/gainz_db
```

## 📦 Dependencies

The following packages were added to `requirements.txt`:

```txt
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

## 🗄️ Database Schema

The application uses SQLAlchemy with a unified schema that supports both databases:

- **Backward compatible** with existing SQLite data
- **Production ready** for PostgreSQL with proper indexing and constraints
- **Automatic table creation** on startup

## 🚀 Deployment

### Render (Recommended)

1. **Connect your repository** to Render
2. **Add environment variables**:
   - `DATABASE_URL`: Your PostgreSQL connection string (auto-provided by Render)
   - `SECRET_KEY`: Your application secret
   - `ADMIN_USER`: Admin username
   - `ADMIN_PASS`: Admin password
   - `ORIGINS`: Allowed CORS origins
3. **Deploy** - The app will automatically create tables and initialize

### Other Platforms

The same approach works for:
- **Heroku**: Uses `DATABASE_URL` automatically
- **Railway**: Set `DATABASE_URL` in environment
- **Digital Ocean**: Configure PostgreSQL connection string

## 🔍 Verification

You can verify the configuration is working:

```bash
# Check configuration
python -c "from app.config import settings; print('Production:', settings.is_production)"

# Test database connection
python -c "from app.database import init_database; init_database()"
```

## 🐛 Troubleshooting

### Connection Issues
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
- Check database server is running and accessible
- Confirm credentials are correct

### Migration Issues
- Tables are created automatically on startup
- Existing SQLite data can be migrated using the provided scripts
- Check logs for detailed error messages

## 📋 Code Changes Made

1. **`app/database.py`** (NEW): SQLAlchemy engine and table definitions
2. **`app/config.py`**: Added production/development detection
3. **`app/main.py`**: Added database initialization on startup
4. **`requirements.txt`**: Added SQLAlchemy and psycopg2-binary

## 🧪 Testing

Run the comprehensive test:

```bash
python test_database_config.py
```

This verifies:
- SQLite configuration (development)
- PostgreSQL configuration (production)  
- URL detection logic
- Environment switching