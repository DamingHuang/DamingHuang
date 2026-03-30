/*Select Items */
const alert = document.querySelector(".alert");
const form = document.querySelector(".postIt-form");
const posts = document.getElementById("posts");
const addBtn = document.querySelector(".btn-add");
const container = document.querySelector(".postIt-container");
const postIt_Items_container = document.querySelector(".postIt-Items-container");
const clearBtn = document.querySelector(".clr-btn");
/* commenting out as no longer used - formally part of delete function*/
//const postIt_item = document.querySelector(".postIt-item"); 
const btndel = document.querySelector(".btn-delete");



let currentPostItBGColor = 'postIt-Item';

let editElement;
let editFlag = false;
let editID = '';

// ****** EVENT LISTENERS **********
//Submit form
form.addEventListener("submit", PostsItem);
// clear items
clearBtn.addEventListener('click', clrItems);

// load items
window.addEventListener('DOMContentLoaded', setupPosts);
// ****** FUNCTIONS **********
// create a call back function that references from addEventListener
function PostsItem(e) {

    e.preventDefault();
    console.log(posts.value);
    //    assgin a value variable 
    const value = posts.value;
    const id = new Date().getTime().toString();

    if (value && !editFlag) {
        createPostItem(id, value);


        //display alert when item are added to list 
        displayAlert("item added to the list", "success");
        //when item is added success , show container 
        container.classList.add("show-container");

        //add to local storage
        addToLocalStorage(id, value);

        // set back to default 
        setBackToDefault();

        console.log("add item to the list");
    } else if (value && editFlag) {
        editElement.innerHTML = value;
        displayAlert("value changed", "success");
        // edit  local storage
        editLocalStorage(editID, value);
        setBackToDefault();
        console.log("editing");

    }
    else {
        console.log("empty vaule");
        displayAlert("please enter a vlue", "danger");
    }


}
//display alert functions

function displayAlert(text, action) {
    alert.textContent = text;
    alert.classList.add(`alert-${action}`);
    // remove alert
    setTimeout(function () {
        alert.textContent = " ";
        alert.classList.remove(`alert-${action}`);
    }, 1000);

}

// clear items
function clrItems() {
    const items = document.querySelectorAll('.postIt-Items-container');

    if (items.length > 0) {
        items.forEach(function (item) {
            postIt_Items_container.parentElement.parentElement;
        });
    }


    container.classList.remove('show-container');
    postIt_Items_container.textContent = null;
    displayAlert('empty posts');
    setBackToDefault();
    localStorage.removeItem('postIt_Items_container');

}


function deleteItem(e) {
   
    const element = e.target.closest('div[data-id]');
     
    console.log('delete event (e) :', e);
    
    element.remove();

     
    if (!postIt_Items_container.childElementCount) container.classList.remove("show-container");
    displayAlert("item removed", "danger");

    setBackToDefault();
  
    removeFromLocalStorage(element.dataset.id);
}

//edit function
function editPostText(e) {
    console.log('item-edited');

    const element = e.currentTarget.parentElement.parentElement.parentElement;
    //set edit item
    editElement = e.currentTarget.parentElement.parentElement.nextElementSibling;
    //console.log(element);

    //set form value
    posts.value = editElement.innerHTML;
    editFlag = true;
    editID = element.dataset.id;
    addBtn.textContent = "Edit";
}

//set back to default {
function setBackToDefault() {

    posts.value = '';
    editFlag = false;
    editID = '';

}



// ****** LOCAL STORAGE **********
function addToLocalStorage(id, value) {
    const posts = { id: id, value: value };
    console.log('add to local storage ');
    console.log(posts);
    let items = getLocalStorage();
    items.push(posts);
    localStorage.setItem("postIt_Items_container", JSON.stringify(items));

}
function removeFromLocalStorage(id) {
    let items = getLocalStorage();

    items = items.filter(function (item) {
        if (item.id !== id) {
            return item;
        }
    });
    localStorage.setItem("postIt_Items_container", JSON.stringify(items));


}
function editLocalStorage(id, value) {
    let items = getLocalStorage();
    items = items.map(function (item) {
        if (item.id === id) {
            item.value = value;
        }
        return item;
    });

    localStorage.setItem("postIt_Items_container", JSON.stringify(items));

}

function getLocalStorage() {
    return localStorage.getItem("postIt_Items_container") ? JSON.parse(localStorage.getItem("postIt_Items_container")) : [];
}
// ****** SETUP ITEMS **********
function setupPosts() {
    let items = getLocalStorage();  //getting item from local storage 
    if (items.length > 0) {
        items.forEach(function (item) {
            // these value are from local storage 
            createPostItem(item.id, item.value);
        });
        // last thing we want to do is to show the container
        container.classList.add("show-container");
    }

}
function createPostItem(id, value) {
    //create an element
    const element = document.createElement("div");


    
    element.classList.add(currentPostItBGColor);

    // add id (unique)
    const attr = document.createAttribute('data-id');
    //set up value for atrr
    attr.value = id;
    //add it to attr to element 
    element.setAttributeNode(attr);

    element.innerHTML = `
    <div class="postIt-item" >
        <div class="postIt-item-btn-container"  > 
        <button  class="btn-delete" type="button"  > <i class="fa fa-trash" aria-hidden="true"></i></button>
        <button  class="btn-edit" type="button"><i class="fa fa-pencil" aria-hidden="true"></i></button>
        </div>  
    </div> 
    <p id=""> ${value}</p>
    `;
    //append child
    postIt_Items_container.appendChild(element);
    const deletebtn = element.querySelector('.btn-delete');
    deletebtn.addEventListener('click', deleteItem);
    const editbtn = element.querySelector('.btn-edit');
    editbtn.addEventListener('click', editPostText);
    console.log(element);

}
function display() {
    // document.getElementById('dropdown').style.visibility = 'visible';

    var x = document.getElementById('dropdown');
    if (x.style.visibility === 'visible') {
        x.style.visibility = 'hidden';
    } else {
        x.style.visibility = 'visible';
    }

}

 
const buttons = document.querySelectorAll('button.btn');

for (let i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener('click', function () {

         
        const GETposts = document.querySelectorAll('div[data-id]');

        //loop through each post and add color class
        for (let j = 0; j < GETposts.length; j++) {
            console.log(j, GETposts[j]);

      
            currentPostItBGColor && GETposts[j].classList.remove(currentPostItBGColor);
            /* Add color class to postIt */
            GETposts[j].classList.add(this.dataset.color);
        }
        /* Update currentPostItBGColor - must be done outside the update loop*/
        currentPostItBGColor = this.dataset.color;
    });
}
