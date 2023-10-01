import cv2
import os
import sys
from threading import Timer
import numpy as np
import pygame
from pygame import *
Blanco = (255, 255, 255)
STEP_CALIBRATE = 'calibrate'
STEP_ON_GAME = 'onGame'

class Capture:

    captureCamera = 0
    umbral = 30
    proportionFactor = 10

    shapes = []
    captureImage = 0
    captureImageFirts = 0
    shapeContactPoint = [[0, 0], [800,0], [0, 600], [800, 600]]

    currentStep = STEP_CALIBRATE

    screenWidth = 800
    screenHeight = 600

    def __init__(self, camera = 0, screenWidth = 800, screenHeight = 600):
        self.captureCamera = cv2.VideoCapture(camera)
        self.screenWidth = screenWidth 
        self.screenHeight = screenHeight
        self.shapeContactPoint = [[0, 0], [screenWidth,0], [0, screenHeight], [screenWidth, screenHeight]]



    def geometricTranformCapture(self, captureImage):

        # Puntos de coordenadas del paralelogramo original
        original_points = np.array(self.shapeContactPoint, dtype=np.float32)

        # Puntos de coordenadas del rectángulo de destino (en el mismo orden: superior izquierdo, superior derecho, inferior izquierdo, inferior derecho)
        width = self.screenWidth # Ancho del rectángulo final
        height = self.screenHeight# Alto del rectángulo final
        destination_points = np.array([[0, 0], [width, 0], [0, height], [width, height]], dtype=np.float32)

        # Calcular la matriz de transformación
        transformation_matrix = cv2.getPerspectiveTransform(original_points, destination_points)

        # Aplicar la transformación a la imagen
        rectangular_image = cv2.warpPerspective(captureImage, transformation_matrix, (width, height))
 
        return rectangular_image

    def captureFrame(self):
        # camara 1
        ret1, frame = self.captureCamera.read()
        if ret1 == False:
            return False

        gris = frame
        if self.currentStep == STEP_ON_GAME:
            gris = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

        captureImage = cv2.resize(
            gris, (self.screenWidth, self.screenHeight))

        ##realiza tranformación geométrica
        if self.currentStep == STEP_ON_GAME: 
            captureImage = self.geometricTranformCapture(captureImage)

        return captureImage 

    def captureIteration(self):
        currentCapture = self.captureFrame()
        self.captureImage = currentCapture

    def captureFirts(self):
        currentCapture = self.captureFrame()
        self.captureImageFirts = currentCapture



    def showCalibrateArea(self): 
        borderWidth = 2 
        # dibuja la cruz
        cv2.line(self.captureImage, self.shapeContactPoint[0], self.shapeContactPoint[1], (255,255,255), borderWidth)
        cv2.line(self.captureImage, self.shapeContactPoint[1], self.shapeContactPoint[3], (255,255,255), borderWidth)
        cv2.line(self.captureImage, self.shapeContactPoint[3], self.shapeContactPoint[2], (255,255,255), borderWidth)
        cv2.line(self.captureImage, self.shapeContactPoint[2], self.shapeContactPoint[0], (255,255,255), borderWidth)    



    selectingPoint = 0

    def selectCalibrationPoint (self, x, y):
        self.shapeContactPoint[self.selectingPoint] = [x, y]
        if self.selectingPoint == len(self.shapeContactPoint)-1:
            #vuelve al inicio
            self.selectingPoint = 0
        elif self.selectingPoint < len(self.shapeContactPoint)-1:
            self.selectingPoint = self.selectingPoint+1

    def onExitCalibration(self):
        pass

    def calibrate(self, windowName = 'Calibrate DEFAULT Camera'):
        self.showCalibrateArea()
        ##abre vista camara frontal
        ##selecciona 4 puntos
        def clickImage (event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.selectCalibrationPoint(x,y)
            if event == cv2.EVENT_RBUTTONUP:
                self.currentStep = STEP_ON_GAME
                self.onExitCalibration()  
                cv2.destroyWindow(windowName)  


        cv2.setMouseCallback(windowName, clickImage)
        ##actualiza los puntos en self.frontShapeContactPoint
        cv2.imshow(windowName, self.captureImage)


    def drawCross (self, capture, px, py):
        # dibuja la cruz
        cv2.line(capture, ((px), (py)), ((px+self.proportionFactor),
                (py+self.proportionFactor)), Blanco, 1)
        cv2.line(capture, ((px), (py+self.proportionFactor)),
                ((px+self.proportionFactor), (py)), Blanco, 1)


    def checkObjectOnCapture(self, px, py, capture):
        # Recibe coordenada en pixeles (px,py)
        entero = 0
        promedio = 0
        resguardar = 0

        self.drawCross(capture, px, py)

        for ixx in range(self.proportionFactor):
            for iyy in range(self.proportionFactor):
                indexX = py+(ixx*2)
                indexY = px+(iyy*2)
                if len(capture) > indexX and len(capture[indexX]) > indexY:
                    entero += 1
                    promedio = promedio+int(capture[indexX, indexY])

        if entero > 0:
            resguardar = int(promedio/entero)
        return resguardar


    def checkContactOnZone(self, zone):
        ##identificar cuando el objeto tiene cero sombra
        for i in range(0, int(zone.width/self.proportionFactor)):  # foto camara 1
                for j in range(0, int(zone.height/self.proportionFactor)):
                    captureColor = self.checkObjectOnCapture(
                        zone.origin[0]+(i*self.proportionFactor),
                        zone.origin[1]+(j*self.proportionFactor),
                        self.captureImage
                    )
                    captureColorFirst = self.checkObjectOnCapture(
                        zone.origin[0]+(i*self.proportionFactor),
                        zone.origin[1]+(j*self.proportionFactor),
                        self.captureImageFirts
                    )
                    ##se oscurece o se ilumina
                    if (captureColorFirst-self.umbral) > captureColor or (captureColorFirst+self.umbral) < captureColor:
                        return True
        return False

    

    def checkContact(self):
        for shape in self.shapes:
            if shape.zone.disabled is False and self.checkContactOnZone(shape.zone):
                return shape.zone
        return False        


    ##
    # Start:
    #   1. Captura la primera imagen
    # Calibrate Contact (iteración):
    #   1. Muestra image para calibrar area de contacto
    # Show:
    #   1. Muestra la imagen
    # Capture (iteración):
    #   1. Captura imagen
    # Checking (iteración):
    #   1. Mapea imagen y contrasta con la primera
    # Finish:
    #   1. Cierra ventanas
    # ##

    def start(self):
        self.captureFirts()

    def calibrateContact(self, windowName = 'Calibration DEFAULT'):
        self.calibrate(windowName)

    def show(self, windowName = 'Camera DEFAULT'):
        cv2.imshow(windowName, self.captureImage) 

    def capture(self):
        self.captureIteration()

    def checking(self):
        return self.checkContact()   

    def finish(self):
        self.captureCamera.release()
        cv2.destroyAllWindows()           
