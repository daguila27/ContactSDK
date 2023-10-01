
from ContactSDK.Contact.Zone import Zone
##cada figura implementa Zone para definir un area
## de contacto con las mismas dimensiones (que si misma)

class Square:
    zone = 0
    size = 0
    origin = [0,0]
    def __init__(self, size, origin):
        self.size = size
        self.origin = origin
        self.zone = Zone(size, size, origin)


    def setOnContact(self, onContact):
        self.zone.onContact = onContact

    def checkContact(self, contact):
        self.zone.checkContact(contact)    