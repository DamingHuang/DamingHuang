'use strict'

//DOM Document Object Model

let highscore=[]; // Array. To record the highest score.
let score = 10; //Number of times for click Check! button.
let secrectNumber = Math.round(Math.random()*100); // random number 1-100.
// document.getElementById("scorenumber").innerHTML = score;   //already in the fuction. NO NEED.

 const updateValue = function(){
    score--; // Score number will - 1 when you click the Check! button every time, until the number become 0.
    let userInput = document.getElementById("randomnumber").value; // A place can let user to input the value.
    let x = userInput; //we store userInput to the x value

    // document.getElementById("display").innerHTML = userInput;   // display on input number on ??? frame.
    document.getElementById("scoreNumber").innerHTML = score; //Display the score 



    // If you get 10 times wrong, Check! button will disabled.
    if (score==0){
        document.getElementById("display").innerHTML="&#128560 Lose!"; // output lose... text when someone wins. right container
        document.getElementById("randomnumber").disabled = true;  // disabled input box
        document.getElementById("checkButton").disabled = true; // disabled check button

        document.body.style.backgroundColor = '#F5EEF8'; // body background color
        document.getElementById("display").style.color = 'red'; // text color
        document.getElementById("titlebg").style.backgroundColor = '#D7BDE2'; // header background color
        document.getElementById("gameborder").style.borderColor = '#AF7AC5'; //  border color
        document.getElementById("scoreborder").style.borderColor = '#AF7AC5'; //  border color
        document.getElementById("gameborder").style.boxShadow = "10px 10px 10px #D2B4DE"; //  box shadow color
        document.getElementById("scoreborder").style.boxShadow = "10px 10px 10px #D2B4DE"; //  box shadow color
    }  



    // Input number matches secret number.
    if (userInput == secrectNumber){
        document.getElementById("p1").innerHTML="&#128523 Congrats! You Win The Game!"; // output congrats... text when someone wins. left container
        document.getElementById("display").innerHTML="&#128523 Congrats!"; // output congrats... text when someone wins. right container

        document.body.style.backgroundColor = '#D5F5E3'; // body background color
        document.getElementById("display").style.color = 'Gold'; // text color
        document.getElementById("titlebg").style.backgroundColor = '#82E0AA'; // header background color
        document.getElementById("gameborder").style.borderColor = '#58D68D'; //  border color
        document.getElementById("scoreborder").style.borderColor = '#58D68D'; //  border color
        document.getElementById("gameborder").style.boxShadow = "10px 10px 10px #76D7C4"; //  box shadow color
        document.getElementById("scoreborder").style.boxShadow = "10px 10px 10px #76D7C4"; //  box shadow color


        highscore.push(score); // push score into the array
        console.log(highscore); // for us to see what we have in the array
        document.getElementById("randomnumber").disabled = true; // disabled input box
        document.getElementById("checkButton").disabled = true; // disabled check button
        document.getElementById("highestScoreNumber").innerHTML=Math.max(...highscore); // to record highest score
    } 
    


    // Input Number is TOO HIGH.
    else if ( userInput > secrectNumber){
        document.getElementById("p1").innerHTML="&#128546 Too high"; // output high when someone input a number higher than secret number
     }


    // Input Number is TOO LOW.
    else if ( userInput < secrectNumber) {
        document.getElementById("p1").innerHTML="&#128543 Too low "; // output Too low when someone input a number lower than secret number
    }  


    // Input Number is not between 1 - 100 or nothing is input.
    if (x>100 || x<1) {
        document.getElementById("p1").innerHTML="&#9940 Invild Input/No Input."; // output Invild/No Input when someone input text, number<0, number>100, or didn't input anything. left container
    }


    console.log(secrectNumber);  // Secrect number display on console log
}



// Reset button function

 function resetGame(){
    score = 10; // reset to score = 10 as the default
    secrectNumber = Math.round(Math.random()*100); // reset random secret number 
    document.getElementById("scoreNumber").innerHTML = score; // reset the score
    document.getElementById("randomnumber").disabled = false; // enable input box
    document.getElementById("checkButton").disabled = false; // enable check button

    document.getElementById("p1").innerHTML = "&#127774 Start Guessing..."; // reset text. left container
    document.getElementById("display").innerHTML = "&#128563; ? ? ?"; // reset text. right container
    document.body.style.backgroundColor = '#D6EAF8'; // body background color
    document.getElementById("display").style.color = 'white'; // text color
    document.getElementById("titlebg").style.backgroundColor = '#AED6F1'; // header background color
    document.getElementById("display").style.borderColor = 'white'; //  border color
    document.getElementById("gameborder").style.borderColor = '#5DADE2'; //  border color
    document.getElementById("scoreborder").style.borderColor = '#5DADE2'; //  border color
    document.getElementById("gameborder").style.boxShadow = "10px 10px 10px rgb(123, 202, 236)"; //  box shadow color
    document.getElementById("scoreborder").style.boxShadow = "10px 10px 10px rgb(123, 202, 236)"; //  box shadow color
    document.getElementById('randomnumber').value =  ''; // clear input
    
}

