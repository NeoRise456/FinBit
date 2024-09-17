import tkinter as tk
from tkinter import messagebox
import networkx as nx
import heapq
from scipy.spatial import KDTree
import sqlite3
from haversine import haversine, Unit
import matplotlib.pyplot as plt
import numpy as np

class Haversinemethod:
    def __init__(self) -> None:
        pass
    def calcular_distancia(x1,y1,x2,y2) -> float:
        coord1 = (x1,y1)
        coord2 = (x2,y2)
        return haversine(coord1, coord2, unit=Unit.METERS)

class SQLiteHandler:
    def __init__(self):
        self.conection = None
    
    def open_conection(self):
        self.conection = sqlite3.connect('Complejidad1')
    
    def close_conection(self):
        self.conection.close()
        
    def obtener_usuarios(self) -> list:
        self.open_conection()
        
        query = "SELECT * FROM Users LIMIT 250;"
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close()        
        self.close_conection()
        
        return results
    
    def obtener_entidades(self) -> list:
        self.open_conection()
        
        query = "SELECT * FROM EntidadFinanciera LIMIT 250;"
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close()        
        self.close_conection()
        
        return results

    def obtener_user_from_dni(self,dni) -> tuple:
        self.open_conection()
        query = f"SELECT * FROM Users WHERE DNIUser = {dni} ;"
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close() 
        
        self.close_conection()
        
        return 0 if len(results) == 0 else results[0]
    
    def obtener_relacion_bancoComercial_user(self) -> list:
        self.open_conection()
        query = ''' select Users.DNIUser , Clientes.IDEntidad
                    from Clientes
                    inner join Users on Clientes.ID_User = Users.ID_User;'''
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close() 
        
        self.close_conection()
        return results
    
    def obtener_id_bancos_from_usuarios(self,ID_User):
        self.open_conection()
        query = f'''select Clientes.IDEntidad from Clientes where ID_User = {ID_User}; '''
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close() 
        self.close_conection()
        return results

    def transferencia_entre_usuarios(self,ID_User1,ID_User2,ID_TipoTransaccion,MontoTransferido):
        self.open_conection()
        query = f'''insert into 
        Transacciones(ID_User1,ID_User2,ID_TipoTransaccion,MontoTransferido)
        VALUES({ID_User1},{ID_User2},{ID_TipoTransaccion},{MontoTransferido});'''
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        self.conection.commit()
        cursor.close() 
        self.close_conection()
        return results
    
    def obtener_clientes_bancos_segun_IDUser(self,ID_User):
        self.open_conection()
        query = f'''select IDEntidad from Clientes where ID_User = {ID_User};'''
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close() 
        self.close_conection()
        return results
    
    def obtener_banco_from_id(self,IDEntidad):
        self.open_conection()
        query = f'''select * from EntidadFinanciera where IDEntidad = {IDEntidad};'''
        cursor = self.conection.execute(query)
        results = cursor.fetchall()
        cursor.close() 
        self.close_conection()
        return 0 if len(results) == 0 else results[0]
    
    def crear_solicitud(self,ID_User,suma_solicitada):
        
        bancos_pertenecientes = self.obtener_clientes_bancos_segun_IDUser(ID_User)
        #print(bancos_pertenecientes)
        for e in bancos_pertenecientes:
            self.open_conection()
            query = f'''insert into Solicitudes(ID_User,SumaSolucitud,IDEntidad,IDEstadoSolicitud)
                    VALUES({ID_User},{suma_solicitada},{e[0]},1);'''
            cursor = self.conection.execute(query)
            results = cursor.fetchall()
            self.conection.commit()
            cursor.close() 
            self.close_conection()
    

