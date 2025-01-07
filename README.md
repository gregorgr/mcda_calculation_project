# mcda_calculation_project




# MCDA Calculation Project

A Flask-based web application for Multi-Criteria Decision Analysis (MCDA). This project allows users to evaluate and rank Fortune 500 companies using advanced decision-making methods like AHP, PROMETHEE, and WSM.

---

## **Table of Contents**
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Methods](#methods)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**
- **Fortune 500 Scraper**: Extract company data directly from the Fortune 500 rankings.
- **MCDA Methods**:
  - **AHP (Analytic Hierarchy Process)**: Basic and advanced implementations.
  - **PROMETHEE**: Add-on for pairwise comparisons.
  - **WSM (Weighted Sum Model)**: Simplified ranking method.
- **Dynamic Analysis**: Filter and analyze subsets of Fortune 500 companies.
- **Interactive Web Interface**: Designed with Flask, Bootstrap, and responsive templates.
- **Database Integration**: Results and company data are stored in SQLite.

---

## **Project Structure**

```plaintext
mcda_calculation_project/
├── app
│   ├── app.py
│   ├── app_v0.001.py
│   ├── constants.py
│   ├── db
│   │   ├── database.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── fortune500.db
│   ├── __init__.py
│   ├── methods
│   │   ├── ahp
│   │   ├── promethee
│   │   └── wsm
│   ├── __pycache__
│   │   └── constants.cpython-313.pyc
│   ├── routes.py
│   ├── scrape500
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── scrape500.py
│   ├── static
│   │   └── css
│   ├── templates
│   │   ├── base.html
│   │   ├── companies
│   │   ├── compare.html
│   │   ├── header.html
│   │   ├── home.html
│   │   ├── index.html
│   │   ├── methods
│   │   ├── plot.html
│   │   ├── results.html
│   │   ├── scrape.html
│   │   ├── select_companies.html
│   │   └── sidebar.html
│   └── venv
│       ├── bin
│       ├── include
│       ├── lib
│       ├── lib64 -> lib
│       └── pyvenv.cfg
├── config.py
├── README.md
├── requirements.txt
└── tests
    ├── database.py
    ├── models.py
    └── test_app.py

```

## Installation
1. Clone the repository
```bash
git clone https://github.com/gregorgr/mcda_calculation_project.git
cd mcda_calculation_project
```

2. **Set up a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```
4. **Set up the database**

python app/db/database.py

## Usage
1. **Run the Flask server**

	```bash
	python app/app.py
	```

2. **Access the web interface**

Open your browser and navigate to:

[link](http://127.0.0.1:5000)

3. **Simple scrape fortune 500 API**

Scrape API (JSON):

[link](http://127.0.0.1:5000/api/scrape-fortune-500)



## Methods
1. **AHP (Analytic Hierarchy Process)**

    Basic and advanced implementations available.
    Supports pairwise comparisons and consistency checks.

2. **PROMETHEE**

    Pairwise preference-based comparison for ranking.

3. **WSM (Weighted Sum Model)**

    Simplified linear combination method for decision-making.
   


## Contributing
Contributions are welcome! To contribute:

    Fork the repository.
    Create a new branch for your feature.
    Commit and push your changes.
    Submit a pull request.


## Avtor

- **Gregor Grajzar** - GitHub profil



## License

This project is licensed under the MIT License. See the LICENSE file for details.







