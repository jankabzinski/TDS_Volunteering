import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from streamlit_modal import Modal
# CONFIG ------------------------------------------------------------------

st.set_page_config(page_title="Volunteering", layout="wide")

data = json.load(open('volunteering.json', encoding='utf-8'))
SEARCH_SIDEBAR = 'search'
RESULTS_SIDEBAR = 'results'

# SIDEBAR -----------------------------------------------------------------

sidebar  = st.sidebar

# Inicjalizacja zmiennej sesji do przechowywania aktywnego expandera
if 'active_expander' not in st.session_state:
    st.session_state['active_expander'] = None

# Funkcja do zmiany aktywnego expandera
def set_active_expander(expander_id):
    st.session_state['active_expander'] = expander_id


# Inicjalizacja zmiennej sesji
if 'current_option' not in st.session_state:
    st.session_state['current_option'] = SEARCH_SIDEBAR

# Funkcje do zmiany zawartości
def show_home():
    st.session_state['current_option'] = SEARCH_SIDEBAR

def show_option1(city, location, distance, date_from, date_to, category, preferences):
    st.session_state['current_option'] = RESULTS_SIDEBAR

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(f"{city_filter}")
    if location:
        return location.latitude, location.longitude
    else:
        st.error(f"Nie można znaleźć współrzędnych dla miejscowości: {city_name}")
        return None
# Logika wyświetlania zawartości

current_option = st.session_state['current_option']

if current_option == SEARCH_SIDEBAR:
    with sidebar.expander("Filtruj"):
      # Filtry
      city_filter = st.text_input('Miasto:')
      location_filter = st.text_input('Lokalizacja (np. Warszawa):')
      distance_filter = st.slider('Odległość (km)', 0, 100, 10)
      date_from_filter = st.date_input('Data od:')
      date_to_filter = st.date_input('Data do:')
      category_filter = st.selectbox('Kategoria:', ['wszystkie'] + list(set(record['kategoria'] for record in data)))
      preference_filter = st.multiselect("Jakie umiejętności chcesz wykorzystać?", ['uwu', 'owo', 'dudu'])

      # Jeśli podano nazwę miejscowości, uzyskaj współrzędne
      location_coords = None
      if location_filter:
          location_coords = get_coordinates(location_filter)
          st.write(location_coords)

      # Dodaj markery dla każdego rekordu w danych
      for record in data:
          # Filtruj po mieście
          if city_filter and record['miasto'].lower() != city_filter.lower():
              continue

          # Filtruj po lokalizacji i odległości
          if location_coords:
              record_coords = record['wspolrzedne']
              distance = geodesic(location_coords, record_coords).kilometers
              if distance > distance_filter:
                  continue

          # Filtruj po dacie
          if date_from_filter and record['data_od'] < str(date_from_filter):
              continue
          if date_to_filter and record['data_do'] > str(date_to_filter):
              continue

          # Filtruj po kategorii
          if category_filter != 'wszystkie' and record['kategoria'] != category_filter:
              continue

          # Filtruj po preferencjach kandydata
          if preference_filter and not any(pref.lower() in record['preferencje_kandydata'].lower() for pref in preference_filter):
              continue
      st.button("Szukaj", on_click=show_option1, args=(city_filter, location_filter, distance_filter, date_from_filter, date_to_filter, category_filter, preference_filter))

    sidebar.divider()
    for record in data:
        is_expanded = (record['id'] == st.session_state['active_expander'])
        with sidebar.expander(f"{record['nazwa']}", expanded=is_expanded):
            set_active_expander(record['id'])  # Ustawienie tego expandera jako aktywnego

            st.write(f"Miasto: {record['miasto']}")
            st.write(f"Adres: {record['adres']}")
            st.write(f"Data od: {record['data_od']}")
            st.write(f"Data do: {record['data_do']}")
            st.write(f"Liczba potrzebnych ochotników: {record['liczba_potrzebnych_ochotnikow']}")
            st.write(f"Liczba zapisanych ochotników: {record['liczba_zapisanych_ochotnikow']}")
            st.write(f"Opis: {record['opis']}")
            st.write(f"Preferencje kandydata: {record['preferencje_kandydata']}")
            st.write(f"Kategoria: {record['kategoria']}")
elif current_option == RESULTS_SIDEBAR:
    sidebar.button("Powrót", on_click=show_home)
    sidebar.button("Filtruj")

    # przefiltrowane dane


# MAP ---------------------------------------------------------------------

# Create a map centered around a location
map = folium.Map(location=[52.5200, 19.4050], zoom_start=6)

for record in data:
    folium.Marker(location=record['wspolrzedne'], tooltip=record['nazwa']).add_to(map)


# Display the map in Streamlit
st_folium(map, width='100%')