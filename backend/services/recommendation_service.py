"""
Doctor and Hospital Recommendation Service
Uses Google Maps API for location-based search
"""
import googlemaps
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthcareRecommendationService:
    """Find nearby doctors and hospitals"""
    
    def __init__(self, api_key=None):
        """
        Initialize recommendation service
        
        Args:
            api_key: Google Maps API key
        """
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if self.api_key:
            self.gmaps = googlemaps.Client(key=self.api_key)
        else:
            logger.warning("Google Maps API key not provided")
            self.gmaps = None
    
    def find_nearby_cardiologists(self, latitude, longitude, radius=5000, limit=10):
        """
        Find nearby cardiologists
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            radius: Search radius in meters (default: 5km)
            limit: Maximum number of results
            
        Returns:
            list: List of cardiologist information
        """
        if not self.gmaps:
            return self._get_mock_cardiologists()
        
        try:
            # Search for cardiologists
            places_result = self.gmaps.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                keyword='cardiologist',
                type='doctor'
            )
            
            cardiologists = []
            for place in places_result.get('results', [])[:limit]:
                cardiologist = self._format_place_data(place, latitude, longitude)
                cardiologists.append(cardiologist)
            
            logger.info(f"Found {len(cardiologists)} cardiologists")
            return cardiologists
            
        except Exception as e:
            logger.error(f"Error finding cardiologists: {e}")
            return []
    
    def find_nearby_hospitals(self, latitude, longitude, radius=10000, limit=10):
        """
        Find nearby hospitals with cardiology departments
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            radius: Search radius in meters (default: 10km)
            limit: Maximum number of results
            
        Returns:
            list: List of hospital information
        """
        if not self.gmaps:
            return self._get_mock_hospitals()
        
        try:
            # Search for hospitals
            places_result = self.gmaps.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                keyword='cardiology hospital',
                type='hospital'
            )
            
            hospitals = []
            for place in places_result.get('results', [])[:limit]:
                hospital = self._format_place_data(place, latitude, longitude)
                hospitals.append(hospital)
            
            logger.info(f"Found {len(hospitals)} hospitals")
            return hospitals
            
        except Exception as e:
            logger.error(f"Error finding hospitals: {e}")
            return []
    
    def get_place_details(self, place_id):
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Places ID
            
        Returns:
            dict: Detailed place information
        """
        if not self.gmaps:
            return {}
        
        try:
            result = self.gmaps.place(place_id)
            return result.get('result', {})
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return {}
    
    def _format_place_data(self, place, user_lat, user_lng):
        """
        Format place data for response
        
        Args:
            place: Google Places API result
            user_lat: User's latitude
            user_lng: User's longitude
            
        Returns:
            dict: Formatted place data
        """
        location = place.get('geometry', {}).get('location', {})
        
        # Calculate distance
        distance = self._calculate_distance(
            user_lat, user_lng,
            location.get('lat', 0), location.get('lng', 0)
        )
        
        return {
            "place_id": place.get('place_id'),
            "name": place.get('name'),
            "address": place.get('vicinity'),
            "rating": place.get('rating', 0),
            "total_ratings": place.get('user_ratings_total', 0),
            "distance_km": round(distance, 2),
            "latitude": location.get('lat'),
            "longitude": location.get('lng'),
            "is_open": place.get('opening_hours', {}).get('open_now', None),
            "types": place.get('types', []),
        }
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates (Haversine formula)
        
        Returns:
            float: Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance
    
    def get_recommendations_by_risk(self, risk_level, latitude, longitude):
        """
        Get recommendations based on risk level
        
        Args:
            risk_level: 'Low', 'Medium', or 'High'
            latitude: User's latitude
            longitude: User's longitude
            
        Returns:
            dict: Recommendations with urgency level
        """
        recommendations = {
            "urgency": "",
            "message": "",
            "cardiologists": [],
            "hospitals": [],
            "actions": []
        }
        
        if risk_level == "High":
            recommendations["urgency"] = "URGENT"
            recommendations["message"] = "⚠️ High risk detected. Please consult a cardiologist immediately."
            recommendations["cardiologists"] = self.find_nearby_cardiologists(
                latitude, longitude, radius=5000, limit=5
            )
            recommendations["hospitals"] = self.find_nearby_hospitals(
                latitude, longitude, radius=10000, limit=5
            )
            recommendations["actions"] = [
                "Schedule appointment within 24-48 hours",
                "Visit emergency if experiencing chest pain",
                "Carry medical reports to consultation"
            ]
            
        elif risk_level == "Medium":
            recommendations["urgency"] = "MODERATE"
            recommendations["message"] = "Moderate risk detected. Consultation recommended within 1-2 weeks."
            recommendations["cardiologists"] = self.find_nearby_cardiologists(
                latitude, longitude, radius=10000, limit=5
            )
            recommendations["actions"] = [
                "Schedule consultation within 2 weeks",
                "Monitor symptoms regularly",
                "Follow lifestyle modifications"
            ]
            
        else:  # Low risk
            recommendations["urgency"] = "LOW"
            recommendations["message"] = "Low risk. Continue healthy lifestyle and regular checkups."
            recommendations["actions"] = [
                "Annual health checkup recommended",
                "Maintain healthy diet and exercise",
                "Monitor blood pressure monthly"
            ]
        
        return recommendations
    
    def _get_mock_cardiologists(self):
        """Mock data for testing without API key"""
        return [
            {
                "name": "Dr. Rajesh Kumar - Cardiologist",
                "address": "Apollo Hospital, Delhi",
                "rating": 4.5,
                "total_ratings": 120,
                "distance_km": 2.3,
                "is_open": True
            },
            {
                "name": "Dr. Priya Sharma - Heart Specialist",
                "address": "Fortis Hospital, Mumbai",
                "rating": 4.7,
                "total_ratings": 95,
                "distance_km": 3.1,
                "is_open": True
            }
        ]
    
    def _get_mock_hospitals(self):
        """Mock data for testing without API key"""
        return [
            {
                "name": "Apollo Hospital - Cardiology",
                "address": "Sarita Vihar, Delhi",
                "rating": 4.6,
                "total_ratings": 450,
                "distance_km": 2.5,
                "is_open": True
            },
            {
                "name": "Fortis Escorts Heart Institute",
                "address": "Okhla Road, Delhi",
                "rating": 4.8,
                "total_ratings": 680,
                "distance_km": 4.2,
                "is_open": True
            }
        ]


# Example usage
if __name__ == "__main__":
    service = HealthcareRecommendationService()
    
    # Test with Delhi coordinates
    lat, lng = 28.6139, 77.2090
    
    recommendations = service.get_recommendations_by_risk("High", lat, lng)
    print(recommendations)
