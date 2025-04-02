"""PRACTICA 10: 02-04-2025
Instrucciones:
- Modifica el nombre de archivo para que comience por los 6 primeros dígitos de tu DNI/Pasaporte
- Anota tu score=asistencia en el apartado correspondiente del CV
- Trabaja en la función "arregla" (línea 371)
- En la función que comprueba la triangulación hay dos casos fijados, puedes usarlos para depurar el código
- Sube el código .py a la tarea del CV 
"""
import numpy as np
import random
import math
import matplotlib.pyplot as plt
ERROR = 1e-9

##################################### INICIO DCEL ######################################################
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    #La coordenada x del Punto p es p.x y la coordenada y del Punto p es p.y
    def __repr__(self):
        return "({0},{1})".format(self.x, self.y)  
    def __add__(self, other):
        return Punto(self.x + other.x, self.y + other.y)  
    def __sub__(self, other):
        return Punto(self.x - other.x, self.y - other.y)
    def __eq__(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) < ERROR
    def __hash__(self):
        return 1000000000*int(self.x) + 1000*int(self.y)

class Arista:
    def __init__(self, origen, final, anterior = None, siguiente = None, gemela = None, cara = None):
        self.origen, self.final = origen, final
        self.anterior = anterior
        self.siguiente = siguiente
        self.gemela = gemela
        self.cara = cara           
    def __repr__(self):
        return "Arista de {0} a {1}".format(self.origen, self.final)
    def __eq__(self, other):
        return self.origen == other.origen and self.final == other.final
    def __hash__(self):
        return 1000000000*int(self.origen.x) + 1000*int(self.origen.y) + 10000000*int(self.final.x) + 10*int(self.final.y)
    def opuesta(self):
        return Arista(self.final, self.origen)

class Cara:
    def __init__(self, arista_incidente = None):
        self.arista_incidente = arista_incidente

    def __repr__(self):
        return "Cara cuya arista es {0}".format(self.arista_incidente)                

    def lista_vertices(self):        
        e0 = self.arista_incidente
        vertices = [e0.origen]
        e = e0.siguiente
        while e != e0:
            vertices.append(e.origen)
            e = e.siguiente        
        return vertices

    def lista_lados(self):
        e0 = self.arista_incidente
        lados = [e0]
        e = e0.siguiente
        while e0 != e:
            lados.append(e)
            e = e.siguiente
        return lados

class DCEL:
    def __init__(self, vertices = None):
        self.lista_aristas = []
        self.lista_caras = []   
        self.lista_vertices = {} # diccionario con los vértices como llaves y una arista incidente como valor 
        if vertices:
            n = len(vertices)
            for i in range(n):
                self.lista_aristas.append(Arista(vertices[i], vertices[(i+1) % n]))
            c = Cara(self.lista_aristas[0])
            self.lista_caras.append(c)
            for i in range(n):
                self.lista_aristas[i].anterior = self.lista_aristas[(i-1) % n]
                self.lista_aristas[i].siguiente = self.lista_aristas[(i+1) % n]
                self.lista_aristas[i].cara = c
                v = self.busca_vertice(self.lista_aristas[i].origen)
                self.lista_vertices[v] = self.lista_aristas[i]

    def __repr__(self):
        print("Imprimimos toda la informacion de la DCEL:")
        print("Lista de aristas:", self.lista_aristas)
        print("Lista de caras:", self.lista_caras)
        for c in self.lista_caras:
            print(c)
            e0 = c.arista_incidente
            print(e0)
            e = e0.siguiente
            while e != e0: 
                print(e)
                e = e.siguiente
        return ""  

    def plot(self, grados = None):
        fig, ax = plt.subplots()
        for c in self.lista_caras:
            aristas = c.lista_lados()
            valores_x = [e.origen.x for e in aristas] + [aristas[0].origen.x]
            valores_y = [e.origen.y for e in aristas] + [aristas[0].origen.y]
            ax.fill(valores_x, valores_y, alpha=0.3)
            ax.plot(valores_x, valores_y)
        
        if grados is not None:
            for p in self.lista_vertices.keys():
                ax.text(p.x, p.y, f'{grados[p]}')

        ax.set_aspect('equal')
        plt.show()
      

    def busca_vertice(self, v_buscado):
        for v in self.lista_vertices: # itero sobre las claves del diccionario
            if v == v_buscado: return v        
        return v_buscado

    def busca_arista(self, e_buscada):
        for e in self.lista_aristas:
            if e == e_buscada: return e
        print("No se ha encontrado la arista {}".format(e_buscada))
        return

    def une_dcel(self, other, e1, e2):
        if e1.origen != e2.final or e1.final != e2.origen: print("Uniendo dos DCEL pegando una pareja de lados que no son gemelos")
        self.lista_aristas.extend(other.lista_aristas)
        self.lista_caras.extend(other.lista_caras)
        self.lista_vertices.update(other.lista_vertices)
        e1.gemela, e2.gemela = e2, e1
        return self

    def une_caras(self, e1, e2): #une self con otra cara pegando las aristas (sentidos opuestos) e1 y e2        
        # eliminamos el rastro de la cara de e2
        c, c_vieja = e1.cara, e2.cara        
        self.lista_caras.remove(c_vieja)
        e2.cara = c
        e = e2.siguiente
        while e != e2:
            e.cara = c
            e = e.siguiente
        #enlazamos las aristas
        e1.anterior.siguiente = e2.siguiente
        e2.siguiente.anterior = e1.anterior
        e1.siguiente.anterior = e2.anterior
        e2.anterior.siguiente = e1.siguiente
        # eliminamos rastro de la arista e1
        c.arista_incidente = e1.siguiente        
        return self
    