class Grader:
    def __init__(self) -> None:
        self.database = SQLiteHandler()
    
    def dijkstra_networkx(self,G, s):
        visited = {}  # Diccionario para mantener los nodos visitados
        path = {}     # Diccionario para mantener el predecesor de cada nodo en el camino más corto
        cost = {}     # Diccionario para mantener el costo acumulado del camino más corto hacia cada nodo
    
        cost[s] = 0
        pqueue = [(0, s)]
    
        while pqueue:
            g, u = heapq.heappop(pqueue)
        
            if u in visited:
                continue
        
            visited[u] = True
        
            for v, w in G.adj[u].items():
                if v not in visited:
                    f = g + w['weight']
                    if v not in cost or f < cost[v]:
                        cost[v] = f
                        path[v] = u
                        heapq.heappush(pqueue, (f, v))
        return path, cost
    
    def obtener_aristas(self, graph, cur_node, peso_min, peso_max):
        aristas = graph.edges(cur_node, data=True)
        #print(aristas)
        aristas_filtradas = [(u, v, float(data['weight'])) for u, v, data in aristas 
                            #if peso_min <= data['weight'] <= peso_max
                            ]
        return aristas_filtradas

    
    def lazy_prim_intervalo(self,graph: nx.Graph, peso_min, peso_max,idx_inicio):
        #print("RIESGOS: ",peso_min," | ",peso_max)
        nodes = list(graph.nodes())
        visited = [idx_inicio]
        mst_edges = []
        edge_queue = []
        cur_node = idx_inicio
        #print(nodes)
        while len(visited) < len(nodes):
            node_edges = self.obtener_aristas(graph,cur_node,peso_min,peso_max)
            #print(cur_node,node_edges)
            for edge in node_edges:
                #print(edge)
                if edge[1] not in visited and edge not in edge_queue and peso_min<=edge[2]<=peso_max:
                    heapq.heappush(edge_queue, (edge[2], edge))
        
            while True:
                if not edge_queue:
                    return mst_edges  # No se encontraron más aristas válidas dentro del intervalo
                priority, edge = heapq.heappop(edge_queue)
                if edge[1] not in visited:
                    mst_edges.append(edge)
                    cur_node = edge[1]
                    break
            visited.append(cur_node)
        return mst_edges
    
    
    def evaluate_transaction_between_users(self, user1, user2, graph: nx.Graph):
    # Encontrar el camino más corto desde user1 usando el algoritmo de Dijkstra
        path, cost = self.dijkstra_networkx(graph, user1)
        
        #print(path)
        
        
        # Verificar si user2 está en el camino
        if int(user2) in path.keys() or int(user2) in path.values():
            #print("ESTA")
            graph.nodes[int(user1)]['color'] = '#ff0066'
            graph.nodes[int(user2)]['color'] = '#ff0066'
            return 1
        else:
            return 0

    
    def evaluate_bank_transacction(self,id_bankC,graph: nx.Graph,risk1,risk2):
        
        #lazy_prim_intervalo(self,graph: nx.Graph, peso_min, peso_max,idx_inicio)
        aristas = self.lazy_prim_intervalo(graph,risk1,risk2,id_bankC)
        nodos_afectados = []
        for arista in aristas:
            if arista[0] not in nodos_afectados:
                nodos_afectados.append(arista[0])
            if arista[1] not in nodos_afectados:
                nodos_afectados.append(arista[1])
        
        #print(nodos_afectados)
        bancos_comerciales = []
        bancos_inversores = []
        aseguradoras = []
        
        for e in nodos_afectados:
            if e != id_bankC:
                data = self.database.obtener_banco_from_id(e)
                if data[2] == 1:
                    bancos_comerciales.append(data[0])
                elif data[2] == 2:
                    bancos_inversores.append(data[0])
                elif data[2] == 3:
                    aseguradoras.append(data[0])
        
        #print(bancos_comerciales)
        #print(bancos_inversores)
        #print(aseguradoras)
        
        rev_max = 0
        
        banco_inversor_escogido = id_bankC
        
        for e in bancos_inversores:
            data = self.database.obtener_banco_from_id(e)
            rev_aprox = int(data[4]) * float(data[3])
            if rev_aprox > rev_max:
                rev_max = rev_aprox
                banco_inversor_escogido = data[0]
        
        if banco_inversor_escogido == id_bankC:
            print("No existe un buen DEAL para todos")
            return
        
        rev_max_seguro = 0
        banco_asegurador_escogido = banco_inversor_escogido
        
        for e in aseguradoras:
            data = self.database.obtener_banco_from_id(e)
            rev_aprox = int(data[4]) * float(data[3])
            if rev_aprox > rev_max_seguro:
                rev_max_seguro = rev_aprox
                banco_asegurador_escogido = data[0]
            
        if banco_asegurador_escogido == banco_inversor_escogido:
            print("No existe un buen DEAL para todos")
            return
        
        print("Retribucion maxima:",rev_max)
        print("Paquete Asegurado por:",rev_max_seguro)
        
        #print(id_bankC)
        #print(banco_inversor_escogido)
        #print(banco_asegurador_escogido)
        
        #graph[id_bankC][banco_inversor_escogido]['color'] = 'red'
        #graph[banco_inversor_escogido][banco_asegurador_escogido]['color'] = 'red'
        
        grafo_resultante = nx.Graph()
        grafo_resultante.add_node(id_bankC,color='blue',label=("BC" + str(id_bankC)))
        
        for e in bancos_inversores:
            name = "BI"+ str(e)
            grafo_resultante.add_node(e,color='red',label = name)
        
        
        for e in aseguradoras:
            name = "A"+ str(e)
            grafo_resultante.add_node(e,color='green',label=name)
        
        for e in bancos_inversores:
            data = self.database.obtener_banco_from_id(e)
            grafo_resultante.add_edge(id_bankC,e,
            weight=data[3],color='black')
        
        for a in aseguradoras:
            data = self.database.obtener_banco_from_id(a)
            for b in bancos_inversores:
                grafo_resultante.add_edge(a,b,
                weight= data[3] ,color='black')
        
        grafo_resultante[id_bankC][banco_inversor_escogido]['color'] = 'red'
        grafo_resultante[banco_inversor_escogido][banco_asegurador_escogido]['color'] = 'red'
        
        graph_viewer = Graph()
        graph_viewer.draw_graph(grafo_resultante)
        
        
        #realizar queries
        
        return 

