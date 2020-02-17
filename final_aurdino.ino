/*Motor Driver Configuration-
MOTOR-A
Pin 1- High-Clockwise
Pin 2- High- Anticlockwise
MOTOR-B
Pin 3- High-Clockwise
Pin 4- High- Anticlockwise*/
#include<Servo.h>
Servo myservo1,myservo2; //Servo Objects
int pos=0; //Initial Position of both the servos
int l1=6; // Connect l1 to Pin 1 of Motor Driver
int l2=7; //Connect l2 to pin 2 
int r1=9; //connect r1 to pin 3
int r2=8;//connect r2 to pin 4
int ena=5; //Enable A, Pin 5 is PWM for controlling speed
int enb=11;//Enable B, Pin 11 is PWM for controlling speed of motor
int speedr=69; //Chenge the values in order to configure perfectly of sppedl and speedr
int speedl=57;
char  val;
int rled=4;
int gled=3;
int bled=2;
char data;
int lm;
int rm;
int f;
int b;
void forward()
{
  //Both motors will run clockwise here
  analogWrite(ena,speedl); //These tell motor with which speed it needs to move
  analogWrite(enb,speedr);
  digitalWrite(l1,HIGH);
  digitalWrite(l2,LOW);
  digitalWrite(r1,LOW);
  digitalWrite(r2,HIGH);
}

void reverse()
{
  //Both motors will run anti clockwise here
  analogWrite(ena,speedl+1);
  analogWrite(enb,speedr);
  digitalWrite(l1,LOW);
  digitalWrite(l2,HIGH);
  digitalWrite(r1,HIGH);
  digitalWrite(r2,LOW);
}

void right()
{
  //Similar to right()
  //speedl=125;
  analogWrite(ena,speedl-8);
  analogWrite(enb,speedr-10);
  digitalWrite(l1,LOW);
  digitalWrite(l2,HIGH);
  digitalWrite(r1,LOW);
  digitalWrite(r2,HIGH); 
}


void left()
{//speedr=90;
  //Motor A goes clockwise and Motor B goes anti clockwise for very fast turning (keeping bot steady, it turns)
  analogWrite(ena,speedl-8);
  analogWrite(enb,speedr-10);
  digitalWrite(l1,HIGH);
  digitalWrite(l2,LOW);
  digitalWrite(r1,HIGH);
  digitalWrite(r2,LOW); 
}

void RIGHT()
{
  //Similar to right()
  //speedl=125;
  analogWrite(ena,speedl+7);
  analogWrite(enb,speedr+9);
  digitalWrite(l1,LOW);
  digitalWrite(l2,HIGH);
  digitalWrite(r1,LOW);
  digitalWrite(r2,HIGH); 
}


void LEFT()
{//speedr=90;
  //Motor A goes clockwise and Motor B goes anti clockwise for very fast turning (keeping bot steady, it turns)
  analogWrite(ena,speedl+7);
  analogWrite(enb,speedr+9);
  digitalWrite(l1,HIGH);
  digitalWrite(l2,LOW);
  digitalWrite(r1,HIGH);
  digitalWrite(r2,LOW); 
}
void Stop()
{
  //Stop the bot
  analogWrite(ena,0);
  analogWrite(enb,0);
  digitalWrite(l1,LOW);
  digitalWrite(l2,LOW);
  digitalWrite(r1,LOW);
  digitalWrite(r2,LOW);
}

void u2d()
{ //For servo movement from up to down
  for (pos = 20; pos <= 75; pos += 1) { // goes from intial degrees to final degrees
    // in steps of 1 degree
    myservo1.write(pos);
    //delay(20); 
    myservo2.write(180-pos); // tell servo to go to position in variable 'pos'
    delay(40);                       
  }
}

void d2u()
{
  //For servo movement from down to up
  for (pos = 75; pos >= 20; pos -= 1) { // goes from final degrees to initial degrees
    myservo1.write(pos);
    //delay(20);
    myservo2.write(180-pos);// tell servo to go to position in variable 'pos'
    delay(40);                       
  }
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  myservo1.attach(12);
  myservo2.attach(13);
 d2u();//Set initial servos to 'pos' initial degrees
  pinMode(l1,OUTPUT);
  //pinMode(l2,OUTPUT);
  pinMode(r1,OUTPUT);
  pinMode(r2,OUTPUT);
  pinMode(ena,OUTPUT);
  pinMode(enb,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(rled,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(bled,OUTPUT);
  pinMode(10,OUTPUT);
  //Serial.write('1');
}

void loop() {
    //reverse();
    //delay(3000);
    //Stop();
    //delay(1000);
    //bright();
    //delay(5000);

    

  if(Serial.available() > 0)
  {
    data=Serial.read();
    Serial.print(data);

    if(data == 'f'){
      forward();
      //digitalWrite(rled,HIGH);
    }

    else if(data == 'b'){
      reverse();
      //digitalWrite(rled,LOW);
    }

    else if(data == 'r'){
      right();
      //Serial.println(data);
      //delay(90); // 
      //Stop();
    
    }
    else if(data == 'l'){
      left();
      //delay(60); //45
      //Stop();
    }

    else if(data == 'R'){
      RIGHT();
      //Serial.println(data);
      //delay(90); // 
      //Stop();
    
    }
    else if(data == 'L'){
      LEFT();
      //delay(60); //45
      //Stop();
    }

     else if(data == 'U'){
      d2u();
      //delay(60); //45
      //Stop();
    }
     else if(data == 'D'){
      u2d();
      //delay(60); //45
      //Stop();
    }
    
    else if(data == 's')
    {
      Stop();
      }
     else if(data=='N')
     {
      digitalWrite(bled,HIGH);
     }
     else if(data=='F')
     {
        digitalWrite(bled,LOW);
      }

      else if(data=='G')
     {
      digitalWrite(gled,HIGH);
     }
     else if(data=='g')
     {
        digitalWrite(gled,LOW);
      }

      else if(data=='E')
     {
      digitalWrite(rled,HIGH);
     }
     else if(data=='e')
     {
        digitalWrite(rled,LOW);
      }
  
  }
}
