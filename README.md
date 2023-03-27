#Argyle Skanning Task


Scanner of website [upwork.com](https://upwork.com), that gets information about best matches of jobs and profile info.

[Link for task](https://argylesystems.notion.site/Argyle-Scanning-Task-Programming-71f79b9deda041bf84db0e0e4bcfc2af)

## Setup

#### **Login variables**

Add .env file to folder UpworkScanner and add credentials here:
```
    USERNAME=<username>
    PASSWORD=<password>
    SECRET=<secret phrase>
```

#### **Installing dependencies**

To install dependencies you may use both pip and poetry.

**Pip:**

```bash
pip install -r requirements.txt
playwright install-deps
```

**Poetry**

```bash
pip install poetry
poetry install --no-interaction
poetry playwright install-deps
```

#### **Running**

To start scrapping run src/app.py

## Output

Results of scrapping wil be saved in files jobs.json and profile.json

**jobs.json**

```json
[
    {
        "title": "Make i2p console accessible remotely",
        "url": "https://www.upwork.com//jobs/Make-i2p-console-accessible-remotely_~019f14b7ecdd8709e1/",
        "description": "description",
        "job_type": "Fixed-price",
        "time_posted": "14 hours ago",
        "tier": "Entry level",
        "est_time": "3 to 6 months, Less than 30 hrs/week",
        "budget": "$15",
        "skills": [
            "Linux System Administration"
        ],
        "client_country": "United States",
        "client_rating": 4.904581678,
        "payment_verified": true,
        "client_spending": "$2k+ spent",
        "proposals": "Less than 5"
    }
]
```

**profile.json**

```json
{
    "id": "42380e7c",
    "account": "1637475147748556800",
    "employer": null,
    "created_at": "2023-03-19T15:24:32.697Z",
    "updated_at": "2023-03-26T18:54:40.226Z",
    "first_name": "John",
    "last_name": "Smith",
    "full_name": "John Smith",
    "email": "john.smith.54@internet.ru",
    "phone_number": "+39495959",
    "birth_date": null,
    "picture_url": "https://www.upwork.com/profile-portraits/c1NqJxk9vZtSCOGL9n8-4e3l3IWPkGQ4fTZsgOaiTIjCA77GtNbT9YXAMAqH8caKay",
    "address": {
        "line1": "Bndndnmd",
        "line2": "312",
        "city": "Desio",
        "state": ", Lombardy",
        "postal_code": "2020",
        "country": "Italy"
    },
    "ssn": null,
    "marital_status": null,
    "gender": null,
    "metadata": {}
}
```
