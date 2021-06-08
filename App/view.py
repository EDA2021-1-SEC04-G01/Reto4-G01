"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import controller
import model
from DISClib.ADT import list as lt
assert cf
import threading
from App import controller
from DISClib.ADT import stack
import datetime
import time
import tracemalloc


connections = 'connections.csv'
countries = "countries.csv"
points = "landing_points.csv"
initialStation = None

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("Bienvenido")
    print("1- Iniciar Analizador")
    print("2- Cargar datos")
    print("3- Encontrar cantidad de Clústeres y ver si 2 landing points pertecen al mismo clúster")
    print("4- Encontrar Landing points con mas cables concectados")
    print("5- Encontrar ruta minima entre dos paises")
    print("6- Red de conexion minima")
    print("7- Encontrar los paises afectados por el fallo de un landing point")
    print("8- Lista de paises conectados a un cable y su maximo de ancho de banda")
    print("9- Ruta minima entre dos IPs")
    print("10-Req 8")

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def getMemory():
    """
    toma una muestra de la memoria alocada en instante de tiempo
    """
    return tracemalloc.take_snapshot()


def deltaMemory(start_memory, stop_memory):
    """
    calcula la diferencia en memoria alocada del programa entre dos
    instantes de tiempo y devuelve el resultado en bytes (ej.: 2100.0 B)
    """
    memory_diff = stop_memory.compare_to(start_memory, "filename")
    delta_memory = 0.0

    # suma de las diferencias en uso de memoria
    for stat in memory_diff:
        delta_memory = delta_memory + stat.size_diff
    # de Byte -> kByte
    delta_memory = delta_memory/1024.0
    return delta_memory
def optionTwo(cont):
    print("\nCargando información....")
    ans= controller.loadServices(cont, connections, points, countries)
    numedges = controller.totalConnections(cont)
    numvertex = controller.totalPoints(cont)
    numcountries= model.totalCountries(cont)
    print('Landing Points Totales: ' + str(numvertex))
    print('Conexiones Totales: ' + str(numedges))
    print('Numero de Paises: ' + str(numcountries))
    print("\nPrimer landing point cargado:")
    print("Identifcador: "+ans[1])
    print("Nombre: "+ans[2])
    print("Latitud: "+ans[3])
    print("Longitud: "+ans[4])
    print("\nUltimo pais cargado: ")
    print("Nombre: "+ans[5])
    print("Poblacion: "+ans[6])
    print("Numero de usuarios de internet: "+ans[7])

def optionThree(cont, lp1, lp2):
    print('El número de clústeres es: ' +
          str(controller.connectedComponents(cont)))
    model.isscc(cont, lp1, lp2)

def optionFour(cont):
    return controller.mostConnections(cont)

def optionFive(cont, origin, dest):
    distance= 0
    path= model.minimumPath(cont, origin, dest)
    if path is not None:
        while (not stack.isEmpty(path)):
            stop = stack.pop(path)
            distance += int(stop["weight"])
            print(stop)
    else:
        print('No hay camino')
    print("La distancia total de la ruta (en Km) es: "+ str(distance))

def optionSix(cont):
    
    model.minimumExpansion(cont)

def optionSeven(cont,lanname):
    model.failLanding(cont,lanname)

def optionEight(cont, country,name):
    print("Los paises conectados a este cable son: ")
    model.maxBb(cont, country, name)
def optionNine(cont, ip1,ip2):
    model.ipdistance(cont,ip1,ip2)    

catalog = None

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("\nInicializando....")
        # cont es el controlador que se usará de acá en adelante
        cont = controller.init()
        
    elif int(inputs[0]) == 2:
        optionTwo(cont)
        pass
    
    elif int(inputs[0]) == 3:
         print("A continuacion ingrese dos landing points para mirar si estan fuertemente conectados:")
         lp1= input("Landing point 1: ")
         lp2= input("Landing point 2: ")
         delta_time = -1.0
         delta_memory = -1.0
         tracemalloc.start()
         start_time = getTime()
         start_memory = getMemory()
         optionThree(cont, lp1, lp2)
         stop_memory = getMemory()
         stop_time = getTime()
         tracemalloc.stop()
         delta_time = stop_time - start_time
         delta_memory = deltaMemory(start_memory, stop_memory)
         print("Tiempo [ms]: ", f"{delta_time:.3f}", "  ||  ",
              "Memoria [kB]: ", f"{delta_memory:.3f}")

    elif int(inputs[0]) == 4:
        delta_time = -1.0
        delta_memory = -1.0
        tracemalloc.start()
        start_time = getTime()
        start_memory = getMemory()
        optionFour(cont)
        stop_memory = getMemory()
        stop_time = getTime()
        tracemalloc.stop()
        delta_time = stop_time - start_time
        delta_memory = deltaMemory(start_memory, stop_memory)
        print("Tiempo [ms]: ", f"{delta_time:.3f}", "  ||  ",
              "Memoria [kB]: ", f"{delta_memory:.3f}")

    elif int(inputs[0]) == 5:
        origin= input("Ingrese el pais de origen: ")
        dest= input("Ingrese el pais de destino: ")
        delta_time = -1.0
        delta_memory = -1.0
        tracemalloc.start()
        start_time = getTime()
        start_memory = getMemory()
        optionFive(cont, origin, dest)
        stop_memory = getMemory()
        stop_time = getTime()
        tracemalloc.stop()
        delta_time = stop_time - start_time
        delta_memory = deltaMemory(start_memory, stop_memory)
        print("Tiempo [ms]: ", f"{delta_time:.3f}", "  ||  ",
              "Memoria [kB]: ", f"{delta_memory:.3f}")
    
    elif int(inputs[0]) == 6:
        delta_time = -1.0
        delta_memory = -1.0
        tracemalloc.start()
        start_time = getTime()
        start_memory = getMemory()
        optionSix(cont)
        stop_memory = getMemory()
        stop_time = getTime()
        tracemalloc.stop()
        delta_time = stop_time - start_time
        delta_memory = deltaMemory(start_memory, stop_memory)
        print("Tiempo [ms]: ", f"{delta_time:.3f}", "  ||  ",
              "Memoria [kB]: ", f"{delta_memory:.3f}")

    elif int(inputs[0]) == 7:
        lanname=input("Ingrese el nombre del Landing Point: ")
        delta_time = -1.0
        delta_memory = -1.0
        tracemalloc.start()
        start_time = getTime()
        start_memory = getMemory()
        optionSeven(cont, lanname)
        stop_memory = getMemory()
        stop_time = getTime()
        tracemalloc.stop()
        delta_time = stop_time - start_time
        delta_memory = deltaMemory(start_memory, stop_memory)
        print("Tiempo [ms]: ", f"{delta_time:.3f}", "  ||  ",
              "Memoria [kB]: ", f"{delta_memory:.3f}")

    elif int(inputs[0]) == 8:
        country=input("Ingrese el pais: ")
        name=input("Ingrese el nombre del cable: ")
        optionEight(cont, country,name)
    
    elif int(inputs[0]) == 9:
        ip1=input("Ingrese la primera direccion IP: ")
        ip2=input("Ingrese la segunda direccion IP: ")
        optionNine(cont, ip1, ip2)


    else:
        sys.exit(0)

    sys.setrecursionlimit(2 ** 30)
sys.exit(0)
