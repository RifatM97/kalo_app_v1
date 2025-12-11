# Kalo Backend Deployment Guide

Complete production deployment instructions for the Kalo backend with AI recipe extraction pipeline.

## Deployment Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Production Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer (Nginx)                                      │
│         ↓                                                    │
│  FastAPI Instances (3-5 replicas)                           │
│         ↓                                                    │
│  PostgreSQL Database (managed service)                      │
│  Redis Cluster (managed service)                            │
│         ↓                                                    │
│  Celery Workers (5-10 workers, can scale)                   │
│  Celery Beat (1 instance)                                   │
│  Flower Dashboard (1 instance, for monitoring)              │
└─────────────────────────────────────────────────────────────┘
```

## Pre-Deployment Checklist

- [ ] Obtain OPENAI_API_KEY or ANTHROPIC_API_KEY
- [ ] Setup PostgreSQL database (AWS RDS recommended)
- [ ] Setup Redis cluster (AWS ElastiCache recommended)
- [ ] Configure DNS records
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Setup monitoring and alerting (CloudWatch, Datadog, etc.)
- [ ] Setup log aggregation (CloudWatch Logs, ELK, etc.)
- [ ] Create backup strategy for database
- [ ] Test disaster recovery procedure
- [ ] Document runbooks for common operations

## Deployment Options

### Option 1: Docker Compose (Small/Medium Scale)

Best for: Development, staging, small production

**Pros**: Simple, fast, all-in-one

**Cons**: Single machine, limited scalability

```bash
# 1. Clone repository
git clone https://github.com/kalo/kalo-backend.git
cd kalo-backend

# 2. Create environment file
cp .env.example .env
# Edit .env with production values

# 3. Build and deploy
docker-compose up -d

# 4. Verify services
docker-compose ps
docker-compose logs api
docker-compose logs celery_worker

# 5. Access services
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Flower: http://localhost:5555

# 6. Monitor
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### Option 2: Kubernetes (Large Scale)

Best for: Enterprise, high availability, auto-scaling

See `k8s-deployment.yaml` for full Kubernetes setup.

```bash
# 1. Create namespace
kubectl create namespace kalo-prod

# 2. Create secrets
kubectl create secret generic kalo-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=redis-url="redis://..." \
  --from-literal=openai-api-key="sk-..." \
  -n kalo-prod

# 3. Deploy application
kubectl apply -f k8s-deployment.yaml

# 4. Verify deployment
kubectl get pods -n kalo-prod
kubectl logs -n kalo-prod -l app=kalo-api

# 5. Check services
kubectl get services -n kalo-prod
```

### Option 3: Cloud Platforms

#### AWS ECS (Elastic Container Service)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name kalo-backend

# 2. Build and push image
docker build -t kalo-backend .
docker tag kalo-backend:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/kalo-backend:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/kalo-backend:latest

# 3. Create ECS task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# 4. Create ECS service
aws ecs create-service --cluster kalo-prod --service-name kalo-api --task-definition kalo-backend --desired-count 3

# 5. Monitor
aws ecs describe-services --cluster kalo-prod --services kalo-api
```

#### Heroku

```bash
# 1. Create app
heroku create kalo-backend-prod

# 2. Add buildpacks
heroku buildpacks:set heroku/python
heroku buildpacks:add heroku/apt

# 3. Set environment variables
heroku config:set OPENAI_API_KEY="sk-..."
heroku config:set DATABASE_URL="postgresql://..."

# 4. Add Redis add-on
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0

# 5. Deploy
git push heroku main

# 6. Run migrations
heroku run alembic upgrade head

# 7. Scale workers
heroku ps:scale web=2 worker=3
```

## Database Setup

### PostgreSQL with AWS RDS

```bash
# 1. Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier kalo-db-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password "very-secure-password" \
  --allocated-storage 100 \
  --backup-retention-period 30 \
  --multi-az

# 2. Wait for instance to be available
aws rds describe-db-instances --db-instance-identifier kalo-db-prod

# 3. Get endpoint
ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier kalo-db-prod \
  --query 'DBInstances[0].Endpoint.Address' --output text)

# 4. Connect and create database
psql -h $ENDPOINT -U admin -c "CREATE DATABASE kalo_db;"

# 5. Run migrations
alembic upgrade head
```

### Database Backups

```bash
# Automatic backups (AWS RDS)
aws rds create-db-snapshot \
  --db-instance-identifier kalo-db-prod \
  --db-snapshot-identifier kalo-db-snapshot-$(date +%Y%m%d)

