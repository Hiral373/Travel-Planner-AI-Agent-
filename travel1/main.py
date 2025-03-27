from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

with open('destinations.json', 'r', encoding='utf-8') as f:
    destinations = json.load(f)  # Load destination and itinerary data

with open('itineraries.json', 'r', encoding='utf-8') as f:
    itineraries = json.load(f)

session_data = {
    "destination": None,
    "travel_date": None
}  # Session data


def get_weather(destination):
    API_KEY = "1aef80f017ed462bbfd61e21d76abd91"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={destination}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return None
        weather = f"{data['main']['temp']}°C, {data['weather'][0]['description'].capitalize()}"
        return weather
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_message = request.form["msg"].lower().strip()
    response = ""

    if any(greet in user_message for greet in ['hello', 'hi', 'hii', 'hey']):
        response = "👋 Hello! How can I assist you in planning your trip?"

    elif "south india" in user_message or "north india" in user_message or "west india" in user_message or "east india" in user_message:
        region = ""
        if "south india" in user_message:
            region = "South India"
        elif "north india" in user_message:
            region = "North India"
        elif "west india" in user_message:
            region = "West India"
        elif "east india" in user_message:
            region = "East India"

        region_destinations = [d["name"] for d in destinations if d["region"].lower() == region.lower()]
        if region_destinations:
            dest_list = ", ".join(region_destinations)
            response = f"🌍 The popular destinations in {region} are: {dest_list}. Which one would you like to visit?"
        else:
            response = f"Sorry, I don't have any destinations listed for {region}."

    elif "i want to go" in user_message:
        for dest in destinations:
            if dest["name"].lower() in user_message:
                session_data["destination"] = dest["name"]
                response = f"🌍 You want to go to {dest['name']}. When do you plan to travel?"
                break
        else:
            response = "Please mention a valid city or destination."

    elif "after" in user_message and "day" in user_message:
        num_days = [int(s) for s in user_message.split() if s.isdigit()]
        if num_days and session_data["destination"]:
            travel_date = datetime.today() + timedelta(days=num_days[0])
            session_data["travel_date"] = travel_date.strftime("%d-%m-%Y")
            response = f"✅ Your trip to {session_data['destination']} is planned on {session_data['travel_date']}. Do you want to know further information like weather, best time to visit or itinerary?"
        else:
            response = "Please first tell me your destination."

    elif "weather" in user_message:
        if session_data["destination"]:
            weather = get_weather(session_data["destination"])
            if weather:
                response = f"🌤️ Current weather in {session_data['destination']}: {weather}"
            else:
                response = "Sorry, I couldn't fetch the weather information."
        else:
            response = "Please tell me which city you want to know about."

    elif "best time" in user_message:
        if session_data["destination"]:
            dest_info = next((d for d in destinations if d["name"] == session_data["destination"]), None)
            if dest_info:
                months = ", ".join(dest_info["best_time_to_visit"])
                response = f"📅 Best time to visit {dest_info['name']} is: {months}."
            else:
                response = "I don't have information about that city."
        else:
            response = "Please mention a city first."

    elif "itinerary" in user_message:
        if session_data["itinerary"]:
            itinerary = itineraries.get(session_data["itinerary"])
            if itinerary:
                response = f"🗺️ Here’s a 3-day itinerary for {session_data['itinerary']}:\n" + "\n".join(itinerary)
            else:
                response = "Itinerary is not available."
        else:
            response = "Please mention a city first."

    elif user_message in ['yes', 'yeah', 'yup', 'sure']:
        if session_data["destination"]:
            dest_info = next((d for d in destinations if d["name"] == session_data["destination"]), None)
            itinerary = itineraries.get(session_data["destination"])
            weather = get_weather(session_data["destination"])

            if dest_info:
                months = ", ".join(dest_info["best_time_to_visit"])
                activities = ", ".join(dest_info["special_activities"])
                response = f"Here are the details for {dest_info['name']}:\n"
                response += f"🌤️ Weather: {weather}\n"
                response += f"📅 Best Time to Visit: {months}\n"
                response += f"🎯 Special Activities: {activities}\n"

                if itinerary:
                    response += f"🗺️ 3-Day Itinerary:\n" + "\n".join(itinerary)
                else:
                    response += "\nItinerary is not available."
            else:
                response = "I don't have information about that city."
        else:
            response = "Please tell me which city you want to plan for."

    else:
        response = "🙂 I didn't understand. Please mention a city, region or say 'hello'."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
