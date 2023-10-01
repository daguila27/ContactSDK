import cv2
import os
import sys
from threading import Timer
import numpy as np
import pygame
from pygame import *
from ContactSDK.Contact.Capture import Capture
from ContactSDK.Shapes.Rectangle import Rectangle


Blanco = (255, 255, 255)


class Contact:
    wallDetectionMode = 1
    
    count = 0
    cuenta = 0

    ready = False

    screenWidth = 0
    screenHeight = 0

    frontCapture = Capture(0, 800, 600)
    wallCapture = Capture(0, 800, 600)

    def __init__(self, screenWidth, screenHeight, proportionFactor=10):
        pygame.init()
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.sonidoColision = pygame.mixer.Sound(
            "sonidos/marcarJugada.mp3")
        
        self.frontCapture = Capture(0, screenWidth, screenHeight)
        self.frontCapture.proportionFactor = proportionFactor
        
        ##self.wallCapture = Capture(1, screenWidth, screenHeight)
        self.wallCapture = Capture(0, screenWidth, screenHeight)
        self.wallCapture.proportionFactor = proportionFactor
        # self.wallCapture.umbral = 30
        
        if self.wallDetectionMode == 1:
            self.wallCapture.shapes = [Rectangle(60, 600, [0,0])]


    def captureIteration(self):
        self.frontCapture.capture()
        self.wallCapture.capture()

    def startCameras(self):
        self.frontCapture.start()
        self.wallCapture.start()
        self.ready = True

    def start(self):
        # espera 10 segundos
        r = Timer(10.0, self.startCameras, ())
        r.start()

    debugMode=True
    def showCapture(self):
        if not self.debugMode: return
        self.frontCapture.show('Front Vision')
        self.wallCapture.show('Wall Vision')

    def getCaptureFront(self):
        return self.frontCapture.captureImage

    def getCaptureWall(self):
        return self.wallCapture.captureImage


    sonidoColision = 0

    def appendShape(self, shape):
        self.frontCapture.shapes.append(shape) 
        if self.wallDetectionMode == 0: self.wallCapture.shapes.append(shape)


    ##luego de hacer contacto, deshabilita la zonas por 350 milisegundos
    delayAfterContact = False
    delayInMiliseconds = 0.350
    def toggleDelayAfterContact (self):
        self.delayAfterContact = not self.delayAfterContact

    def getShapes(self):
        return self.frontCapture.shapes

    def checkShapes(self):
        def executeContact (zone):
            zone.onContact(zone)
            self.delayAfterContact = True
            ##espera 350 milisegundos 
            r = Timer(self.delayInMiliseconds, self.toggleDelayAfterContact, ())
            r.start() 

        if self.ready and self.delayAfterContact is False:
            contactWall = False
            contactFront = False
            if self.wallDetectionMode == 0:
                contactFront = self.frontCapture.checking()
                if contactFront is not False:
                    contactWall = self.wallCapture.checking()
                                   
            elif self.wallDetectionMode == 1:
                contactWall = self.wallCapture.checking()
                if contactWall is not False:
                    contactFront = self.frontCapture.checking()

            if contactWall is not False and contactFront is not False and self.delayAfterContact is False: 
                executeContact(contactFront)            


    def check (self):
        self.captureIteration()
        ##verifica alguna colisión en el tablero
        self.checkShapes()
        self.showCapture()


            
    def gotoWallCalibrationCamera(self):
        self.calibratePage = 'wall-camera'
    
    def gotoGame(self):
        self.currentStep = self.onGameStepKey

    calibrateCamerasStepKey = 'calibrate-cameras' 
    onGameStepKey = 'on-game' 
    currentStep = calibrateCamerasStepKey ##'on-game'

    calibratePage = 'front-camera' ##wall-camera
    selectingPoint = 0
    selectingWallPoint = 0
    def calibrateCameras(self):    
        if self.calibratePage == 'front-camera':
            self.frontCapture.onExitCalibration = self.gotoWallCalibrationCamera
            self.frontCapture.calibrateContact("Calibrate FRONT Camera")

        elif self.calibratePage == 'wall-camera':
            self.wallCapture.onExitCalibration = self.gotoGame
            wallDetectionMode = self.wallDetectionMode
            def selectWallPoint (x, y):
                selfCapture = self.wallCapture
                if wallDetectionMode == 0:
                    selfCapture.shapeContactPoint[selfCapture.selectingPoint] = [x, y]
                    if selfCapture.selectingPoint == len(selfCapture.shapeContactPoint)-1:
                        #vuelve al inicio
                        selfCapture.selectingPoint = 0
                    elif selfCapture.selectingPoint < len(selfCapture.shapeContactPoint)-1:
                        selfCapture.selectingPoint = selfCapture.selectingPoint+1
                elif wallDetectionMode == 1:        
                    selfCapture.shapeContactPoint[selfCapture.selectingPoint] = [x,y]
                    selfCapture.shapeContactPoint[selfCapture.selectingPoint+1] = [selfCapture.screenWidth,y]
                    if selfCapture.selectingPoint == 0:
                        selfCapture.selectingPoint = 2
                    else:
                        selfCapture.selectingPoint = 0

            self.wallCapture.selectCalibrationPoint = selectWallPoint
            self.wallCapture.calibrateContact("Calibrate WALL Camera")
        return True


    primeraEjecucion = True
    def iteration(self):
        self.captureIteration()
        if self.currentStep == self.calibrateCamerasStepKey:
            self.calibrateCameras()
        elif self.currentStep == self.onGameStepKey:
            if self.primeraEjecucion:
                self.primeraEjecucion = False 
                ##captura las imagenes de muestra
                self.start()
            self.checkShapes()
            self.showCapture()

    def finish(self):
        self.frontCapture.finish()
        self.wallCapture.finish()
        cv2.destroyAllWindows()
