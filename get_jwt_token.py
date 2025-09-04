#!/usr/bin/env python3
"""
Utility script to get JWT token for testing staff chat interface
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_jwt_token():
    """Get JWT token by signing in a user"""
    
    # Get Supabase credentials
    url = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
    key = os.getenv("EXPO_PUBLIC_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Error: Missing Supabase environment variables")
        print("Please set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY")
        return None
    
    try:
        # Create Supabase client
        supabase: Client = create_client(url, key)
        
        print("🔐 Supabase JWT Token Generator for Staff Chat Testing\n")
        
        # Get user credentials
        print("Enter your credentials to get JWT token:")
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if not email or not password:
            print("❌ Email and password are required")
            return None
        
        print("\n🔄 Authenticating...")
        
        # Sign in user
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user and auth_response.session:
            jwt_token = auth_response.session.access_token
            user_id = auth_response.user.id
            
            print("✅ Authentication successful!")
            print(f"👤 User ID: {user_id}")
            print(f"📧 Email: {auth_response.user.email}")
            print("\n🎯 JWT Token for API testing:")
            print("=" * 80)
            print(jwt_token)
            print("=" * 80)
            
            print("\n📋 How to use this token:")
            print("1. Copy the JWT token above")
            print("2. Use it in API requests with Authorization header:")
            print(f"   Authorization: Bearer {jwt_token}")
            print("\n🧪 Test with curl:")
            print(f'curl -X POST http://localhost:5000/api/staff/chat \\')
            print(f'  -H "Content-Type: application/json" \\')
            print(f'  -H "Authorization: Bearer {jwt_token}" \\')
            print(f'  -d \'{{"message": "How many bookings today?", "restaurant_id": "your-restaurant-id"}}\'')
            
            # Save to file for easy access
            with open('jwt_token.txt', 'w') as f:
                f.write(jwt_token)
            print(f"\n💾 Token saved to: jwt_token.txt")
            
            return jwt_token
            
        else:
            print("❌ Authentication failed - check your credentials")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def get_restaurant_id(supabase_client, jwt_token):
    """Helper to get restaurant ID for staff testing"""
    try:
        # Set the JWT token for authenticated requests
        supabase_client.auth.set_session(jwt_token, None)
        
        print("\n🏪 Looking up restaurants for testing...")
        
        # Get restaurants
        restaurants = supabase_client.table("restaurants").select("id, name").limit(5).execute()
        
        if restaurants.data:
            print("\n🏨 Available restaurants for testing:")
            for i, restaurant in enumerate(restaurants.data, 1):
                print(f"{i}. {restaurant['name']} (ID: {restaurant['id']})")
            
            print(f"\n💡 Use any restaurant ID above in your staff chat requests")
            print(f"   Example restaurant_id: {restaurants.data[0]['id']}")
        else:
            print("⚠️  No restaurants found in database")
            
    except Exception as e:
        print(f"⚠️  Could not fetch restaurants: {str(e)}")

if __name__ == "__main__":
    print("🚀 Getting JWT token for staff chat interface testing...\n")
    
    token = get_jwt_token()
    
    if token:
        print("\n" + "="*80)
        print("🎉 SUCCESS! You now have a JWT token for testing.")
        print("="*80)
        
        # Try to get restaurant info for convenience
        try:
            url = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
            key = os.getenv("EXPO_PUBLIC_SUPABASE_ANON_KEY")
            supabase = create_client(url, key)
            get_restaurant_id(supabase, token)
        except:
            pass
            
    else:
        print("\n❌ Failed to get JWT token")
        sys.exit(1)
