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
    print("4-Req 2")
    print("5-Req 3")
    print("6-Req 4")
    print("7-Req 5")
    print("8-Req 6")
    print("9-Req 7")
    print("10-Req 8")


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
         optionThree(cont, lp1, lp2)



    else:
        sys.exit(0)
sys.exit(0)
