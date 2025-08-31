# 🔗 Unified Data Studio v2 - Integration Guide

## 📋 Overview

This guide covers integrating Unified Data Studio v2 with other systems, APIs, and workflows.

## 🚀 Quick Start

### Basic Integration
```python
# Python example
from unified_data_studio import DataStudio

# Initialize connection
studio = DataStudio(host='localhost', port=8080)

# Connect to data source
studio.connect_database('postgresql://user:pass@localhost/db')

# Execute query
result = studio.execute_query('SELECT * FROM users LIMIT 10')
```

## 🔌 API Reference

### Core API Endpoints

#### Data Operations
```http
# Query data
POST /api/v2/query
Content-Type: application/json

{
  "sql": "SELECT * FROM users WHERE active = true",
  "parameters": {},
  "timeout": 30000
}

# Response
{
  "success": true,
  "data": [...],
  "columns": [...],
  "rowCount": 100,
  "executionTime": 45
}
```

#### Workflow Management
```http
# Create workflow
POST /api/v2/workflows
Content-Type: application/json

{
  "name": "Data Processing Pipeline",
  "steps": [
    {
      "type": "query",
      "sql": "SELECT * FROM raw_data",
      "output": "raw_data"
    },
    {
      "type": "transform",
      "input": "raw_data",
      "operation": "clean_data",
      "output": "clean_data"
    }
  ]
}
```

### Authentication

#### API Key Authentication
```http
Authorization: Bearer YOUR_API_KEY
X-API-Version: 2.0
```

#### Session Authentication
```http
Cookie: session_id=YOUR_SESSION_ID
X-API-Version: 2.0
```

## 🗄️ Database Integration

### Supported Databases

#### Relational Databases
- **PostgreSQL** - Full support with advanced features
- **MySQL/MariaDB** - Core functionality
- **SQLite** - Built-in, always available
- **SQL Server** - Enterprise features
- **Oracle** - Basic support

#### NoSQL Databases
- **MongoDB** - Document operations
- **Redis** - Caching and sessions
- **Elasticsearch** - Search and analytics

### Connection Examples

#### PostgreSQL
```python
# Python
studio.connect_database(
    'postgresql://username:password@localhost:5432/database',
    options={
        'sslmode': 'require',
        'connect_timeout': 10
    }
)

# JavaScript
const studio = new DataStudio();
await studio.connectDatabase({
    type: 'postgresql',
    host: 'localhost',
    port: 5432,
    database: 'mydb',
    username: 'user',
    password: 'pass',
    ssl: true
});
```

#### SQLite
```python
# Local SQLite database
studio.connect_database('sqlite:///./data/local.db')

# In-memory database
studio.connect_database('sqlite:///:memory:')
```

## 📊 Data Processing

### Formula Engine

#### Supported Functions
```sql
-- Mathematical
SUM(), AVG(), COUNT(), MAX(), MIN()

-- Text Processing
TEXT_JOIN(), CONCAT(), UPPER(), LOWER()

-- Conditional
IF(), CASE WHEN, COALESCE()

-- Advanced
PIVOT(), UNPIVOT(), WINDOW functions
```

#### Custom Functions
```python
# Register custom function
@studio.register_function
def calculate_ratio(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator

# Use in queries
result = studio.execute_query("""
    SELECT 
        product_name,
        calculate_ratio(sales, units) as sales_per_unit
    FROM sales_data
""")
```

### Workflow Engine

#### Workflow Definition
```yaml
# workflow.yaml
name: "Data Pipeline"
version: "2.0"
steps:
  - id: "extract"
    type: "extract"
    source: "database"
    query: "SELECT * FROM source_table"
    
  - id: "transform"
    type: "transform"
    input: "extract"
    operations:
      - type: "filter"
        condition: "status = 'active'"
      - type: "aggregate"
        group_by: ["category"]
        aggregations:
          - column: "amount"
            function: "sum"
            
  - id: "load"
    type: "load"
    target: "database"
    table: "processed_data"
    mode: "replace"
```

#### Workflow Execution
```python
# Execute workflow
workflow_id = studio.create_workflow('workflow.yaml')
execution_id = studio.execute_workflow(workflow_id)

# Monitor progress
status = studio.get_workflow_status(execution_id)
print(f"Progress: {status['progress']}%")

# Get results
results = studio.get_workflow_results(execution_id)
```

## 🔄 Real-time Integration

### WebSocket API
```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'data_update':
            console.log('Data updated:', data.payload);
            break;
        case 'workflow_progress':
            console.log('Workflow progress:', data.payload);
            break;
        case 'error':
            console.error('Error:', data.payload);
            break;
    }
};

// Subscribe to specific events
ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['data_updates', 'workflow_progress']
}));
```

### Event Streaming
```python
# Subscribe to events
@studio.on_event('data_changed')
def handle_data_change(event):
    print(f"Data changed in table: {event.table}")
    print(f"Change type: {event.change_type}")
    print(f"Affected rows: {event.row_count}")

# Trigger custom events
studio.emit_event('custom_event', {
    'message': 'Custom event triggered',
    'timestamp': datetime.now().isoformat()
})
```

