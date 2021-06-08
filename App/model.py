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


from DISClib.ADT.indexminpq import size
from DISClib.DataStructures.chaininghashtable import get, keySet
import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
assert cf
from DISClib.ADT.graph import edges, gr
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import bellmanford as bf
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from math import radians, cos, sin, asin, sqrt
from DISClib.Algorithms.Graphs import prim
from DISClib.Algorithms.Graphs import dfo
import json
from urllib.request import urlopen
import re
import urllib3
from DISClib.ADT import stack
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
        analyzer['cableinfo'] = m.newMap(numelements=14000,
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
        m.put(analyzer["cableinfo"], origin, cable)
        m.put(analyzer["cableinfo"], destination, cable) 
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
        addConnection(analyzer, destination, origin, distance)
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
  
def createCapital(analyzer):
    countries= m.keySet(analyzer["countryPoints"])
    for i in lt.iterator(countries):
        info= m.get(analyzer["countriesInfo"], i)["value"]
        capital= info["CapitalName"]
        lat1= float(info["CapitalLatitude"])
        lon1= float(info["CapitalLongitude"])
        gr.insertVertex(analyzer["connections"], capital)
        lstpoints= m.get(analyzer["countryPoints"], i)["value"]
        for k in lt.iterator(lstpoints):
            point= k.partition("*")
            point= point[0]
            cityinfo= m.get(analyzer["pointsInfo"], point)["value"]
            lat2= float(cityinfo["latitude"])
            lon2= float(cityinfo["longitude"])
            distance= haversine(lon1, lat1, lon2, lat2)
            addConnection(analyzer, capital, k, distance)
            addConnection(analyzer, k, capital, distance)


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


def mostConnections(analyzer):
    """
    Retorna la estación que sirve a mas rutas.
    Si existen varias rutas con el mismo numero se
    retorna una de ellas
    """
    lstvert = m.keySet(analyzer['landingPoints'])
    maxvert = None
    maxdeg = 0
    iteration= 0
    lstPoints= {}
    while iteration < 5:
        for vert in lt.iterator(lstvert):
            lstroutes = m.get(analyzer['landingPoints'], vert)['value']
            degree = lt.size(lstroutes)
            if(degree > maxdeg) and vert not in lstPoints:
                maxvert = vert
                maxdeg = degree
        lstPoints[maxvert]= maxdeg
        iteration +=1
        maxvert= None
        maxdeg= 0           
    print("Landing points con mas cables conectados: ")
    count= 1
    for i in lstPoints.keys():
       info= m.get(analyzer['pointsInfo'], i)["value"]
       print("Top "+str(count)+"\nNombre y pais: "+ info["name"]+"\nIdentificador: "+i)
       print("Total de cables conectados: "+str(lstPoints[i]))
       count +=1

def minimumPath(analyzer, origin, dest):
    orndest= []
    orndest.append(origin)
    orndest.append(dest)
    count= 1
    itcount= 0
    for origin in orndest:
        originPoint= None
        country= m.get(analyzer["countriesInfo"], origin)['value']
        capital= country["CapitalName"]
        lstpoints= m.get(analyzer["countryPoints"], origin)['value']
        for i in lt.iterator(lstpoints):
            key= i.partition("*")
            key= key[0]
            countryinfo= m.get(analyzer["pointsInfo"], key)['value']
            countryncity= countryinfo["name"]
            times= countryncity.count(",")
            if times == 1:
                partition= countryncity.partition(", ")
                city= partition[0]
            elif times == 2:
                partition= countryncity.partition(", ")       
                city= partition[0]
            elif times == 3:
                city= "Kihei"
            else:
                pass
            if city == capital:
                originPoint= i
                break
        if count == 1:
           if originPoint== None:
               originPoint= lt.lastElement(lstpoints)
           analyzer['paths'] = djk.Dijkstra(analyzer['connections'], originPoint)
        else:
            if originPoint== None:
               originPoint= lt.lastElement(lstpoints)
            path = djk.pathTo(analyzer['paths'], originPoint)
        count+=1
    
    return path

def minimumExpansion(analyzer):
    
    min= prim.PrimMST(analyzer["connections"])
    distance=prim.weightMST(analyzer["connections"],min )
    distance= round(distance, 2)
    nodes = min["mst"] ["size"]
    print("El total de nodos conectados a la red de expansion minima es: "+str(nodes))
    print("La distancia total (en km) de la red de expansion minima es: "+str(distance))
    
    
def failLanding(analyzer,lanname): 
    countrylist= []
    countrydict= {}   
    keys= m.keySet(analyzer["pointsInfo"])
    for key in lt.iterator(keys):
        lanp= m.get(analyzer["pointsInfo"], key)["value"]
        name= lanp["name"]
        times= name.count(",")
        if times == 1:
            partition= name.partition(", ")
            city= partition[0]
        elif times == 2:
            partition= name.partition(", ")       
            city= partition[0]
        elif times == 3:
            city= "Kihei"
        else:
            pass
        if city == lanname:
            lat1= float(lanp["latitude"])
            lon1= float(lanp["longitude"])
            cables = m.get(analyzer["landingPoints"], key)["value"]
            for i in lt.iterator(cables):
                vertice= key + '*' + i
                lstpoints= gr.adjacents(analyzer["connections"], vertice)
                for j in lt.iterator(lstpoints):
                    countrykeys= m.keySet(analyzer["countryPoints"])
                    for k in lt.iterator(countrykeys):
                        pointslist= m.get(analyzer["countryPoints"], k)["value"]
                        isin= lt.isPresent(pointslist, j)
                        if isin != 0 and k not in countrylist  :
                            countrylist.append(k)
    for i in countrylist:
        info= m.get(analyzer["countriesInfo"],i)["value"]
        lat2= float(info["CapitalLatitude"])
        lon2= float(info["CapitalLongitude"])
        distance= haversine(lon1, lat1, lon2, lat2)
        countrydict[i]= distance
    print("La cantidad de paises afectados es: "+str(len(countrylist)))
    print("Pasises afectados:")
    while countrydict:       
        longest= max(countrydict, key=countrydict.get)
        print(longest+" ("+str(countrydict[longest])+")")
        del countrydict[longest]

def maxBb(analyzer, country, cable):
    pointslist= []
    countrydict= {}
    keys= m.keySet(analyzer["landingPoints"])
    for i in lt.iterator(keys):
        lst= m.get(analyzer["landingPoints"], i)["value"]
        isit= lt.isPresent(lst, cable)
        if isit != 0:
            point= i+"*"+cable
            pointslist.append(point)
    countries= m.keySet(analyzer["countryPoints"])
    for i in pointslist:
        for j in lt.iterator(countries):
            pointslt= m.get(analyzer["countryPoints"], j)["value"]
            isin= lt.isPresent(pointslt, i)
            if isin != 0 and j not in countrydict and j != country:
                countrydict[j]= i
        
    bb= m.get(analyzer["cableinfo"], pointslist[0]) ["value"]
    bb= float(bb["capacityTBPS"])*1000000
    for i in countrydict.keys():
        info= m.get(analyzer["countriesInfo"],i)["value"]
        users= float(info["Internet users"])
        ab= round((bb/users), 3)
        print(i+"-se puede asegurar un ancho de banda de "+str(ab)+" Mbps")

def ipdistance(cont,ip1,ip2):
    url = 'http://ip-api.com/json/' + ip1
    response = urlopen(url)
    data = json.load(response)
    country1= data["country"]
    url = 'http://ip-api.com/json/' + ip2
    response = urlopen(url)
    data = json.load(response)
    country2= data["country"]
    path= minimumPath(cont, country1, country2)
    if path is not None:
        pathlen = stack.size(path)
        while (not stack.isEmpty(path)):
            stop = stack.pop(path)
            print(stop)
    else:
        print('No hay camino')
    print('El total de saltos de la ruta es : ' + str(pathlen))




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