##################################### FIN DCEL ######################################################

##################################### INICIO "LIBRERIA" GCOM ###########################################
def prod_vect(u, v):
    return u.x * v.y - u.y * v.x
def det(a, b, c):
    return prod_vect(b - a, c - a)
def alineados(a, b, c):
    #Devuelve True(False) si los puntos a, b, c están alineados(no lo están)
    return abs(det(a, b, c)) < ERROR
def izda(a, b, c):
    #true si c a la izquierda estrictamente de ab    
    return det(a, b, c) > ERROR
def izda_o_alineado(a, b, c):
    #True si c a la izquierda de ab o en la recta ab
    return det(a, b, c) > -ERROR
def punto_en_triangulo(p, a, b, c):
    #devuelve True si p está dentro del triángulo abc o en el borde
    if not izda(a, b, c):
        return punto_en_triangulo(p, a, c, b)    
    return izda_o_alineado(a, b, p) and izda_o_alineado(b, c, p) and izda_o_alineado(c, a, p)
def punto_en_segmento(p, s):
    #p punto, s segmento = lista con dos puntos
    #devuelve True si p está dentro del segmento, incluyendo sus extremos
    if not alineados(p, s[0], s[1]):
        return False
    if abs(s[0].x - s[1].x) > ERROR:
        return min(s[0].x, s[1].x) - ERROR <= p.x <= max(s[0].x, s[1].x) + ERROR
    else:
        return min(s[0].y, s[1].y) - ERROR <= p.y <= max(s[0].y, s[1].y) + ERROR
def segmentos_se_cortan(s, t):
    """Determina si dos segmentos se intersecan (en su interior o en sus extremos)
    Cada segmento es una lista con dos Puntos: s = [P0, P1]"""
    #si los cuatro puntos están alineados
    if alineados(s[0], s[1], t[0]) and alineados(s[0], s[1], t[1]):
        if  abs(s[0].x - s[1].x) > ERROR:
            return max(s[0].x, s[1].x) >= min(t[0].x, t[1].x) - ERROR and max(t[0].x, t[1].x) >= min(s[0].x, s[1].x) - ERROR
        else:
            return max(s[0].y, s[1].y) >= min(t[0].y, t[1].y) - ERROR and max(t[0].y, t[1].y) >= min(s[0].y, s[1].y) - ERROR
    #si tres puntos están alineados (y no los cuatro) devuelve True solo si uno está dentro del otro segmento
    for p in s:
        if alineados(p, t[0], t[1]): return punto_en_segmento(p, t)        
    for p in t:
        if alineados(p, s[0], s[1]): return punto_en_segmento(p, s)        
    #(sabemos que no hay tres alineados) usamos xor = '^' (True ^ False = True, F^T=T T^T=F, F^F=F)
    return (izda(s[0], s[1], t[0]) ^ izda(s[0], s[1], t[1])) and (izda(t[0], t[1], s[0]) ^ izda(t[0], t[1], s[1]))
