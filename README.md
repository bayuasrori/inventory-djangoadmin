# Django Inventory Management System

A comprehensive inventory management system built with Django, featuring warehouse management, stock tracking, and automated stock movements.

## Features

- Multiple warehouse management
- Stock tracking with stockards
- Automated stock movement processing
- Reference number generation
- User authentication and authorization
- Admin interface for managing inventory

## Tech Stack

- Django
- PostgreSQL (or SQLite for development)
- Python 3.8+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bayuasrori/inventory-djangoadmin.git
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the admin interface at http://localhost:8000/admin/
2. Log in with your superuser credentials
3. Manage warehouses, products, and stock movements

### Stock Movement Types

- **Inbound (IN)**: Add stock to a warehouse
- **Outbound (OUT)**: Remove stock from a warehouse
- **Transfer (TRANSFER)**: Move stock between warehouses

## Project Structure

```
inventory-djangoadmin/
├── core/               # Django project settings
├── inventory/          # Main app
│   ├── admin.py        # Admin configurations
│   ├── apps.py         # App configuration
│   ├── migrations/     # Database migrations
│   ├── models.py       # Database models
│   ├── tests.py        # Test cases
│   └── views.py        # Views
└── manage.py           # Django management script
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or questions, please open an issue in the repository.
