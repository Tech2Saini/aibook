let searchbox = document.getElementById("searchbox");
let suggesion_box = document.getElementById("suggesion_box");
let searchcontainer = document.getElementById("searchcontainer");
let clearbtn = document.getElementById("clearbtn");
let submitbtn = document.getElementById("submitbtn");
let radiocard = document.querySelectorAll(".radiocard");
let radiocardOne = document.querySelector(".radiocard");

let toolIconImg = document.getElementById("toolIconImg");
let iconurl = document.getElementById("iconurl");

function emptySearchBox(){
    clearbtn.classList.toggle("d-none");
    searchbox.value = "";
    suggesion_box.classList.add('d-none');
    searchcontainer.classList.remove("rounded-bottom-0")

}

function fillSearchBox(){
    suggesion_box.classList.remove('d-none');
    document.getElementById('clearbtn').classList.remove('d-none')
    searchcontainer.classList.add("rounded-bottom-0")

    if (searchbox.value.length <1) {
        console.log("empty box")
        emptySearchBox()
    }
}

function changeSelection(obj){
    unCheckAll()

    parent = obj.parentElement;
    parent.classList.add('btn-dark')
}

function unCheckAll(){
    radiocard.forEach(element => {
        element.classList.remove("btn-dark")
    });
}

function addSearch(obj){
    searchbox.value = obj.innerText;
    setTimeout(() => {
        submitbtn.click()
    }, 500);
}

function showIconUrl(target){
    console.log(iconurl.value)
    toolIconImg.src = iconurl.value
}

