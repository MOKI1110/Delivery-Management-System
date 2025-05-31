# views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Delivery, username
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from geopy.geocoders import Nominatim
import requests
import json # Import json for parsing JSON requests

# Helper function to map stored weight text back to form value
def map_weight_text_to_value(weight_text):
    if not weight_text:
        return ""
    if "500gm - 5kg" in weight_text: return "5005"
    if "5kg - 10kg" in weight_text: return "510"
    if "10kg - 25kg" in weight_text: return "1025"
    return ""

@csrf_exempt
def add_item(request):
    if request.method == 'GET':
        data = 'Sample data from local server'
        return JsonResponse({'info': data})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def home(request):
    return render(request, "home.html")

def user_view_delivery(request):
    names = username.objects.last()
    if names: # Check if a username object exists
        name = names.name
        deliveries = Delivery.objects.filter(recipient_name=name) # Consider if recipient_name is unique or if it should be user_id
    else:
        deliveries = [] # No user, no deliveries
        name = None
    return render(request, "user_view_delivery.html", {'deliveries': deliveries, 'username': name})


def login(request):
    return render(request, "login.html")

def logout(request):
    return render(request, "logout.html")

def dcharge(request):
    return render(request, "dcharge.html")

def user_admin_login(request):
    return render(request, "user_admin_login.html")

def user_home(request):
    return render(request, "user_home.html")

def admin_login(request):
    return render(request, "admin_login.html")

def user_sign_in(request):
    if request.method == "POST":
        name = request.POST.get('username')
        username.objects.create(name=name) # This will create a new entry every time, consider get_or_create or login logic
        return render(request, "user_home.html")
    return render(request, "user_sign_in.html")

def user_sign_up(request):
    return render(request, "user_sign_up.html")

@csrf_exempt
def add_delivery(request):
    initial_data = {}
    error_message = None
    delivery_instance_id = request.session.get('delivery_id')

    if request.method == 'GET':
        if delivery_instance_id:
            try:
                delivery = Delivery.objects.get(id=delivery_instance_id)
                initial_data = {
                    'recipient_name': delivery.recipient_name,
                    'recipient_mobile_number': delivery.recipient_mobile_number,
                    'pickup': delivery.pickup,
                    'destination': delivery.destination,
                    'product_type': delivery.product_type,
                    'weight_value': map_weight_text_to_value(delivery.weight),
                    'distance': str(delivery.distance) if delivery.distance is not None else '',
                    'pickup_coordinates': '', # Not stored on model, will be blank
                    'destination_coordinates': '', # Not stored on model, will be blank
                    'calculate_delivery_charge': f'₹{delivery.delivery_charge:.2f}' if delivery.delivery_charge is not None else '',
                    'hidden_delivery_charge': f'{delivery.delivery_charge:.2f}' if delivery.delivery_charge is not None else ''
                }
            except Delivery.DoesNotExist:
                request.session.pop('delivery_id', None) # Clear invalid ID
        return render(request, 'add_delivery.html', {'initial_data': initial_data})

    if request.method == 'POST':
        # Preserve current form inputs in case of error and re-render
        current_form_data = request.POST.copy()
        initial_data = { # For re-rendering form with current (potentially invalid) values
            'recipient_name': current_form_data.get('recipient_name'),
            'recipient_mobile_number': current_form_data.get('recipient_mobile_number'),
            'pickup': current_form_data.get('pickup'),
            'destination': current_form_data.get('destination'),
            'product_type': current_form_data.get('product_type'),
            'weight_value': current_form_data.get('weight'),
            'distance': current_form_data.get('distance'),
            'pickup_coordinates': current_form_data.get('pickup_coordinates'),
            'destination_coordinates': current_form_data.get('destination_coordinates'),
            'calculate_delivery_charge': current_form_data.get('calculate_delivery_charge'),
            'hidden_delivery_charge': current_form_data.get('hidden_delivery_charge'),
        }

        recipient_name = current_form_data.get('recipient_name')
        recipient_mobile_number = current_form_data.get('recipient_mobile_number')
        pickup = current_form_data.get('pickup')
        destination = current_form_data.get('destination')
        product_type = current_form_data.get('product_type')
        distance_str = current_form_data.get('distance')
        weight_code = current_form_data.get('weight')
        hidden_delivery_charge_str = current_form_data.get('hidden_delivery_charge')

        if not all([recipient_name, recipient_mobile_number, pickup, destination, product_type, distance_str, weight_code]):
            error_message = "All fields except coordinates and delivery cost are required before proceeding."
            return render(request, 'add_delivery.html', {'initial_data': initial_data, 'error': error_message})

        try:
            distance = float(distance_str)
        except (ValueError, TypeError):
            error_message = "Invalid distance. Please click 'Get Coordinates & Distance'."
            return render(request, 'add_delivery.html', {'initial_data': initial_data, 'error': error_message})

        weight_text = ""
        weight_factor = 0
        if weight_code == '5005':
            weight_factor = 1.5
            weight_text = "500gm - 5kg"
        elif weight_code == '510':
            weight_factor = 2
            weight_text = "5kg - 10kg"
        elif weight_code == '1025':
            weight_factor = 3
            weight_text = "10kg - 25kg"
        else:
            error_message = "Invalid weight range selected."
            return render(request, 'add_delivery.html', {'initial_data': initial_data, 'error': error_message})

        delivery_charge = 0
        if hidden_delivery_charge_str: # Trust the charge calculated by JS if available
            try:
                delivery_charge = float(hidden_delivery_charge_str)
            except (ValueError, TypeError):
                delivery_charge = distance * 5 * weight_factor # Fallback: CONSISTENT CALCULATION
        else:
            delivery_charge = distance * 5 * weight_factor # CONSISTENT CALCULATION

        delivery_data = {
            'recipient_name': recipient_name,
            'recipient_mobile_number': recipient_mobile_number,
            'pickup': pickup,
            'destination': destination,
            'product_type': product_type,
            'distance': distance,
            'weight': weight_text,
            'delivery_charge': delivery_charge,
            'status': "Ordered"
        }

        if delivery_instance_id:
            try:
                Delivery.objects.filter(id=delivery_instance_id).update(**delivery_data)
                delivery = Delivery.objects.get(id=delivery_instance_id)
            except Delivery.DoesNotExist:
                request.session.pop('delivery_id', None)
                delivery = Delivery.objects.create(**delivery_data) # Create new if update target lost
        else:
            delivery = Delivery.objects.create(**delivery_data)

        request.session['delivery_id'] = delivery.id
        return redirect(f"{reverse('payment')}?deliveryCharge={delivery.delivery_charge:.2f}")

    return render(request, 'add_delivery.html', {'initial_data': initial_data, 'error': error_message})


