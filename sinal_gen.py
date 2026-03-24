import usb.core
import usb.util

# Conexão direta via PyUSB (sem PyVISA)
dev = usb.core.find(idVendor=0x5345, idProduct=0x1234)

if dev is None:
    print("Dispositivo sumiu novamente!")
else:
    print("Dispositivo acessível via PyUSB. Tentando reset...")
    dev.set_configuration()
    # Aqui a comunicação seria via endpoints (mais complexo)
    # Por isso o ideal é fazer o PyVISA funcionar acima.