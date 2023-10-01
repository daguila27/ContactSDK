def defaultOnContact (self):
    return
class Zone:
    origin = [0,0]
    #ancho y alto de la sección en pixeles
    width = 0
    height = 0

    onContact = defaultOnContact
    disabled = False

    metadata = dict({})
    
    def __init__(self, width, height, origin, disabled = False):
        self.width = width
        self.height = height
        self.origin = origin
        self.disabled = disabled

    def setMetadata(self, meta):
        self.metadata = meta

    def checkContact(self, contact):
        if self.disabled: return False
        return contact.checkContact(self)

    def setOnContanct(self, onContact):
        self.onContact = onContact


    def setDisabled(self, dis = False):
        self.disabled = dis    