def payment(request):
    delivery_id = request.session.get('delivery_id', None)
    if delivery_id is None:
        return redirect(reverse('add_delivery'))

    delivery = Delivery.objects.get(id=delivery_id)

    if request.method == 'POST':
        request.session.pop('delivery_id', None)
        return redirect(reverse('admin_view_delivery'))

    return render(request, 'payment.html', {'delivery': delivery, 'delivery_charge': delivery.delivery_charge})


def admin_home(request):
    return render(request, 'admin_home.html')

def admin_view_delivery(request):
    deliveries = Delivery.objects.all()
    return render(request, 'admin_view_delivery.html', {'deliveries': deliveries})

@csrf_exempt
def calculate_delivery_charge(request):
    if request.method == 'POST':
        distance_str = request.POST.get('distance')
        weight_code = request.POST.get('weight')

        if not distance_str:
            return JsonResponse({'error': 'Distance is required. Click "Get Coordinates & Distance" first.'}, status=400)
        try:
            distance = float(distance_str)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid distance value.'}, status=400)

        weight_factor = 0
        if weight_code == '5005':
            weight_factor = 1.5
        elif weight_code == '510':
            weight_factor = 2
        elif weight_code == '1025':
            weight_factor = 3
        else:
            return JsonResponse({'error': 'Invalid weight range selected.'}, status=400)

        delivery_charge = distance * 5 * weight_factor # CONSISTENT CALCULATION
        return JsonResponse({'delivery_charge': delivery_charge})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def get_trip_details(request): # Renamed from get_coordinates for clarity
    pickup_name = request.GET.get('pickup')
    destination_name = request.GET.get('destination')

    if not pickup_name or not destination_name:
        return JsonResponse({"success": False, "error": "Pickup and destination addresses are required."})

    geolocator = Nominatim(user_agent="my_custom_geocoder_app_v1", timeout=10) # Use a unique user_agent
    
    try:
        pickup_location = geolocator.geocode(pickup_name)
        destination_location = geolocator.geocode(destination_name)
    except Exception as e: # Catch potential geocoding errors (timeout, service unavailable)
        return JsonResponse({"success": False, "error": f"Geocoding error: {str(e)}"})


    if not pickup_location or not destination_location:
        error_message = "Could not find coordinates for:"
        if not pickup_location: error_message += " pickup"
        if not destination_location: error_message += " destination"
        return JsonResponse({"success": False, "error": error_message.replace(":",": ") + "."})

    pickup_coords = (pickup_location.latitude, pickup_location.longitude)
    destination_coords = (destination_location.latitude, destination_location.longitude)

    GRAPH_HOPPER_API_KEY = getattr(settings, 'GRAPH_HOPPER_API_KEY', None)
    if not GRAPH_HOPPER_API_KEY:
        return JsonResponse({"success": False, "error": "GraphHopper API key not configured in settings."})

    url = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{pickup_location.latitude},{pickup_location.longitude}", f"{destination_location.latitude},{destination_location.longitude}"],
        "vehicle": "car",
        "locale": "en",
        "calc_points": "false",
        "key": GRAPH_HOPPER_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10) # Added timeout for robustness
        response.raise_for_status() # Raise HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        if "paths" in data and data["paths"]:
            distance_km = round(data["paths"][0]["distance"] / 1000, 2)
            return JsonResponse({
                "success": True,
                "pickup": pickup_coords,
                "destination": destination_coords,
                "distance_km": distance_km
            })
        elif "message" in data: # Graphhopper often returns error messages in "message"
             return JsonResponse({"success": False, "error": f"GraphHopper: {data['message']}"})
        else:
            return JsonResponse({"success": False, "error": "Distance not available from GraphHopper."})
    except requests.exceptions.RequestException as e: # Catch network/request errors
        return JsonResponse({"success": False, "error": f"API request error: {str(e)}"})
    except Exception as e: # Catch other unexpected errors
        return JsonResponse({"success": False, "error": f"An unexpected error occurred: {str(e)}"})

# New view function to update delivery status
@csrf_exempt # Use csrf_exempt for simplicity in this example, but consider csrf_protect or Django's Form for more security
def update_delivery_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            delivery_id = data.get('delivery_id')
            new_status = data.get('status')

            if not delivery_id or not new_status:
                return JsonResponse({'success': False, 'error': 'Missing delivery_id or status.'}, status=400)

            delivery = Delivery.objects.get(id=delivery_id)
            delivery.status = new_status
            delivery.save()

            return JsonResponse({'success': True})
        except Delivery.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Delivery not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
