# Distributed File Storage and Retrieval System

<div align="center">

<!-- ![Project Logo](https://via.placeholder.com/150) -->

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.0+-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

</div>

## 🚀 Project Overview

A scalable, redundant, and efficient distributed file storage system built using Django, MinIO, and Docker. The project addresses limitations of traditional single-server file storage by providing distributed storage across multiple nodes.

### 🎯 Key Features

- **Distributed Storage**: Files are automatically distributed across multiple storage nodes
- **Load Balancing**: Smart allocation of resources to maximize performance
- **Fault Tolerance**: System continues to function even if some nodes fail
- **User-friendly Interface**: Simple web interface for file operations
- **Enhanced Security**: Secure file upload and retrieval mechanisms

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django (Python) |
| **Database** | PostgreSQL / SQLite |
| **Object Storage** | MinIO |
| **Containerization** | Docker & Docker Compose |
| **Frontend** | Django Templates, HTML, CSS, JavaScript |

## 🏗️ System Architecture

The system works by:

1. Distributing uploaded files across multiple MinIO storage nodes
2. Storing file metadata in a Django database
3. Retrieving files from the nearest or least-loaded node
4. Ensuring data redundancy and fault tolerance

<div align="center">
  
```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|  Client        |     |  Django App    |     |  MinIO Nodes   |
|                |     |                |     |                |
+-------+--------+     +-------+--------+     +-------+--------+
        |                      |                      |
        +----------------------+----------------------+
```

</div>

## 📦 Installation and Setup

### Prerequisites

- Python 3.8+
- Docker
- Docker Compose

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository_url>
cd distributed-file-storage
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run database migrations**
```bash
python manage.py migrate
```

5. **Start MinIO storage nodes**
```bash
docker-compose up -d
```

6. **Run Django server**
```bash
python manage.py runserver
```

## 🌐 Accessing the Application

- **Web Interface**: `http://127.0.0.1:8000/`
- **MinIO Console**: `http://127.0.0.1:9001/`

## 🔮 Future Enhancements

- [ ] Auto-scaling storage nodes
- [ ] Advanced access control and permissions
- [ ] Performance optimization and caching
- [ ] Enhanced file versioning and recovery
- [ ] Mobile application support

## 💡 Potential Use Cases

- **Enterprise Storage Solutions**: Scalable storage for businesses of all sizes
- **Media and Content Storage**: Efficient storage for media files
- **Data Science and Analytics**: Distributed storage for large datasets
- **Backup and Disaster Recovery**: Redundant storage for critical data

## 🙏 Acknowledgements

- Django Software Foundation
- MinIO Inc.
- Docker Inc.

## 📚 References

- [Django Documentation](https://docs.djangoproject.com)
- [MinIO Documentation](https://min.io/docs/)
- [Docker Documentation](https://docs.docker.com)

---

<div align="center">
  
**Developed as part of COMP-8347: Internet Applications and Distributed Systems**

</div>