def punto_en_poligono(q, pol):
    #devuelve True/False si q está dentro de pol (vale en el borde) o fuera de pol.
    """Contamos el número de cortes del polígono con un segmento que comienza en q y acaba fuera del polígono.
    Si es par q está fuera y si es impar está dentro del polígono"""
    maxcoord = max(p.x for p in pol)
    """El segmento acaba en un punto cuya coordenada x es mayor que las de los vértices del polígono y su coordenada y es un real aleatorio"""
    t = [q, Punto(maxcoord + 1, random.uniform(-1, 1))]
    count = 0
    n = len(pol)
    for i in range(n):        
        """Si q está encima de un lado del polígono puede fallar la cuenta de intersecciones pero la función debe devolver True"""
        if punto_en_segmento(q, [pol[i], pol[(i+1)%n]]): return True
        """Nos avisa si se da la improbable situación en que el segmento pasa por un vértice de pol (en cuyo no bastaría con contar intersecciones)"""
        if alineados(t[0], t[1], pol[i]): print(t[0], t[1], pol[i], "El rayo pasa por un vértice")
        if segmentos_se_cortan([pol[i], pol[(i+1)%n]], t):
            count = count + 1
    return (count % 2 == 1)
def pendiente(q, p): 
    if abs(p.x - q.x) < ERROR:
        if p.y > q.y: return 1e30
        else: return -1e30  
    return (p.y - q.y)/(p.x - q.x)
def distancia2(q, p):
    return (q.x - p.x) * (q.x - p.x) + (q.y - p.y) * (q.y - p.y)
def ordena_angularmente(puntos, foco):
    def angulo_desde_foco(p):
        return math.atan2(p.y - foco.y, p.x - foco.x)
    return sorted(puntos, key=angulo_desde_foco)
def prod_escalar(u, v):
    return u.x * v.x + u.y * v.y
##################################### FIN "LIBRERIA" GCOM ###########################################


def genera_nube_puntos(n, entero, size, conciclicos):
    puntos = []
    usados = set()
    if n > (size + 1)**2:
        print("No caben tantos puntos")
        return
    if conciclicos:
        centro = Punto(size//2, size//2)
        n_lados = random.randint(4, 6)
        radio = size/(3*math.sqrt(n))
        for i in range(n_lados):
            p = Punto(centro.x + radio*math.cos(i*2*math.pi/n_lados), centro.y + radio*math.sin(i*2*math.pi/n_lados))
            puntos.append(p)
            usados.add(p)
      #  n = n - n_lados        
    for _ in range(n):
        if entero: p = Punto(random.randint(0, size), random.randint(0, size))
        else: p = Punto(random.uniform(0, size), random.uniform(0, size))
        if p not in usados:
            puntos.append(p)
            usados.add(p)
    return puntos

def determinante(m): #m es una matriz n x n
    n = len(m)
    if n == 1: return m[0][0]
    ip, i = -1, 0
    while ip == -1 and i < n:
        if abs(m[i][0]) > ERROR:
            ip = i
        i += 1
    if ip == -1: return 0
    mm = []
    for i in range(n):
        if i != ip:
            c = m[i][0]/m[ip][0]
            mm.append([m[i][j] - c * m[ip][j] for j in range(1, n)])
    if ip % 2 == 0: signo = 1
    else: signo = -1
    return signo * m[ip][0] * determinante(mm)
    
def dentro_circunf(a, b, c, d): #decide si d está dentro de la circunferencia por a, b, c
    if izda(a, b, c): puntos = [a, b, c, d] #triangulo abc bien orientado
    else: puntos = [b, a, c, d]
    matriz = [[p.x, p.y, p.x**2 + p.y**2, 1] for p in puntos]
    det = determinante(matriz)    
    if det > ERROR: return 1
    elif det > -ERROR: return 0
    else: return -1

def triangulacion_delaunay_bruta2(puntos): #algoritmo O(n^4) que devuelve una triangulación de Delaunay
    n = len(puntos)
    triangulos = []   
    lista_circunferencias = set() # aquí guardaremos las n-uplas de puntos concíclicos (evitando repeticiones de conjuntos)
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n): # incorporo el triangulo i, j, k si no hay puntos dentro (estrictamente) y guardo los concíclicos
                vacia, l = True, 0
                vacia = not alineados(puntos[i], puntos[j], puntos[k]) # si están alineados no lo debe incluir como triangulo
                conciclicos = set()
                while vacia and l < n:
                    valor = dentro_circunf(puntos[i], puntos[j], puntos[k], puntos[l])
                    if valor == 1: vacia = False
                    elif valor == 0 and l not in [i, j, k]: # los índices i, j, k, l corresponden a puntos concíclicos
                        conciclicos.add(puntos[l])
                    l = l+1
                if vacia:
                    if len(conciclicos) > 0:
                        conciclicos.update([puntos[i], puntos[j], puntos[k]])
                        lista_circunferencias.add(frozenset(conciclicos))
                    else:                    
                        triangulos.append([puntos[i], puntos[j], puntos[k]])  

    # hasta aquí en triangulos solo está el grafo de Delaunay, ahora añadimos las triangulaciones de los polígonos concíclicos
    for c in lista_circunferencias:
        # triangulamos el polígono concíclico (=> convexo) que tiene vértices en c
        lista = list(c)
        foco = lista.pop()
        poligono = ordena_angularmente(lista, foco)
        poligono.append(foco)        
        for i in range(1, len(poligono) - 1):
            triangulos.append([poligono[0], poligono[i], poligono[i+1]])
                         
    return triangulos