# Manual backup (local)
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup-$(date +%Y%m%d-%H%M%S).sql

# Restore from backup
psql -h $DB_HOST -U $DB_USER $DB_NAME < backup-2024-01-15-120000.sql
```

## Redis Setup

### Redis with AWS ElastiCache

```bash
# 1. Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id kalo-redis-prod \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --engine-version 7.0

# 2. Wait for cluster to be available
aws elasticache describe-cache-clusters --cache-cluster-id kalo-redis-prod

# 3. Get endpoint
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
  --cache-cluster-id kalo-redis-prod \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text)

# For production with failover
aws elasticache create-replication-group \
  --replication-group-description "Kalo Redis" \
  --replication-group-id kalo-redis-prod \
  --engine redis \
  --cache-node-type cache.t3.small \
  --num-cache-clusters 2 \
  --automatic-failover-enabled
```

## SSL/TLS Setup

### Using Let's Encrypt with Certbot

```bash
# 1. Install certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. Create certificate
sudo certbot certonly --standalone \
  -d api.kaloapp.com \
  -d www.kaloapp.com

# 3. Configure Nginx
# See nginx.conf for SSL configuration

# 4. Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# 5. Verify renewal
sudo certbot renew --dry-run
```

## Monitoring & Logging

### CloudWatch (AWS)

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /kalo/api

# Configure application to send logs
# Add to your FastAPI app:
import logging
import watchtower
handler = watchtower.CloudWatchLogHandler(
    log_group="/kalo/api",
    stream_name="api-prod"
)
logging.getLogger().addHandler(handler)
```

### Datadog

```bash
# Install Datadog agent
DD_AGENT_MAJOR_VERSION=7 \
DD_API_KEY=your-api-key \
DD_SITE="datadoghq.com" \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_agent.sh)"

# Add to docker-compose.yml or Kubernetes
environment:
  DD_ENV: prod
  DD_SERVICE: kalo-api
  DD_VERSION: 1.0.0
  DD_AGENT_HOST: localhost
  DD_AGENT_PORT: 8126
```

### Prometheus & Grafana

```bash
# 1. Add Prometheus metrics to FastAPI
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
requests_total = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    requests_total.labels(method=request.method, endpoint=request.url.path).inc()
    request_duration.observe(duration)
    
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

# 2. Deploy Prometheus
docker run -d -p 9090:9090 \
  -v prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# 3. Deploy Grafana
docker run -d -p 3000:3000 grafana/grafana
```

## Security Hardening

### Network Security

```bash
# 1. Setup security groups (AWS)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# 2. Restrict database access
aws rds authorize-db-security-group-ingress \
  --db-security-group-name kalo-db \
  --ec2-security-group-id sg-xxxxxxxx

# 3. Enable VPC
# Deploy database and Redis in private subnets
# Only API server in public subnet
```

### Application Security

```python
# 1. Enable HTTPS only
# In FastAPI app:
@app.middleware("http")
async def https_redirect(request: Request, call_next):
    if request.url.scheme == "http":
        url = URL(request.url).replace(scheme="https")
        return RedirectResponse(url)
    return await call_next(request)

# 2. Set security headers
# In Nginx config:
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;

# 3. CORS settings
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kaloapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Secrets Management

```bash
# 1. Use AWS Secrets Manager
aws secretsmanager create-secret \
  --name kalo/prod/database-url \
  --secret-string "postgresql://..."

# 2. Use HashiCorp Vault
# Deploy Vault and retrieve secrets
vault kv get secret/kalo/prod

# 3. Use Kubernetes Secrets
kubectl create secret generic kalo-secrets \
  --from-literal=database-url="..." \
  --from-literal=openai-api-key="..."
```

## Scaling

### Horizontal Scaling (Add More Instances)

```bash
# 1. Scale API servers
docker-compose up -d --scale api=5

# 2. Scale Celery workers
docker-compose up -d --scale celery_worker=10

# 3. Load balancing (Nginx routes to multiple API instances)
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
    server api4:8000;
    server api5:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}

# 4. For Kubernetes
kubectl scale deployment kalo-api --replicas=10
kubectl scale deployment kalo-worker --replicas=20
```

### Vertical Scaling (Bigger Machines)

```bash
# Increase machine specs
# AWS EC2: Stop instance → Change instance type → Start instance

# For managed services
# RDS: Modify → Change instance class
# Redis: Modify → Change node type
```

### Auto-scaling

```bash
# AWS Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name kalo-api-asg \
  --launch-configuration-name kalo-api-lc \
  --min-size 3 \
  --max-size 20 \
  --desired-capacity 5 \
  --availability-zones us-east-1a us-east-1b

