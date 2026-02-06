Morse_Code_Chart = {
    'A':'.-', 'B':'-...',
    'C':'-.-.', 'D':'-..', 'E':'.',
    'F':'..-.', 'G':'--.', 'H':'....',
    'I':'..', 'J':'.---', 'K':'-.-',
    'L':'.-..', 'M':'--', 'N':'-.',
    'O':'---', 'P':'.--.', 'Q':'--.-',
    'R':'.-.', 'S':'...', 'T':'-',
    'U':'..-', 'V':'...-', 'W':'.--',
    'X':'-..-', 'Y':'-.--', 'Z':'--..',
    '1':'.----', '2':'..---', '3':'...--',
    '4':'....-', '5':'.....', '6':'-....',
    '7':'--...', '8':'---..', '9':'----.',
    '0':'-----',
    ',':'--..--', '.':'.-.-.-',
    '?':'..--..', '/':'-..-.', '-':'-....-',
    '(':'-.--.', ')':'-.--.-', ' ':' '
}

class Morse:

   Morse_Code = Morse_Code_Chart
   
   sent_box =  [ ]
   reply_box = [ ] 
 

   inital_msg = input('please input your message: ').upper()
   inital_msg_characters = list(inital_msg)
   sent_box.extend( inital_msg_characters)
   out_msg = [Morse_Code_Chart.get(x) for (x) in  sent_box]
 
 
   print(out_msg)

class  decode(Morse): 
    def decrypt(self): 
        inbox = self.out_msg
        Morse_Code = Morse_Code_Chart
 
        
        print(inbox)
        print(Morse_Code)
        for msg in inbox:
             if msg in Morse_Code: 
                 print(f"'{msg}' is a KEY -> value: {Morse_Code[msg]}")
             matching_keys = [k for k, v in Morse_Code.items() if v == msg]
             if matching_keys:
                 print(f"'{msg}' is a VALUE -> key(s): {matching_keys}")
 

                  
            
            
       
        


decode=decode()
decode.decrypt()