class Graph:
    def __init__(self):
        self.graph = nx.Graph()
        self.database = SQLiteHandler()
        
    def insert_users(self):
        data = self.database.obtener_usuarios()
        for e in data:
            name = "U" + str(e[0])
            self.graph.add_node(e[3],color='skyblue',label=name)
            
    
    def insert_entities(self):
        data = self.database.obtener_entidades()
        for e in data:
            #print(e)
            if e[2] == 1:
                name = "BC" + str(e[0])
                self.graph.add_node(e[0],color='#ff3b4b',label=name,
                                    bank_type=e[2],risk=e[3],max_risk=e[5])
            elif e[2] == 2:
                name = "BI" + str(e[0])
                self.graph.add_node(e[0],color='#b4ff3b',label=name,
                                    bank_type=e[2],risk=e[3],max_risk=e[5])
            elif e[2] == 3:
                name = "A" + str(e[0])
                self.graph.add_node(e[0],color='#933bff',label=name,
                                    bank_type=e[2],risk=e[3],max_risk=e[5])
        
        tipo_banco = nx.get_node_attributes(self.graph,'bank_type')
        riesgos = nx.get_node_attributes(self.graph,'risk')
        riesgos_max = nx.get_node_attributes(self.graph,'max_risk')
        
        #print(nx.get_node_attributes(self.graph,'risk'))
        type1_bank = [e for e in tipo_banco if tipo_banco[e] == 1]
        type2_bank = [e for e in tipo_banco if tipo_banco[e] == 2]
        type3_bank = [e for e in tipo_banco if tipo_banco[e] == 3]
        
        for bank in type1_bank:
            for inversionbank in type2_bank:
                if(riesgos_max[bank] >= riesgos[inversionbank]):
                    self.graph.add_edge(bank,inversionbank,
                                        weight=riesgos[inversionbank],color='#002ad1')
        
        
        for inversionbank in type2_bank:
            for securebank in type3_bank:
                if(riesgos_max[inversionbank] >= riesgos[securebank]):
                    self.graph.add_edge(inversionbank,securebank,
                                        weight=riesgos[securebank],color='#5bd100')
        
        
        
    def insert_relation_comercialbank_users(self):
        data_relation = self.database.obtener_relacion_bancoComercial_user()
        for user,bank in data_relation:
            data_user = self.database.obtener_user_from_dni(user)
            self.graph.add_edge(user,bank,weight=data_user[4],color='#000000')
            
    def insert_relation_between_users(self):
        
        distancia_maxima = 800 #metros
        data_users = self.database.obtener_usuarios()
        coordenadas = [(usuario[6], usuario[7]) for usuario in data_users]
        tree = KDTree(coordenadas, leafsize=10)
        
        for i in range(len(data_users)):
            coord = (data_users[i][6], data_users[i][7])  # Coordenadas del usuario i
            # Consultar el árbol KD para encontrar puntos dentro del radio n
            cerca_indices = tree.query_ball_point(coord, r=distancia_maxima, p=2.0)
        
            for j in cerca_indices:
                if i != j:
                    distancia = haversine(coord, coordenadas[j], unit=Unit.METERS)
                    if distancia < distancia_maxima:
                        distancia = round(distancia,1)
                        self.graph.add_edge(data_users[i][3],data_users[j][3],
                                            weight=distancia,color='#75512d')
    
    def draw_graph(self,G):
        
        pos = nx.spring_layout(G, k=27, iterations=200, seed=2)
        #pos = nx.planar_layout(G)
        
        node_colors_dict = nx.get_node_attributes(G,'color')
        edge_color_dict = nx.get_edge_attributes(G,'color')
        edge_weights = nx.get_edge_attributes(G, 'weight')
        
        node_colors_list = list(node_colors_dict.values())
        edge_colors_list = list(edge_color_dict.values())
        
        nx.draw(G, pos, 
                #with_labels=True, 
                node_size=200, 
                #node_color="skyblue", 
                font_size=15, 
                font_color="black", 
                font_weight="bold",
                node_color= node_colors_list,
                edge_color=edge_colors_list)
        node_labels = nx.get_node_attributes(G, 'label')
        
        nx.draw_networkx_labels(G, pos, node_labels, font_size=15, font_color='black')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_weights)
        plt.show()
        
    def users_graph(self):
        
        self.insert_users()
        self.insert_relation_between_users()
        return self.graph
    
    def bank_graph(self):
        #self.insert_users()
        #self.insert_relation_between_users()
        self.insert_entities()
        #self.insert_relation_comercialbank_users()
        return self.graph