def convierte_lista_triangulos_a_DCEL(triangulos):

    for t in triangulos:
        if not izda(t[0], t[1], t[2]): t[0], t[1] = t[1], t[0]

    lista_DCEL = []
    for t in triangulos:
        lista_DCEL.append(DCEL(t))
    
    def reduce_lista():
        n = len(lista_DCEL)
        for i in range(n):
            lista_i = set()
            for e in lista_DCEL[i].lista_aristas:
                lista_i.add(e.opuesta())
            for j in range(i+1, n):
                lista_j = set(lista_DCEL[j].lista_aristas)
                interseccion = lista_i & lista_j
                if len(interseccion) > 0:
                    e = interseccion.pop()
                    lista_DCEL[i].une_dcel(lista_DCEL[j], e, e.opuesta())
                    lista_DCEL.remove(lista_DCEL[j])
                    return True
        return False     

    while len(lista_DCEL) > 1:               
        reduccion_hecha = reduce_lista()
        if not reduccion_hecha:
            print("No se ha podido reducir la DCEL")
            break

    #actualizamos gemelas
    for e1 in lista_DCEL[0].lista_aristas:
        for e2 in lista_DCEL[0].lista_aristas:
            if e1.opuesta() == e2:
                e1.gemela, e2.gemela = e2, e1

    return lista_DCEL[0]

def estropea(triangulacion):     
    while True:
        e = random.choice(triangulacion.lista_aristas) 
        if e.gemela is not None:
            print("Se elimina la ", e, " y su gemela")
            triangulacion.une_caras(e, e.gemela)
            return
    

def arregla(triangulacion):
    # a la triangulacion le falta una arista! Encuentrala y añadela
    for cara in triangulacion.lista_caras:
        lista_vertices_car = cara.lista_vertices()
        if len(lista_vertices_car) == 4:
            poligono = cara
            break
    v1 = lista_vertices_car[0]
    v2 = lista_vertices_car[2]
            
    
    e = Arista(v1,v2)
    E = Arista(v2,v1)
            
    e.gemela = E
    E.gemela = e
            
    caraE = Cara(E)
    E.cara = caraE
            
    e1, e2, e3, e4 = poligono.lista_lados()
            
    e1.anterior, e4.anterior = e, e
    e2.anterior, e3.siguiente = E, E
    e.anterior , e.siguiente = e1, e4
    E.anterior, E.siguiente = e3, e2
            
    poligono.arista_incidente = e
            
    triangulacion.lista_aristas.append(e)
    triangulacion.lista_aristas.append(E)
                

    return triangulacion

def comprueba_triangulacion(n, entero = None, size = None, conciclicos = None):
    if not n: n = 7
    if not size: size = 10
    if entero is None: entero = False 
    if conciclicos is None: conciclicos = False   

    puntos = genera_nube_puntos(n, entero, size, conciclicos)
    
    triangulos = triangulacion_delaunay_bruta2(puntos)
    triangulacion = convierte_lista_triangulos_a_DCEL(triangulos)
    estropea(triangulacion)
    arregla(triangulacion)
    triangulacion.plot()

    """
    Extra: en el diccionario "grados" introduce el valor del grado de cada vértice de la triangulación
    grados = {}
    for p in triangulacion.lista_vertices.keys():
        grados[p] = 0
    triangulacion.plot(grados)"
    """
    return


#cambia los parámetros para probar tu triangulación:
comprueba_triangulacion(n = 12, entero = True, size = 20, conciclicos = False)
