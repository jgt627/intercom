# Llamamos a la librerias de socket para utilizar udp
# Y pyaudio para enviar audio
import socket
import pyaudio

# Formato que llevara el audio, canales,...
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# Recibimos audio usando udp
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Socket escucha por el puerto indicado
s.bind(("0.0.0.0", 50007))
s.listen(1)
# Si se crea la conexion hace esta parte
conn, addr = s.accept()
print 'Connected by', addr

# Creamos una variable para pyaudio y despues
# Creamos otra necesaria para el envio de audio
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

frames = []
# Iniciamos el envio de audio
stream.start_stream()


def main():


# Igualamos los datos a lo que recibimos de la conexion
    data = conn.recv(CHUNK)
# Si los datos no son nulos escribimos esos datos, es decir, el audio

    while data != '':
        stream.write(data)
        data = conn.recv(CHUNK)
        frames.append(data)

# Si no hay datos paramos el audio, cerramos la conexion y terminamos de usar
# pyaudio
    stream.stop_stream()
    stream.close()
    p.terminate()
    conn.close()

if __name__ == '__main__':
    main()