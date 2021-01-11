/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {

        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

const modal = document.querySelector('.modal');
const overlay = document.querySelector('.overlay')


function closeWindow(){
    modal.style.display = 'none';
    overlay.style.display = 'none';
}

function openWindow(){
    modal.style.display = 'inline-block';
    overlay.style.display = 'block';
}

const closeWindowBtn = document.querySelector('.closeWindowBtn');
closeWindowBtn.addEventListener('click', closeWindow)

const openWindowBtn = document.querySelector('.openWindowBtn');
openWindowBtn.addEventListener('click', openWindow);
