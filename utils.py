import streamlit as st
from typing import Any
from geopy.geocoders import Nominatim
import json

geolocator = Nominatim(user_agent="my_geocoder")

@st.cache_resource
def get_data():
    return []

def change_session_variable(session_var_name: str, session_var_value: Any) -> None:
    st.session_state[session_var_name] = session_var_value


def get_coordinates(city_name: str, street: str = '') -> tuple[float, float] | None:
    location = geolocator.geocode(f"{city_name}, {street} Polska")
    if location:
        return location.latitude, location.longitude
    else:
        # st.error(f"Nie można znaleźć współrzędnych dla miejscowości: {city_name}")
        return None

def zapisz_mnie(data, id, session_var, session_var_target_value):
    for i in range(len(data)):
        if data[i]['id'] == id:
            data[i]['liczba_zapisanych_ochotnikow'] += 1

            # Zapisz zaktualizowane dane do pliku JSON
            with open('volunteering.json', 'w') as file:
                json.dump(data, file, indent=2)
            change_session_variable(session_var, session_var_target_value)
            return

    raise Exception("XD")

def change_view_and_set_chosen_voluteering(variable_record_chosen:str, id:int, cur_view:str, new_view:str):
    st.session_state[variable_record_chosen] = id
    st.session_state[cur_view]=new_view


