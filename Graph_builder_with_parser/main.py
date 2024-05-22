import eel
from Class.graphbuilder import GraphBuilder


@eel.expose
def click_graph_build_button(countries_list: list, first_day, first_month, first_year, last_day, last_month, last_year):

    graph_builder = GraphBuilder(countries_list, first_day, first_month, first_year, last_day, last_month, last_year)
    graph_builder.build_graph()


eel.init('web')  # Инициализация каталога с HTML и CSS
eel.start('main.html', mode='chrome', size=(400, 670))
