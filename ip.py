import requests

def get_ip_location(ip):
    response = requests.get(f'http://ip-api.com/json/{ip}')
    data = response.json()
    return data

ip = input("Enter IP address: ")
location_data = get_ip_location(ip)

print("IP Location Data:")
print(f"Country: {location_data['country']}")
print(f"City: {location_data['city']}")
print(f"Region: {location_data['regionName']}")
print(f"Latitude: {location_data['lat']}")
print(f"Longitude: {location_data['lon']}")
print(f"ISP: {location_data['isp']}")