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
int speedr=30; //Chenge the values in order to configure perfectly of sppedl and speedr
int speedl=37;
char  val;
int rled=13; 
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
  analogWrite(ena,speedl);
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
  analogWrite(ena,speedl);
  analogWrite(enb,speedr);
  digitalWrite(l1,LOW);
  digitalWrite(l2,HIGH);
  digitalWrite(r1,LOW);
  digitalWrite(r2,HIGH); 
}


void left()
{//speedr=90;
  //Motor A goes clockwise and Motor B goes anti clockwise for very fast turning (keeping bot steady, it turns)
  analogWrite(ena,speedl);
  analogWrite(enb,speedr);
  digitalWrite(l1,HIGH);
  digitalWrite(l2,LOW);
  digitalWrite(r1,HIGH);
  digitalWrite(r2,LOW); 
}

void stop()
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
  for (pos = 100; pos <= 180; pos += 1) { // goes from intial degrees to final degrees
    // in steps of 1 degree
    myservo1.write(pos); 
    myservo2.write(180-pos); // tell servo to go to position in variable 'pos'
    delay(20);                       
  }
}

void d2u()
{
  //For servo movement from down to up
  for (pos = 180; pos >= 100; pos -= 1) { // goes from final degrees to initial degrees
    myservo1.write(pos);
    myservo2.write(pos-100);// tell servo to go to position in variable 'pos'
    delay(20);                       
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  myservo1.attach(12);
  myservo2.attach(13);
  //u2d(pos,pos);  //Set initial servos to 'pos' initial degrees
  pinMode(l1,OUTPUT);
  //pinMode(l2,OUTPUT);
  pinMode(r1,OUTPUT);
  pinMode(r2,OUTPUT);
  pinMode(ena,OUTPUT);
  pinMode(enb,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(4,OUTPUT);
  pinMode(rled,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(bled,OUTPUT);
  pinMode(10,OUTPUT);
  //Serial.write('1');
}

void loop() {
  if(Serial.available() > 0){
    lm=Serial.parseInt();
    rm=Serial.parseInt();
    f=Serial.parseInt();
    b=Serial.parseInt();
    data = Serial.read();
    speedr=lm;
    speedl=rm;
    Serial.print(lm);
    Serial.print(' ');
    Serial.print(rm);
    Serial.print(' ');
    Serial.print(f);
    Serial.print(' ');
    Serial.println(b);
    //Serial.print(data);
    if(f==0 && b==0 && lm==0 && rm==0)
    {
      stop();
    }
  else if(f==1 && b==1){
    forward();
  }
  else if(f==0 && b==0){
    reverse();
  }
  else if(f==1 && b==0){
    right();
  }
  else if(f==0 && b==1){
    left();
  }
 // delay(2000);
  

    /*if(data == 'o'){
      digitalWrite(rled,HIGH);
    }

    else if(data == 'a'){
      digitalWrite(rled,LOW);
    }

    if(data == 'f'){
      forward();
      Serial.println(data);
      //delay(90); // 
      //stop();
    
    }
    else if(data == 'r'){
      fright();
      //delay(60); //45
      //stop();
    
    }
    else if(data == 'l'){
      fleft();
      //delay(60); //30
      //stop();
 
    }


    else if(data == 's')
    {
      stop();
      }
     
    //Serial.write('0');
    */
  }
}
