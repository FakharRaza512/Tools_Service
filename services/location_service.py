import os
import csv
import json
import sys
import spacy
from fuzzywuzzy import fuzz
from nltk import download as nltk_download

# Increase CSV field size limit to handle large GeoJSON data
csv.field_size_limit(sys.maxsize)

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
        self.province_coords_file = os.path.join("utils", "province.csv")
        self.district_coords_file = os.path.join("utils", "district.csv")
        self.tehsil_coords_file = os.path.join("utils", "tehsil.csv")
        
        self.Data_of_region, self.index = self.load_cities(self.data_file)
        self.province_coords = self.load_coordinates(self.province_coords_file, "province")
        self.district_coords = self.load_coordinates(self.district_coords_file, "district")
        self.tehsil_coords = self.load_coordinates(self.tehsil_coords_file, "tehsil")
        
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

    def load_coordinates(self, file, coord_type):
        """Load coordinates from province, district, or tehsil CSV files"""
        coords_dict = {}
        try:
            with open(file, "r", encoding="utf8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        try:
                            if coord_type == "province":
                                # province.csv format: PROVINCE_NAME, GEOJSON
                                name = row[0].strip().lower()
                                geojson = row[1].strip()
                            elif coord_type == "district":
                                # district.csv format: PROVINCE, DISTRICT, GEOJSON
                                if len(row) >= 3:
                                    name = row[1].strip().lower()
                                    geojson = row[2].strip()
                                else:
                                    continue
                            elif coord_type == "tehsil":
                                # tehsil.csv format: DISTRICT, TEHSIL, GEOJSON
                                if len(row) >= 3:
                                    name = row[1].strip().lower()
                                    geojson = row[2].strip()
                                else:
                                    continue
                            
                            # Parse GeoJSON
                            coords_dict[name] = json.loads(geojson)
                            
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON for '{name}': {str(e)[:100]}")
                            continue
                        except Exception as e:
                            print(f"Error processing row in {coord_type}: {str(e)[:100]}")
                            continue
                            
        except FileNotFoundError:
            print(f"Warning: {file} not found")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")
        
        return coords_dict

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
            end_i = start_i + 400
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

    def map_location_admin(self, location: str):
        """
        Maps location to province using simple province → list of cities.
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

        return None

    def get_coordinates(self, province=None, district=None, tehsil=None):
        """
        Get coordinates based on province, district, or tehsil.
        Returns coordinates for the most specific level provided.
        """
        result = {
            "province": province,
            "district": district,
            "tehsil": tehsil,
            "coordinates": None,
            "level": None
        }

        # Normalize inputs
        province_normalized = province.strip().lower() if province else None
        district_normalized = district.strip().lower() if district else None
        tehsil_normalized = tehsil.strip().lower() if tehsil else None

        # Try to find coordinates in order of specificity: tehsil -> district -> province
        if tehsil_normalized and tehsil_normalized in self.tehsil_coords:
            result["coordinates"] = self.tehsil_coords[tehsil_normalized]
            result["level"] = "tehsil"
        elif district_normalized and district_normalized in self.district_coords:
            result["coordinates"] = self.district_coords[district_normalized]
            result["level"] = "district"
        elif province_normalized and province_normalized in self.province_coords:
            result["coordinates"] = self.province_coords[province_normalized]
            result["level"] = "province"

        return result

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

    def get_coordinates_from_mapping(self, mapping_result):
        """
        Get coordinates from a mapping result (output of extract_single).
        """
        if not mapping_result or not mapping_result.get("mapping"):
            return {
                "location": mapping_result.get("location") if mapping_result else None,
                "mapping": mapping_result.get("mapping") if mapping_result else None,
                "coordinates": None,
                "level": None
            }

        mapping = mapping_result["mapping"]
        coords_result = self.get_coordinates(
            province=mapping.get("province"),
            district=mapping.get("district"),
            tehsil=mapping.get("tehsil")
        )

        return {
            "location": mapping_result.get("location"),
            "mapping": mapping,
            "coordinates": coords_result["coordinates"],
            "level": coords_result["level"]
        }