## 📱 Frontend Integration

### React Components
```jsx
import { DataStudioProvider, useDataStudio } from '@unified-data-studio/react';

function App() {
    return (
        <DataStudioProvider 
            apiUrl="http://localhost:8080"
            apiKey="your-api-key"
        >
            <DataDashboard />
        </DataStudioProvider>
    );
}

function DataDashboard() {
    const { studio, data, loading, error } = useDataStudio();
    
    const handleQuery = async () => {
        const result = await studio.executeQuery('SELECT * FROM users');
        // Handle result
    };
    
    return (
        <div>
            <button onClick={handleQuery}>Load Data</button>
            {loading && <div>Loading...</div>}
            {error && <div>Error: {error.message}</div>}
            {data && <DataTable data={data} />}
        </div>
    );
}
```

### Vanilla JavaScript
```html
<script src="https://unpkg.com/@unified-data-studio/client@2.0/dist/bundle.js"></script>
<script>
    const studio = new DataStudio({
        apiUrl: 'http://localhost:8080',
        apiKey: 'your-api-key'
    });
    
    // Execute query
    studio.executeQuery('SELECT * FROM products')
        .then(result => {
            console.log('Query result:', result);
        })
        .catch(error => {
            console.error('Query failed:', error);
        });
</script>
```

## 🔒 Security & Permissions

### Role-Based Access Control
```python
# Define roles and permissions
studio.create_role('analyst', {
    'permissions': [
        'read:data',
        'execute:queries',
        'create:reports'
    ],
    'restrictions': {
        'max_query_time': 300,
        'max_result_rows': 10000,
        'allowed_tables': ['public.*']
    }
});

# Assign role to user
studio.assign_role('user123', 'analyst');
```

### Data Masking
```sql
-- Apply data masking
CREATE VIEW masked_users AS
SELECT 
    id,
    MASK_EMAIL(email) as email,
    MASK_PHONE(phone) as phone,
    name  -- Unmasked
FROM users;
```

## 📈 Monitoring & Analytics

### Performance Metrics
```python
# Get query performance stats
stats = studio.get_query_stats(time_range='24h')

print(f"Total queries: {stats['total_queries']}")
print(f"Average execution time: {stats['avg_execution_time']}ms")
print(f"Slow queries (>5s): {stats['slow_queries']}")

# Get workflow performance
workflow_stats = studio.get_workflow_stats('pipeline_123')
print(f"Success rate: {workflow_stats['success_rate']}%")
print(f"Average duration: {workflow_stats['avg_duration']}s")
```

### Health Checks
```python
# Check system health
health = studio.get_health_status()

if health['status'] == 'healthy':
    print("✅ All systems operational")
else:
    print(f"⚠️ Issues detected: {health['issues']}")
    
# Check specific components
db_health = studio.check_database_health()
api_health = studio.check_api_health()
```

## 🚀 Deployment

### Docker Integration
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 8080
CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  unified-data-studio:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/studio
    depends_on:
      - db
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=studio
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Kubernetes
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unified-data-studio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unified-data-studio
  template:
    metadata:
      labels:
        app: unified-data-studio
    spec:
      containers:
      - name: studio
        image: unified-data-studio:2.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: unified-data-studio-service
spec:
  selector:
    app: unified-data-studio
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

## 🔧 Configuration

### Environment Variables
```bash
# Core settings
UNIFIED_DATA_STUDIO_PORT=8080
UNIFIED_DATA_STUDIO_HOST=0.0.0.0
UNIFIED_DATA_STUDIO_LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/studio
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30000

# Security
API_KEY_SECRET=your-secret-key
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Performance
MAX_CONCURRENT_QUERIES=50
QUERY_TIMEOUT=300000
RESULT_CACHE_TTL=3600
```

### Configuration File
```yaml
# config.yaml
server:
  port: 8080
  host: 0.0.0.0
  cors:
    origins: ["http://localhost:3000"]
    credentials: true

database:
  url: "postgresql://user:pass@localhost:5432/studio"
  pool:
    min: 5
    max: 20
  timeout: 30000

security:
  api_key_required: true
  jwt_expiry: "24h"
  rate_limit:
    window: "15m"
    max_requests: 1000

workflows:
  max_concurrent: 10
  timeout: 3600000
  retry_attempts: 3
```

## 📚 Additional Resources

- [Setup Guide](SETUP.md) - Installation and configuration
- [Build Guide](BUILD.md) - Development and building
- [API Documentation](https://api.unifieddatastudio.com)
- [GitHub Repository](https://github.com/Raghavendra-Pratap/Data_Studio)
- [Community Forum](https://community.unifieddatastudio.com)

## 🤝 Support

### Getting Help
- **Documentation**: Check this guide and related docs
- **GitHub Issues**: [Report bugs](https://github.com/Raghavendra-Pratap/Data_Studio/issues)
- **Community**: Join discussions and get help
- **Enterprise Support**: Contact for business inquiries

### Contributing
We welcome contributions! See [BUILD.md](BUILD.md) for development setup and contribution guidelines.

---

*For installation, see [SETUP.md](SETUP.md). For development, see [BUILD.md](BUILD.md).*
