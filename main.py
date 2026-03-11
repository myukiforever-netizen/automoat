"""
Simple POST request to https://crm.truemedia.ch/fr/properties/filter

Requirements:
	pip install requests beautifulsoup4

Run:
	python lab.py
"""

import requests
import re
from bs4 import BeautifulSoup

URL = "https://crm.truemedia.ch/fr/properties/filter"
HEADERS = {
	"Cookie": (
		"remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IjROMUlNMFY2ZXVHd3lcL3dUVElsenBnPT0iLCJ2YWx1ZSI6Imtjb3ZcL3huRjJiRVRUa0pQSzZ5b2lKZVVQREVNT0h3aFl3MXJZYUZjNTR0d0ErbWh2UTNzelRDMFwvaVJBVDZMSVYyS0JGQXpqZDhiZnJ6QWZZNFhyMDZ1Rkd3dXpjTXZubFQ1ZW92KzdXOFk9IiwibWFjIjoiY2ZmZWUxZDc2Y2MwMDJlYmE1OThjMDkzMzE0OTU5ZmYzZWM2MmZlN2RmYjhhMTFlYzdiMDk1ZGM5Y2NjMmViZSJ9; "
		"laravel_session=eyJpdiI6Ing3Slhqd0lOeDZSdWdQY0ZTakpVV3c9PSIsInZhbHVlIjoiWTF6WEVkaEhcL3huTXZNR05lblZ3WWNyYStqWEQ4NkYwMFpmZzEwZHZDM1Z0MWhCRzMySWZraVFtMVQ3aXVGVUFYZmlBQ25Db3lCME1ocTFcL1ZEUk5XUT09IiwibWFjIjoiZGI5YjQxYzY3MGQ3Nzg5MDJiNjJkMWZjYzNjOGU3NTVmMzRlYWEwYmFiZDRjMGFiMGU1ZTU5Njg2NGVmNmJiMSJ9"
	),
	"User-Agent": (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/145.0.0.0 Safari/537.36"
	),
	"x-csrf-token": "z5DKVXOGI4Y2T8ZWEKj1DP8E7MiIXXOhkZxH136u",
}

DATA = {
	"_token": "z5DKVXOGI4Y2T8ZWEKj1DP8E7MiIXXOhkZxH136u",
	"status[]": "1",
	"mode": "list",
	"cat": "0",
}

API_TOKEN = "bf550817828687e40a2322cc7b31e31cfa51820397815500f891e63e43c8e1c7"
COLLECTION_ID = "699227dfaf393c48ed063651"
BASE_URL = "https://api.webflow.com/v2"


def extract_agent_ids(html_text):

    """Return a list of ints found in the `value` attribute of
    inputs with class "agents-checkbox selectable-item".

    Tries BeautifulSoup if available, falls back to a regex.
    """

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_text, "html.parser")
        inputs = soup.select("input.agents-checkbox.selectable-item")
        ids = []
        for inp in inputs:
            val = inp.get("value") or ""
            m = re.search(r"\d+", val)
            if m:
                ids.append(int(m.group()))
        return ids

    except Exception:
        pattern = r'<input[^>]*class=["\'][^"\']*agents-checkbox[^"\']*selectable-item[^"\']*["\'][^>]*value=["\']([^"\']+)["\']'
        vals = re.findall(pattern, html_text)
        out = []
        for v in vals:
            m = re.search(r"\d+", v)
            if m:
                out.append(int(m.group()))
        return out

def send_request():
	with requests.Session() as s:
		s.headers.update(HEADERS)
		try:
			resp = s.post(URL, data=DATA, timeout=30)
		except requests.RequestException as e:
			print("Request failed:", e)
			return

		print("Status:", resp.status_code)
		ct = resp.headers.get("Content-Type", "")
		body = resp.text
		if "application/json" in ct:
			try:
				print("hello body")
			except ValueError:
				print("body")
		else:
			print("body")

		ids = extract_agent_ids(body)
		print("Extracted agent ids:", ids)
		return ids



def find_id(uid):
    FIELD_SLUG = "uid"
    SEARCH_TEXT = uid


    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "accept": "application/json"
    }

    # -----------------------------
    # URL API V2
    # -----------------------------

    url = f"https://api.webflow.com/v2/collections/{COLLECTION_ID}/items"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Erreur API :", response.status_code)
        print(response.text)
        exit()


    data = response.json()

    items = data.get("items", [])
    #print(items)


    # -----------------------------
    # CHECK TEXT
    # -----------------------------

    found = []

    for item in items:
        
        
        fields = item.get("fieldData", {})
        

        value = fields.get(FIELD_SLUG)


        if str(SEARCH_TEXT).lower() in str(value).lower():
            found.append(item)
        
        #print(SEARCH_TEXT.lower(), "in", str(value).lower(), "->", SEARCH_TEXT.lower() in str(value).lower())


    print("Items trouvés :", len(found))

    for item in found:

        print("-----")

        print("ID :", item.get("id"))

        print("Valeur :", item["fieldData"].get(FIELD_SLUG))
        
    return found


def get_property_by_id(prop_id, session=None, timeout=30):
    """GET https://crm.truemedia.ch/fr/properties/{id}

    Returns a `requests.Response`. If `session` is None a temporary
    session is created and closed; otherwise the provided session is used.
    The module `HEADERS` are applied when a new session is created.
    """
    url = f"https://crm.truemedia.ch/fr/properties/{prop_id}/slidepanel?"
    if session is None:
        with requests.Session() as s:
            s.headers.update(HEADERS)
            resp = s.get(url, timeout=timeout)
            return resp
    else:
        return session.get(url, timeout=timeout)