class MyApp:
    def __init__(self) -> None:
        self.app = tk.Tk()
        self.app.title("TipoLogin")
        self.database = SQLiteHandler()
        
        #self.app.geometry("400x200")
    
    def login(self) -> None:
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)
        tk.Button(self.app, 
                text="Iniciar Sesión Usuario",
                command=self.login_usuario).grid(row=1, column=0,sticky="ew",padx=50,pady=50)
        tk.Button(self.app, 
                text="Iniciar Sesión Banco",
                command=self.login_banco).grid(row=2, column=0,sticky="ew",padx=50,pady=50)
    
    def kill(self) -> None:
        self.app.destroy()
        
    def verificar_usuario(self,dni,app):
        dni = int(dni)
        data = self.database.obtener_user_from_dni(dni)
        if data != 0:
            #messagebox.showinfo("Inicio de Sesión Exitoso", "INICIO SESION EXITOSO")
            app.destroy()
            self.usuario_mainframe(dni)
        else:
            messagebox.showerror("Error en Inicio de Sesion", "DNI NO ENCONTRADO")
    
    def login_usuario(self):
        user_login = tk.Toplevel(self.app)
        user_login.title("User Login")
        user_login.geometry("400x200")
        
        tk.Label(user_login, text="Dni de Usuario").pack(pady=15)
        
        entry_dni= tk.Entry(user_login)
        entry_dni.pack(pady=10)
        
        tk.Button(user_login, text="Log In", command=lambda: self.verificar_usuario(entry_dni.get(),user_login)).pack(pady=5)
        tk.Button(user_login, text="Cerrar", command=user_login.destroy).pack(pady=5)
    
    def usuario_mainframe(self,dni):
        data = self.database.obtener_user_from_dni(dni)
        
        nom_usuario = data[1] + " " + data[2]
        dni_usuario=data[3]
        dinero_en_cuenta = data[5]
        
        user_mainframe = tk.Toplevel(self.app)
        user_mainframe.title(( nom_usuario + " Dashboard"))
        user_mainframe.geometry("720x600")
        
        #info usuario en pantalla
        tk.Label(user_mainframe,
                text="Nombre Completo:" + nom_usuario).grid(row=0,column=0,pady=10)
        tk.Label(user_mainframe,
                text="DNI:" + str(dni_usuario)).grid(row=1,column=0,pady=10)
        tk.Label(user_mainframe,
                text="Dinero En Cuenta:" + str(dinero_en_cuenta)).grid(row=2,column=0,pady=10)
        
        tk.Label(user_mainframe,
                text="ACCIONES").grid(row=3,column=0,padx=20,pady=20)
        
        
        #transferencia
        tk.Label(user_mainframe,
                text="DNI de a quien Transferir:").grid(row=4,column=0,pady=10)
        dni_transferencia = tk.Entry(user_mainframe)
        dni_transferencia.grid(row=4,column=1,padx=10,pady=10)

        tk.Label(user_mainframe,
                text="Monto A Transferir:").grid(row=5,column=0,pady=10)
        dinero_a_transferir = tk.Entry(user_mainframe)
        dinero_a_transferir.grid(row=5,column=1,padx=10,pady=10)
        
        tk.Button(user_mainframe, text="Realizar Transferencia", 
                command=lambda: self.transferencia_entre_usuarios(data,dni_transferencia.get(),
                                                                dinero_a_transferir.get()
                                                                ,user_mainframe) 
                ).grid(row=7,column=0,padx=10,pady=10)
        
        #23456789
        tk.Label(user_mainframe,
                text="Monto A Solicitar:").grid(row=8,column=0,pady=10)
        dinero_a_solicitar = tk.Entry(user_mainframe)
        dinero_a_solicitar.grid(row=8,column=1,padx=10,pady=10)
        
        tk.Button(user_mainframe, text="Solicitar Prestamo",
                command=lambda: self.solicitud_prestamo(data,dinero_a_solicitar.get(),user_mainframe)
                ).grid(row=10,column=0,padx=10,pady=10)
        
        
        tk.Button(user_mainframe, text="Cerrar",
                command=lambda: self.kill()).grid(row=11,column=0,padx=10,pady=10)
    
    def transferencia_entre_usuarios(self,data,dni2,dinero_a_transferir,app):
        app.destroy()
        data_usuario2 = self.database.obtener_user_from_dni(dni2)
        if int(dinero_a_transferir) < 0:
            messagebox.showerror("Error en Tranferencia", "No puede transferir Numeros Negativos")
            self.usuario_mainframe(data[3])
            return
        if data_usuario2 == 0:
            messagebox.showerror("Error en Tranferencia", "DNI a quien transferir\n NO ENCONTRADO")
            self.usuario_mainframe(data[3])
            return
        if data[3] == int(dni2):
            messagebox.showerror("Error en Tranferencia", 
                                "el Dni de a quien transfieres no puede ser el mismo")
            self.usuario_mainframe(data[3])
            return
        if (data[5] - int(dinero_a_transferir)) < 0:
            messagebox.showerror("Error en Tranferencia", "FONDOS INSUFICIENTES")
            self.usuario_mainframe(data[3])
            return
        #self,ID_User1,ID_User2,ID_TipoTransaccion,MontoTransferido
        #self.database.transferencia_entre_usuarios(data[3],data_usuario2[3],)
        
        algo = Grader()
        grafoViewer = Graph()
        grafo_usuarios = grafoViewer.users_graph()
        
        condicion_transaccion = algo.evaluate_transaction_between_users(
            data[3],dni2,grafo_usuarios)
        
        if condicion_transaccion == 0:
            messagebox.showerror("Error en Tranferencia", "Usuario a Transferir Fuera del sistema")
            grafoViewer.draw_graph(grafo_usuarios)
            return
        
        #grafo_usuarios = Graph()
        
        banco1 = self.database.obtener_id_bancos_from_usuarios(data[0])
        banco2 = self.database.obtener_id_bancos_from_usuarios(data_usuario2[0])
        tipo = ""
        
        if banco1== banco2:
            #tipo1
            self.database.transferencia_entre_usuarios(data[0]
                                                    ,data_usuario2[0]
                                                    ,1
                                                    ,dinero_a_transferir)
            tipo = "ORDINARIA"
        else:
            #tipo2
            self.database.transferencia_entre_usuarios(data[0]
                                                    ,data_usuario2[0]
                                                    ,2
                                                    ,dinero_a_transferir)
            tipo = "INTERBANCARIA"
            
        grafoViewer.draw_graph(grafo_usuarios)
        
        messagebox.showinfo("Transferencia Exitosa", 
                            "La Transferencia se realizo con exito a:\n" + data_usuario2[1] + " " 
                            + data_usuario2[2] + " | DNI: " + str(data_usuario2[3])
                            + "\nTipo Transferencia: " + tipo)
        self.usuario_mainframe(data[3])
    
    def solicitud_prestamo(self,data,monto_solicitado,app):
        app.destroy()
        if int(monto_solicitado) < 0:
            messagebox.showerror("Error en Solicitud", "No puede solicitar Numeros Negativos")
            self.usuario_mainframe(data[3])
        #self,ID_User,suma_solicitada
        self.database.crear_solicitud(data[0],monto_solicitado)
        messagebox.showinfo("Solicitud Prestamo Exitosa", "La solicitud de Prestamo ha sido creada")
        self.usuario_mainframe(data[3])
    
    def login_banco(self):
        bank_login = tk.Toplevel(self.app)
        bank_login.title("Bank Login")
        bank_login.geometry("400x200")
        
        tk.Label(bank_login, text="ID del Banco").pack(pady=15)
        entry_id= tk.Entry(bank_login)
        entry_id.pack(pady=10)
        
        tk.Button(bank_login, text="Log In", command=lambda: self.verificar_banco(entry_id.get(),bank_login)).pack(pady=5)
        tk.Button(bank_login, text="Cerrar", command=bank_login.destroy).pack(pady=5)
    
    def verificar_banco(self,idbank,app):
        
        data = self.database.obtener_banco_from_id(idbank)
        if data != 0 and data[2] == 1:
            app.destroy()
            #messagebox.showinfo("Inicio de Sesión Exitoso", str(data))
            self.bancoComercial_mainframe(data[0])
        else:
            messagebox.showerror("Error en Inicio de Sesion", "Banco No Encontrado")
    
    def bancoComercial_mainframe(self,idbank):
        data = self.database.obtener_banco_from_id(idbank)
        
        nom_banco = data[1]
        capital = data[4]
        riesgo=data[3]
        riesgo_maximo_permitido = data[5]
        
        bancoComercial_mainframe = tk.Toplevel(self.app)
        bancoComercial_mainframe.title(( nom_banco + " Dashboard"))
        bancoComercial_mainframe.geometry("720x600")
        
        tk.Label(bancoComercial_mainframe,
                text=("Banco: " + str(nom_banco))).grid(row=1,column=0,pady=10,padx=10)
        
        tk.Label(bancoComercial_mainframe,
                text=("Capital: " + str(capital))).grid(row=2,column=0,pady=10,padx=10)
        
        tk.Label(bancoComercial_mainframe,
                text=("Riesgo de Invertir: " + str(riesgo))).grid(row=3,column=0,pady=10,padx=10)
        
        tk.Label(bancoComercial_mainframe,
                text=("Riesgo Maximo a Soportar: " + str(riesgo_maximo_permitido))
                ).grid(row=4,column=0,pady=10,padx=10)
        
        
        tk.Label(bancoComercial_mainframe,
                text="Tipo de Riesgo a tomar (A,B,C): ").grid(row=5,column=0,pady=10,padx=10)
        riesgo_entry = tk.Entry(bancoComercial_mainframe)
        riesgo_entry.grid(row=5,column=1,padx=10,pady=10)
        
        tk.Button(bancoComercial_mainframe, text="Transaccion",
                command=lambda: self.transaccion_bancaria(data,riesgo_entry.get())
                ).grid(row=6,column=0,padx=10,pady=10)
        
        
        tk.Button(bancoComercial_mainframe, text="Cerrar",
                command=lambda: self.kill()).grid(row=7,column=0,padx=10,pady=10)
    
    
    
    def transaccion_bancaria(self,data,riesgo):
        #esta funcion recorre el grafo de los bancos
        #y realiza la transaccion de la manera que
        #todos obtengan la mejor transaccion posible
        
        riesgo_intervalo1 = riesgo_intervalo2 = 0
        if riesgo == "A":
            riesgo_intervalo1 = 0
            riesgo_intervalo2 = 0.3
        elif riesgo == "B":
            riesgo_intervalo1 = 0.3
            riesgo_intervalo2 = 0.65
        elif riesgo == "C":
            riesgo_intervalo1 = 0.65
            riesgo_intervalo2 = 1
        
        
        
        algo = Grader()
        
        graphViwer = Graph()
        grafoBancos = graphViwer.bank_graph()
        
        algo.evaluate_bank_transacction(data[0],grafoBancos,riesgo_intervalo1,riesgo_intervalo2)
        
        #graphViwer.draw_graph(grafoBancos)
        
        
        return
        
        
    def run(self) ->None:
        self.login()
        self.app.mainloop()


if __name__ == "__main__":
    app = MyApp()
    app.run()