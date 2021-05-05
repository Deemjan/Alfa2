function expand() {
            let acc = document.getElementsByClassName("signature_button");
            let i;

            for (i = 0; i < acc.length; i++) {
                acc[i].addEventListener("click", function () {
                    /* Toggle between adding and removing the "active" class,
                    to highlight the button that controls the panel */
                    this.classList.toggle("active");

                    /* Toggle between hiding and showing the active panel */
                    let panel = this.nextElementSibling;
                    if (panel.style.display === "block") {
                        panel.style.display = "none";
                    } else {
                        panel.style.display = "block";
                    }
                });
            }
        }


        expand();

formElem.onsubmit = async (e) => {
    e.preventDefault();

    let select = document.querySelector('.uploaddoc');
    let input = select.querySelector('input[type="file"]');
    const token = select.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(formElem);
    data.append('usert', 'hubot');
    let response = await fetch("testUploadDoc", {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
    });
    let result = await response.json();
    console.log(result);
    alert(result.message);
};

formElem_sing_doc.onsubmit = async (e) => {
    e.preventDefault();

    let select = document.querySelector('.singdoc');
    const token = select.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(formElem_sing_doc);
    let response = await fetch("testSingDoc", {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
    });
    let result = await response.json();
    console.log(result);
    alert(result.message);
};


formElem_verify_doc.onsubmit = async (e) => {
    e.preventDefault();

    let select = document.querySelector('.verify');
    const token = select.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(formElem_verify_doc);
    let response = await fetch("testVerifyDoc", {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
    });
    let result = await response.json();
    console.log(result);
    alert(result.message);
};

fillUserDocumentsTable();

function fillUserDocumentsTable(){
    let docTable = document.getElementById("docTable");
    let docInfo = getUserDocuments();
    console.log(docInfo)
    for (let i = 0; i < 3;i++){
        let newRow = docTable.insertRow(docTable.length)
        for (let j = 0; j< 3;j++){
            let cell = newRow.insertCell(j);
            cell.innerHTML = "1";
        }
    }
}

async function getUserDocuments() {
    let response = await fetch("testGetUsersDocs", {
        method: 'GET',
        credentials: "same-origin"
    });
    if (response.ok){
        let json = await response.json()
        console.log(json)
        console.log(json.docs)
        console.log(json.success)
        return(json.docs)
    }
    else(
        console.log(response.status)
    )
}