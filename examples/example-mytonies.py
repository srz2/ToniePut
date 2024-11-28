from tonie_api.api import TonieAPI

username = ''
password = ''

print('Starting ToniePut')
api = TonieAPI(username, password)
households = api.get_households()
print('Hello from tonies!')
household_count = len(households)
print(f'Found {household_count} households')
if (household_count <= 0):
    print('No houses found...')
    exit(0)
    
# Retrieve first house
house = households[0]
id = house.id
name = house.name
print(f'First house is {name} ({id})')

# Get Creative Tonies
creative_tonies = api.get_all_creative_tonies_by_household(house)
creative_tonies_count = len(creative_tonies)
print(f'Found {creative_tonies_count} creative tonies')
