"""_summary_
制御信号 Pwm を出力するサーボモーターのクラス

テストサーボ
GWServo
S03T2BBMG

"""
from Actuator import Actuator
import pigpio
from typing import Any

class PWMServo(Actuator):
    def __init__(self,pi, name: str, driver: str, param: dict, weight: dict[str, float], response: dict[str, Any]):
        self.name = name
        self.pi = pi
        self.driver = driver
        self.param = param
        self.weight = weight
        self.response = response
    
        self.pwmPin : int = int(param['pwmPin'])
        self.returnDegIndex : int = int(param['degReturnIndex'])
        if('Mode' not in param):
            self.mode : int = 0
        else:
            self.mode : int = int(param['Mode'])
        self.pwm = 0.0
        if(response['type'] == "polynomial" or response['type'] == "linear"):
            self.coefficients = [float(x) for x in response['coefficient'].split(",")]
            self.response['type'] = "polynomial"
            
        self.initPins()
    
    def initPins(self):
        """各ピンの初期化
        pwmPinのみしか使わないので、pwmPinのみ初期化する
        """
        self.pi.set_mode(self.pwmPin, pigpio.OUTPUT)    
    
    
    def update(self,u):
        # PWMサーボへの指令送信コードはここに追加
        tempU = 0.0
        self.pwm = 0.0
        # 重み付き和を計算
        for weight in self.weight:
            tempU += u[int(weight["index"])] * weight["weight"]
        
        #print(f"Calculated weighted input: {tempU}")
        
        # 応答関数に基づいて速度を計算
        if(self.response['type'] == "polynomial"):
            for i, coeff in enumerate(self.coefficients):
                self.pwm += coeff * (tempU ** (self.coefficients.__len__() - 1 - i))
        
        
        #print(f"Calculated PWM: {self.pwm}")
        
        if(self.mode == 0):
            
            self.pwm = max(min(self.pwm, 1.0), 0.0)  # 0から1の範囲に制限
            
            self.pwm = (self.pwm) * 2000 + 500  # 0から1の値を500-2500の範囲に変換
            if(self.pwm < 500):
                self.pwm = 100
            elif(self.pwm > 2500):
                self.pwm = 2500
            
            #print(f"Converted PWM: {self.pwm}")
            self.pi.set_servo_pulsewidth(self.pwmPin, int(self.pwm))  # 中央
       
        else:
            self.pwm = max(min(self.pwm, 1.0), -1.0)  # -1から1の範囲に制限
                       
            self.pwm = (self.pwm) * 1000 + 1500  # -1から1の値を500-2500の範囲に変換
            if(self.pwm < 500):
                self.pwm = 500
            elif(self.pwm > 2500):
                self.pwm = 2500
            
            #print(f"Converted PWM: {self.pwm}")
            self.pi.set_servo_pulsewidth(self.pwmPin, int(self.pwm))  # 中央
        
        
        #print(f"Converted PWM: {self.pwm}")
        self.pi.set_servo_pulsewidth(self.pwmPin, int(self.pwm))  # 中央
                    

    def getFeedbackList(self)-> list[list]:
        # エンコーダーの値や現在の速度などを取得するコードはここに追加
    
        if(1 <= self.returnDegIndex <= 4):
            # PWMの値から角度を計算
            deg = (self.pwm - 500) / (2500 - 500) * 180  
            
            return [[self.returnDegIndex, deg]]
        return []
        
    def stop(self):
        pass
    
