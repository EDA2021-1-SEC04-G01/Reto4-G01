"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import model
import csv


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros

def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer



# Funciones para la carga de datos
def loadServices(analyzer, connections, points, countries):
    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de estaciones que
    pertenecen al mismo servicio y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
   
    
    pointsfile = cf.data_dir + points
    input_pfile = csv.DictReader(open(pointsfile, encoding="utf-8"),
                                delimiter=",")
    for point in input_pfile:
        id= point["landing_point_id"]
        name= point["name"]
        latitude= point["latitude"]
        longitude= point["longitude"]
        model.addpointInfo(analyzer,point)
        break
    for point in input_pfile:    
        model.addpointInfo(analyzer,point)
        
    countriesfile = cf.data_dir + countries
    input_cofile = csv.DictReader(open(countriesfile, encoding="utf-8"),
                                delimiter=",")
    for country in input_cofile:
        model.addcountryInfo(analyzer,country)
        countryname= country["CountryName"]
        population= country["Population"]
        users= country["Internet users"]


    connectionsfile = cf.data_dir + connections
    input_cfile = csv.DictReader(open(connectionsfile, encoding="utf-8"),
                                delimiter=",")
    for cable in input_cfile:
        model.addpointConnection(analyzer,cable)
        model.addCountryPoints(analyzer, cable)  
    model.addCableConnections(analyzer)
    model.addCapitalConnections(analyzer)
    model.createCapital(analyzer)
    
    return analyzer, id, name, latitude, longitude, countryname, population, users

def totalPoints(analyzer):
    """
    Total de landing points
    """
    return model.totalPoints(analyzer)


def totalConnections(analyzer):
    """
    Total de conexiones entre los landing points
    """
    return model.totalConnections(analyzer)

def connectedComponents(analyzer):
    """
    Numero de componentes fuertemente conectados
    """
    return model.connectedComponents(analyzer)

def mostConnections(analyzer):
    return model.mostConnections(analyzer)
# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo
