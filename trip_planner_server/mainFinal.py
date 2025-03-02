import googlemaps
import json
from geopy.distance import geodesic
from flask import Flask, request, jsonify
import io
import qrcode
from flask import Flask, request, send_file, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import json

SCOPES = ["https://www.googleapis.com/auth/drive"]

app = Flask(__name__)

# Initialize Google Maps API
API_KEY = "XXXXXXXXXXXXX"  # Replace with your actual API key
gmaps = googlemaps.Client(key=API_KEY)

# Replace this with your actual Yelp API Key
YELP_API_KEY = "XXXXXXXXXXXXXXXXXXXM97XXXXXXXXXn5fXXXXXXXXXXXXx"
headers = {"Authorization": f"Bearer {YELP_API_KEY}"}


price_levels = ["1", "2", "3"]  # 1 = $, 2 = $$, 3 = $$$

# ++++++++++ FUNCTIONS HERE++++++++++++++

def create_drive_folder_with_qr(folder_name="Default_Folder"):
    """
    Creates a Google Drive folder, generates a sharable upload link,
    and returns a QR code image in memory.
    
    Parameters:
        folder_name (str): The name of the folder to create.
    
    Returns:
        io.BytesIO: The generated QR code image in memory.
    """
    
    # Authenticate and authorize
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    drive_service = build("drive", "v3", credentials=creds)

    # Step 1: Create folder
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder.get("id")

    # Step 2: Make the folder accessible (Change permissions)
    permission = {
        "role": "writer",  # Users can upload files
        "type": "anyone"  # Anyone with the link can upload
    }
    drive_service.permissions().create(fileId=folder_id, body=permission).execute()

    # Step 3: Generate sharable link
    sharable_link = f"https://drive.google.com/drive/folders/{folder_id}"
    
    # Step 4: Generate QR Code
    qr = qrcode.make(sharable_link)
    img_io = io.BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)

    return img_io

def get_restaurants_nearby(location):
    """
    Fetch top 3 restaurants near the given location using Yelp API.
    """
    recommendations = []
    
    for price in price_levels:
        params = {
            "term": "restaurant",
            "location": f"{location}, Las Vegas, NV",
            "limit": 5,  # Fetch more and filter manually
            "sort_by": "rating",
            "price": price
        }

        url = "https://api.yelp.com/v3/businesses/search"
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ API Error for {location}: {response.status_code} - {response.text}")
            continue

        data = response.json()

        for restaurant in data.get("businesses", []):
            recommendations.append({
                "Name": restaurant.get("name", "Unknown"),
                "Location": location,
                "Timing": restaurant.get("hours", "Not Available"),
                "Famous Food": ", ".join([cat["title"] for cat in restaurant.get("categories", [])]),
                "Google Maps Link": f"https://www.google.com/maps/search/?api=1&query={restaurant['coordinates']['latitude']},{restaurant['coordinates']['longitude']}"
            })
        
        # Stop after 3 recommendations
        if len(recommendations) >= 3:
            break

    return recommendations[:3]

def find_meeting_places(user_locations, search_type="restaurant", radius=1000):
    """
    Finds the best meeting place based on user locations.
    
    Parameters:
    - user_locations: List of tuples (lat, lon) representing user coordinates.
    - search_type: Type of place to search for (default is 'restaurant').
    - radius: Search radius in meters (default is 1000m).

    Returns:
    - JSON response containing recommended places in the required format.
    """

    # Step 1: Compute centroid (average lat, lon) as an approximate meeting point
    centroid_lat = sum(lat for lat, lon in user_locations) / len(user_locations)
    centroid_lon = sum(lon for lat, lon in user_locations) / len(user_locations)
    approx_meeting_point = (centroid_lat, centroid_lon)

    # Step 2: Find nearby places (restaurant, cafe, etc.) using Google Places API
    places_result = gmaps.places_nearby(
        location=approx_meeting_point,
        radius=radius,  
        type=search_type
    )

    # Step 3: Extract top 3 meeting locations in the required format
    locations = {}
    for idx, place in enumerate(places_result.get("results", [])[:3], start=1):  # Limit to top 3
        name = place["name"]
        lat = place["geometry"]["location"]["lat"]
        lon = place["geometry"]["location"]["lng"]
        
        # Generate Google Maps link
        maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        
        locations[f"Location {idx}"] = {"link": maps_link}

    # Step 4: Return JSON response in required format
    return json.dumps(locations, indent=4)


#+++++++++++ APIS HERE +++++++++++++


