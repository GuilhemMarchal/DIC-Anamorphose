import yaml
import os.path, sys
import numpy as np
import cv2 as cv2

class Deck():
    """
    A class to parse input data
    
    Attributes
    ----------
    inputpath : str
        The file location of the deck
    
    Methods
    -------
    Images():
        Loads all the speckle sheets in one list
    """
    def __init__(self, inputpath):
        """
        Parameters
        ----------
        inputpath : str
            The file location of the deck
        """
        self.inputpath = inputpath
        if not os.path.exists(self.inputpath):
            print("File " + self.inputpath + " not found")
            sys.exit(1)
        else:
            with open(self.inputpath, 'r') as f:
                try: 
                    self.doc = yaml.load(f, Loader=yaml.UnsafeLoader)
                    self.deck = self.doc['Deck']
                    self.Camera = self.deck['Camera']
                    self.Focal_length = float(self.Camera['Focal_length'])
                    self.Sensor_height = float(self.Camera['Sensor_height'])

                    self.Input_Speckle = self.deck['Input_speckle']
                    self.Step = int(self.Input_Speckle['Step'])
                    self.Begining = int(self.Input_Speckle['Begining'])
                    self.Height = float(self.Input_Speckle['Height'])
                    self.Width = float(self.Input_Speckle['Width'])
                    self.Path = self.Input_Speckle['Path']
                    self.Generic_name = self.Input_Speckle['Generic_name']

                    self.Surface = self.deck['Surface']
                    self.Angle = int(self.Surface['Angle'])
                    self.Length_Surface = float(self.Surface['Length_Surface'])
                    self.Width_Surface = float(self.Surface['Width_Surface'])
                    self.Dist_cam = float(self.Surface['Dist_cam'])
                    self.Radius = float(self.Surface['Radius'])
                    self.Surface_type = self.Surface['Surface_type']
                    if self.Surface_type =='Plan':
                        self.a = -np.sin((self.Angle+90)*np.pi/180)
                        self.b = 0
                        self.c = -np.cos((self.Angle+90)*np.pi/180)
                        self.Wingframe = np.array([[ float(self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2),  float(0)        , float(-np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                      [ float(self.Dist_cam + np.sin(self.Angle*np.pi/180)*self.Length_Surface/2) ,    float(0)      ,  float(np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                      [ float(self.Dist_cam),  float(self.Width_Surface/2)         , float(0)],
                                      [ float(self.Dist_cam), float(-self.Width_Surface/2)         , float(0)]])
                        self.Position = self.Wingframe[0]
                        self.NbImageH = int(self.Width_Surface/self.Width)+1
                        self.NbImageV = int(self.Length_Surface*np.cos(self.Angle*np.pi/180)/self.Height)+1
                        self.Z_proj = self.Height*(self.NbImageV-1)*self.Wingframe[1,0]/self.Wingframe[0,0]
                        self.Surface_Height = self.Wingframe[1,2]-self.Wingframe[0,2]
                        while (self.Z_proj - self.Surface_Height) >= 0 and (self.NbImageV) >1:
                            self.NbImageV -= 1
                            self.Z_proj = self.Z_proj/self.NbImageV*(self.NbImageV-1)
                        self.NbImage = self.NbImageH*self.NbImageV
                        self.Position_centre = np.zeros([self.NbImage,3])
                        self.coeffdir_Surface = np.tan((90-self.Angle)*np.pi/180)
                        for i in range(1,self.NbImageV+1):
                            self.Y_image = self.Width_Surface/2
                            if i > 1:
                                self.Z_image = (i-1)*self.Height+self.Wingframe[0,2]
                                self.coeffdir_Proj = self.Z_image/self.Wingframe[0,0]
                                self.X_proj = (self.Wingframe[0,2]-(self.coeffdir_Surface*self.Wingframe[0,0]))/(self.coeffdir_Proj-self.coeffdir_Surface)
                                self.Y_image = (self.Width_Surface/2)*(self.Wingframe[0,0]/self.X_proj)
                                self.YM_image = self.Y_image - (self.NbImageH-1)*self.Width
                                self.YM_proj = self.YM_image*(self.X_proj/self.Wingframe[0,0])
                                if self.YM_proj < -self.Width_Surface/2:
                                    self.NbImageV -= 1
                                    self.NbImage -= 1
                                    np.delete(self.Position_centre,-1)
                            for j in range(1,self.NbImageH+1):
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),0] = self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),1] = self.Y_image - self.Width/2 - (j-1)*self.Width
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),2] = self.Height/2 - np.cos(self.Angle*np.pi/180)*self.Length_Surface/2+(i-1)*self.Height
                    elif self.Surface_type =='Cylindre':
                        self.a = np.sin((self.Angle)*np.pi/180)
                        self.b = 0
                        self.c = np.cos((self.Angle)*np.pi/180)
                        self.Width_Surface = 2*self.Radius
                        self.Wingframe = np.array([[ float(self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2),  float(0)        , float(-np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                        [ float(self.Dist_cam + np.sin(self.Angle*np.pi/180)*self.Length_Surface/2) ,    float(0)      ,  float(np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                        [ float(self.Dist_cam + self.Radius*np.cos(self.Angle*np.pi/180)),  float(self.Radius)         , float(-self.Radius*np.sin(self.Angle*np.pi/180))],
                                        [ float(self.Dist_cam + self.Radius*np.cos(self.Angle*np.pi/180)), float(-self.Radius)         , float(-self.Radius*np.sin(self.Angle*np.pi/180))]])
                        self.Position = np.array([self.Wingframe[2][0],0,self.Wingframe[2][2]])
                        self.NbImageH = int(self.Width_Surface/self.Width)+1
                        self.NbImageV = int((self.Length_Surface*np.cos(self.Angle*np.pi/180)+self.Radius*np.sin(self.Angle*np.pi/180))/self.Height)+1
                        self.Z_proj = (self.Height*(self.NbImageV-1)-self.Radius*np.sin(self.Angle*np.pi/180))*self.Wingframe[1,0]/self.Wingframe[0,0]
                        self.Surface_Height = self.Wingframe[1,2]-self.Wingframe[0,2]
                        while (self.Z_proj - self.Surface_Height) >= 0 and (self.NbImageV) >1:
                            self.NbImageV -= 1
                            self.Z_proj = self.Z_proj/(self.Height*self.NbImageV-self.Radius*np.sin(self.Angle*np.pi/180))*(self.Height*(self.NbImageV-1)-self.Radius*np.sin(self.Angle*np.pi/180))
                        self.NbImage = self.NbImageH*self.NbImageV
                        self.Position_centre = np.zeros([self.NbImage,3])
                        for i in range(1,self.NbImageV+1):
                            for j in range(1,self.NbImageH+1):
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),0] = self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),1] = self.Width_Surface/2 - self.Width/2 - (j-1)*self.Width
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),2] = self.Height/2 - np.cos(self.Angle*np.pi/180)*self.Length_Surface/2 - self.Radius*np.sin(self.Angle*np.pi/180) +(i-1)*self.Height
                

                    self.Output_Speckle = self.deck['Output_speckle']
                    self.Height_printable = float(self.Output_Speckle['Height_printable'])
                    self.Width_printable = float(self.Output_Speckle['Width_printable'])
                    self.Print_path = self.Output_Speckle['Print_path']

                except KeyError:
                    self.Camera = self.doc['Camera']
                    self.Focal_length = float(self.Camera['Focal_length'])
                    self.Sensor_height = float(self.Camera['Sensor_height'])

                    self.Input_Speckle = self.doc['Input_speckle']
                    self.Step = int(self.Input_Speckle['Step'])
                    self.Begining = int(self.Input_Speckle['Begining'])
                    self.Height = float(self.Input_Speckle['Height'])
                    self.Width = float(self.Input_Speckle['Width'])
                    self.Path = self.Input_Speckle['Path']
                    self.Generic_name = self.Input_Speckle['Generic_name']

                    self.Surface = self.doc['Surface']
                    self.Angle = int(self.Surface['Angle'])
                    self.Length_Surface = float(self.Surface['Length_Surface'])
                    self.Width_Surface = float(self.Surface['Width_Surface'])
                    self.Dist_cam = float(self.Surface['Dist_cam'])
                    self.Radius = float(self.Surface['Radius'])
                    self.Surface_type = self.Surface['Surface_type']
                    if self.Surface_type =='Plan':
                        self.a = -np.sin((self.Angle+90)*np.pi/180)
                        self.b = 0
                        self.c = -np.cos((self.Angle+90)*np.pi/180)
                        self.Wingframe = np.array([[ float(self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2),  float(0)        , float(-np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                      [ float(self.Dist_cam + np.sin(self.Angle*np.pi/180)*self.Length_Surface/2) ,    float(0)      ,  float(np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                      [ float(self.Dist_cam),  float(self.Width_Surface/2)         , float(0)],
                                      [ float(self.Dist_cam), float(-self.Width_Surface/2)         , float(0)]])
                        self.Position = self.Wingframe[0]
                        self.NbImageH = int(self.Width_Surface/self.Width)+1
                        self.NbImageV = int(self.Length_Surface*np.cos(self.Angle*np.pi/180)/self.Height)+1
                        self.Z_proj = self.Height*(self.NbImageV-1)*self.Wingframe[1,0]/self.Wingframe[0,0]
                        self.Surface_Height = self.Wingframe[1,2]-self.Wingframe[0,2]
                        while (self.Z_proj - self.Surface_Height) >= 0 and (self.NbImageV) >1:
                            self.NbImageV -= 1
                            self.Z_proj = self.Z_proj/self.NbImageV*(self.NbImageV-1)
                        self.NbImage = self.NbImageH*self.NbImageV
                        self.Position_centre = np.zeros([self.NbImage,3])
                        self.coeffdir_Surface = np.tan((90-self.Angle)*np.pi/180)
                        for i in range(1,self.NbImageV+1):
                            self.Y_image = self.Width_Surface/2
                            if i > 1:
                                self.Z_image = (i-1)*self.Height+self.Wingframe[0,2]
                                self.coeffdir_Proj = self.Z_image/self.Wingframe[0,0]
                                self.X_proj = (self.Wingframe[0,2]-(self.coeffdir_Surface*self.Wingframe[0,0]))/(self.coeffdir_Proj-self.coeffdir_Surface)
                                self.Y_image = (self.Width_Surface/2)*(self.Wingframe[0,0]/self.X_proj)
                                self.YM_image = self.Y_image - (self.NbImageH-1)*self.Width
                                self.YM_proj = self.YM_image*(self.X_proj/self.Wingframe[0,0])
                                if self.YM_proj < -self.Width_Surface/2:
                                    self.NbImageV -= 1
                                    self.NbImage -= 1
                                    np.delete(self.Position_centre,-1)
                            for j in range(1,self.NbImageH+1):
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),0] = self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),1] = self.Y_image - self.Width/2 - (j-1)*self.Width
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),2] = self.Height/2 - np.cos(self.Angle*np.pi/180)*self.Length_Surface/2+(i-1)*self.Height
                    elif self.Surface_type =='Cylindre':
                        self.a = np.sin((self.Angle)*np.pi/180)
                        self.b = 0
                        self.c = np.cos((self.Angle)*np.pi/180)
                        self.Width_Surface = 2*self.Radius
                        self.Wingframe = np.array([[ float(self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2),  float(0)        , float(-np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                        [ float(self.Dist_cam + np.sin(self.Angle*np.pi/180)*self.Length_Surface/2) ,    float(0)      ,  float(np.cos(self.Angle*np.pi/180)*self.Length_Surface/2)],
                                        [ float(self.Dist_cam + self.Radius*np.cos(self.Angle*np.pi/180)),  float(self.Radius)         , float(-self.Radius*np.sin(self.Angle*np.pi/180))],
                                        [ float(self.Dist_cam + self.Radius*np.cos(self.Angle*np.pi/180)), float(-self.Radius)         , float(-self.Radius*np.sin(self.Angle*np.pi/180))]])
                        self.Position = np.array([self.Wingframe[2][0],0,self.Wingframe[2][2]])
                        self.NbImageH = int(self.Width_Surface/self.Width)+1
                        self.NbImageV = int((self.Length_Surface*np.cos(self.Angle*np.pi/180)+self.Radius*np.sin(self.Angle*np.pi/180))/self.Height)+1
                        self.Z_proj = (self.Height*(self.NbImageV-1)-self.Radius*np.sin(self.Angle*np.pi/180))*self.Wingframe[1,0]/self.Wingframe[0,0]
                        self.Surface_Height = self.Wingframe[1,2]-self.Wingframe[0,2]
                        while (self.Z_proj - self.Surface_Height) >= 0 and (self.NbImageV) >1:
                            self.NbImageV -= 1
                            self.Z_proj = self.Z_proj/(self.Height*self.NbImageV-self.Radius*np.sin(self.Angle*np.pi/180))*(self.Height*(self.NbImageV-1)-self.Radius*np.sin(self.Angle*np.pi/180))
                        self.NbImage = self.NbImageH*self.NbImageV
                        self.Position_centre = np.zeros([self.NbImage,3])
                        for i in range(1,self.NbImageV+1):
                            for j in range(1,self.NbImageH+1):
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),0] = self.Dist_cam - np.sin(self.Angle*np.pi/180)*self.Length_Surface/2
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),1] = self.Width_Surface/2 - self.Width/2 - (j-1)*self.Width
                                self.Position_centre[(i-1)*self.NbImageH+(j-1),2] = self.Height/2 - np.cos(self.Angle*np.pi/180)*self.Length_Surface/2 - self.Radius*np.sin(self.Angle*np.pi/180) +(i-1)*self.Height
                
                    self.Output_Speckle = self.doc['Output_speckle']
                    self.Height_printable = float(self.Output_Speckle['Height_printable'])
                    self.Width_printable = float(self.Output_Speckle['Width_printable'])
                    self.Print_path = self.Output_Speckle['Print_path']


    def Images(self):
        """
        Returns
        ----------
        list
            A list of numpy arrays that represents the speckle image 
        """
        list=[]
        i=0
        while len(list) < self.NbImage:
            if type((cv2.imread(self.Path + '/' + self.Generic_name + str(i) + '.png'))) != type(None):
                print(self.Generic_name + str(i) + '.png loaded')
                list.append(cv2.imread(self.Path + '/' + self.Generic_name + str(i) + '.png'))
            elif i == 100:
                print('No .png file found until '+ self.Generic_name + str(100)+'. Research abandoned.\nProgram stop')
                sys.exit()
            else:
                print(self.Generic_name + str(i) + '.png not found')
            i+=1
        return list