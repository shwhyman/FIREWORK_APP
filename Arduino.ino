void setup() 
{
  Serial.begin(9600); 
  
}

void loop() 
{
  
  String content = "";
  if(Serial.available()){
    
    content = Serial.readString();
    
    int len = count(content, ',');
    len += 1; 
  
    long data[len];
    for (int i = 0; i < len; i++){
      int index = content.indexOf(",");
      data[i] = atol(content.substring(0, index).c_str());
      content = content.substring(index+1); 
      }

    for (int i = 0; i < len; i++){
      digitalWrite(data[i], HIGH);
    }
    delay(1000); 
    for (int i = 0; i < len; i++){
      digitalWrite(data[i], LOW);
    } 

  
  }
  
}

int count(String haystack, char needle){

  int count = 0;
  for(int i=0; i<haystack.length(); i++){
      if(haystack[i] == needle){
          count++;
      }
  }
  return count;
}

  


