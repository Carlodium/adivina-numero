import random

def adivina_el_numero():
    numero_secreto = random.randint(1, 100)
    intentos = 0
    
    print("¡Bienvenido al juego de Adivina el Número!")
    print("He pensado un número entre 1 y 100.")
    print("¿Puedes adivinar cuál es?")

    while True:
        try:
            entrada = input("Introduce tu número: ")
            if not entrada:
                print("Por favor, escribe algo.")
                continue
                
            estimacion = int(entrada)
            intentos += 1

            if estimacion < numero_secreto:
                print("Más alto...")
            elif estimacion > numero_secreto:
                print("Más bajo...")
            else:
                print(f"¡Felicidades! Has adivinado el número en {intentos} intentos.")
                break
        except ValueError:
            print("Por favor, introduce un número válido.")

if __name__ == "__main__":
    adivina_el_numero()
