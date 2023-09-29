import queue
import threading
import time
import hashlib

class Block:
    def __init__(self, data, previous_block_hash, amount=None, nonce=None, difficulty=None):
        self.data = data
        self.previous_block_hash = previous_block_hash
        self.amount = amount
        self.nonce = nonce
        self.difficulty = difficulty

    def hash(self):
        """
        Calcula el hash del bloque
        """
        sha = hashlib.sha256()
        sha.update(str(self.data).encode('utf-8') +
                  str(self.previous_block_hash).encode('utf-8') +
                  str(self.amount).encode('utf-8') +
                  str(self.nonce).encode('utf-8') +
                  str(self.difficulty).encode('utf-8'))
        return sha.hexdigest()

class Miner:
    def __init__(self, worker_id, block, start_nonce, end_nonce, result_queue, stop_event):
        self.worker_id = worker_id
        self.block = block
        self.start_nonce = start_nonce
        self.end_nonce = end_nonce
        self.result_queue = result_queue
        self.stop_event = stop_event

    def run(self):
        for nonce in range(self.start_nonce, self.end_nonce):
            if self.stop_event.is_set():
                break

            self.block.nonce = nonce
            if self.block.hash()[:self.block.difficulty] == '0' * self.block.difficulty:
                self.result_queue.put((self.worker_id, nonce))
                self.stop_event.set()

class Blockchain:
    def __init__(self, genesis_block):
        self.blocks = [genesis_block]

    def add_block(self, block):
        """
        Agrega un bloque a la cadena de bloques
        """
        block.previous_block_hash = self.blocks[-1].hash()
        self.blocks.append(block)

    def is_chain_valid(self):
        """
        Verifica la integridad de la cadena de bloques
        """
        for i, block in enumerate(self.blocks):
            if i == 0:
                continue

            if block.previous_block_hash != self.blocks[i-1].hash():
                return False

            if block.hash()[:block.difficulty] != '0' * block.difficulty:
                return False

        return True

def get_transaction_data():
    """
    Solicita al usuario la información de la transacción a través de la consola
    """
    receiver = input("Ingrese el receptor de la transacción: ")
    sender = input("Ingrese el emisor de la transacción: ")
    amount = input("Ingrese el monto de la transacción: ")

    en_receiver = receiver.encode()
    hash_object = hashlib.sha256(en_receiver)
    hex_receiver = hash_object.hexdigest()

    en_sender = sender.encode()
    hash_object = hashlib.sha256(en_sender)
    hex_sender = hash_object.hexdigest()


    return hex_receiver, hex_sender, amount

def mine(block, blockchain, num_workers):
    """
    Busca el nonce correcto para el bloque utilizando la prueba de trabajo Hashcash
    y simula la competición entre nodos mineros utilizando hilos y una cola de resultados
    """
    start_time = time.time()
    print("Iniciando minería con", num_workers, "trabajadores...")

    # dividir el rango de nonce en bloques para cada trabajador
    num_blocks_per_worker = 10000000
    num_blocks = 2 ** 32
    blocks_per_chunk = num_blocks_per_worker * num_workers
    num_chunks = num_blocks // blocks_per_chunk

    # crear trabajadores y asignar bloques de nonce
    workers = []
    result_queue = queue.Queue()
    stop_event = threading.Event()
    for i in range(num_workers):
        start_nonce = i * num_blocks_per_worker
        end_nonce = (i + 1) * num_blocks_per_worker
        worker = Miner(i, block, start_nonce, end_nonce, result_queue, stop_event)
        workers.append(worker)

    # iniciar trabajadores
    for worker in workers:
        worker_thread = threading.Thread(target=worker.run)
        worker_thread.start()

    # esperar hasta que se encuentre un nonce correcto
    winning_worker_id, nonce = result_queue.get()
    stop_event.set()

    # verificar que el nonce encontrado sea correcto
    block.nonce = nonce
    if block.hash()[:block.difficulty] != '0' * block.difficulty:
        print("Nonce incorrecto encontrado")
        return

    # agregar bloque a la cadena de bloques
    blockchain.add_block(block)

    end_time = time.time()
    print("Bloque minado en", round(end_time - start_time, 2), "segundos por el trabajador", winning_worker_id)
    print("Hash del bloque:", block.hash())
    print("La dificultad actual es: ", dif)

if __name__ == '__main__':
    # crear bloque génesis
    genesis_block = Block("Genesis Block", "0")
    blockchain = Blockchain(genesis_block)
    
    
    # Preguntar al usuario la dificultad inicial del minado
    dif = int(input("Ingrese la dificultad inicial del minado: "))
    num_workers = int(input("Ingrese la cantidad de trabajadores con los que desea trabajar: "))
    
    # Mostrar el menú y ejecutar las opciones elegidas por el usuario
    while True:
        print("\n--- MENÚ ---")
        print("1. Agregar un nuevo bloque")
        print("2. Mostrar la lista de bloques con su información respectiva")
        print("3. Cerrar el programa")
        option = input("Elija una opción: ")

        if option == "1":
            # minar un bloque
            hex_receiver, hex_sender, amount = get_transaction_data()
            block = Block(hex_sender + "  ->  " + hex_receiver, blockchain.blocks[-1].hash(), int(amount), difficulty=dif)
            mine(block, blockchain, num_workers)
            dif = dif + 1

        elif option == "2":
            # mostrar la lista de bloques con su información respectiva
            for i, block in enumerate(blockchain.blocks):
                print(f"\n--- Bloque {i} ---")
                print(f"Datos: {block.data}")
                print(f"Hash del bloque: {block.hash()}")
                print(f"Hash del bloque anterior: {block.previous_block_hash}")
                print(f"Monto: {block.amount}")
                print(f"Nonce: {block.nonce}")
                print(f"Dificultad: {block.difficulty}")

        elif option == "3":
            # cerrar el programa
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida, por favor elija otra.")
    
        # verificar la integridad de la cadena de bloques
        print("La cadena de bloques es válida:", blockchain.is_chain_valid())