@app.route('/get_locations', methods=['GET'])
def find_meeting_point():
    """
    Flask API endpoint to get meeting places based on user coordinates.
    
    Request JSON Format:
    {
        "user_locations": [
            {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 40.73061, "longitude": -73.935242},
            {"latitude": 40.758896, "longitude": -73.985130}
        ]
    }
    
    Response JSON Format:
    {
        "Location 1": {"link": "https://maps.google.com/?q=location1"},
        "Location 2": {"link": "https://maps.google.com/?q=location2"},
        "Location 3": {"link": "https://maps.google.com/?q=location3"}
    }
    """
    try:
        data = request.get_json()

        # If user_locations are missing, use default locations
        user_locations = [
            (loc["latitude"], loc["longitude"]) for loc in data.get("user_locations", DEFAULT_LOCATIONS)
        ]

        result = find_meeting_places(user_locations)
        return jsonify(json.loads(result))  # Convert JSON string back to dict
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_hotels', methods=['GET'])
def get_hotel_recommendations():
    """
    Flask API endpoint to get restaurant recommendations based on the itinerary.
    
    Request JSON Format:
    {
        "locations": ["Caesars Palace", "Bellagio", "Grand Canyon"]
    }

    Response JSON Format:
    {
        "Hotel 1": {"location": "Location 1", "timing": "10 AM - 10 PM", "famous food": "Burgers"},
        "Hotel 2": {"location": "Location 2", "timing": "9 AM - 9 PM", "famous food": "Pizza"},
        "Hotel 3": {"location": "Location 3", "timing": "24/7", "famous food": "Sushi"}
    }
    """
    try:
        data = request.get_json()

        # If locations are missing, return default hotel recommendations
        locations = data.get("locations", [])


        # Fetch recommendations from Yelp API
        recommendations = {}
        for idx, location in enumerate(locations[:3], start=1):  # Limit to 3 hotels
            restaurants = get_restaurants_nearby(location)

            if restaurants:
                recommendations[f"Hotel {idx}"] = {
                    "location": location,
                    "timing": restaurants[0].get("Timing", "Unknown"),
                    "famous food": restaurants[0].get("Famous Food", "Unknown")
                }

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    """
    Flask API endpoint to generate a QR code for a Google Drive folder.
    
    Request JSON Format:
    {
        "folder_name": "My Project Files"
    }

    Response: 
    Returns a PNG image of the QR code.
    """
    try:
        data = request.get_json()
        folder_name = data.get("folder_name", "Default_Folder")

        # Generate QR Code
        qr_image = create_drive_folder_with_qr(folder_name)

        return send_file(qr_image, mimetype="image/png")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# LM Studio API URL
LLM_API_URL = "http://localhost:1234/v1/completions"

def query_llm(prompt, max_tokens=1400):
    """Queries the local LLM and ensures clean output."""
    payload = {
        "model": "meta-llama-3.1-8b-instruct",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stop": [
            "END OF TASK", "✅", "💰", "🚀", "🏝️", "** **", "✍️", "🎉", "🙏"
        ]
    }
    response = requests.post(LLM_API_URL, json=payload)
    return response.json().get("choices", [{}])[0].get("text", "").strip()

@app.route('/ai_response', methods=['POST'])
def ai_response():
    try:
        data = request.json
        user_input = data.get("message", "")
        
        # Prompt for AI to extract details and generate trip plan
        trip_prompt = f"""
        You are an expert travel planner. The user provided this input:
        "{user_input}"
        
        Extract the following details from the input and generate a JSON response:
        - Name
        - Group size
        - Age range
        - Preferred activities (at most 3)
        - Nightlife preference (Vibrant, Relaxed, None)
        - Budget per person (USD)
        - Trip duration (days)
        - Any specific destinations mentioned
        - Suggested destinations (5 if none given)
        - A structured trip itinerary including:
            - Accommodations within budget
            - Daily activities (morning, afternoon, night)
            - Estimated costs per person
        
        📌 **Format the output in JSON format like this:**
        {{
            "Name": "John Doe",
            "Group Size": 2,
            "Age Range": "25-35",
            "Preferred Activities": ["Outdoor Adventures", "Food & Drink"],
            "Nightlife Preference": "Relaxed",
            "Budget": "$1000",
            "Trip Duration": "5 days",
            "Special Destination": "Hawaii",
            "Suggested Destinations": ["Honolulu", "Maui", "Big Island", "Kauai", "Oahu"],
            "Trip Plan": {{
                "Destination": "Hawaii",
                "Accommodations": [{{"Name": "Beach Resort", "Price": "$200 per night"}}],
                "Itinerary": [
                    {{"Day": "Day 1", "Time": "Morning", "Location": "Waikiki Beach", "Activity": "Surfing", "Price": "$50"}},
                    {{"Day": "Day 1", "Time": "Afternoon", "Location": "Hiking Trail", "Activity": "Hiking", "Price": "Free"}}
                ],
                "Total Estimated Cost": "$XXX per person"
            }}
        }}
        """
        
        ai_response_json = query_llm(trip_prompt)
        trip_data = json.loads(ai_response_json)
    except json.JSONDecodeError:
        return jsonify({"response": "The Trip Details have analyzed"}), 200
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)