# What Happens in Vegas

**Smart, Social, and Seamless Travel – Powered by AI, Designed for You.**

## Project Overview
What Happens in Vegas is a next-generation travel planning platform that enhances trip experiences through AI-powered itinerary generation and seamless group coordination.

## Architecture
- **Frontend (UI-Swift Code):** Developed in **Swift** for an intuitive iOS experience.
- **Backend (trip_planner_server):** Built using **Python (Flask API)** to handle AI-driven itinerary generation, geolocation services, and real-time coordination.

## Core Features
- **AI-Powered Itinerary Generator:** Uses **Llama 3.1** to create personalized trip plans based on destination, duration, interests, budget, and group preferences.
- **Collaborative Planning:** Enables users to vote on activities, ensuring group consensus in itinerary creation.
- **Hyperlocal Recommendations:** AI-driven suggestions for restaurants, attractions, and deals based on real-time location data.
- **Location Sharing & Coordination:** Helps groups find meeting points and stay connected throughout their trip.
- **Integrated Ride Sharing:** Schedules rides for the group and provides real-time location tracking.
- **Unified Photo Album:** Generates a **trip-specific QR code** for users to upload and access photos in shared **Google Cloud storage**.
- **Seamless Communication:** Built-in chat functionality with optional **WhatsApp integration** for easy messaging.

## Technology Stack
- **Frontend:** Swift (iOS Development)
- **Backend:** Python (Flask API)
- **AI & ML:** Llama 3.1 for itinerary generation and travel insights
- **Geolocation:** Google Maps API for real-time tracking and geofencing
- **Cloud Storage:** Google Cloud for photo sharing and trip data storage

## Backend Requirements
To run the Flask server, install the following dependencies:

### Required Python Packages:
```bash
pip install flask googlemaps geopy qrcode google-auth-oauthlib google-auth google-auth-httplib2 google-auth google-auth-oauthlib google-auth google-api-python-client requests
```

### Required Files:
- **`credentials.json`**: Google API credentials for Drive integration.
- **API Keys**:
  - `API_KEY`: Google Maps API Key.
  - `YELP_API_KEY`: Yelp API Key for restaurant recommendations.

## Deployment
- The **iOS app** is built in **Swift** and interacts with the **Flask backend** via REST API.
- AI-generated itineraries and recommendations are processed server-side and sent to the app.
- Google Cloud handles **photo uploads and trip data storage** for seamless access.

## Future Enhancements
- **Augmented Reality (AR) Travel Guides:** Interactive travel insights using AR overlays.
- **Gamification Features:** Challenges, leaderboards, and rewards for exploring destinations.
- **Smart Budgeting Tools:** AI-powered expense tracking and budgeting assistance.
- **Social Media Integration:** Seamless sharing of trip moments to Instagram and Snapchat.

This project revolutionizes travel planning by combining **AI-driven insights, real-time collaboration, and intuitive user experiences** to make trips smarter, more social, and completely seamless. 🚀

