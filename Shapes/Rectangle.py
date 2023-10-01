from ContactSDK.Contact.Zone import Zone

class Rectangle:
    zone = 0
    width = 0
    height = 0
    origin = [0,0]
    def __init__(self, width, height, origin):
        self.width = width
        self.height = height
        self.origin = origin
        self.zone = Zone(width, height, origin)


    def setOnContact(self, onContact):
        self.zone.onContact = onContact

    def checkContact(self, contact):
        self.zone.checkContact(contact) 