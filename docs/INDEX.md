# Family CFO Documentation Index

> **Version**: 2.0
> **Last Updated**: 2026-01-01

Welcome to the Family CFO documentation. This index will help you find the information you need.

---

## 📚 Core Documentation

### Architecture & Design
- **[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)** - System architecture, tech stack, data flow
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database tables, relationships, and indexes

### Getting Started
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Quick setup and installation
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Docker-specific deployment guide

### Configuration
- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - Environment variables and configuration
- **[CONFIG_TEST_REPORT.md](CONFIG_TEST_REPORT.md)** - Configuration testing results

---

## 🧪 Testing & Development

### Test Data Management
- **`../scripts/seed_mock_data.py`** - Generate comprehensive test data
- **`../scripts/clear_data.py`** - Clear database for fresh start

### Testing Guides
- **[QUICK_TEST_GUIDE.md](QUICK_TEST_GUIDE.md)** - Quick testing procedures

---

## 📊 Project Progress

### Completion Reports
- **[ALL_PHASES_COMPLETION_SUMMARY.md](ALL_PHASES_COMPLETION_SUMMARY.md)** - Overall project summary
- **[FINAL_PROJECT_SUMMARY.md](FINAL_PROJECT_SUMMARY.md)** - Final deliverables summary
- **[PROJECT_REVIEW_REPORT.md](PROJECT_REVIEW_REPORT.md)** - Project review and assessment

### Phase Reports
- **[PHASE_3_COMPLETION_REPORT.md](PHASE_3_COMPLETION_REPORT.md)**
- **[PHASE_4_COMPLETION_REPORT.md](PHASE_4_COMPLETION_REPORT.md)**
- **[PHASE_5_COMPLETION_REPORT.md](PHASE_5_COMPLETION_REPORT.md)**
- **[PHASE_6_COMPLETION_REPORT.md](PHASE_6_COMPLETION_REPORT.md)**

### Execution Plans
- **[PHASE_5_EXECUTION_PLAN.md](PHASE_5_EXECUTION_PLAN.md)**
- **[PHASE_6_EXECUTION_PLAN.md](PHASE_6_EXECUTION_PLAN.md)**
- **[IMPLEMENTATION_PROGRESS.md](IMPLEMENTATION_PROGRESS.md)**

---

## 🐛 Bug Fixes & Issues

- **[BUG_FIXES_REPORT.md](BUG_FIXES_REPORT.md)** - Bug fix documentation
- **[BUG_FIX_SUMMARY_CN.md](BUG_FIX_SUMMARY_CN.md)** - Bug fix summary (Chinese)
- **[ACTUAL_BUG_FIX_STATUS.md](ACTUAL_BUG_FIX_STATUS.md)** - Current bug fix status

---

## 🗂️ Project Structure

```
familyltdcfo/
├── backend/           # FastAPI backend (Port 6501)
├── admin/             # Admin web app (Port 6502)
├── frontend/          # Mobile app (Port 6503)
├── docs/              # Documentation (this folder)
├── scripts/           # Utility scripts
├── docker-compose.yml # Container orchestration
└── README.md          # Project overview
```

---

## 🔑 Quick Reference

### Ports
- **6500**: PostgreSQL Database
- **6501**: Backend API
- **6502**: Admin Panel
- **6503**: Mobile App

### Default Credentials (Development)
```
Username: admin
Password: admin123
```

### Useful Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Generate mock data
docker exec familycfo_backend python scripts/seed_mock_data.py

# Clear database
docker exec -it familycfo_backend python scripts/clear_data.py

# Rebuild containers
docker-compose build
docker-compose up -d
```

---

## 📖 Additional Resources

### External Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)

### API Documentation
- Swagger UI: http://localhost:6501/docs
- ReDoc: http://localhost:6501/redoc

---

## 💡 Tips

1. **Start with**: [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for initial setup
2. **For development**: Use `seed_mock_data.py` to generate test data
3. **For production**: Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
4. **Database schema**: Reference [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
5. **Architecture**: See [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)

---

**Need help?** Check the [README.md](../README.md) in the project root.
