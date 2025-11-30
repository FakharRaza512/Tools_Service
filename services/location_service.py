import os
import csv
import spacy
#import mysql.connector
from fuzzywuzzy import fuzz
from nltk import download as nltk_download

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


class LocationService:

    def __init__(self):
        self.data_file = os.path.join("utils", "Alldata_refined.csv")
        self.Data_of_region, self.index = self.load_cities(self.data_file)
        #self.map = {
        #    "Punjab": ["Lahore", "Rawalpindi", "Faisalabad", "Multan"],
        #    "Sindh": ["Karachi", "Hyderabad", "Sukkur"],
        #    "KPK": ["Peshawar", "Swat"],
        #    "Balochistan": ["Quetta", "Gwadar"]
            # Add more if needed
        #}
        self.map = {
                "Punjab": [
        "Lahore", "Rawalpindi", "Faisalabad", "Multan", "Gujranwala",
        "Sialkot", "Sargodha", "Bahawalpur", "Rahim Yar Khan",
        "Sheikhupura", "Kasur", "Okara", "Sahiwal", "Jhang",
        "Toba Tek Singh", "Mianwali", "Attock", "Chakwal",
        "Gujrat", "Mandi Bahauddin", "Muzaffargarh", "Dera Ghazi Khan",
        "Pakpattan", "Vehari", "Khanewal", "Hafizabad",
        "Nankana Sahib", "Layyah", "Burewala", "Sadiqabad",
        "Khanpur", "Kot Momin", "Arifwala", "Wazirabad",
        "Sambrial", "Kharian", "Jhelum"
    ],

    "Sindh": [
        "Karachi", "Hyderabad", "Sukkur", "Larkana", "Mirpur Khas",
        "Nawabshah", "Thatta", "Badin", "Dadu", "Jamshoro",
        "Jacobabad", "Ghotki", "Khairpur", "Shikarpur", "Sanghar",
        "Kashmore", "Umerkot", "Tando Allahyar", "Tando Muhammad Khan",
        "Kotri", "Mirpur Mathelo", "Ranipur", "Qambar",
        "Shahdadkot", "Tando Adam", "Manzoor Colony (Karachi)",
        "Sultanabad (Karachi)", "Kehkeshan (Karachi)"
    ],

    "KPK": [
        "Peshawar", "Mardan", "Swat", "Mingora", "Abbottabad",
        "Mansehra", "Haripur", "Swabi", "Nowshera", "Charsadda",
        "Kohat", "Dera Ismail Khan", "Bannu", "Battagram",
        "Buner", "Lower Dir", "Upper Dir", "Chitral",
        "Batkhela", "Karak", "Hangu", "Shangla",
        "Pattan", "Banda", "Razar", "Beka",
        "Gandaf", "Arkot", "Bandi Shungli"
    ],

    "Balochistan": [
        "Quetta", "Gwadar", "Turbat", "Khuzdar", "Hub",
        "Chaman", "Pishin", "Sibi", "Zhob",
        "Loralai", "Kalat", "Panjgur", "Ormara",
        "Dera Murad Jamali", "Usta Muhammad", "Kharan",
        "Awaran", "Lasbela"
    ]
    }

    # -----------------------------------------
    # LOAD CITIES + INDEX
    # -----------------------------------------
    def load_cities(self, file):
        data = []
        with open(file, "r", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                loc = row["Locations"].strip().lower()
                data.append(loc)

        data = sorted(list(set(data)))

        # build letter index
        index = {}
        for i, word in enumerate(data):
            first = word[0]
            if first not in index:
                index[first] = i

        return data, index

    # -----------------------------------------
    # EXTRACT LOCATION
    # -----------------------------------------
    def extract_location(self, text: str):
        if not text or not isinstance(text, str):
            return {"location": None, "candidates": {}}

        doc = nlp(text)
        cities = {}

        for token in doc:
            if token.pos_ != "PROPN":
                continue

            key = token.text.lower()[0]
            if key not in self.index:
                continue

            start_i = self.index[key]
            end_i = start_i + 400  # similar windowing as legacy code
            if end_i > len(self.Data_of_region):
                end_i = len(self.Data_of_region)

            for loc in self.Data_of_region[start_i:end_i]:
                parts = loc.split()
                if fuzz.ratio(token.text.lower(), parts[0]) < 95:
                    continue

                match_len = 1
                good = True

                # Multi-word matching
                for j in range(1, len(parts)):
                    if token.i + j >= len(doc):
                        good = False
                        break
                    if fuzz.ratio(doc[token.i + j].text.lower(), parts[j]) < 70:
                        good = False
                        break
                    match_len += 1

                if not good:
                    continue

                matched = " ".join(parts)
                cities[matched] = cities.get(matched, 0) + 1

        if not cities:
            return {"location": None, "candidates": {}}

        best = max(cities, key=cities.get)
        return {"location": best, "candidates": cities}

    # -----------------------------------------
    # MAP EXTRACTED LOCATION → PROVINCE / DISTRICT / TEHSIL
    # -----------------------------------------
    def map_location_admin(self, location: str):
        """
        Maps location to province using simple province → list of cities.
        Works for:
        - City only (e.g. 'Quetta')
        - Province only (e.g. 'Punjab')
        - Both present in input text (separate detection)
        """

        if not location:
            return None

        location_upper = location.upper()

        # ---- Province match ----
        for province in self.map.keys():
            if province.upper() == location_upper:
                return {
                    "province": province,
                    "district": None,
                    "tehsil": None
                }

        # ---- City match ----
        for province, cities in self.map.items():
            for city in cities:
                if city.upper() == location_upper:
                    return {
                        "province": province,
                        "district": None,
                        "tehsil": city
                    }

        # No match
        return None

    """
    def map_location_admin(self, location: str):
        if not location:
            return None

        location_upper = location.upper()
        
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="newsnet"
        )
        cur = conn.cursor()

        # PROVINCE
        cur.execute("SELECT name FROM province WHERE name=%s", (location_upper,))
        province = cur.fetchone()
        if province:
            cur.close()
            conn.close()
            return {
                "province": province[0],
                "district": None,
                "tehsil": None
            }

        # DISTRICT
        cur.execute("SELECT name, province FROM district WHERE name=%s", (location_upper,))
        district = cur.fetchone()
        if district:
            cur.close()
            conn.close()
            return {
                "province": district[1],
                "district": district[0],
                "tehsil": None
            }

        # TEHSIL
        cur.execute("SELECT name, district FROM tehsil WHERE name=%s", (location_upper,))
        tehsil = cur.fetchone()
        if tehsil:
            tehsil_name, tehsil_district = tehsil

            cur.execute("SELECT name, province FROM district WHERE name=%s", (tehsil_district,))
            dist = cur.fetchone()

            cur.close()
            conn.close()
            return {
                "province": dist[1],
                "district": dist[0],
                "tehsil": tehsil_name
            }

        cur.close()
        conn.close()
        return None
        """
    # -----------------------------------------
    # ENDPOINT WRAPPERS
    # -----------------------------------------
    def extract_single(self, text: str):
        loc = self.extract_location(text)
        mapped = self.map_location_admin(loc["location"])
        return {
            "location": loc["location"],
            "mapping": mapped,
            "candidates": loc["candidates"]
        }

    def extract_bulk(self, texts: list[str]):
        return [self.extract_single(t) for t in texts]