# Kubernetes HPA (Horizontal Pod Autoscaler)
kubectl autoscale deployment kalo-api \
  --min=3 \
  --max=20 \
  --cpu-percent=70
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_recipes_status ON recipes(extraction_status);
CREATE INDEX idx_recipes_created_at ON recipes(created_at DESC);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM recipes WHERE user_id = 123;

-- Vacuum and analyze tables
VACUUM ANALYZE recipes;
```

### Caching Strategy

```python
# Redis caching
from functools import wraps
import json
import redis

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{json.dumps(args)}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        
        return wrapper
    return decorator

@cache_result(ttl=3600)
async def get_recipe(recipe_id: int):
    # Database query
    pass
```

### CDN for Media

```bash
# Setup CloudFront for media files
aws cloudfront create-distribution \
  --origin-domain-name media.s3.amazonaws.com \
  --default-cache-behavior file://cache-policy.json
```

## Disaster Recovery

### Backup & Restore

```bash
# 1. Automated daily backups
# AWS RDS: Enable automated backups with 30-day retention

# 2. Point-in-time recovery
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier kalo-db-restore \
  --db-snapshot-identifier kalo-db-snapshot-2024-01-15

# 3. Test restore procedure monthly
```

### Failover Testing

```bash
# 1. Test database failover (RDS Multi-AZ)
aws rds reboot-db-instance \
  --db-instance-identifier kalo-db-prod \
  --force-failover

# 2. Test API failover
# Stop one API instance, verify others handle traffic

# 3. Test Redis failover
# Failover primary Redis instance
```

## Troubleshooting

### API Server Issues

```bash
# 1. Check logs
docker-compose logs api
kubectl logs -n kalo-prod -l app=kalo-api

# 2. Check metrics
curl http://localhost:8000/metrics

# 3. Test database connection
docker-compose exec api python -c "from app.database import engine; engine.execute('SELECT 1')"

# 4. Restart service
docker-compose restart api
kubectl rollout restart deployment kalo-api -n kalo-prod
```

### Celery Worker Issues

```bash
# 1. Check queue
redis-cli LLEN celery

# 2. Check failed tasks
celery -A app.ai.tasks inspect active

# 3. Restart worker
docker-compose restart celery_worker

# 4. Clear queue (CAREFUL!)
redis-cli DEL celery

# 5. Check specific task
celery -A app.ai.tasks inspect result task-id
```

### Database Issues

```bash
# 1. Check connections
SELECT count(*) FROM pg_stat_activity;

# 2. Kill idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';

# 3. Check locks
SELECT * FROM pg_locks;

# 4. Analyze slow queries
SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC;
```

## Rollback Procedure

```bash
# 1. Keep previous Docker images
docker tag kalo-backend:latest kalo-backend:v1.0.0

# 2. Rollback to previous version
docker-compose down
docker-compose up -d --image kalo-backend:v1.0.0

# 3. Database rollback (if needed)
alembic downgrade -1

# 4. Verify rollback
docker-compose ps
curl http://localhost:8000/health
```

## Documentation & Runbooks

Create runbooks for common operations:

1. **Deployment Runbook**: Step-by-step deployment process
2. **Incident Response Runbook**: What to do when things break
3. **Scaling Runbook**: When and how to scale
4. **Backup & Recovery Runbook**: How to backup and restore
5. **Security Incidents Runbook**: What to do if security issue occurs

## Production Checklist

- [ ] All environment variables configured
- [ ] Database backup strategy implemented
- [ ] Monitoring and alerting setup
- [ ] Log aggregation configured
- [ ] SSL certificate installed
- [ ] Security groups configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] API documentation updated
- [ ] Runbooks created and tested
- [ ] Disaster recovery tested
- [ ] Team trained on procedures
- [ ] Monitoring dashboards created
- [ ] Alert thresholds configured
- [ ] On-call rotation established

## Support

For deployment issues:
1. Check logs: `docker-compose logs` or `kubectl logs`
2. Check metrics: Prometheus/Grafana dashboards
3. Check infrastructure: CloudWatch console
4. Review runbooks
5. Contact support team

## Next Steps

1. ✅ Choose deployment platform
2. ✅ Setup infrastructure (database, Redis)
3. ✅ Deploy application
4. ✅ Configure monitoring
5. ✅ Setup backups
6. ✅ Run disaster recovery test
7. ✅ Optimize performance
8. ✅ Train team
9. ✅ Go live!
