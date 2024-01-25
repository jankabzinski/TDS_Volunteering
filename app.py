import folium
from datetime import datetime
import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from geopy.distance import geodesic
import json

from utils import change_session_variable, get_coordinates, get_data,zapisz_mnie, change_view_and_set_chosen_voluteering

# SETUP --------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Volunteering", layout="wide")
data = json.load(open('volunteering.json', encoding='utf-8'))
filtered_data = get_data()

# VIEW CHOICE
CHOOSE_VIEW = 'choose_view'
CURRENT_VIEW_VARIABLE = 'current_view'
ADD_NEW_VOLUNTEERING = 'add_new_volunteering'
EXPANDER_VARIABLE = 'active_expander'
ADD_ME = 'add_me'
SIDEBAR_SEARCH = 'search'
SIDEBAR_RESULTS = 'results'
CHOSEN_VOLUNTEERING_VARIABLE = '-1'

CATEGORIES_ALL_OPTION = 'Wszystkie'
CATEGORIES = [CATEGORIES_ALL_OPTION] + sorted(list(set(record['kategoria'] for record in data)))
SKILLS = sorted([
    "Komunikacja",
    "Empatia",
    "Organizacja",
    "Praca w grupie",
    "Pierwsza pomoc",
    "Edukacja",
    "Ekologia",
    "Media",
    "Opieka nad zwierzętami",
    "Opieka nad dziećmi",
    "Opieka nad starszymi",
    "Plastyka",
    "Gotowanie",
    "Ogrodnictwo"
])

def calculate_score(element, distance, coordinates, date_from, date_to, category, preferences) -> tuple[float, set]:
    # kategoria
    if category != element['kategoria'] and category != CATEGORIES_ALL_OPTION:
      return .0, set()

    # miasto (odległość)
    try:
      distance_calc = geodesic(element['wspolrzedne'], coordinates).kilometers if coordinates is not None else 0
      if distance_calc > distance:
          return .0, set()
    except Exception:
      ...

    # daty
    if date_to < datetime.strptime(element['data_od'], '%Y-%m-%d').date() or date_from > datetime.strptime(element['data_do'], '%Y-%m-%d').date():
        return .0, set()

    # preferencje użytkownika (preferences), preferencje kandydata: element['preferencje_kandydata']
    if not element['preferencje_kandydata'] or not preferences:
      return 1.0, set()

    intersection = set(element['preferencje_kandydata']).intersection(set(preferences))
    return len(intersection) / len(element['preferencje_kandydata']), intersection


def filter_data(filtered_data, city, distance, date_from, date_to, category, preferences):
    filtered_data.clear()
    coords = get_coordinates(city) if city else None
    for el in data:
        score, intersection = calculate_score(el, distance, coords, date_from, date_to, category, preferences)
        if score > .0:
          el['wynik'] = score
          el['intersection'] = intersection
          filtered_data.append(el)

    filtered_data.sort(key=lambda el: -el['wynik'])
    change_session_variable(CURRENT_VIEW_VARIABLE, SIDEBAR_RESULTS)


if __name__ == '__main__':

  # Init session variable
  if EXPANDER_VARIABLE not in st.session_state:
      st.session_state[EXPANDER_VARIABLE] = None
  if CURRENT_VIEW_VARIABLE not in st.session_state:
      st.session_state[CURRENT_VIEW_VARIABLE] = CHOOSE_VIEW
  if CHOSEN_VOLUNTEERING_VARIABLE not in st.session_state:
      st.session_state[CHOSEN_VOLUNTEERING_VARIABLE] = -1

  if st.session_state[CURRENT_VIEW_VARIABLE] == CHOOSE_VIEW:
      st.button("Dodaj nowy wolontariat", on_click=change_session_variable, args = (CURRENT_VIEW_VARIABLE, ADD_NEW_VOLUNTEERING))
      st.button("Uczestnicz w wolontariacie", on_click=change_session_variable, args = (CURRENT_VIEW_VARIABLE, SIDEBAR_SEARCH))


  # SIDEBAR LOGIC ------------------------------------------------------------------------------------------------------

  sidebar  = st.sidebar
  current_sidebar_option = st.session_state[CURRENT_VIEW_VARIABLE]
  map = folium.Map(location=[52.5200, 19.4050], zoom_start=6)

  if current_sidebar_option == SIDEBAR_SEARCH :
      with sidebar.expander("Filtruj"):
        # Filtry
        city_filter = st.text_input('Miejscowość:')
        distance_filter = st.slider('Odległość (km)', 0, 300, 10)
        date_from_filter = st.date_input('Data od:')
        date_to_filter = st.date_input('Data do:')
        category_filter = st.selectbox('Kategoria:', CATEGORIES)
        preference_filter = st.multiselect("Jakie umiejętności chcesz wykorzystać?", SKILLS)
        st.button("Szukaj", on_click=filter_data, args=(filtered_data, city_filter, distance_filter, date_from_filter, date_to_filter, category_filter, preference_filter))

      sidebar.divider()
      for record in data:
          is_expanded = (record['id'] == st.session_state['active_expander'])
          with sidebar.expander(f"{record['nazwa']}", expanded=is_expanded):
              # set_active_expander(record['id'])  # Ustawienie tego expandera jako aktywnego

              st.write(f"Miasto: {record['miasto']}")
              st.write(f"Adres: {record['adres']}")
              st.write(f"Data od: {record['data_od']}")
              st.write(f"Data do: {record['data_do']}")
              st.write(f"Liczba potrzebnych ochotników: {record['liczba_potrzebnych_ochotnikow']}")
              st.write(f"Liczba zapisanych ochotników: {record['liczba_zapisanych_ochotnikow']}")
              st.write(f"Opis: {record['opis']}")
              st.write(f"Preferencje kandydata: {', '.join(record['preferencje_kandydata'])}")
              st.write(f"Kategoria: {record['kategoria']}")

              st.button("Zapisz mnie", type="primary", key=record['id'],  on_click=change_view_and_set_chosen_voluteering, args=(CHOSEN_VOLUNTEERING_VARIABLE ,record['id'],CURRENT_VIEW_VARIABLE, ADD_ME))

      for record in data:
        folium.Marker(location=record['wspolrzedne'], tooltip=record['nazwa']).add_to(map)
      st.button("Powrót", on_click=change_session_variable, args = (CURRENT_VIEW_VARIABLE, CHOOSE_VIEW))
      st_folium(map, width='100%')

  elif current_sidebar_option == SIDEBAR_RESULTS:
      sidebar.button("Powrót", on_click=change_session_variable, args=(CURRENT_VIEW_VARIABLE, SIDEBAR_SEARCH))

      for record in filtered_data:
        is_expanded = (record['id'] == st.session_state['active_expander'])
        with sidebar.expander(f"{record['nazwa']} | score: {record['wynik']}", expanded=is_expanded):
            # set_active_expander(record['id'])  # Ustawienie tego expandera jako aktywnego

            st.write(f"Miasto: {record['miasto']}")
            st.write(f"Adres: {record['adres']}")
            st.write(f"Data od: {record['data_od']}")
            st.write(f"Data do: {record['data_do']}")
            st.write(f"Liczba potrzebnych ochotników: {record['liczba_potrzebnych_ochotnikow']}")
            st.write(f"Liczba zapisanych ochotników: {record['liczba_zapisanych_ochotnikow']}")
            st.write(f"Opis: {record['opis']}")
            st.write(f"Preferencje kandydata: {', '.join(record['preferencje_kandydata'])}")
            st.write(f"Kategoria: {record['kategoria']}")

            st.button("Zapisz mnie", type="primary", key=record['id'],  on_click=change_view_and_set_chosen_voluteering, args=(CHOSEN_VOLUNTEERING_VARIABLE ,record['id'],CURRENT_VIEW_VARIABLE, ADD_ME))

      # przefiltrowane dane
      for record in filtered_data:
        folium.Marker(location=record['wspolrzedne'], tooltip=record['nazwa']).add_to(map)

      st_folium(map, width='100%')

  # ADD NEW VOLUNTEERING LOGIC ------------------------------------------------------------------------------------------------------
  if current_sidebar_option == ADD_NEW_VOLUNTEERING :
      def add_event_record(nazwa, miasto, adres, data_od, data_do, liczba_potrzebnych_ochotnikow, preferencje_kandydata, opis, kategoria):
          if not (nazwa and miasto and adres and data_od and data_do and liczba_potrzebnych_ochotnikow and opis and kategoria and preferencje_kandydata):
              st.warning('Wypełnij wszystkie pola formularza!')
              return

          # Dodaj nowy rekord
          coordinates = get_coordinates(miasto, adres)
          if coordinates is not None:
              record = {
                  'id': len(data) + 1,
                  'nazwa': nazwa,
                  'miasto': miasto,
                  'adres': adres,
                  'data_od': data_od.__str__(),
                  'data_do': data_do.__str__(),
                  'liczba_potrzebnych_ochotnikow': liczba_potrzebnych_ochotnikow,
                  'liczba_zapisanych_ochotnikow': 0,
                  'opis': opis,
                  'preferencje_kandydata': preferencje_kandydata,
                  'kategoria': kategoria,
                  'wspolrzedne': coordinates
              }
              data.append(record)

              # Zapisz zaktualizowane dane do pliku JSON
              with open('volunteering.json', 'w') as file:
                  json.dump(data, file, indent=2)

              st.success('Rekord dodany pomyślnie!')
              st.session_state[CURRENT_VIEW_VARIABLE]=CHOOSE_VIEW
          else:
              st.error('Błędny adres')


      st.button("Powrót", on_click=change_session_variable, args = (CURRENT_VIEW_VARIABLE, CHOOSE_VIEW))
      st.title('Formularz Dodawania Wydarzenia')

      # Formularz
      nazwa = st.text_input('Nazwa wydarzenia:')
      miasto = st.text_input('Miasto:')
      adres = st.text_input('Adres:')
      data_od = st.date_input('Data rozpoczęcia:')
      data_do = st.date_input('Data zakończenia:')
      liczba_potrzebnych_ochotnikow = st.number_input('Liczba potrzebnych ochotników:', min_value=0)
      preferencje_kandydata = st.multiselect("Jakie umiejętności chcesz wykorzystać?", SKILLS)
      opis = st.text_area('Opis wydarzenia:')
      kategoria = st.selectbox('Kategoria:', CATEGORIES)

      st.button('Dodaj rekord',on_click = add_event_record, args=(nazwa, miasto, adres, data_od, data_do, liczba_potrzebnych_ochotnikow, preferencje_kandydata,opis,kategoria))

  # ADD NEW VOLUNTEER LOGIC ------------------------------------------------------------------------------------------------------
  if current_sidebar_option == ADD_ME:
      st.button("Powrót", on_click=change_session_variable, args = (CURRENT_VIEW_VARIABLE, SIDEBAR_SEARCH))
      imie = st.text_input('Imię:')
      nazwisko = st.text_input('Nazwisko:')
      wiek = st.number_input('Wiek:', min_value=0)
      st.button("Zapisz mnie!", on_click= zapisz_mnie, args=(data, st.session_state[CHOSEN_VOLUNTEERING_VARIABLE], CURRENT_VIEW_VARIABLE, SIDEBAR_SEARCH))