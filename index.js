const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelectorAll('.nav__link')  //find all the nav links
navToggle.addEventListener('click', () => {
    document.body.classList.toggle('nav-open');  //add a class to the body
});


navLinks.forEach(link => {
    link.addEventListener('click', () => {
     document.body.classList.remove('nav-open'); // use remove to close toggle
    })
})



const work = [
    {         
    
        category: "School_Work",
         
        img: 'img/Classroom.jpg' ,
   
        link:"<a class='text-layer' href='portfolioitem1.html'>Class Final</a>",
       
    },     
      {         
    
    category: "Bootcamp-Work",
    img:"img/portfolio-03.jpg",
  
    link:"<a class='text-layer' href='portfolioitem2.html'>Boot Camp</a>",
    },{         
    
        category: "Bootcamp-Work",
        img:"img/Bootcamp.jpg",
        link:"<a class='text-layer' href='portfolioitem3.html'>Boot Camp</a>",
        },{         
        
        category: "Bootcamp-Work",
        img:"img/Bootcamp1.jpg",
        link:"<a class='text-layer' href='portfolioitem4.html'>Boot Camp</a>",
        },{         
        
        category: "Personal-excerise",
        img:"img/Bootcamp3.jpg",
        link:"<a class='text-layer' href='portfolioitem5.html'>Personal Excerise</a>",
        },{         
        
        category: "Personal-excerise",
        img:"img/portfolio-04.jpg",
        link:"<a class='text-layer' href='portfolioitem6.html'>Personal Excerise</a>",
        }
        ,{         
        
            category: "Personal-excerise",
            img:"img/coffee.jpg",
            link:"<a class='text-layer' href='portfolioitem7.html'>Personal Excerise</a>",
            }
            ,{         
        
                category: "Bootcamp-Work",
                img:"img/bootcamp4.jpg",
                link:"<a class='text-layer' href='portfolioitem8.html'>Boot Camp</a>",
                }

    ]
    const BtnContainer = document.querySelector(".btn_container")
    const portfolio = document.querySelector (".portfolio");


    window.addEventListener("DOMContentLoaded",function(){
       // console.log ('Blank');
       displayWorkItems(work); // a call function to display work

    });

    function displayWorkItems(workitems){
       let displayWork = workitems.map(function(item){ 
           // console.log (item);

           return ` <div class ="Portfolio-Item-border">
           <!-- Portfolio item 01 -->
           <a class="portfolio__item">
               <img src=${item.img} alt="" class="portfolio__img">
            </a>
        <a class="text-layer">     ${item.link}       </a>   
         
            
           </div>
              
          
            ` ;
                    });
                console.log(displayWork);
                portfolio.innerHTML = displayWork.join("");
                }


    
    //filter items 
      
        const btnfilter = BtnContainer.querySelectorAll(".btn")
        console.log(btnfilter)
     

           
        btnfilter.forEach(function (btn) {  // referencing each every buttons as a pramaneter btn
       btn.addEventListener("click",function(e) { // for all button add.eventlisteer as click event ,
                                                 // e is the short var reference for event object which will be passed to event handlers.
           console.log(e.currentTarget.dataset);
           // dataset is not unquie to a button, on the element we can add an attribute with data prefix , for example, data- "choose any name" 
           //, data-id, data-category, etc. <button type="button" class="filter-btn" data-id="All">
            //data-id="ALL" reference all, you can reference your own type of button in your array category  "<button type="button" class="filter-btn" data-id=${category}>"
           const category = e.currentTarget.dataset.id;
           const workCategory = work.filter(function (wItem) {
       
           if (wItem.category === category) {// return to category is equal to certain category, for example category lunch = lunch ,school = school,
               return wItem;  //// return to ceartain category
           }
           });
               //need to setup category to all becuase ,we didnt have an all category yet
            if (category === "all") {
                displayWorkItems(work); // call the  diplayMenuItems(work)Function
               } else {
                 displayWorkItems(workCategory); // call the diplayMenuItems(workCategory)Function
           }
        });
      });
   


