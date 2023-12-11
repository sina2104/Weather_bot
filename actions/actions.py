# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from bs4 import BeautifulSoup as our_BS
import requests
request = requests.get('https://www.yandex.com/weather/segment/details?offset=0&lat=55.753215&lon=37.622504&geoid=213&limit=10', headers = {'User-Agent':'Mozilla/5.0'})
soup = our_BS(request.content, 'lxml')


class ActionTempTomorrow(Action):

    def name(self) -> Text:
        return "action_weather_temps_tomorrow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ''
        cards = soup.select('.card:not(.adv)')
        correct_cards = []
        for i in range(len(cards)):
            if ' '.join([i.text for i in cards[i].select('[class$=number],[class$=month]')]) != '':
                correct_cards.append(cards[i])
        card = correct_cards[1]
        date = ' '.join([i.text for i in card.select('[class$=number],[class$=month]')])
        dispatcher.utter_message(text=f'Tomorrow is {date.split()[1]} {date.split()[0]}:')
        temps = list(zip(
                        [i.text for i in card.select('.weather-table__daypart')]
                        , [i.text for i in card.select('.weather-table__body-cell_type_feels-like .temp__value')]
                        , [i.text for i in card.select('.weather-table__body-cell_type_humidity')] 
                        , [i.text for i in card.select('.weather-table__body-cell_type_condition')]
                        , [i.text for i in card.select('.weather-table__body-cell_type_wind .wind-speed')]
                        ))  

        for i in temps:
            if i[0] != 'day':
                message += f'{i[0]}: {i[1]}° |Humidity:{i[2]} |Condition: {i[3]} |Wind speed:{i[4]} m/c\n'
        dispatcher.utter_message(text=message)

        return []


class ActionTempInNDays(Action):

    def name(self) -> Text:
        return "action_weather_temps_in_N_days"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract the value of the 'N' entity from the user's message
        n_value = tracker.latest_message['entities'][0]['value']
        if n_value:
            # Use the 'N' value in your logic
            try:
                n_days = int(n_value)
                if 10 > n_days > 0:
                    # Your logic to fetch weather information for N days
                    response_message = f"Fetching weather information for {n_days} days from now..."
                    dispatcher.utter_message(text=response_message)
                    message = ''
                    cards = soup.select('.card:not(.adv)')
                    correct_cards = []
                    for i in range(len(cards)):
                        if ' '.join([i.text for i in cards[i].select('[class$=number],[class$=month]')]) != '':
                            correct_cards.append(cards[i])
                    card = correct_cards[n_days]
                    date = ' '.join([i.text for i in card.select('[class$=number],[class$=month]')])
                    dispatcher.utter_message(text=f'{n_days} from today will be {date.split()[1]} {date.split()[0]}:')
                    temps = list(zip(
                                    [i.text for i in card.select('.weather-table__daypart')]
                                    , [i.text for i in card.select('.weather-table__body-cell_type_feels-like .temp__value')]
                                    , [i.text for i in card.select('.weather-table__body-cell_type_humidity')] 
                                    , [i.text for i in card.select('.weather-table__body-cell_type_condition')]
                                    , [i.text for i in card.select('.weather-table__body-cell_type_wind .wind-speed')]
                                    ))  

                    for i in temps:
                        if i[0] != 'day':
                            message += f'{i[0]}: {i[1]}° |Humidity:{i[2]} |Condition: {i[3]} |Wind speed:{i[4]} m/c\n'
                    dispatcher.utter_message(text=message)
                elif n_days < 0:
                    dispatcher.utter_message(text="Please provide a valid positive number for days.")
                else:
                    dispatcher.utter_message(text="I can not predict the weather above 10 days :(")
            except ValueError:
                dispatcher.utter_message(text="Invalid value for number of days. Please provide a valid number.")
        else:
            dispatcher.utter_message(text="I couldn't extract the number of days. Please try again.")

        return []


class ActionTempsWeek(Action):

    def name(self) -> Text:
        return "action_weather_temps_next_week"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text=f'Here is the forecast for the whole week ahead of us:')
        days = 0
        message = ''
        for card in soup.select('.card:not(.adv)'):
            date = ' '.join([i.text for i in card.select('[class$=number],[class$=month]')])
            if date != '':
                message += f'{date}\n'
            temps = list(zip(
                            [i.text for i in card.select('.weather-table__daypart')]
                            , [i.text for i in card.select('.weather-table__body-cell_type_feels-like .temp__value')]
                            , [i.text for i in card.select('.weather-table__body-cell_type_humidity')] 
                            , [i.text for i in card.select('.weather-table__body-cell_type_condition')]
                            , [i.text for i in card.select('.weather-table__body-cell_type_wind .wind-speed')]
                        ))   
            for i in temps:
                if i[0] != 'day':
                    message += f'{i[0]}: {i[1]}° |Humidity:{i[2]} |Condition: {i[3]} |Wind speed:{i[4]} m/c\n'
            if days > 7:
                break
            days += 1
        dispatcher.utter_message(text=message)
        return []
