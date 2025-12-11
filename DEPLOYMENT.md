# KALO - Deployment Guide

## Quick Start (Local Development)

```bash
# Clone repository
git clone <repo>
cd kalo-backend

# Setup environment
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Start services with Docker Compose
docker-compose up

# Initialize database
python -c "from app.db.database import init_db; import asyncio; asyncio.run(init_db())"

# Backend runs at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## PRODUCTION DEPLOYMENT

### Option 1: Railway (Recommended for Simplicity)

1. **Create Railway Account**
   - Go to https://railway.app
   - Connect GitHub repo

2. **Add Services**
   ```
   - PostgreSQL (built-in)
   - Redis (built-in)
   - Python FastAPI (custom)
   ```

3. **Environment Variables**
   ```
   DATABASE_URL=postgresql://user:pass@db:5432/kalo
   REDIS_URL=redis://redis:6379
   SECRET_KEY=<random-64-char-string>
   OPENAI_API_KEY=<your-key>
   AWS_ACCESS_KEY=<your-key>
   AWS_SECRET_KEY=<your-key>
   ```

4. **Procfile**
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   worker: celery -A app.celery_app worker -l info
   ```

5. **Deploy**
   - Push to main branch → Auto deploys

---

### Option 2: AWS (Scale to Production)

#### Setup EC2 + RDS + Elasticache

1. **Create EC2 Instance**
   ```bash
   # Ubuntu 22.04 LTS, t3.medium or larger
   ssh -i key.pem ubuntu@<instance-ip>
   
   # Install dependencies
   sudo apt update
   sudo apt install -y python3.11 python3-pip git nginx supervisor postgresql-client redis-tools
   
   # Clone repo
   git clone <repo> /home/ubuntu/kalo
   cd /home/ubuntu/kalo
   
   # Setup Python environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create RDS PostgreSQL**
   - Engine: PostgreSQL 15
   - Multi-AZ: Yes (production)
   - Storage: 20GB gp3
   - Backup: 30 days

3. **Create ElastiCache Redis**
   - Engine: Redis 7.0
   - Node type: cache.t3.micro (or larger)
   - Multi-AZ: Enabled

4. **Setup Nginx**
   ```nginx
   # /etc/nginx/sites-available/kalo
   server {
       listen 80;
       server_name kalo-api.example.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Setup Supervisor** (for process management)
   ```ini
   # /etc/supervisor/conf.d/kalo.conf
   [program:kalo-web]
   command=/home/ubuntu/kalo/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
   directory=/home/ubuntu/kalo
   autostart=true
   autorestart=true
   ```

6. **Setup Systemd Timer** for Celery
   ```ini
   # /etc/systemd/system/kalo-celery.service
   [Unit]
   Description=KALO Celery Worker
   After=network.target
   
   [Service]
   Type=forking
   User=ubuntu
   WorkingDirectory=/home/ubuntu/kalo
   ExecStart=/home/ubuntu/kalo/venv/bin/celery -A app.celery_app worker -l info -c 4
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

7. **SSL Certificate (Let's Encrypt)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d kalo-api.example.com
   ```

8. **Start Services**
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo systemctl restart kalo-celery
   sudo systemctl restart nginx
   ```

---

### Option 3: DigitalOcean App Platform (Mid-tier)

1. Create new App
2. Connect GitHub repo
3. Configure build: `pip install -r requirements.txt`
4. Configure run: `uvicorn main:app --host 0.0.0.0 --port 8080`
5. Add PostgreSQL and Redis components
6. Deploy

---

### Option 4: Heroku (Deprecated but still works)

```bash
# Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create kalo-api

# Add Postgres
heroku addons:create heroku-postgresql:standard-0 -a kalo-api

# Add Redis
heroku addons:create heroku-redis:premium-0 -a kalo-api

# Set environment
heroku config:set SECRET_KEY=<random> OPENAI_API_KEY=<key> -a kalo-api

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## DATABASE SETUP

### Initial Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head

# For production, track migrations in git:
git add alembic/
git commit -m "Add database migrations"
```

### Indexes for Performance

```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_daily_logs_user_date ON daily_logs(user_id, date);
CREATE INDEX idx_workouts_user_date ON workouts(user_id, completed_at);
CREATE INDEX idx_posts_created ON posts(created_at);
CREATE INDEX idx_runs_user_date ON runs(user_id, completed_at);
```

---

## MONITORING & LOGGING

### Application Monitoring

```python
# app/monitoring.py
from pythonjsonlogger import jsonlogger
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Recommended Tools
- **Errors**: Sentry (sentry.io)
- **Logs**: DataDog, New Relic, or CloudWatch
- **Metrics**: Prometheus + Grafana
- **Uptime**: Uptime Robot

### Example Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

---

## SCALING CONSIDERATIONS

### Horizontal Scaling

1. **Multiple API instances** behind load balancer
2. **Database read replicas** for queries
3. **Redis Cluster** for distributed caching
4. **Celery workers** autoscale based on queue

### Bottlenecks to Watch

1. **Video processing**: Use dedicated worker fleet
2. **Database queries**: Add read replicas, optimize indexes
3. **File uploads**: Use S3 + CloudFront CDN
4. **Real-time features**: Consider WebSocket server

---

## BACKUP & DISASTER RECOVERY

```bash
# Backup PostgreSQL
pg_dump -h <host> -U <user> kalo > backup.sql

# Restore
psql -h <host> -U <user> kalo < backup.sql

# Backup S3
aws s3 sync s3://kalo-media s3://kalo-media-backup/

# Automated backups (AWS RDS handles this)
```

---

## CI/CD SETUP

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
      - name: Deploy to Railway
        uses: railway-app/actions@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
```

---

## SECURITY CHECKLIST

- [ ] HTTPS/SSL enforced
- [ ] Rate limiting on API endpoints
- [ ] CORS properly configured
- [ ] JWT secret rotated regularly
- [ ] Database credentials in secrets manager
- [ ] S3 bucket private (not public)
- [ ] Regular security audits
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] CSRF protection for state-changing operations

---

## PERFORMANCE OPTIMIZATION

### Cache Strategy
```python
# Cache frequently accessed data
CACHE_TTL = {
    "user_profile": 3600,      # 1 hour
    "recipes": 1800,            # 30 minutes
    "workout_history": 300,     # 5 minutes
}
```

### Query Optimization
```python
# Use select() with joins, avoid N+1 queries
from sqlalchemy import select, joinedload

result = await db.execute(
    select(Recipe)
    .options(joinedload(Recipe.user))
    .where(Recipe.user_id == user_id)
)
```

---

## NEXT STEPS

1. Setup production database
2. Configure S3 bucket + CloudFront
3. Add OpenAI API key
4. Setup CI/CD pipeline
5. Deploy backend
6. Test all endpoints
7. Setup monitoring
8. Deploy iOS app against production API

---

End of deployment guide. See iOS app setup in main README.