def extract_property_for_webflow(html: str) -> dict:

    soup = BeautifulSoup(html, "lxml")

    ###############################
    # UTILS
    ###############################

    def extract_number(text):
        if not text:
            return None
        n = re.sub(r"[^\d]", "", text)
        return int(n) if n else None

    def find_value(label):

        strongs = soup.find_all("strong")

        for s in strongs:

            if label.lower() in s.get_text().lower():

                parent = s.parent.get_text()

                value = parent.replace(s.get_text(), "").strip()

                return value

        return None


    ###############################
    # UID
    ###############################

    uid = ""

    header = soup.find("header")

    if header:

        match = re.search(r"P(\d+)", header.get_text())

        if match:
            uid = match.group(1)


    ###############################
    # NAME
    ###############################

    title = soup.find("h3")

    name = title.get_text(strip=True) if title else ""


    ###############################
    # PRIX
    ###############################

    price = soup.find(string=re.compile("Prix"))

    loyer = None

    if price:

        parent = price.parent

        span = parent.find("span")

        if span:

            loyer = extract_number(span.get_text())


    ###############################
    # ADRESSE + VILLE
    ###############################

    ville = ""

    adresse = soup.find(string=re.compile("Adresse"))

    if adresse:

        a = adresse.parent.find("a")

        if a:

            txt = a.get_text()

            if adresse:
                ville = txt.split("Adresse")[-1]
                ville = ville.split(">")[-1]
                ville = ville.split(",")[0]
                ville = ville.split(" ")[-1].strip()


            print("ok adresse", ville)


    ###############################
    # CARACTERISTIQUES
    ###############################

    pieces = extract_number(find_value("Pièce"))

    chambres = extract_number(find_value("Chambre"))

    salle_bain = extract_number(find_value("Salle"))

    etage = extract_number(find_value("Etage"))

    parking = extract_number(find_value("parking"))
    
    if str(parking).lower() in ["oui", "yes", "1"]:
        parking = "Oui"


    ###############################
    # SURFACE
    ###############################

    surface = extract_number(find_value("Surface habitable"))
    
    #if 2 is the last number we remove it because it's probably "m2"
    if surface and str(surface).endswith("2"):
        surface = int(str(surface)[:-1])


    ###############################
    # CATEGORIE
    ###############################

    cat = ""

    category_text = soup.find(string=re.compile("Catégorie"))

    if category_text:

        parent = category_text.parent.get_text()

        cat = parent.split(":")[-1].strip()


    ###############################
    # DESCRIPTION
    ###############################

    desc_title = soup.find("h4", string=re.compile("Description"))

    description = ""

    if desc_title:

        texts = []

        for el in desc_title.next_siblings:

            if getattr(el, "name", None) == "div":

                break

            if isinstance(el, str):

                texts.append(el.strip())

        description = "\n".join(t for t in texts if t)
        
    #if description have rturn line we remove any \n or \r to avoid issues in Webflow
    description = description.replace("\n", " ").replace("\r", " ")


    ###############################
    # PHOTOS
    ###############################

    photos = []

    gallery = soup.select(".owl-carousel a[data-gallery]")

    for a in gallery:

        url = a.get("href")

        if url:

            photos.append({

                "fileId": "",   # Webflow upload après
                "url": url,
                "alt": None

            })


    miniature = photos[0] if photos else None


    ###############################
    # NAME AUTO GENERATION
    ###############################

    if not name:

        name = f"{cat} {pieces} pièces à {ville}"


    ###############################
    # WEBFLOW DICTIONNAIRE FINAL
    ###############################

    webflow_item = {

            "name": name,

            "uid": uid,

            "ville": ville,

            "cat": cat,

            "loyer": loyer,

            "pieces": pieces,

            "nb-chambre": chambres,

            "nb-salle-de-bain": salle_bain,

            "nb-toilette": salle_bain,

            "surface": surface,

            "etage": etage,

            "parking": parking,

            "description": description,

            "miniature": miniature,

            "photos": photos,

            "slug": re.sub(
                r"[^a-z0-9]+",
                "-",
                name.lower()
            ).strip("-")

        }

    return webflow_item


def get_headers(api_token: str) -> dict:
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }



def create_collection_item(
    api_token,
    collection_id,
    field_data,
    is_draft=False,
    is_archived=False
):

    url = f"{BASE_URL}/collections/{collection_id}/items/live"

    payload = {
        "isDraft": is_draft,
        "isArchived": is_archived,
        "fieldData": field_data
    }

    response = requests.post(
        url,
        json=payload,
        headers=get_headers(api_token)
    )

    # ✅ Webflow V2 accepte 202
    if response.status_code in [200, 201, 202]:

        print("✅ Item créé avec succès")

        return response.json()

    raise Exception(
        f"Erreur API {response.status_code} : {response.text}"
    )

"""
item = create_collection_item(

    API_TOKEN,
    COLLECTION_ID,

    {
        "name": "Article API Python",
        "slug": "article-api-python",
        "description": "Ajout automatique V2"
    }

)
"""

response = send_request()

print("NEXT : ",response)

for uid in response:
    print(f"Recherche de l'uid {uid} dans Webflow...")
    find = find_id(uid)
    
    if not find:
        print("Aucun uid trouvé dans la réponse.")
        Dproperty = get_property_by_id(uid).text
        print("DPROPERTY : ", Dproperty)
        item = extract_property_for_webflow(Dproperty)
        elem = create_collection_item(
        API_TOKEN,
        COLLECTION_ID,
        item
        )
        
        print(elem)
        
        


    








