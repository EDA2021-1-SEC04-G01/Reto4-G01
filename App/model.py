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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
assert cf
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from math import radians, cos, sin, asin, sqrt

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos
def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'landingPoints': None,
                    'connections': None,
                    'components': None,
                    'paths': None
                    }

        analyzer['landingPoints'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)

        analyzer['pointsInfo'] = m.newMap(numelements=2000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)
        analyzer["countriesInfo"] = m.newMap(numelements=300,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)
        analyzer['countryPoints'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo
def addpointConnection(analyzer,cable):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        origin = cable['\ufefforigin'] + '*' + cable['cable_name']
        destination = cable['destination'] + '*' + cable['cable_name']
        distance= cable["cable_length"]
        distance= distance.replace(',' , '')
        distance= filter(str.isdigit, distance)
        distance= "".join(distance)
        if distance == '':
            distance = 0
        distance= int(distance)
        addPoint(analyzer, origin)
        addPoint(analyzer, destination)
        addConnection(analyzer, origin, destination, distance)
        addlandingPoint(analyzer, cable)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addpointConnection')

def addPoint(analyzer, point):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], point):
            gr.insertVertex(analyzer['connections'], point)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addPoint')

def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer


def addlandingPoint(analyzer, cable):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    entry = m.get(analyzer['landingPoints'], cable['\ufefforigin'])
    if entry is None:
        lstpoints = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstpoints, cable['cable_name'])
        m.put(analyzer['landingPoints'], cable['\ufefforigin'], lstpoints)
    else:
        lstpoints = entry['value']
        info = cable['cable_name']
        if not lt.isPresent(lstpoints, info):
            lt.addLast(lstpoints, info)
    entry2 = m.get(analyzer['landingPoints'], cable['destination'])
    if entry2 is None:
        lstpoints2 = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstpoints2, cable['cable_name'])
        m.put(analyzer['landingPoints'], cable['destination'], lstpoints2)
    else:
        lstpoints2 = entry2['value']
        info = cable['cable_name']
        if not lt.isPresent(lstpoints2, info):
            lt.addLast(lstpoints2, info)  
    return analyzer


def addCableConnections(analyzer):
    """
    Por cada vertice (cada estacion) se recorre la lista
    de rutas servidas en dicha estación y se crean
    arcos entre ellas para representar el cambio de ruta
    que se puede realizar en una estación.
    """
    lststops = m.keySet(analyzer['landingPoints'])
    for key in lt.iterator(lststops):
        lstpoints = m.get(analyzer["landingPoints"], key)['value']
        prevcable = None
        for cable in lt.iterator(lstpoints):
            cable = key + '*' + cable
            if prevcable is not None:
                addConnection(analyzer, prevcable, cable, 0)
                addConnection(analyzer, cable, prevcable, 0)
            prevcable = cable


def addpointInfo(analyzer,point):
    m.put(analyzer["pointsInfo"],point["landing_point_id"],point)
def addcountryInfo(analyzer,country):
    m.put(analyzer["countriesInfo"],country["CountryName"],country)

def addCountryPoints(analyzer, cable):
    country= ""
    origin = cable['\ufefforigin']
    destination = cable['destination']
    oNd= lt.newList()
    lt.addLast(oNd, origin)
    lt.addLast(oNd, destination)
    for i in lt.iterator(oNd):
        ocinfo= (m.get(analyzer["pointsInfo"], i)['value'])["name"]
        times= ocinfo.count(",")
        if times == 1:
            partition= ocinfo.partition(", ")
            country= partition[2]
        elif times == 2:
            partition= ocinfo.partition(", ")
            partition2= partition[2].partition(", ")
            country= partition2[2]
        elif times == 3:
            country = "United States"
        else:
            pass
        if country != "":
            iscountry= m.get(analyzer["countryPoints"], country)
            if iscountry == None:
                lstpoints= lt.newList(cmpfunction=compareroutes)
                vertice= i + '*' + cable['cable_name']
                lt.addLast(lstpoints, vertice)
                m.put(analyzer["countryPoints"],country,lstpoints)
            else:
                lstpoints= iscountry["value"]
                vertice= i + '*' + cable['cable_name'] 
                if not lt.isPresent(lstpoints, vertice):
                    lt.addLast(lstpoints, vertice)

def addCapitalConnections(analyzer):
    
    listpoints= gr.vertices(analyzer['connections'])
    for key in lt.iterator(listpoints):
        number= key.partition("*")
        number= number[0]
        countryinfo= m.get(analyzer["pointsInfo"], number)['value']
        countryncity= countryinfo["name"]
        times= countryncity.count(",")
        if times == 1:
            partition= countryncity.partition(", ")
            country= partition[2]
            city= partition[0]
        elif times == 2:
            partition= countryncity.partition(", ")
            partition2= partition[2].partition(", ")
            country= partition2[2]
            city= partition[0]
        elif times == 3:
            country = "United States"
            city= "Kihei"
        else:
            pass
        if country != "":      
            capital= m.get(analyzer["countriesInfo"], country)['value']
            capital= capital["CapitalName"]
            if capital == city:
                latitude1= float(countryinfo["latitude"])
                longitude1= float(countryinfo["longitude"])
                pointslist= m.get(analyzer["countryPoints"], country)["value"]
                for i in lt.iterator(pointslist):
                    point= i.partition("*")
                    point= point[0]
                    pointInfo= m.get(analyzer["pointsInfo"], point)['value']
                    latitude2= float(pointInfo["latitude"])
                    longitude2= float(pointInfo["longitude"])
                
                    
                    if longitude1 == longitude2 and latitude1 == latitude2:
                        pass
                    else:
                        
                        distance= haversine(longitude1, latitude1, longitude2, latitude2)
                        addConnection(analyzer, key, i, distance)
                        addConnection(analyzer, i, key, distance)    
    return analyzer             

def totalPoints(analyzer):
    """
    Retorna el total de landing points (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])

def totalCountries(analyzer):
    return m.size(analyzer["countriesInfo"])

def connectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    return scc.connectedComponents(analyzer['components'])
# Funciones para creacion de datos

# Funciones de consulta
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
def isscc(analyzer, lp1, lp2):
    ans= scc.stronglyConnected(analyzer["components"], lp1, lp2)
    if ans:
        print("Los dos landing points pertecen al mismo clúster")
    else:
        print("Los dos landing points NO pertecen al mismo clúster")
# Funciones utilizadas para comparar elementos dentro de una lista
def compareStopIds(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1


def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

# Funciones de ordenamiento

