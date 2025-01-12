# URL za Fortune 500
FORTUNE_URL = "https://fortune.com/ranking/global500/search/"

SECRET_KEY = "^iaB)4_r%v'0^WcF4XeAn:F$}0$Qj"
SECRET_KEY = "ZfuiOaTZy7wB^iaB)4_r%v'A8rPURFBxAndn:F$}0$nrNzEnh7"

METHODS = {
    1: "AHP",
    2: "Topsis",
    3: "PROMETHEE",
    4: "WSM"
}

sidebar_links = [
    {
        "title": "Functions",
        "links": [
            {
                "name": "Scrape Fortune 500",
                "url": "/api/scrape-fortune-500",
                "sub_links": [
                    {"name": "Scrape and Save", "url": "/scrape-and-save"}
                ]
            },
            {"name": "Fortune 500", "url": "/companies"},
            {"name": "Select companies", "url": "/select-companies"}
        ]
    },
    {
        "title": "Methods",
        "links": [
            {
                "name": "AHP",
                "url": "/ahp",
                "sub_links": [
                    {"name": "Results", "url": "/results/1"}
                ]
            },
            {
                "name": "Topsis",
                "url": "/topsis",
                "sub_links": [
                    {"name": "Results", "url": "/results/2"}
                ]
            },
            {
                "name": "PROMETHEE",
                "url": "/promethee",
                "sub_links": [
                    {"name": "Results", "url": "/results/3"}
                ]
            },
            {
                "name": "WSM",
                "url": "/wsm",
                "sub_links": [
                    {"name": "Results", "url": "/results/4"}
                ]
            }
        ]
    },
    {
        "title": "Results",
        "links": [
            {"name": "Compare Results", "url": "/compare"}
        ]
    }
]